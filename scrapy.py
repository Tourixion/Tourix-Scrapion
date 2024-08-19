import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def wait_and_click(driver, selector, by=By.CSS_SELECTOR, timeout=10):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, selector))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)
        element.click()
        logger.info(f"Successfully clicked element: {selector}")
        return True
    except Exception as e:
        logger.error(f"Failed to click element {selector}: {str(e)}")
        return False

def login_and_scrape(url, email, password):
    logger.info(f"Starting scraper for URL: {url}")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Add these options to automatically download files
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "/github/workspace/downloads",  # Adjust this path for GitHub Actions
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        logger.info(f"Navigated to: {driver.current_url}")

        # Login
        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-input:nth-child(2)")))
        email_input.send_keys(email)
        logger.info("Entered email")

        password_input = driver.find_element(By.CSS_SELECTOR, ".ant-input:nth-child(1)")
        password_input.send_keys(password)
        logger.info("Entered password")

        login_button = driver.find_element(By.CSS_SELECTOR, ".ant-btn")
        login_button.click()
        logger.info("Clicked login button")

        # Wait for the page to change after login
        WebDriverWait(driver, 20).until(EC.url_changes(url))
        logger.info(f"Page changed after login. New URL: {driver.current_url}")

        # Click the '.btn' element (possibly for authentication)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn"))).click()
        logger.info("Clicked .btn element")

        # Navigate to reviews
        reviews_icon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".fa-comment-o")))
        reviews_icon.click()
        logger.info("Clicked reviews icon")

        reviews_header = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".reviews-header")))
        reviews_header.click()
        logger.info("Clicked reviews header")

        # Mouse over and out of '.active > a' element
        active_element = driver.find_element(By.CSS_SELECTOR, ".active > a")
        actions = ActionChains(driver)
        actions.move_to_element(active_element).perform()
        actions.move_to_element(driver.find_element(By.TAG_NAME, "body")).perform()
        logger.info("Performed mouse over and out actions")

        # Click on date picker and select a tag
        date_picker = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-calendar-range-picker-input:nth-child(3)")))
        date_picker.click()
        logger.info("Clicked date picker")

        tag = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-tag:nth-child(3)")))
        tag.click()
        logger.info("Selected tag")

        # Click download link
        download_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".download-link path")))
        download_link.click()
        logger.info("Clicked download link")

        # Wait for and click the download confirmation button
        confirmation_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-btn-primary")))
        confirmation_button.click()
        logger.info("Clicked download confirmation button")

        # Wait for download to complete (adjust the time as needed)
        time.sleep(10)
        logger.info("Waited for download to complete")

        logger.info("Scraping and download process completed")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        driver.quit()
        logger.info("Scraper finished, browser closed")

if __name__ == "__main__":
    login_url = "https://app.localclarity.com/login"
    username = os.environ.get('LC_USERNAME')
    password = os.environ.get('LC_PASSWORD')
    login_and_scrape(login_url, username, password)