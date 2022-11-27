import pymysql


def connection(user, password):
    """"""
    con = pymysql.connect(host='localhost',
                          user=user,
                          password=password,
                          cursorclass=pymysql.cursors.DictCursor)
    return con


def create_database(con, name):
    """"""
    with con.cursor() as cursor:
        database = f'CREATE DATABASE {name}'
        cursor.execute(database)


def create_table(con, database, name, *args):
    """"""
    with con.cursor() as cursor:
        select_database = f'USE {database}'
        cursor.execute(select_database)
        content = str(args).replace("'", "")
        table = f'CREATE TABLE {name} {content}'
        cursor.execute(table)


def filling_table(con, database, table, variables, *data):
    """"""
    with con.cursor() as cursor:
        select_database = f"USE {database}"
        cursor.execute(select_database)
        variables = variables.replace("'", "")
        values = len(data)*'%s, '
        values = values.rstrip(", ")
        fill_table = f"REPLACE INTO {table} {variables} VALUES ({values})"
        cursor.execute(fill_table, [*data])
        con.commit()


if __name__ == '__main__':
    connect = connection('root', 'rootroot')
    create_database(connect, 'shufersal')
    category_table_data = 'name VARCHAR(45) PRIMARY KEY', 'url VARCHAR(500)'
    create_table(connect, 'shufersal', 'category', *category_table_data)
    suppliers_table_data = 'id INT AUTO_INCREMENT PRIMARY KEY', 'name VARCHAR(45)'
    create_table(connect, 'shufersal', 'suppliers', *suppliers_table_data)
    product_details_data = 'id VARCHAR(45) PRIMARY KEY', 'name VARCHAR(45)', \
                           'FOREIGN KEY (name) REFERENCES category(name)',\
                           'FOREIGN KEY (id) REFERENCES suppliers(id)'
    create_table(connect, 'shufersal', 'product_details', *product_details_data)
    product_price_data = 'id INT AUTO_INCREMENT PRIMARY KEY', 'price INT', 'price_unit INT',\
                         'container VARCHAR(45)'\
                         'FOREIGN KEY (id) REFERENCES product_details(id)'
    create_table(connect, 'shufersal', 'product_price', *product_price_data)
