import pymysql
import sys


def connection(user, password):
    """'connection' gets a user and a password to MySQL Server
    and returns a pymysql.connection.connection attribute"""

    con = pymysql.connect(host='localhost',
                          user=user,
                          password=password,
                          cursorclass=pymysql.cursors.DictCursor)
    return con


def create_database(con, name):
    """'create_database' get a pymysql.connection.connection attribute and a name and creates an sql database, called by the name input"""

    with con.cursor() as cursor:
        database = f'CREATE DATABASE {name}'
        cursor.execute(database)


def create_table(con, database, name, *args):
    """'attribute' get a pymysql.connection.connection attribute,
    name of a database, name of a new table and
    a list of arguments containing an sql code to implement on the new table"""

    with con.cursor() as cursor:
        select_database = f'USE {database}'
        cursor.execute(select_database)
        content = str(args).replace("'", "")
        table = f'CREATE TABLE {name} {content}'
        cursor.execute(table)


def filling_table(con, database, table, variables, *data):
    """'filling_table' get a pymysql.connection.connection attribute,
    name of a database, name of a table, string of variables and a list of data
    and add it to the table """

    with con.cursor() as cursor:
        select_database = f"USE {database}"
        cursor.execute(select_database)
        variables = variables.replace("'", "")
        values = len(data) * '%s, '
        values = values.rstrip(", ")
        fill_table = f"INSERT INTO {table} {variables} VALUES ({values})"
        cursor.execute(fill_table, [*data])
        con.commit()


def main():
    """
    Main function of the module, creates the foundation of the 'shufersal' database using the MySQL Server
    """

    user = sys.argv[1]
    password = sys.argv[2]

    connect = connection(user, password)
    database_name = 'shufersal'

    create_database(connect, database_name)
    category_table_data = 'id INT AUTO_INCREMENT PRIMARY KEY', 'name VARCHAR(45)', 'url VARCHAR(200)'
    create_table(connect, database_name, 'category', *category_table_data)
    suppliers_table_data = 'id INT AUTO_INCREMENT PRIMARY KEY', 'name VARCHAR(45)'
    create_table(connect, database_name, 'suppliers', *suppliers_table_data)
    product_details_data = 'id INT AUTO_INCREMENT PRIMARY KEY', 'name VARCHAR(45)', \
                           'FOREIGN KEY (id) REFERENCES suppliers(id)', 'FOREIGN KEY (id) REFERENCES category(id)'
    create_table(connect, database_name, 'product_details', *product_details_data)
    product_price_data = 'id INT AUTO_INCREMENT PRIMARY KEY', 'price INT', 'price_unit INT', \
                         'price_unit_unit VARCHAR(45)', 'container VARCHAR(45)', 'date_time DATETIME', \
                         'FOREIGN KEY (id) REFERENCES product_details(id)'
    create_table(connect, database_name, 'product_price', *product_price_data)


if __name__ == '__main__':
    main()
