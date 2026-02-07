from deep_translator import GoogleTranslator

def translate_text(text, target_lang='pt'):
    """
    Translates text to the target language using Google Translator.
    """
    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
        return translated
    except Exception as e:
        print(f"Error translating text: {e}")
        return text
