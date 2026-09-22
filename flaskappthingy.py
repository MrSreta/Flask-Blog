from flask import Flask, request, redirect, render_template, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "yippityappity"

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
            return redirect("/dashboard")

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

if __name__ == "__main__":
    app.run()