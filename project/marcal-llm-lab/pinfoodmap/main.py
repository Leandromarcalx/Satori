# main.py

import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  # Import Keys for RETURN
from src.scraper import start_driver, scrape_favorites, scrape_chat
from src.classifier import is_food_related
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
    driver = start_driver()
    
    # Automatically log in with credentials
    #login(driver)
    
    mode = input("Select mode (favorites/chat): ").strip().lower()

    if mode == "favorites":
        texts = scrape_favorites(driver)
    elif mode == "chat":
        texts = scrape_chat(driver)
    else:
        print("Invalid mode selected.")
        driver.quit()
        return

    driver.quit()

    print("🔍 Filtering food-related content...")
    food_texts = [text for text in texts if is_food_related(text)]

    save_to_csv(food_texts, f"food_related_{mode}.csv")

if __name__ == "__main__":
    main()
