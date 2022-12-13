import logging
import json
import pymysql
from googletrans import Translator
import tqdm

logging.basicConfig(filename='common.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


def read_from_config(key):
    """ gets a key and returns its value from the configuration file 'conf.json'"""
    try:
        with open('conf.json', 'r') as f:
            config = json.load(f)
            try:
                return config[key]
            except KeyError:
                msg = f"KeyError in the configuration file, conf.json, missing key: {key}"
                print(msg)
                logging.error(f'KeyError in the configuration file, conf.json,'
                              f' missing key: %s', {key})
                raise KeyError
    except FileNotFoundError:
        msg = "configuration file, conf.json, not found"
        print(msg)
        logging.warning(f'configuration file, conf.json, not found: %s')
        raise FileNotFoundError


def connection(user, password):
    """'connection' gets a user and a password to MySQL Server
    and returns a pymysql.connection.connection attribute"""

    try:
        connect = pymysql.connect(host='localhost',
                                  user=user,
                                  password=password,
                                  cursorclass=pymysql.cursors.DictCursor)
        return connect
    except RuntimeError as err:
        print(f'{err}')
    except pymysql.err.OperationalError:
        print(f"MySQL server access denied for user '{user}' at localhost (using password: {password})")
        raise pymysql.err.OperationalError


def create_connection(user, password):
    con = pymysql.connect(host='localhost',
                          user=user,
                          password=password,
                          database=read_from_config('DATABASE_NAME'))
    return con


def sql_query(query, user, password):
    """
    "sql_connection" receives a string with sql query and returns it result using pymysql module.
    """
    logging.info(f'SQL query received: {query}')
    con = pymysql.connect(host='localhost',
                          user=user,
                          password=password,
                          database=read_from_config('DATABASE_NAME'))
    with con:
        with con.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            logging.info(f'SQL query result received')
        return result


def get_categories_links(user, password):
    categories_link_list_query = f"SELECT url FROM category;"
    categories_link = sql_query(categories_link_list_query, user, password)
    return list(map(lambda x: x[0], categories_link))


def create_new_column(user, password, table, column, data_type):
    query = f"ALTER TABLE {table} ADD {column}_{read_from_config('TARGET_TRANS')} {data_type} AFTER {column}"
    sql_query(query, user, password)
    logging.info(f'Column {column}, data type: {data_type}, where added to table {table}')


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
        fill_table = f"REPLACE INTO {table} {variables} VALUES ({values})"
        cursor.execute(fill_table, [*data])
        con.commit()


def translate_text(text):
    """Translates text into the target language.
    """
    translator = Translator()
    result = translator.translate(text, dest=read_from_config('TARGET_TRANS')).text
    logging.info(f'Translation: {text} where translated to {result}')
    return result


def translate(user, password, table, column, data_type=read_from_config("DATA_TYPE")):
    logging.info(f'Starting to translate table {table}, column {column}')
    con = create_connection(user, password)
    database = read_from_config('DATABASE_NAME')
    variable = f"{column}_{read_from_config('TARGET_TRANS')}"
    query = f'SELECT {column} FROM {table}'
    data = sql_query(query, user, password)
    row = 0
    for value in data:
        row += 1
        try:
            with con.cursor() as cursor:
                create_new_column(user, password, table, column, data_type)
                logging.info(f'New column, {column}, added to table {table}')
                select_database = f"USE {database}"
                cursor.execute(select_database)
                update_query = f"UPDATE {table} SET {variable} = %s WHERE id = {row}"
                cursor.execute(update_query, f'{translate_text(*value)}')
                con.commit()
        except pymysql.err.OperationalError:
            with con.cursor() as cursor:
                select_database = f"USE {database}"
                cursor.execute(select_database)
                update_query = f"UPDATE {table} SET {variable} = %s WHERE id = {row}"
                cursor.execute(update_query, f'{translate_text(*value)}')
                con.commit()
