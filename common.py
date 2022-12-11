import json
import pymysql
from googletrans import Translator


def read_from_config(key):
    """ gets a key and returns its value from the configuration file 'conf.json'"""
    try:
        with open('conf.json', 'r') as f:
            config = json.load(f)
            try:
                return config[key]
            except KeyError as err:
                msg = f"KeyError in the configuration file, conf.json, missing key: {key} "
                print(msg)
                raise KeyError

    except FileNotFoundError as err:
        msg = "configuration file, conf.json, not found"
        print(msg)
        raise FileNotFoundError


def connection(user, password):
    """'connection' gets a user and a password to MySQL Server
    and returns a pymysql.connection.connection attribute"""

    try:
        connect = pymysql.connect(host='localhost',
                                  user=user,
                                  password=password,
                                  cursorclass=pymysql.cursors.DictCursor)
    except RuntimeError as err:
        print(f'{err}')
    except pymysql.err.OperationalError as err2:
        print(f"MySQL server access denied for user '{user}' at localhost (using password: {password})")
        raise pymysql.err.OperationalError

    return connect


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
    TARGET_TRANS = read_from_config('TARGET_TRANS')
    translator = Translator()
    translation = translator.translate(text, dest=TARGET_TRANS)
    return translation.text

