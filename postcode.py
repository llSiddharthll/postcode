from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

# Install the ChromeDriver
chromedriver_autoinstaller.install()

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape_postcode_data():
    postcode = request.json.get('postcode')
    
    # Configure Selenium WebDriver for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--window-size=1920x1080")
    
    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the target website
    driver.get("https://www.utilitybidder.co.uk/business-gas/")

    # Handle cookie consent if it appears
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll'))
        )
        cookie_button.click()
    except Exception:
        pass

    # Input the postcode
    postcode_field = driver.find_element(By.ID, 'address')
    postcode_field.send_keys(postcode)

    # Click the "Compare Prices" button
    compare_button = driver.find_element(By.XPATH, '//button[@id="search"]')
    compare_button.click()

    # Wait for the results to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'addressSelect')))

    # Extract all options from the select field
    select_element = driver.find_element(By.ID, 'addressSelect')
    options = select_element.find_elements(By.TAG_NAME, 'option')

    # Format the options as a list of dictionaries for JSON response
    option_data = [{"address": option.text} for option in options[1:]]

    # Close the browser
    driver.quit()

    return jsonify(option_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
