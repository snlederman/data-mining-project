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
import grequests
from bs4 import BeautifulSoup
# ____selenium____
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from database import connection
from database import filling_table


## main url
con = connection('root', 'rootroot')
MAIN_URL = 'https://www.shufersal.co.il/online/he/S'
general_url = 'https://www.shufersal.co.il'
categories = 3
LENGTH_GENERAL_URL = len(general_url)

def get_urls():
    """Finds the link to specific category websites."""
    options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    driver.get(MAIN_URL)
    action = ActionChains(driver)
    range_list = [(3, 15), (2, 10), (4, 15)]
    category_urls = dict()
    for i in range(categories):
        ELEMENT = driver.find_element(By.XPATH, f'/ html / body / main / header / div[2] / nav / div / ul[1] / li[{i+2}]')
        action.move_to_element(ELEMENT).perform()
        time.sleep(1)
        elements = range_list[i]
        for j in range(*elements):
            ELEMENT = driver.find_element(By.XPATH, f'// *[ @ id = "secondMenu{i+2}"] / li[{j}]')
            action.move_to_element(ELEMENT).perform()
            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")
            menu_elements = soup.find_all('ul', class_="thirdMenu")
            for menu_element in menu_elements:
                category_elements = menu_element.find_all('div', class_="content")
                for category_element in category_elements:
                    category = category_element.find("a").text.strip()
                    url = category_element.find("a")["href"]
                    category_url = url
                    if url[1:7] == 'online':
                        category_url = general_url + url
                    if category_url[:LENGTH_GENERAL_URL] == general_url:
                        category_urls[category] = category_url
                        filling_table(con, 'shufersal', 'category', '(name, url)', category, category_url)
    return category_urls


def parse_data(category_urls):
    category_urls_values = list(category_urls.values())
    for category_url in category_urls_values:
        options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.maximize_window()
        driver.get(category_url)
        for scroll in range(10):
            SCROLL_PAUSE_TIME = 5
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

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

                    product_id = product['data-product-code']
                    print(product_id)

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
    U = get_urls()
#    parse_data(U)

#filling_table(con, 'shufersal', 'category', '(name, url)', product_name, price)
#filling_table(con, 'shufersal', 'category', '(name, url)', product_name, price)
#filling_table(con, 'shufersal', 'category', '(name, url)', product_name, price)
#filling_table(con, 'shufersal', 'category', '(name, url)', product_name, price)
