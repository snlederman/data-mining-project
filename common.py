import logging
import json
import pymysql
from googletrans import Translator
from tqdm import tqdm

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
        connect = pymysql.connect(host=read_from_config("HOST"),
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
    con = pymysql.connect(host=read_from_config("HOST"),
                          user=user,
                          password=password,
                          database=read_from_config('DATABASE_NAME'))
    return con


def sql_query(query, user, password):
    """
    "sql_connection" receives a string with sql query and returns it result using pymysql module.
    """
    con = pymysql.connect(host=read_from_config("HOST"),
                          user=user,
                          password=password,
                          database=read_from_config('DATABASE_NAME'))
    with con:
        with con.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        return result


def get_categories_links(user, password):
    categories_link_list_query = f"SELECT url FROM category;"
    categories_link = sql_query(categories_link_list_query, user, password)
    return list(map(lambda x: x[0], categories_link))


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


def create_new_column(user, password, table, column, language, data_type):
    query = f"ALTER TABLE {table} ADD {column}_{language} {data_type} AFTER {column}"
    sql_query(query, user, password)
    logging.info(f'New column, {column}, added to table {table}.')


def update_column_row(user, password, table, column, language, row, value):
    database = read_from_config('DATABASE_NAME')
    variable = f"{column}_{language}"
    con = create_connection(user, password)
    with con.cursor() as cursor:
        select_database = f"USE {database}"
        cursor.execute(select_database)
        update_query = f"UPDATE {table} SET {variable} = %s WHERE id = {row}"
        cursor.execute(update_query, f'{translate_text(*value, language)}')
        con.commit()


def translate_text(text, language):
    """Translates text into the target language.
    """
    translator = Translator()
    if text == 'NaN':
        trans_result = 'NaN'
    else:
        trans_result = translator.translate(text, dest=language).text
    logging.info(f'Translated input: "{text}" to "{trans_result}"')
    return trans_result


def translate(user, password, table, column, language, data_type=read_from_config("DATA_TYPE")):
    query = f'SELECT {column} FROM {table}'
    data = sql_query(query, user, password)
    row = 0
    for i in tqdm(range(18704, len(data))):
        row += 1
        try:
            create_new_column(user, password, table, column, language, data_type)
            update_column_row(user, password, table, column, language, row, data[i])
        except pymysql.err.OperationalError:
            update_column_row(user, password, table, column, language, row, data[i])
