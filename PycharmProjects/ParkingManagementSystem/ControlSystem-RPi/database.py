import sqlite3
from sqlite3 import Error
from datetime import datetime, timedelta

DB_PATH = r'/home/pi/parking.db'
# parking table
create_table_sql = """CREATE TABLE IF NOT EXISTS parking (
	licence text PRIMARY KEY,
	expiry_date text);"""

insert_sql = """INSERT INTO parking(licence, expiry_date)
              VALUES(?,?)"""

sample_licence = ['TFS676', 'DB6007', 'YPD640', '1AB1CD']

sample_expired = ['I35VQD', 'CD130A']

try:
    db = sqlite3.connect(DB_PATH) # create database object
    cur = db.cursor()
    cur.execute(create_table_sql) # create table

    # insert sample licences
    expiry_date = datetime.now() + timedelta(days=10)
    expiry_date = expiry_date.strftime("%Y-%m-%d")
    for licence in sample_licence:
        cur.execute(insert_sql, (licence, expiry_date))

    expiry_date = datetime.now() + timedelta(days=-1)
    expiry_date = expiry_date.strftime("%Y-%m-%d")
    for licence in sample_expired:
        cur.execute(insert_sql, (licence, expiry_date))

    db.commit()
except Error as e:
    print(e)
finally:
    if db:
        db.close()

