import sqlite3 as sql

CONN = sql.connect('lib/scores.db')
CURSOR = CONN.cursor()