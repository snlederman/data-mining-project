import pymysql
import getting_shufersal_links
import database
import page_scraper
import argparse

DATABASE_NAME = 'shufersal'


def delete_database(user, password):
    delete_database_q = input("this will delete the existing 'Shufersal' database, to proceed? [y/n]")
    if delete_database_q == 'y':
        database.delete_database(user, password, DATABASE_NAME)
        print(f'"{DATABASE_NAME}" database was deleted successfully.')
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


def main():
    parser = argparse.ArgumentParser(description="""Welcome to the Shufersal scraper!
    the Shufersal scraper enables the user to scrab the data 
    from the online supermarket site of the Shufersal chain: https://www.shufersal.co.il""")

    parser.add_argument('user', help='user name to mySQL data server')
    parser.add_argument('password', help='password to mySQL data server')
    parser.add_argument('-url',
                        help='specific category url from the "Shufersal" online site to parse and collect to the Shufersal database')
    parser.add_argument('-gl', action='store_true', help='get subcategories links to parse and fill category table')
    parser.add_argument('-all', action='store_true', help='get all links from category table, parse and fill "Shufersal" database')
    parser.add_argument('-c', action='store_true', help='create "Shufersal" database')
    parser.add_argument('-dc', action='store_true', help='delete existing "Shufersal" database and creating a new one')
    parser.add_argument('-d', action='store_true', help='delete "Shufersal" database')

    args = parser.parse_args()
    user = args.user
    password = args.password

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
        getting_shufersal_links.get_urls(user, password)

    if args.url:
        page_scraper.parse_data(user, password, args.url)

    if args.all:
        page_scraper.parse_data(user, password)


if __name__ == '__main__':
    main()
