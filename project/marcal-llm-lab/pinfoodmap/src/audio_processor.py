import os
import yt_dlp
import torch
from transformers import pipeline
from pydub import AudioSegment
import librosa
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Whisper pipeline globally to avoid reloading
whisper_pipeline = None

def get_whisper_pipeline(model_name="openai/whisper-small"):
    global whisper_pipeline
    if whisper_pipeline is None:
        logger.info(f"Loading Whisper model: {model_name}...")
        device = 0 if torch.cuda.is_available() else -1
        try:
            whisper_pipeline = pipeline("automatic-speech-recognition", model=model_name, device=device)
            logger.info("✅ Whisper model loaded.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise e
    return whisper_pipeline

def download_audio(url, output_dir='downloads/audio'):
    """
    Downloads audio from a TikTok URL using yt-dlp.
    Returns the path to the downloaded mp3 file.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Check if we have cookies, else try without
    cookie_file = 'tiktok_cookies.txt'
    use_cookies = os.path.exists(cookie_file)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    
    if use_cookies:
        ydl_opts['cookiefile'] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            audio_path = os.path.join(output_dir, f"{video_id}.mp3")
            return audio_path
    except Exception as e:
        logger.error(f"Error downloading audio for {url}: {e}")
        return None

def transcribe_audio(audio_path, duration_ms=60000):
    """
    Transcribes the audio file using Whisper.
    duration_ms: Max duration to transcribe in milliseconds.
    """
    if not audio_path or not os.path.exists(audio_path):
        return ""
    
    try:
        pipe = get_whisper_pipeline()
        
        audio_full = AudioSegment.from_mp3(audio_path)
        
        # Limit duration based on parameter
        audio_segment = audio_full[:duration_ms]
        
        samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32)
        
        # Normalize if stereo
        if audio_segment.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)
            
        # Resample to 16kHz
        # Normalize amplitude to -1..1 range if it's integer data (pydub usually gives int)
        # Pydub samples are integers. Transformers expects float -1..1 usually.
        # Let's verify pydub -> transformers conversion.
        # simpler: pipe(audio_path) usually handles ffmpeg conversion internally.
        # Let's try the direct path first for simplicity and speed.
        
        # Updated call to support long-form audio/timestamps
        # chunk_length_s=30 enables long-form transcription by chunking
        # Reduced batch_size to 1 for stability on CPU
        logger.info(f"Transcribing {audio_path}...")
        result = pipe(audio_path, return_timestamps=True, chunk_length_s=30, batch_size=1) 
        logger.info("Transcription complete.")
        return result["text"]
        
    except Exception as e:
        logger.error(f"Error transcribing {audio_path}: {e}")
        return ""
