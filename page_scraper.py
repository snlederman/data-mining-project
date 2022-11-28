"""
page_scraper: the script takes an url* of one of the subcategories in the Shufersal site and prints
the following attributes for each product in that category:
    - product name
    - price
    - price unit
    - container
    - supplier
"""
import datetime
import time
import sys
from bs4 import BeautifulSoup
import pymysql
# ____selenium____
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from database import connection
from database import filling_table
from getting_shufersal_links import get_urls

## main url
MAIN_URL = 'https://www.shufersal.co.il/online/he/S'
general_url = 'https://www.shufersal.co.il'
LENGTH_GENERAL_URL = len(general_url)
range_list = [(3, 15), (2, 10), (4, 15)]
categories = len(range_list)
database_name = 'shufersal'


def create_connection(user_name, user_password):
    connection = pymysql.connect(host='localhost', user=user_name, password=user_password, database=database_name)
    return connection

def get_categories_links(user, password):
    connect = create_connection(user, password)
    categories_link_list_query = f"SELECT url FROM category;"
    categories_link = sql_queary(categories_link_list_query, connect)
    return list(map(lambda x: x[0], categories_link))

def sql_queary(query, connection):
    """
    "sql_connection" receives a string with sql query and returns it result using pymysql module.
    """
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return result


def get_category_urls(user, password):
    connect = create_connection(user, password)
    links_query = f"SELECT url FROM category;"
    links = sql_queary(links_query, connect)

    connect = create_connection(user, password)
    category_id_query = f"SELECT id FROM category;"
    category_id = sql_queary(category_id_query, connect)

    return links, category_id


def get_supplier_id(supplier, user, password):
    try:
        connect = create_connection(user, password)
        supplier = supplier.replace('"', '""')
        supplier_id_query = f'SELECT id FROM suppliers WHERE supplier = "{supplier}";'
        supplier_id = sql_queary(supplier_id_query, connect)

    except pymysql.err.ProgrammingError:
        connect = create_connection(user, password)
        supplier_id_query = """SELECT id FROM suppliers WHERE supplier = '{supplier}';"""
        supplier_id = sql_queary(supplier_id_query, connect)

    return supplier_id[0][0]


def get_supplier_list(user, password):
    connect = create_connection(user, password)
    suppliers_list_query = f"SELECT supplier FROM suppliers;"
    suppliers_list = sql_queary(suppliers_list_query, connect)
    return list(map(lambda x: x[0], suppliers_list))


def get_products_id_list(user, password):
    connect = create_connection(user, password)
    products_id_query = f"SELECT product_id FROM product_details;"
    products_id = sql_queary(products_id_query, connect)
    return list(map(lambda x: x[0], products_id))


def get_date_time():
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return timestamp


def fill_url_get_id(user, password, category_url):
    con = connection(user, password)
    categories_links = get_categories_links(user, password)
    if category_url not in categories_links:
        filling_table(con, 'shufersal', 'category', '(url)', category_url)

    connect = create_connection(user, password)
    category_id_query = f"SELECT id FROM category WHERE url = '{category_url}';"
    category_id = sql_queary(category_id_query, connect)
    return [[category_url]], [category_id[0][0]]


def get_product_count(user, password):
    connect = create_connection(user, password)
    count_query = f"SELECT count(*) FROM product_details;"
    count = sql_queary(count_query, connect)
    return count[0][0]


def parse_data(user, password, *args):

    con = create_connection(user, password)
    if args:
        category_urls, category_ids = fill_url_get_id(user, password, args[0])
    else:
        category_urls, category_ids = get_category_urls(user, password)

    product_id_count = get_product_count(user, password)
    for url_index, category_url in enumerate(category_urls):
        options = Options()
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.maximize_window()
        driver.get(category_url[0])
        count = 0
        for scroll in range(10):
            SCROLL_PAUSE_TIME = 5
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)

            html = driver.page_source
            full_content = BeautifulSoup(html, "lxml")

            class_type = ['miglog-prod miglog-sellingmethod-by_package', 'miglog-prod miglog-sellingmethod-by_weight',
                          'miglog-prod miglog-sellingmethod-by_unit', 'tile miglog-prod-inStock notOverlay ui-draggable ui-draggable-handle']

            for class_ in class_type:
                products = full_content.find_all('li', class_=class_type)
                for product in products:

                    try:
                        product_id = product['data-product-code']
                    except AttributeError as err:
                        product_id = 'NaN'

                    try:
                        product_name = product.find('div', class_='text description').strong.text
                    except AttributeError as err:
                        product_name = 'NaN'

                    try:
                        price = product.find('span', class_='price').span.text
                    except AttributeError as err:
                        price = 'NaN'

                    try:
                        priceUnit = product.find('span', class_='priceUnit').text
                    except AttributeError as err:
                        priceUnit = 'NaN'

                    try:
                        row = product.find('div', class_='labelsListContainer').div
                        container = row.find_all('span')
                        if type(container) == str or len(container) < 2:
                            try:
                                supplier = row.span.text
                            except AttributeError as err:
                                supplier = 'NaN'

                        else:
                            try:
                                container = row.find_all('span')[0].text
                            except AttributeError as err:
                                container = 'NaN'

                            try:
                                supplier = row.find_all('span')[1].text
                            except AttributeError as err:
                                supplier = 'NaN'

                    except AttributeError as err:
                        priceUnit = 'NaN'
                        container = 'NaN'

                    products_id = get_products_id_list(user, password)
                    if product_id not in products_id:
                        count += 1
                        product_id_count += 1
                        suppliers = get_supplier_list(user, password)
                        if supplier not in suppliers:
                            filling_table(con, database_name, 'suppliers', '(supplier)', supplier)

                        date_time = get_date_time()
                        filling_table(con, database_name, 'product_price',
                                      '(id, price, price_unit, container, date_time)',
                                      product_id_count, price, priceUnit, container, date_time)

                        supplier_id = get_supplier_id(supplier, user, password)
                        filling_table(con, database_name, 'product_details',
                                      '(id, product_id, name, id_suppliers, id_category)',
                                      product_id_count, product_id, product_name, supplier_id, category_ids[url_index])

        print(f"{count} products were scraped from category in index {category_ids[url_index]} ")
if __name__ == '__main__':
    parse_data(sys.argv[1], sys.argv[2])
