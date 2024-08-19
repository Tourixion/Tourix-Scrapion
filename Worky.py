from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    # Set up the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    return driver

def interact_with_button(driver, url, button_xpath):
    # Navigate to the webpage
    driver.get(url)

    try:
        # Wait for the button to be clickable (timeout after 10 seconds)
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )

        # Click the button
        button.click()

        print("Button clicked successfully!")

        # Here you can add code to handle what happens after clicking the button
        # For example, wait for a new element to appear, or extract some data

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the browser
        driver.quit()

if __name__ == "__main__":
    driver = setup_driver()
    
    # Replace with your target URL and the XPath of the button
    target_url = "https://app.localclarity.com/reviews"
    button_xpath = "//button[@id='submit-button']"
    
    interact_with_button(driver, target_url, button_xpath)
