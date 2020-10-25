from flask import redirect, render_template, request, session
from functools import wraps
import os

import sqlite3


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



def insertBLOB(id_, title, author, category, content):
    try:
        sqliteConnection = sqlite3.connect('SQLite_Python.db')
        cursor = sqliteConnection.cursor()
        print("Connected to SQLite")
        sqlite_insert_query = """ INSERT INTO blogs
                                  (id, title, author, category, content) VALUES (?, ?, ?, ?, ?)"""

        # Convert data into tuple format
        data_tuple = (id_, title, author, category, content)
        cursor.execute(sqlite_insert_query, data_tuple)
        sqliteConnection.commit()
        print("Image and file inserted successfully as a BLOB into a table")
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to insert blob data into sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("the sqlite connection is closed")