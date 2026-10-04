import requests
from bs4 import BeautifulSoup
import openpyxl
from urllib.parse import urlparse
import re

# Function to perform web scraping and save data to an Excel file
def scrape_and_save(urls, directory, name, fields):
    output_file = directory + '/' + name + '.xlsx'
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Scraped Data"
    headers = [i[1] for i in fields]
    ws.append(headers)

    for url in urls:
        print(f"Scraping URL: {url}")
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = "http://" + url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                extracted_data = []
                print(fields)
                for field in fields:
                    field_name, left_selector, right_selector, only_numbers, default_value = field[1:6]
                    data = default_value  # Use default value if provided
                    if not data:
                        # Clean and format the selector for use in BeautifulSoup
                        if '<' in left_selector:
                            # Extracting tag and class/id from the left_selector
                            tag = left_selector.split()[0].replace('<', '')
                            class_or_id = ''.join(left_selector.split()[1:]).replace('>', '').replace("'", "")
                            css_selector = f'{tag}.{class_or_id.split("=")[1]}'
                            data_element = soup.select_one(css_selector)
                            data = data_element.get_text(strip=True) if data_element else ""
                        else:
                            pattern = f'{left_selector}(.*?){right_selector}'
                            data_elements = re.findall(pattern, str(soup), re.S)
                            data = data_elements[0].strip() if data_elements else ""
                    if only_numbers:
                        data = ''.join(filter(str.isdigit, data))
                    extracted_data.append(data)
                ws.append(extracted_data)
        except Exception as e:
            print(f"Error scraping URL {url}: {e}")

    wb.save(output_file)