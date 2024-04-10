from flask import current_app, g
from mysql.connector import connect, Error


def open_connection():
    if 'db' not in g:
        config = {
            'user': current_app.config['DB_USER'],
            'password': current_app.config['DB_PASS'],
            'host': current_app.config['DB_HOST'],
            'port': current_app.config['DB_PORT'],
            'database': current_app.config['DB_NAME']
        }

        cnx = None
        try:
            cnx = connect(**config)
            g.db = cnx
        except Error as e:
            print(f"Error connecting to DB {e}")
            if cnx is not None:
                cnx.close()

    return g.db


def close_connection():
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    cnx = open_connection()
    try:
        with current_app.open_resource('db_schemas.sql') as f:
            cursor = cnx.cursor()
            sql_content = f.read().decode('utf8')
            cursor.execute(sql_content)
            cursor.close()
    except Exception as e:
        print(e)
    finally:
        close_connection()
