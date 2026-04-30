from flask import Flask, render_template, request, redirect, url_for, session
import os
import re
import sqlite3
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
import os

load_dotenv()
# ---------------- APP SETUP ---------------- #

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True
)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.permanent_session_lifetime = timedelta(days=7)

# ---------------- OAUTH SETUP ---------------- #


oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v2/',
    jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


facebook = oauth.register(
    name='facebook',
    client_id=os.getenv("FACEBOOK_CLIENT_ID"),
    client_secret=os.getenv("FACEBOOK_CLIENT_SECRET"),
    access_token_url='https://graph.facebook.com/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    api_base_url='https://graph.facebook.com/',
    client_kwargs={
        'scope': 'email'
    }
)
# ---------------- DATABASE ---------------- #

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()


init_db()

# ---------------- GOOGLE LOGIN ---------------- #


@app.route('/login/google')
def login_google():
    return google.authorize_redirect(url_for('google_callback', _external=True))


@app.route('/login/google/callback')
def google_callback():
    token = google.authorize_access_token()

    user_info = token.get('userinfo')

    # fallback if needed
    if not user_info:
        user_info = google.get('userinfo').json()

    email = user_info['email']

    # Save user if not exists
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()

    if not user:
        conn.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, "google_user")
        )
        conn.commit()

    conn.close()

    session["user"] = email

    return redirect(url_for('dashboard'))

# ---------------- ROUTES ---------------- #


@app.route("/")
def home():
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Email validation
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            return "Invalid email format"

        # Password strength check
        score, feedback = check_password_strength(password)
        if score < 3:
            return "Weak password: " + ", ".join(feedback)

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                (email, hashed_password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered"

        conn.close()
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    remember = request.form.get("remember")

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user"] = email

        if remember:
            session.permanent = True

        return redirect(url_for("dashboard"))

    return "Invalid credentials"


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("home"))

    return render_template("dashboard.html", user=session["user"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route('/login/facebook')
def login_facebook():
    return facebook.authorize_redirect(url_for('facebook_callback', _external=True))


@app.route('/login/facebook/callback')
def facebook_callback():
    token = facebook.authorize_access_token()
    user_info = facebook.get('me?fields=id,name,email').json()

    email = user_info.get('email')

    if not email:
        return "Facebook email not available"

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()

    if not user:
        conn.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, "facebook_user")
        )
        conn.commit()

    conn.close()

    session["user"] = email
    return redirect(url_for('dashboard'))

# ---------------- PASSWORD STRENGTH ---------------- #


def check_password_strength(password):
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("At least 8 characters")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Add an uppercase letter")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Add a lowercase letter")

    if re.search(r"[0-9]", password):
        score += 1
    else:
        feedback.append("Add a number")

    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        score += 1
    else:
        feedback.append("Add a symbol")

    return score, feedback


if __name__ == "__main__":
    app.run(debug=True)
