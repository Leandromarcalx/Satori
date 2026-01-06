from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium import By

def initialize_chromedriver():
    # Setup Chrome options if needed
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')  # Start browser maximized
    options.add_argument('--disable-blink-features=AutomationControlled')  # Disable automation control flag

    # Initialize ChromeDriver using WebDriver Manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver

# Example usage:
driver = initialize_chromedriver()
driver.get("https://www.zara.com/br/pt/man-sale-l7139.html?v1=2212606")

driver.find_element(By.XPATH, "")