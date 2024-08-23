import os
import logging
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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
    
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    
    # Set up Firefox options for downloads
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("browser.download.dir", "/github/workspace/downloads")
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream,application/vnd.ms-excel")
    
    service = FirefoxService('geckodriver')
    driver = webdriver.Firefox(service=service, options=firefox_options)
    
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

        # Ensure the element is present in the DOM
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".profile-item:nth-child(1) .ant-btn")))

        # Wait for the element to be clickable and then click it
        driver.get("https://app.localclarity.com/authorize")
        driver.set_window_size(1061, 679)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".profile-item:nth-child(1) .ant-btn"))).click()
        logger.info("Clicked .profile-item:nth-child(1) .ant-btn element")

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
        date_picker = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ant-calendar-range-picker-input:nth-child(2)")))
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
