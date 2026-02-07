# main.py

import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Import Keys for RETURN
from bs4 import BeautifulSoup
import pandas as pd
from src.scraper import start_driver, scrape_favorites, scrape_chat
from src.classifier import is_food_related
from src.enhanced_classifier import classify_content as classify_content_enhanced
from src.utils import save_to_csv

# Load environment variables
load_dotenv()  # Loads variables from the .env file

tiktok_login = os.getenv("tiktok_login")
tiktok_password = os.getenv("tiktok_password")

def login(driver):
    """
    Log in to TikTok using the credentials from .env.
    """
    driver.get("https://www.tiktok.com/login/phone-or-email/email")
    
    # Wait for login page to load
    input("Please go to TikTok's login page, log in manually, then press ENTER to continue...")
    
    # Alternatively, you can use the username/password with Selenium (needs careful handling)
    if tiktok_login and tiktok_password:
        username_field = driver.find_element(By.XPATH, "//input[@name='username']")
        password_field = driver.find_element(By.XPATH, "//input[@name='password']")
        
        username_field.send_keys(tiktok_login)
        password_field.send_keys(tiktok_password)
        password_field.send_keys(Keys.RETURN)
    
    print("Logged in!")

def main():
    print("Initializing browser (please wait)...")
    driver = start_driver()
    print("Browser initialized.")
    
    # Automatically log in with credentials
    #login(driver)
    
    # login(driver) - Manual login now handled in scraper function or via undetected_chromedriver
    
    mode = input("Select mode (favorites/chat/json): ").strip().lower()
    
    # Ask about classifier type
    use_enhanced = input("Use enhanced classifier? (y/n) [default: y]: ").strip().lower()
    use_enhanced = use_enhanced != 'n'  # Default to yes
    
    if use_enhanced:
        print("✅ Using enhanced classifier with multi-layered validation")
    else:
        print("ℹ️  Using simple classifier")

    if mode == "favorites":
        texts = scrape_favorites(driver)
        print("🔍 Filtering food-related content...")
        if use_enhanced:
            results = []
            for text in texts:
                classification = classify_content_enhanced(text)
                if classification['is_food_related']:
                    results.append({
                        'Text': text,
                        'Confidence': classification['confidence'],
                        'Reasoning': classification['reasoning']
                    })
            pd.DataFrame(results).to_csv(f"data/processed/food_related_{mode}_enhanced.csv", index=False)
            print(f"Saved {len(results)} food-related items with details")
        else:
            food_texts = [text for text in texts if is_food_related(text)]
            save_to_csv(food_texts, f"data/processed/food_related_{mode}.csv")
        
    elif mode == "chat" or mode == "json":
        links = []
        if mode == "chat":
            links = scrape_chat(driver)
        elif mode == "json":
            from src.json_parser import load_json_data, extract_links_from_json
            default_path = "data/raw/user_data_tiktok.json"
            json_path_input = input(f"Enter path to TikTok data JSON file [{default_path}]: ").strip().replace("\"", "")
            json_path = json_path_input if json_path_input else default_path
            
            data = load_json_data(json_path)
            if data:
                # Ask for date filtering
                days_input = input("Enter days limit (e.g., 7 for last week, or Enter for all): ").strip()
                days_limit = int(days_input) if days_input.isdigit() else None
                
                links = extract_links_from_json(data, days_limit=days_limit)
            else:
                links = []

        print(f"Processing {len(links)} links...")
        
        results = []
        from src.translator import translate_text
        from src.extractor import extract_entities
        import time
        # We need the driver for visiting links even if we got them from JSON
        # If scraper wasn't called, driver might not be started if I moved start_driver inside
        # But start_driver IS called at start of main(), so we are good.
        
        # Helper to process audio
        def process_audio_safely(link, duration_ms=60000):
            try:
                from src.audio_processor import download_audio, transcribe_audio, get_whisper_pipeline
                # Ensure model is loaded once
                get_whisper_pipeline() 
                
                audio_path = download_audio(link)
                if audio_path:
                    text = transcribe_audio(audio_path, duration_ms=duration_ms)
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                    return text
            except Exception as e:
                print(f"Audio processing failed: {e}")
            return ""

        output_csv = f"data/processed/processed_{mode}_intermediate.csv"

        for i, link in enumerate(links):
            print(f"Processing {i+1}/{len(links)}: {link}")
            
            try:
                driver.get(link)
                time.sleep(3)
                
                soup = BeautifulSoup(driver.page_source, "html.parser")
                description = ""
                meta_desc = soup.find("meta", {"name": "description"})
                if meta_desc:
                    description = meta_desc.get("content", "")
                
                # STEP 1: PRE-VALUATION (15 Seconds)
                print("  - [Step 1] Pre-transcribing (15s) for valuation...")
                pre_transcription = process_audio_safely(link, duration_ms=15000)
                
                pre_content = f"{description}\n {pre_transcription}".strip()
                
                if not pre_content:
                    print("  - No content. Skipping.")
                    continue
                
                # Translate truncated for valuation
                val_text = pre_content[:4500] 
                translated_val = translate_text(val_text)
                
                # Classify
                print("  - [Step 1] Classifying...")
                if use_enhanced:
                    classification = classify_content_enhanced(translated_val)
                    is_food = classification['is_food_related']
                    confidence = classification['confidence']
                    reasoning = classification['reasoning']
                else:
                    is_food = is_food_related(translated_val)
                    confidence = 1.0 if is_food else 0.0
                    reasoning = "Simple classifier"
                
                if not is_food:
                    print("  - Not food-related. Skipping.")
                    result_entry = {
                        "Link": link,
                        "Description": description,
                        "Category": "Other",
                        "Transcription": pre_transcription
                    }
                    if use_enhanced:
                        result_entry["Confidence"] = confidence
                        result_entry["Classification_Reasoning"] = reasoning
                    results.append(result_entry)
                    continue

                # STEP 2: FULL PROCESSING (Only for Food)
                print("  - [Step 2] Full transcribing (Food detected)...")
                full_transcription = process_audio_safely(link, duration_ms=120000) # 2 mins max
                
                full_content = f"{description}\n {full_transcription}"
                
                # Translate (Truncate to avoid 5000 limit)
                print("  - [Step 2] Translating full content...")
                translated_full = translate_text(full_content[:4500])
                
                # Extract Entities
                print("  - [Step 2] Extracting entities...")
                entities = extract_entities(translated_full)
                locations = entities["locations"]
                organizations = entities["organizations"]

                result_entry = {
                    "Link": link,
                    "Description": description,
                    "Transcription": full_transcription,
                    "Translated Content": translated_full,
                    "Category": "Food",
                    "Locations": ", ".join(locations),
                    "Restaurants": ", ".join(organizations)
                }
                
                # Add enhanced classification details if using enhanced classifier
                if use_enhanced:
                    result_entry["Confidence"] = confidence
                    result_entry["Classification_Reasoning"] = reasoning
                
                results.append(result_entry)
                
                pd.DataFrame(results).to_csv(output_csv, index=False)
                
            except Exception as e:
                print(f"Error processing {link}: {e}")

        # Filter and Save
        df = pd.DataFrame(results)
        if not df.empty:
            df.to_csv(f"data/processed/processed_{mode}.csv", index=False)
            print(f"Saved to processed_{mode}.csv")
            
            food_df = df[df['Category'] == 'Food']
            food_df.to_csv(f"data/processed/food_related_{mode}_translated.csv", index=False)
            print(f"Saved {len(food_df)} food-related items to food_related_{mode}_translated.csv")
        else:
            print("No data found.")

    else:
        print("Invalid mode selected.")
        driver.quit()
        return

if __name__ == "__main__":
    main()
