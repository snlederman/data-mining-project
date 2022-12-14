"""
page_scraper: the script takes an url* of one of the subcategories in the Shufersal site and prints
the following attributes for each product in that category:
    - product name
    - price
    - price unit
    - container
    - supplier
"""
import sys
import logging
import datetime
import time
import requests
from bs4 import BeautifulSoup
import pymysql
# ____selenium____
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# ____internal modules____
from common import read_from_config
from common import connection
from common import get_categories_links
from common import filling_table

logging.basicConfig(filename='page_scraper.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

MAIN_URL = read_from_config("MAIN_URL")
GENERAL_URL = read_from_config("GENERAL_URL")
LENGTH_GENERAL_URL = len(GENERAL_URL)
DATABASE_NAME = read_from_config("DATABASE_NAME")
RANGE_LIST = read_from_config("RANGE_LIST")
CATEGORIES = len(RANGE_LIST)
EXCHANGE_RATE_API_URL = read_from_config("EXCHANGE_RATE_API_URL")
EXCHANGE_RATE_HEADERS = read_from_config("EXCHANGE_RATE_HEADERS")
CONVERSION_RATE = read_from_config("CONVERSION_RATE")
LOCAL_CURRENCY = read_from_config("LOCAL_CURRENCY")
ITEMS_PER_SCROLL = read_from_config("ITEMS_PER_SCROLL")
SCROLL_PAUSE_TIME = read_from_config("SCROLL_PAUSE_TIME")
TARGET_TRANS = read_from_config("TARGET_TRANS")


def create_connection(user, password):
    con = pymysql.connect(host=read_from_config("HOST"),
                          user=user,
                          password=password,
                          database=DATABASE_NAME)
    return con


def sql_query(query, user, password):
    """
    "sql_connection" receives a string with sql query and returns it result using pymysql module.
    """
    con = create_connection(user, password)
    with con:
        with con.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return result


def get_category_urls(user, password):
    links_query = f"SELECT url FROM category;"
    links = sql_query(links_query, user, password)
    category_id_query = f"SELECT id FROM category;"
    category_id = sql_query(category_id_query, user, password)
    return links, category_id


def get_supplier_id(supplier_name, user, password):
    try:
        supplier_name = supplier_name.replace('"', '""')
        supplier_id_query = f'SELECT id FROM suppliers WHERE supplier = "{supplier_name}";'
        supplier_id = sql_query(supplier_id_query, user, password)
    except pymysql.err.ProgrammingError:
        supplier_id_query = """SELECT id FROM suppliers WHERE supplier = '{supplier}';"""
        supplier_id = sql_query(supplier_id_query, user, password)
    return supplier_id[0][0]


def get_supplier_list(user, password):
    suppliers_list_query = f"SELECT supplier FROM suppliers;"
    suppliers_list = sql_query(suppliers_list_query, user, password)
    return list(map(lambda x: x[0], suppliers_list))


def get_products_id_list(user, password):
    products_id_query = f"SELECT product_id FROM product_details;"
    products_id = sql_query(products_id_query, user, password)
    return list(map(lambda x: x[0], products_id))


def get_date_time():
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


def fill_url_get_id(user, password, category_url):
    con = connection(user, password)
    categories_links = get_categories_links(user, password)
    if category_url not in categories_links:
        filling_table(con, DATABASE_NAME, 'category', '(url)', category_url)
    category_id_query = f"SELECT id FROM category WHERE url = '{category_url}';"
    category_id = sql_query(category_id_query, user, password)
    return [[category_url]], [category_id[0][0]]


def get_product_count(user, password):
    count_query = f"SELECT count(*) FROM product_details;"
    count = sql_query(count_query, user, password)
    return count[0][0]


def exchange_rate():
    url = EXCHANGE_RATE_API_URL
    response = requests.request("GET", url, headers=EXCHANGE_RATE_HEADERS)
    if response:
        data = response.json()
        ils_to_usd = data[CONVERSION_RATE][LOCAL_CURRENCY]
        logging.info(f'exchange rate from ILS to USD url successfully scrapped, exchange rate: %s', ils_to_usd)
        return round(ils_to_usd, 2)
    else:
        logging.critical(f'exchange rate from ILS to USD was not found: %s', response)
        return 'NaN'


def parse_data(user, password, *args):
    con = create_connection(user, password)
    if args:
        category_urls, category_ids = fill_url_get_id(user, password, args[0])
    else:
        category_urls, category_ids = get_category_urls(user, password)

    ils_to_usd = exchange_rate()
    product_id_count = get_product_count(user, password)
    for url_index, category_url in enumerate(category_urls):
        print(f'Parsing: {category_url}')
        logging.info(f'Start parsing: {category_url}')
        options = Options()
        options.headless = True
        options.add_argument('--window-size=1920,1080')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(category_url[0])
        count = 0
        for scroll in range(ITEMS_PER_SCROLL):
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

            try:
                html = driver.page_source
            except BaseException as err:
                logging.warning(f"Selenium driver failed to execute script: {err} ")
                print(f"Selenium driver failed to execute script: {err} ")
                continue

            full_content = BeautifulSoup(html, "lxml")

            class_type = ['miglog-prod miglog-sellingmethod-by_package', 'miglog-prod miglog-sellingmethod-by_weight',
                          'miglog-prod miglog-sellingmethod-by_unit', 'tile miglog-prod-inStock notOverlay ui-draggable'
                                                                      ' ui-draggable-handle']

            products = full_content.find_all('li', class_=class_type)
            for product in products:
                try:
                    product_id = product['data-product-code']
                except AttributeError:
                    product_id = 'NaN'

                try:
                    product_name = product.find('div', class_='text description').strong.text
                except AttributeError:
                    product_name = 'NaN'

                try:
                    price = product.find('span', class_='price').span.text
                    if ils_to_usd == 'NaN':
                        price_usd = 'NaN'
                    else:
                        price_usd = float(price)/ils_to_usd
                except AttributeError:
                    price = 'NaN'
                    price_usd = 'NaN'

                try:
                    price_unit = product.find('span', class_='priceUnit').text
                except AttributeError:
                    price_unit = 'NaN'

                try:
                    row = product.find('div', class_='labelsListContainer').div
                    container = row.find_all('span')
                    if type(container) == str or len(container) < 2:
                        try:
                            supplier = row.span.text
                        except AttributeError:
                            supplier = 'NaN'
                    else:
                        try:
                            container = row.find_all('span')[0].text
                        except AttributeError:
                            container = 'NaN'

                        try:
                            supplier = row.find_all('span')[1].text
                        except AttributeError:
                            supplier = 'NaN'
                except AttributeError:
                    price_unit = 'NaN'
                    container = 'NaN'

                products_id = get_products_id_list(user, password)
                if product_id not in products_id:
                    count += 1
                    product_id_count += 1
                    suppliers = get_supplier_list(user, password)
                    if supplier not in suppliers:
                        filling_table(con, DATABASE_NAME, 'suppliers', '(supplier)', supplier)

                    date_time = get_date_time()
                    filling_table(con, DATABASE_NAME, 'product_price',
                                  '(id, price_ILS, price_USD, price_unit, container, date_time)', product_id_count,
                                  price, price_usd, price_unit, container, date_time)

                    supplier_id = get_supplier_id(supplier, user, password)
                    filling_table(con, DATABASE_NAME, 'product_details',
                                  f'(id, product_id, name, id_suppliers, id_category)',
                                  product_id_count, product_id, product_name, supplier_id,
                                  category_ids[url_index])

        print(f"{count} products were scraped. Category index: {category_ids[url_index]} ")
        logging.info(f'f"{count} products were scraped. Category index: {category_ids[url_index]}')
        driver.close()


if __name__ == '__main__':
    parse_data(sys.argv[1], sys.argv[2])
