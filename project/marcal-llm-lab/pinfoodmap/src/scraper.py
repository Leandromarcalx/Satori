# src/scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from src.utils import scroll_down, scroll_up_chat
import time

def start_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)
    return driver

def scrape_favorites(driver):
    """
    Scrape TikTok Favorites captions.
    """
    driver.get("https://www.tiktok.com/favorites")
    input("⚡ Login manually and press ENTER to start scraping favorites...")
    time.sleep(5)

    scroll_down(driver, scrolls=20)

    elements = driver.find_elements(By.XPATH, "//div[contains(@class,'video-feed-item')]//p")
    texts = [el.text.strip() for el in elements if el.text.strip()]
    print(f"Found {len(texts)} items in Favorites.")
    return texts

def scrape_chat(driver):
    """
    Scrape a specific TikTok chat messages.
    """
    driver.get("https://www.tiktok.com/messages")
    input("⚡ Login manually, open the chat, then press ENTER to start scraping chat...")
    time.sleep(5)

    chat_area = driver.find_element(By.XPATH, "//div[contains(@class,'chat')]")
    scroll_up_chat(driver, chat_area, scrolls=15)

    elements = driver.find_elements(By.XPATH, "//div[contains(@class,'bubble-content')]")
    texts = [el.text.strip() for el in elements if el.text.strip()]
    print(f"Found {len(texts)} messages in Chat.")
    return texts
