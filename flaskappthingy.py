from flask import Flask, request, redirect, render_template, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_hashed = generate_password_hash(password)
        conn = sqlite3.connect("users.db")
        try:
            conn.execute("INSERT INTO users (username,password_hash) VALUES (?,?)", (username,password_hashed))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "That username is already taken."
        conn.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user is None:
            return "Invalid username or password."
        elif not check_password_hash(user["password_hash"], password):
            return "Invalid username or password."
        else:
            session["user_id"] = user["id"]
            return redirect("/")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
        if "user_id" not in session:
             return redirect("/login")
        return "Welcome!"

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect("/login")

@app.route("/")
def index():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    posts = conn.execute("""
        SELECT posts.id, posts.title, posts.content, posts.created_at, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """).fetchall()
    conn.close()
    return render_template("index.html", posts=posts)

@app.route("/new_post", methods=["GET","POST"])
def new_post():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        conn = sqlite3.connect("users.db")
        conn.execute("INSERT INTO posts (user_id, title, content) VALUES (?,?,?)", (session["user_id"], title, content))
        conn.commit()
        conn.close()
        return redirect("/")
    
    return render_template("new_post.html")

@app.route("/post/<int:post_id>")
def view_post(post_id):
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    post = conn.execute("""
            SELECT posts.id, posts.title, posts.content, posts.created_at, users.username
            FROM posts
            JOIN users ON posts.user_id = users.id 
            WHERE posts.id = ?
            """, (post_id,)).fetchone()
    conn.close()
    if post is None:
        return "Post not found.", 404

    return render_template("post.html", post=post)

if __name__ == "__main__":
    app.run()