"""
The script extracts all relevant urls addresses from the online supermarket of "Shufersal"
"""
import sys
import logging
import time
from bs4 import BeautifulSoup
# ____selenium____
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# ____internal modules____
from common import read_from_config
from common import connection
from common import get_categories_links
from common import filling_table

logging.basicConfig(filename='getting_shufersal_links.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

MAIN_URL = read_from_config("MAIN_URL")
GENERAL_URL = read_from_config("GENERAL_URL")
LENGTH_GENERAL_URL = len(GENERAL_URL)
DATABASE_NAME = read_from_config("DATABASE_NAME")
RANGE_LIST = read_from_config("RANGE_LIST")
MINIMUM_NUMBER_OF_LINKS = read_from_config("MINIMUM_NUMBER_OF_LINKS")
MOVE_PAUSE_TIME = read_from_config("MOVE_PAUSE_TIME")
TARGET_TRANS = read_from_config("TARGET_TRANS")


def check_urls(user, password):
    urls = get_categories_links(user, password)
    urls_len = len(urls)
    if urls_len == 0:
        print("No links were found in the category table to parse. \nUse -gl argument to get subcategories links or "
              "-url argument for parsing a specific category url.")
    return len(urls)


def get_urls(user, password):
    """
    get_urls runs a search through Shufersal online main header and returns all the links to it sub categories
    and the name of the categories (in hebrew).
    """
    con = connection(user, password)
    options = Options()
    options.headless = True
    options.add_argument('--window-size=1920,1080')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(MAIN_URL)
    action = ActionChains(driver)
    category_urls = dict()
    fill_count = 0

    for i in range(len(RANGE_LIST)):
        element = driver.find_element(By.XPATH,
                                      f'/ html / body / main / header / div[2] / nav / div / ul[1] / li[{i + 2}]')
        action.move_to_element(element).perform()
        time.sleep(MOVE_PAUSE_TIME)
        elements = RANGE_LIST[i]

        for j in range(*elements):
            element = driver.find_element(By.XPATH, f'// *[ @ id = "secondMenu{i + 2}"] / li[{j}]')
            action.move_to_element(element).perform()
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
                        category_url = GENERAL_URL + url
                    if category_url[:LENGTH_GENERAL_URL] == GENERAL_URL:
                        category_urls[category] = category_url
                        categories_links = get_categories_links(user, password)
                        if category_url not in categories_links:
                            fill_count += 1
                            filling_table(con, DATABASE_NAME, 'category', '(category, url)', category, category_url)
    print(f'{fill_count} sub categories urls were scraped successfully from "Shufersal" online site')
    driver.close()
    return category_urls


if __name__ == '__main__':
    get_urls(sys.argv[1], sys.argv[2])
