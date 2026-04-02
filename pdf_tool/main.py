from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from utils.pdf_processor import convert_pdf_to_template_excel
app = Flask(__name__)
app.secret_key = "secret123"

# ---------- DB INIT ----------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

@app.route("/")
def home():
    return redirect("/login")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except sqlite3.IntegrityError:
            return "User already exists"

        conn.close()
        return redirect("/login")

    return render_template("register.html")

# ---------- FORGOT PASSWORD ----------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":
        username = request.form["username"]
        new_password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()

        if user:
            c.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
            conn.commit()
            conn.close()
            return "Password updated successfully"
        else:
            conn.close()
            return "User not found"

    return render_template("forgot.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")

# ---------- UPLOAD ----------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        pdf = request.files.get("pdf_file")

        if pdf and pdf.filename != "":
            
            # Folder create (agar nahi hai)
            upload_folder = "static/uploads"
            os.makedirs(upload_folder, exist_ok=True)

            # Save file
            pdf_path = os.path.join(upload_folder, pdf.filename)
            pdf.save(pdf_path)

            # Process PDF → Template Excel
            output_path = convert_pdf_to_template_excel(pdf_path)

            return render_template(
                "upload.html",
                message="File processed successfully!",
                csv_file=output_path
            )

    return render_template("upload.html")
# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------- RUN ----------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)

