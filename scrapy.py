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
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv")
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("browser.download.manager.closeWhenDone", True)
    firefox_options.set_preference("browser.download.manager.focusWhenStarting", False)
    firefox_options.set_preference("browser.download.useDownloadDir", True)
    
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
            authorize_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".profile-item:nth-child(1) .ant-btn")))
            authorize_button.click()
            logger.info("Clicked authorize button")
            time.sleep(5)  # Wait for authorization to complete
        except TimeoutException:
            logger.info("No authorization needed")

        # Navigate to reviews
        if not wait_and_click(driver, ".fa-comment-o"):
            raise Exception("Failed to navigate to reviews")
        logger.info("Navigated to reviews")

        # Select date range and download CSV
        if not wait_and_click(driver, ".ant-calendar-range-picker-input:nth-child(3)"):
            raise Exception("Failed to open date range picker")
        if not wait_and_click(driver, ".ant-tag:nth-child(3)"):
            raise Exception("Failed to select date range")
        if not wait_and_click(driver, ".download-link path"):
            raise Exception("Failed to click download link")
        if not wait_and_click(driver, ".ant-btn-primary"):
            raise Exception("Failed to confirm download")
        
        logger.info("Initiated CSV download")

        # Wait for download to complete
        download_wait_time = 30  # Increased wait time to 30 seconds
        for i in range(download_wait_time):
            time.sleep(1)
            files = os.listdir(download_dir)
            csv_files = [f for f in files if f.endswith('.csv')]
            if csv_files:
                logger.info(f"CSV file found after {i+1} seconds")
                break
            if i % 5 == 0:
                logger.info(f"Waiting for download... {i+1} seconds elapsed")
        else:
            logger.error(f"No CSV file found after waiting for {download_wait_time} seconds")

        # Check download directory
        logger.info(f"Checking contents of download directory: {download_dir}")
        files = os.listdir(download_dir)
        logger.info(f"Files in download directory: {files}")
        csv_files = [f for f in files if f.endswith('.csv')]
        
        if csv_files:
            old_file = os.path.join(download_dir, csv_files[0])
            new_file = os.path.join(download_dir, "localclarity_data.csv")
            os.rename(old_file, new_file)
            logger.info(f"Renamed downloaded file from {csv_files[0]} to localclarity_data.csv")
        else:
            logger.error("No CSV file found in the download directory")
            raise Exception("Download failed: No CSV file found")

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
