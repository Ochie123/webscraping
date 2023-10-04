from selenium import webdriver

# Configure the Selenium options
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Run Chrome in headless mode (no browser window)
options.add_argument('--disable-gpu')  # Disable GPU acceleration
options.add_argument('--no-sandbox')  # Disable sandboxing for compatibility on some systems

# Create a WebDriver instance
driver = webdriver.Chrome(options=options)

website_url = 'http://www.jobs.utah.gov'  # Replace with the website causing issues

try:
    driver.get(website_url)
    html_content = driver.page_source
    # Now you can parse the HTML content with BeautifulSoup or any other library

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()  # Close the browser instance
