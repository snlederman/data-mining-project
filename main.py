import pymysql
import argparse

# ____internal modules____
from common import read_from_config
from common import connection
import getting_shufersal_links
import database
import page_scraper

DATABASE_NAME = read_from_config('DATABASE_NAME')


def delete_database(user, password):
    delete_database_q = input(f"this will delete the existing '{DATABASE_NAME}' database, to proceed? [y/n]")
    if delete_database_q == 'y':
        try:
            database.delete_database(user, password, DATABASE_NAME)
            print(f'"{DATABASE_NAME}" database was deleted successfully.')
        except pymysql.err.OperationalError as err:
            print(f"Can't delete database {DATABASE_NAME}, database doesn't exist")
            return
    elif delete_database_q == 'n':
        return
    else:
        delete_database(user, password)


def build_shufersal_database(user, password):
    try:
        database.main(user, password)
        print(f'"{DATABASE_NAME}" database was created successfully.')
    except pymysql.err.ProgrammingError:
        raise pymysql.err.ProgrammingError


def check_sql_connection(user, password):
    try:
        connection(user, password)
        return True
    except pymysql.err.OperationalError:
        return False


def main():
    parser = argparse.ArgumentParser(description="""Welcome to the Shufersal scraper!
    the Shufersal scraper enables the user to scrab the data 
    from the online supermarket site of the Shufersal chain: https://www.shufersal.co.il""")

    parser.add_argument('user', help='user name to mySQL data server')
    parser.add_argument('password', help='password to mySQL data server')
    parser.add_argument('-url', help=f'specific category url from the "{DATABASE_NAME}" online site to parse and '
                                     f'collect to the {DATABASE_NAME} database')
    parser.add_argument('-gl', action='store_true', help=f'get subcategories links to parse and fill category table')
    parser.add_argument('-all', action='store_true', help=f'get all links from category table, parse and fill "{DATABASE_NAME}" database')
    parser.add_argument('-c', action='store_true', help=f'create "{DATABASE_NAME}" database')
    parser.add_argument('-dc', action='store_true', help=f'delete existing "{DATABASE_NAME}" database and creating a new one')
    parser.add_argument('-d', action='store_true', help=f'delete "{DATABASE_NAME}" database')

    args = parser.parse_args()
    user = args.user
    password = args.password

    if check_sql_connection(user, password):

        if args.d:
            delete_database(user, password)

        if args.dc:
            delete_database(user, password)
            try:
                build_shufersal_database(user, password)
            except pymysql.err.ProgrammingError:
                return

        if args.c:
            try:
                build_shufersal_database(user, password)
            except pymysql.err.ProgrammingError:
                return

        if args.gl:
            if database.check_database(user, password, DATABASE_NAME):
                getting_shufersal_links.get_urls(user, password)
            else:
                return

        if args.url:
            if database.check_database(user, password, DATABASE_NAME):
                page_scraper.parse_data(user, password, args.url)
            else:
                return

        if args.all:
            if database.check_database(user, password, DATABASE_NAME):
                if getting_shufersal_links.check_urls(user, password):
                    page_scraper.parse_data(user, password)
            else:
                return


if __name__ == '__main__':
    main()
