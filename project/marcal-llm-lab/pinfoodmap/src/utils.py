# src/utils.py

import pandas as pd
import time

def save_to_csv(data, filename):
    """
    Save a list of strings to a CSV file.
    """
    df = pd.DataFrame(data, columns=["text"])
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(data)} items to {filename}")

def scroll_down(driver, scrolls=10, pause=2):
    """
    Scroll down the page to load more items.
    """
    for _ in range(scrolls):
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(pause)

def scroll_up_chat(driver, chat_element, scrolls=15, pause=2):
    """
    Scroll up inside a chat to load old messages.
    """
    for _ in range(scrolls):
        driver.execute_script("arguments[0].scrollTop = 0", chat_element)
        time.sleep(pause)
