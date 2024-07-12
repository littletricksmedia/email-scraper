import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# Function to extract email from source code
def extract_email_from_source(source):
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", source)
    return emails

# Function to extract additional details from source code
def extract_additional_details_from_source(source):
    try:
        match = re.search(r'<div class="wt-mb-xs-4 additional-details-section".*?>(.*?)</div>', source, re.DOTALL)
        if match:
            details_html = match.group(1)
            details_text = re.sub('<[^<]+?>', '', details_html)  # Remove HTML tags
            details_text = details_text.strip()  # Remove leading/trailing whitespace
            return details_text
        else:
            return 'No additional details found'
    except Exception as e:
        return f"Error extracting details: {e}"

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')

# Initialize the Chrome driver
driver = webdriver.Chrome(options=chrome_options)

# Read Etsy listing URLs from CSV file
csv_file = 'jewellery-earring-url-1.csv' 
df = pd.read_csv(csv_file)

# Check the column name and ensure it matches
listing_urls = df['listing_url'].tolist()

# List to hold the data
scraped_data = []

# Iterate over each listing URL
for url in listing_urls:
    try:
        driver.get(url)
        time.sleep(3)  # Adjust sleep time as needed
        
        # Scroll down to load the page fully
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Adjust sleep time as needed

        # Extract page source
        source = driver.page_source

        # Extract emails from the source code
        emails = extract_email_from_source(source)
        
        # Continue only if emails are found
        if emails:
            emails = ', '.join(emails)
            
            # Extract additional details from the source code
            additional_details = extract_additional_details_from_source(source)
            
            # Debug: Print the extracted details
            print(f"URL: {url}")
            print(f"Emails: {emails}")
            print(f"Additional Details: {additional_details}")
            
            # Append the extracted data to the list
            scraped_data.append({
                'listing_url': url,
                'email': emails,
                'additional_details': additional_details,
            })
        else:
            print(f"No emails found for {url}")
    
    except Exception as e:
        print(f"Error processing {url}: {e}")
        scraped_data.append({
            'listing_url': url,
            'email': 'Error',
            'additional_details': f'Error: {e}'
        })

# Close the driver
driver.quit()

# Save the scraped data to a CSV file
output_df = pd.DataFrame(scraped_data)
output_df.to_csv('necklaces_pendant_scraped_data.csv', index=False)

print("Scraping complete. Data saved to necklaces_pendant_scraped_data.csv")
