import sys
import logging
# ____internal modules____
from common import read_from_config
from common import connection

logging.basicConfig(filename='database.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

DATABASE_NAME = read_from_config("DATABASE_NAME")
TARGET_TRANS = read_from_config("TARGET_TRANS")


def create_table(con, database, name, *args):
    """'attribute' get a pymysql.connection.connection attribute,
    name of a database, name of a new table and a list of arguments
    containing a sql code to implement on the new table"""
    with con.cursor() as cursor:
        select_database = f'USE {database}'
        cursor.execute(select_database)
        content = str(args).replace("'", "")
        table = f'CREATE TABLE {name} {content}'
        cursor.execute(table)


def main(user, password):
    """
    Main function of the module, creates the foundation of the 'Shufersal' database using the MySQL Server
    """
    connect = connection(user, password)

    category_table_data = 'id INT AUTO_INCREMENT PRIMARY KEY', 'category VARCHAR(45)', 'url VARCHAR(500)'
    create_table(connect, DATABASE_NAME, 'category', *category_table_data)

    suppliers_table_data = 'id INT AUTO_INCREMENT PRIMARY KEY', 'supplier VARCHAR(45)'
    create_table(connect, DATABASE_NAME, 'suppliers', *suppliers_table_data)

    product_price_data = 'id INT PRIMARY KEY', 'price_ILS FLOAT', 'price_USD FLOAT', 'price_unit VARCHAR(45)', \
                         'container VARCHAR(45)', 'date_time DATETIME'
    create_table(connect, DATABASE_NAME, 'product_price', *product_price_data)

    product_details_data = 'id INT PRIMARY KEY', 'product_id VARCHAR(20)', 'name VARCHAR(200)',\
                           'id_suppliers INT', 'id_category INT', \
                           'FOREIGN KEY (id_suppliers) REFERENCES suppliers(id)', \
                           'FOREIGN KEY (id_category) REFERENCES category(id)', \
                           'FOREIGN KEY (id) REFERENCES product_price(id)'
    create_table(connect, DATABASE_NAME, 'product_details', *product_details_data)

    with connect.cursor() as cursor:
        foreign_key_checks = 'SET FOREIGN_KEY_CHECKS = 0;'
        cursor.execute(foreign_key_checks)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
