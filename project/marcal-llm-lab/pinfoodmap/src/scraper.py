import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from src.utils import scroll_down, scroll_up_chat
import time

def start_driver():
    options = uc.ChromeOptions()
    options.add_argument('--start-maximized')
    # undetected-chromedriver downloads the driver automatically
    # Specifying version to match user's Chrome (144) to avoid mismatch
    driver = uc.Chrome(options=options, version_main=144)
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
    time.sleep(3)

    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    # Try multiple selectors for the chat container
    chat_selectors = [
        "//*[@id='main-content-messages']",
        "//div[contains(@data-e2e, 'chat-room')]",
        "//div[contains(@class, 'chat-room')]", 
        "//div[contains(@class, 'ChatContainer')]",
        "//div[contains(@class, 'chat')]"
    ]

    chat_area = None
    for selector in chat_selectors:
        try:
            print(f"Trying to find chat area with: {selector}")
            chat_area = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, selector))
            )
            print("Chat area found!")
            break
        except:
            continue
    
    anchors = []
    if chat_area:
        try:
            # Scroll up to load snippets of history, but not too much if we only want recent
            scroll_up_chat(driver, chat_area, scrolls=5) 
            anchors = chat_area.find_elements(By.TAG_NAME, "a")
        except Exception as e:
            print(f"Could not scroll: {e}")
            anchors = chat_area.find_elements(By.TAG_NAME, "a")
    else:
        print("⚠️ Chat container not found. Looking for message items directly...")
        # Fallback: Look for message items directly
        # data-e2e="message-item" is common
        messages = driver.find_elements(By.XPATH, "//*[contains(@data-e2e, 'message')]")
        if messages:
            print(f"Found {len(messages)} message items directly.")
            for msg in messages:
                anchors.extend(msg.find_elements(By.TAG_NAME, "a"))
        else:
            print("❌ Could not find Chat Area OR Message Items.")
            print("Please ensure you are inside a specific chat conversation.")
            return []

    # Filter for actual video links (from anchors determined above)
    links = []
    for anchor in anchors:
        try:
            href = anchor.get_attribute("href")
            # Filter for actual video links
            if href and ("tiktok.com" in href) and ("/video/" in href):
                links.append(href)
        except:
            continue
    
    # Remove duplicates but keep order (assuming list is in chronological order of appearance in DOM)
    # In many chat DOMs, lower elements are newer.
    unique_links = []
    seen = set()
    for link in links:
        if link not in seen:
            unique_links.append(link)
            seen.add(link)
            
    # Return only the last 'limit' links (most recent)
    limit = 10
    recent_links = unique_links[-limit:] if limit < len(unique_links) else unique_links
    
    print(f"Found {len(unique_links)} unique links. Keeping the last {len(recent_links)} (most recent).")
    return recent_links
