import argparse
import logging
import pymysql
from googletrans import LANGUAGES
# ____internal modules____
from common import read_from_config
from common import connection
from common import translate
import getting_shufersal_links
import database
import page_scraper

logging.basicConfig(filename='main.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

MYSQL_USER = read_from_config('MYSQL_USER')
MYSQL_PASSWORD = read_from_config('MYSQL_PASSWORD')
DATABASE_NAME = read_from_config('DATABASE_NAME')


def build_shufersal_tables(user, password):
    """'build_shufersal_database' creates the 'shufersal' database."""
    try:
        database.main(user, password)
        print(f'"{DATABASE_NAME}" database was created successfully.')
        logging.info(f'database was created successfully: %s')
    except pymysql.err.ProgrammingError:
        logging.warning(f'"{DATABASE_NAME}" database was not created successfully %s')
        raise pymysql.err.ProgrammingError


def check_sql_connection(user, password):
    try:
        connection(user, password)
        logging.info(f'MySQL connection established: %s', user)
        return True
    except pymysql.err.OperationalError:
        logging.critical(f'no MySQL connection established: %s', user)
        return False


def main():
    parser = argparse.ArgumentParser(description="""Welcome to the Shufersal scraper!
    the Shufersal scraper enables the user to scrab the data 
    from the online supermarket site of the Shufersal chain: https://www.shufersal.co.il""")

    parser.add_argument('-user', help='user name to mySQL data server')
    parser.add_argument('-password', help='password to mySQL data server')
    parser.add_argument('-c', action='store_true', help=f'create tables for "{DATABASE_NAME}" database')
    parser.add_argument('-gl', action='store_true', help=f'get subcategories links to parse and fill category table')
    parser.add_argument('-url', help=f'specific category url from the "{DATABASE_NAME}" online site to parse and '
                        f'collect to the {DATABASE_NAME} database')
    parser.add_argument('-all', action='store_true', help=f'get all links from category table, parse and fill'
                        f' "{DATABASE_NAME}" database')
    parser.add_argument('-translate', nargs=2, metavar=('TABLE', 'COLUMN'),
                        help=f'specific table and column from the "{DATABASE_NAME}" database to translate to '
                             f'the desired language (english by default). To see the available languages insert '
                             f'languages as the argument for LANGUAGE')

    args = parser.parse_args()
    user = MYSQL_USER
    password = MYSQL_PASSWORD

    if check_sql_connection(user, password):
        logging.info(f'mySQL connection checkpoint: login completed successfully.')

        if args.c:
            try:
                build_shufersal_tables(user, password)
                logging.info(f'Client successfully created a new "shufersal" database: %s')
            except pymysql.err.ProgrammingError:
                logging.warning(f'Client failed creating a new "shufersal" database: %s')

        if args.gl:
            print("Getting subcategories' links to parse")
            logging.info("Getting subcategories' links to parse")
            getting_shufersal_links.get_urls(user, password)

        if args.url:
            page_scraper.parse_data(user, password, args.url)

        if args.all:
            if getting_shufersal_links.check_urls(user, password):
                page_scraper.parse_data(user, password)
                logging.info(f'Client succeeded getting all the links from category table to parse'
                             f' and fill "shufersal" database: %s')
            else:
                logging.warning(f'Client failed getting all the links from category table to parse'
                                f' and fill "shufersal" database: %s')

        if args.translate:
            if args.translate[2] == 'languages':
                print(LANGUAGES)
            else:
                logging.info(f'Starting to translate table "{args.translate[0]}", column "{args.translate[1]}".')
                print(f'Starting to translate table "{args.translate[0]}", column "{args.translate[1]}".')
                translate(user, password, args.translate[0], args.translate[1])
                print(f'Successful translation of table "{args.translate[0]}", column "{args.translate[1]}".')
                logging.info(f'Client succeeded specifying table, colum and datatype from the "shufersal"'
                             f' database to translate from hebrew to {args.translate[2]}: %s',
                             (args.translate[0], args.translate[1], args.translate[2]))


if __name__ == '__main__':
    main()
