import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService

# Set up the Selenium WebDriver (update the path to your chromedriver as needed)
service = ChromeService(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)

# URL of the page that contains the table with legislation links
table_url = "https://www.legislation.gov.uk/all?title=The%20Legal%20Aid%20%28Financial%20Resources%20and%20Payment%20for%20Services%29"
driver.get(table_url)
time.sleep(2)  # Allow the page to load

# Extract all legislation URLs and titles from the table.
rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
legislation_items = []
for row in rows:
    try:
        link_element = row.find_element(By.TAG_NAME, "a")
        href = link_element.get_attribute("href")
        title = link_element.text.strip().replace(" ", "_")
        legislation_items.append((href, title))
    except Exception as e:
        print(f"Error extracting link from a row: {e}")

driver.quit()

def get_pdf_url(legislation_url):
    """
    Constructs the PDF URL.
    Expected structure for a legislation URL is:
      https://www.legislation.gov.uk/<act-type>/<year>/<number>/...
    This function takes the first six parts and appends '/data.pdf'
    """
    parts = legislation_url.split('/')
    if len(parts) >= 7:
        base = "/".join(parts[:6])
        return base + "/data.pdf"
    return None

# Process each legislation item by constructing the PDF URL and downloading the file.
for legislation_url, legislation_title in legislation_items:
    try:
        pdf_url = get_pdf_url(legislation_url)
        if pdf_url is None:
            print(f"Could not generate PDF URL for {legislation_title}")
            continue
        print(f"Downloading PDF from: {pdf_url}")
        
        # Download the PDF file with a common user-agent header.
        response = requests.get(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code == 200:
            filename = f"{legislation_title}_Whole_Act.pdf"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Saved PDF as: {filename}")
        else:
            print(f"Failed to download PDF for {legislation_title}: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error processing {legislation_title}: {e}")
