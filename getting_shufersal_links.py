"""
The script extracts all relevant urls addresses from the online supermarket of "shufersal"
"""

import requests
from bs4 import BeautifulSoup
import csv

MAIN_URL = 'https://www.shufersal.co.il/online/he/S'
MINIMUM_NUMBER_OF_LINKS = 20


def from_url_to_soup(url_address):
    """
     get_soup_from_url gets an url address and returns it html content using BeautifulSoup4

    :param url_address:  url address string
    :return: soup - class 'bs4.BeautifulSoup'
    """
    r = requests.get(url_address)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def main():
    """
    main runs a search through Shufersal online main header and returns all the links to it sub categories
    and the name of the categories (in hebrew). all the data is stored in shufersal_links.csv
    """

    full_content = from_url_to_soup(MAIN_URL)
    sub_panels = full_content.find_all('li', class_="second-level-li panel")

    count = 0
    label_list = []
    links_list = []
    category_list = []
    for sub_panel in sub_panels:
        label = sub_panel.a.text.strip()
        if label in label_list:
            break
        else:
            label_list.append(label)
            link = sub_panel.a.get('href')
            if link[1:7] == 'online':
                link = 'https://www.shufersal.co.il' + link
            count += 1
            links_list.append(link)
            category_list.append(label)

    if count <= MINIMUM_NUMBER_OF_LINKS:
        raise Exception(f" only {count} links were scraped, please check the script/file/site...")
    else:
        print(f"{len(links_list)} categories and their links were scraped from the main Shufersal online site .")

    return links_list, category_list


if __name__ == '__main__':
    main()
