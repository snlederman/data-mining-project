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
        table = f'CREATE TABLE {name}{content}'
        cursor.execute(table)


def filling_table(con, database, table, variables, *data):
    """"""
    with con.cursor() as cursor:
        select_database = f"USE {database}"
        cursor.execute(select_database)
        variables = variables.replace("'", "")
        values = len(data)*'%s, '
        values = values.rstrip(", ")
        fill_table = f"INSERT INTO {table} {variables} VALUES ({values})"
        cursor.execute(fill_table, [*data])
        con.commit()


if __name__ == '__main__':
    connect = connection('root', 'rootroot')
    shufersal = create_database(connect, 'shufersal')
    create_table(connect, shufersal, 'category', 'id INT AUTO_INCREMENT PRIMARY KEY',
                 'name VARCHAR(45)', 'url VARCHAR(200)')
    create_table(connect, shufersal, 'suppliers', 'id INT AUTO_INCREMENT PRIMARY KEY',
                 'name VARCHAR(45)')
    create_table(connect, shufersal, 'product_details', 'id INT AUTO_INCREMENT PRIMARY KEY',
                 'name VARCHAR(45)', 'FOREIGN KEY (id) REFERENCES suppliers(id)',
                 'FOREIGN KEY (id) REFERENCES category(id)')
    create_table(connect, shufersal, 'id INT AUTO_INCREMENT PRIMARY KEY', 'price INT',
                 'price_unit INT', 'price_unit_unit VARCHAR(45)', 'container VARCHAR(45)',
                 'date_time DATETIME', 'FOREIGN KEY (id) REFERENCES product_details(id)')
