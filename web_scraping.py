"""
Data Mining Projecting
"""
import lxml
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
import time

URL = 'https://www.shufersal.co.il/online/he/%D7%A7%D7%98%D7%92%D7%95%D7%A8%D7%99%D7%95%D7%AA/%D7%A1%D7%95%D7%A4%D7%A8%D7%9E%D7%A8%D7%A7%D7%98/%D7%A4%D7%99%D7%A8%D7%95%D7%AA-%D7%95%D7%99%D7%A8%D7%A7%D7%95%D7%AA/c/A04'
DELAY = 50
# SHOW_MORE_BUTTON = ''
LI_XPATH = '//*[@id="mainProductGrid"]'
# LI_XPATH = '//*[@id="changeView"]'

options = Options()
# driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=chrome_options)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.set_window_size(1920, 1080)
driver.get(URL)
actions = ActionChains(driver)

for product_index in range(1, 100):
    print('product ', product_index, ':')
    print("------------------------------")
    p_path = f'//*[@id="mainProductGrid"]/li[{product_index}]'
    product = driver.find_element(By.XPATH, p_path)
    # print(product.text)
    actions.move_to_element(product).perform()

    ### open product popup
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.XPATH, p_path))).click()

    # time.sleep(5)

    ### extract data
    new_path = '//*[@id="productModal"]/div'
    try:
        popup_element = WebDriverWait(driver, DELAY).until(EC.visibility_of_element_located((By.XPATH, new_path)))
        html = driver.page_source
        soup = BeautifulSoup(html, "lxml")
        # print(soup.prettify())
        box = soup.find('div', class_="modal fade productModal centerModal bodyModalAppend in")
        # print(box.prettify())
        text = soup.find('div', class_="remarksText")
        print(text)
        price = box.find('span', class_="price").span.text
        print(price)
        title = soup.find('div', class_="text description").strong.text
        print(title)
        container = soup.find('div', class_="labelsListContainer").div.span.text
        print(container)
        manufacture = soup.find('div', class_="labelsListContainer").div.span.text
        print(manufacture)

    except TimeoutException as err:
        print('Timeout error: ', err)

    # price_path = '//*[@id="mCSB_3_container"]/div/div/section[1]/div[2]/div[1]/div[2]/div[2]/div/span[1]'
    # price = WebDriverWait(driver, DELAY).until(EC.visibility_of_element_located((By.XPATH, price_path)))
    # title_path = '//*[@id="modalTitle"]'
    # container_path = '//*[@id="productModal"]/div/div[1]/div/div/text()'
    # title = WebDriverWait(driver, DELAY).until(EC.visibility_of_element_located((By.XPATH, title_path)))
    # print(popup_element.text)

    ### close popup window
    x_path = '// *[ @ id = "productModal"] / div / button'
    # time.sleep(1)
    WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.XPATH, x_path))).click()

    #
    if product_index % 5 == 0:
        #     SCROLL_PAUSE_TIME = 1
        #     # # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     # # Wait to load page
    #     time.sleep(SCROLL_PAUSE_TIME)

# waiter = WebDriverWait(driver, DELAY)

# waiter.until(expected_conditions.presence_of_element_located((By.XPATH, SHOW_MORE_BUTTON)))
# waiter.until(expected_conditions.element_to_be_clickable((By.XPATH, SHOW_MORE_BUTTON))).click()
# waiter.until(expected_conditions.presence_of_element_located((By.XPATH, SHOW_MORE_BUTTON)))

# actions = ActionChains(driver)
# actions.move_to_element(element).perform()
#
#
# def show_more_details():
#     product_id = 1
#     # while True:
#         # try:
#     x_path = f'//*[@id="mainProductGrid"]/li[{product_id}]'
#
#     element = driver.find_element(By.XPATH, x_path)
#     actions.move_to_element(element).perform()
#     WebDriverWait(driver, DELAY).until(EC.element_to_be_clickable((By.XPATH, x_path))).click()
# new_path = '//*[@id="productModal"]/div'
# popup_element = WebDriverWait(driver, DELAY).until(EC.presence_of_element_located((By.XPATH, new_path)))
# # popup_element = driver.find_element(By.XPATH, new_path)
# time.sleep(10)
# print(popup_element.text)
# description = driver.find_element(By.XPATH, '//*[@id="techDetails"]/ul/div/div')
# print(description.text)
# productSku = popup_element.get_attribute("productSku")
# print(productSku)

#     return
#
#
# products = show_more_details()

# for i in range(3):
#     products_top = products[i].text
#     print(f'top {i}:\t', [products])

# print(len(products))

# driver.quit()
