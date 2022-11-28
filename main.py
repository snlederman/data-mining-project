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
        build_shufersal_database(user, password)
    elif delete_database_q == 'n':
        return
    else:
        delete_database(user, password)


def build_shufersal_database(user, password):
    try:
        database.main(user, password)
        print(f'"{DATABASE_NAME}" database was created successfully.')
    except pymysql.err.ProgrammingError:
        print('"Shufersal" database already exist. please see usage:')
        raise pymysql.err.ProgrammingError


def get_categories_links(user, password):
    getting_shufersal_links.get_urls(user, password)
    return


def get_products(user, password):
    page_scraper.parse_data(user, password)


def main():
    parser = argparse.ArgumentParser(description="""Welcome to the Shufersal scraper!
    the Shufersal scraper enables the user to scrab the data 
    from the online supermarket site of the Shufersal chain: https://www.shufersal.co.il""")

    parser.add_argument('user', help='user name to mySQL data server')
    parser.add_argument('password', help='password to mySQL data server')
    parser.add_argument('-url',
                        help='specific category url from the "Shufersal" online site to parse and collect to the Shufersal database')
    parser.add_argument('-gl', action='store_true', help='get subcategories links to parse')
    parser.add_argument('-c', action='store_true', help='create "Shufersal" database')
    parser.add_argument('-dc', action='store_true', help='delete existing "Shufersal" database and creating a new one')
    parser.add_argument('-d', action='store_true', help='delete "Shufersal" database')
    parser.add_argument('-clean', action='store_true', help='clean "Shufersal" database')
    parser.add_argument('-clean_xl', action='store_true',
                        help='clean "Shufersal" database except "category" table containing urls')

    args = parser.parse_args()
    user = args.user
    password = args.password

    if args.d:
        delete_database(user, password)

    elif args.dc:
        delete_database(user, password)
        try:
            build_shufersal_database(user, password)
        except pymysql.err.ProgrammingError:
            return

    elif args.c:
        try:
            build_shufersal_database(user, password)
        except pymysql.err.ProgrammingError:
            return

    elif args.gl:
        get_categories_links(user, password)

    elif args.url:
        page_scraper.parse_data(user, password, args.URL)

    else:
        get_products(user, password)


if __name__ == '__main__':
    main()
