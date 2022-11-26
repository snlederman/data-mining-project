import pymysql
from pymysql import MySQLError

import getting_shufersal_links
import database
import page_scraper
import sys

DATABASE_NAME = 'shufersal'



def delete_database(user, password):
    delete_database = input("would you like to delete the existing 'shufersal' database? [y/n]")
    if delete_database == 'y':
        database.delete_database(user, password, DATABASE_NAME)
        build_shufersal_database(user, password)
    elif delete_database == 'n':
        return
    else:
        delete_database(user, password)

def build_shufersal_database(user, password):
    create_database = input("would you like to create a 'shufersal' database? [y/n]")
    if create_database == 'y':
        try:
            database.main(user, password)
            print(f'"{DATABASE_NAME}" database was created successfully.')
        except pymysql.err.ProgrammingError:
            delete_database(user, password)
            return
    elif create_database == 'n':
        return
    else:
        build_shufersal_database(user, password)


def get_categories_links():
    links_list, category_list = getting_shufersal_links.main()
    return links_list, category_list

def main():

    user = sys.argv[1]
    password = sys.argv[2]


    build_shufersal_database(user, password)
    links, categories = get_categories_links()

if __name__ == '__main__':
    main()