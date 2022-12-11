"""
The script extracts all relevant urls addresses from the online supermarket of "shufersal"
"""

import time

import pymysql
from bs4 import BeautifulSoup
import requests
import sys
# ____selenium____
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from database import connection
from database import filling_table
from google_translate_api import translate_text

BASE_URL = 'https://www.shufersal.co.il/online/he/s'
MAIN_URL = 'https://www.shufersal.co.il'
LENGTH_GENERAL_URL = len(MAIN_URL)
RANGE_LIST = [(3, 15), (2, 10), (4, 15)]
MINIMUM_NUMBER_OF_LINKS = 20
database_name = 'shufersal'


def from_url_to_soup(url_address):
    """
     get_soup_from_url gets an url address and returns it html content using BeautifulSoup4

    :param url_address:  url address string
    :return: soup - class 'bs4.BeautifulSoup'
    """
    r = requests.get(url_address)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def create_connection(user_name, user_password):
    connection = pymysql.connect(host='localhost', user=user_name, password=user_password, database=database_name)
    return connection


def sql_queary(query, connection):
    """
    "sql_connection" receives a string with sql query and returns it result using pymysql module.
    """
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return result


def get_categories_links(user, password):
    connect = create_connection(user, password)
    categories_link_list_query = f"SELECT url FROM category;"
    categories_link = sql_queary(categories_link_list_query, connect)
    return list(map(lambda x: x[0], categories_link))


def get_urls(user, password):
    """
    get_urls runs a search through Shufersal online main header and returns all the links to it sub categories
    and the name of the categories (in hebrew).
    """
    con = connection(user, password)
    options = Options()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    driver.get(BASE_URL)
    action = ActionChains(driver)
    category_urls = dict()
    fill_count = 0

    for i in range(len(RANGE_LIST)):
        element = driver.find_element(By.XPATH,
                                      f'/ html / body / main / header / div[2] / nav / div / ul[1] / li[{i + 2}]')
        action.move_to_element(element).perform()
        time.sleep(1)
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
                        category_url = MAIN_URL + url
                    if category_url[:LENGTH_GENERAL_URL] == MAIN_URL:
                        category_urls[category] = category_url
                        categories_links = get_categories_links(user, password)
                        if category_url not in categories_links:
                            fill_count += 1
                            filling_table(con, 'shufersal', 'category', '(category, url)', category, category_url)

    print(f'{fill_count} sub categories urls were scraped successfully from "Shupersal" online site')
    return category_urls


if __name__ == '__main__':
    get_urls(sys.argv[1], sys.argv[2])
