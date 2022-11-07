import requests
from bs4 import BeautifulSoup
import urllib.parse
import csv

input_product = input('input product:')
find_string = urllib.parse.quote(input_product)

milk_url = 'https://www.shufersal.co.il/online/he/search?text=7296073231547'
find_url = 'https://www.shufersal.co.il/online/he/search?text=' + find_string
temp = 'https://www.shufersal.co.il/online/he/search?text=%D7%91%D7%A0%D7%A0%D7%94'
r = requests.get(find_url)
# ________
csv_file = open('shufersal_scrape.csv', 'a')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Product name', 'Price', 'price_per_unit', 'container'])

# __________
# print(r.headers.keys())
# print(r.headers['content-type'])
# print(r.ok)
# print(r.headers)

soup = BeautifulSoup(r.content, "html.parser")
products = soup.find_all('li', class_='SEARCH tileBlock miglog-prod miglog-sellingmethod-by_unit')

count = 0
for product in products:
    count += 1

    product_name = product.find('div', class_='text description').strong.text
    print(count , '.', product_name)
    price = product.find('div', class_='middleContainer').div.span.span.text
    print(price.strip())
    price_per_unit = product.find('div', class_='smallText pricePerUnit').text
    print(price_per_unit.strip())
    container = product.find('div', class_='labelsListContainer').div.span.text
    print(container.strip())
    print()

    csv_writer.writerow([product_name, price, price_per_unit, container])

csv_file.close()