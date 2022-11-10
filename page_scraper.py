"""
page_scraper: the script takes an url* of one of the subcategories in the Shufersal site and prints
the following attributes for each product in that category:
    - product name
    - price
    - price unit
    - container
    - supplier
"""

import time
import requests
from bs4 import BeautifulSoup
# ____selenium____
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

## main url
MAIN_URL = "https://www.shufersal.co.il/online/he/%D7%A7%D7%98%D7%92%D7%95%D7%A8%D7%99%D7%95%D7%AA/%D7%A1%D7%95%D7%A4%D7%A8%D7%9E%D7%A8%D7%A7%D7%98/%D7%A4%D7%99%D7%A8%D7%95%D7%AA-%D7%95%D7%99%D7%A8%D7%A7%D7%95%D7%AA/c/A04"



def main():
    # ---- activate selenium____
    DELAY = 50
    options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1920, 1080)
    driver.get(MAIN_URL)
    actions = ActionChains(driver)

    for scroll in range(10):
        SCROLL_PAUSE_TIME = 5
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

    # # Get scroll height
    # last_height = driver.execute_script("return document.body.scrollHeight")
    # SCROLL_PAUSE_TIME = 5
    #
    # while True:
    #     # Scroll down to bottom
    #     driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    #
    #     # Wait to load page
    #     time.sleep(SCROLL_PAUSE_TIME)
    #
    #     # Calculate new scroll height and compare with last scroll height
    #     new_height = driver.execute_script("return document.body.scrollHeight")
    #     if new_height == last_height:
    #         break
    #     last_height = new_height

    html = driver.page_source
    full_content = BeautifulSoup(html, "lxml")

    class_type = ['miglog-prod miglog-sellingmethod-by_package', 'miglog-prod miglog-sellingmethod-by_weight',
                  'miglog-prod miglog-sellingmethod-by_unit']
    count = 0
    for class_ in class_type:
        products = full_content.find_all('li', class_=class_type)
        print(f"got {len(products)} products")
        for product in products:
            count += 1

            try:
                product_name = product.find('div', class_='text description').strong.text
                print(count, '.', product_name)
            except AttributeError as err:
                print(count, '.None')

            try:
                price = product.find('span', class_='price').span.text
                print("price:", price.strip())
            except AttributeError as err:
                print("price: None")

            try:
                priceUnit = product.find('span', class_='priceUnit').text
                print("priceUnit:", priceUnit.strip())
            except AttributeError as err:
                print("priceUnit: None")

            try:
                row = product.find('div', class_='labelsListContainer').div
                container = row.find_all('span')
                if type(container) == str or len(container) < 2:
                    try:
                        supplier = row.span.text
                        print("supplier:", supplier.strip())
                    except AttributeError as err:
                        print("supplier: None")

                else:
                    try:
                        container = row.find_all('span')[0].text
                        print("container:", container.strip())
                    except AttributeError as err:
                        print("container: None")

                    try:
                        supplier = row.find_all('span')[1].text
                        print("supplier:", supplier.strip())
                    except AttributeError as err:
                        print("supplier: None")

            except AttributeError as err:
                print("priceUnit: None")
                print("container: None")

            print()


if __name__ == '__main__':
    main()
