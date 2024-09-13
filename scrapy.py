import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
    
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    
    download_dir = os.path.join(os.getcwd(), "downloads")
    logger.info(f"Setting download directory to: {download_dir}")
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("browser.download.dir", download_dir)
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/json")
    
    service = FirefoxService(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    
    try:
        driver.get(url)
        logger.info(f"Navigated to: {driver.current_url}")

        # Login process
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

        # Check if authorization is needed
        try:
            authorize_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".profile-item:nth-child(1) .ant-btn")))
            authorize_button.click()
            logger.info("Clicked authorize button")
            time.sleep(5)  # Wait for authorization to complete
        except TimeoutException:
            logger.info("No authorization needed")

        # Wait for the main dashboard to load
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
        logger.info("Main dashboard loaded")

        # Try to find the reviews icon multiple times
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                reviews_icon = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".fa-comment-o")))
                reviews_icon.click()
                logger.info("Clicked reviews icon")
                break
            except TimeoutException:
                if attempt < max_attempts - 1:
                    logger.warning(f"Attempt {attempt + 1} to find reviews icon failed. Retrying...")
                    time.sleep(5)
                else:
                    raise Exception("Failed to navigate to reviews after multiple attempts")

        # Continue with the rest of your script (date range selection, download, etc.)
        # ...

        logger.info("Scraping and download process completed")

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise
    finally:
        driver.quit()
        logger.info("Scraper finished, browser closed")

if __name__ == "__main__":
    login_url = "https://app.localclarity.com/login"
    username = os.environ.get('LC_USERNAME')
    password = os.environ.get('LC_PASSWORD')
    try:
        login_and_scrape(login_url, username, password)
    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}")
        exit(1)
    password = os.environ.get('LC_PASSWORD')
    login_and_scrape(login_url, username, password)
