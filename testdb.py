import sqlite3
conn = sqlite3.connect("users.db")
print(conn.execute("SELECT * FROM posts").fetchall())
conn.close()