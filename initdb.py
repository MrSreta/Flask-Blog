import sqlite3
conn = sqlite3.connect("users.db")

conn.execute("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", (1, "First post", "Testing the homepage"))

conn.commit()
conn.close()