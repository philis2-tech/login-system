# 🔐 Authentication System (Flask, OAuth2, Production Deployment)

A production-ready authentication system built with Flask, implementing secure session-based authentication and OAuth2 integrations. Designed with security best practices, modular structure, and deployment readiness in mind.

---

## 🌍 Live Application

👉 https://login-system-7c0c.onrender.com

---

## 🧠 Overview

This project demonstrates a full authentication pipeline including:

* Traditional email/password authentication
* OAuth2 login via Google and Facebook
* Secure session handling and cookie configuration
* Backend validation and persistence using SQLite
* Deployment to a cloud environment

The system is structured to reflect real-world backend practices, with attention to security, environment configuration, and scalability considerations.

---

## 🏗️ Architecture

### Backend

* **Framework:** Flask (WSGI-based microframework)
* **Auth Library:** Authlib (OAuth 2.0 client)
* **Server (Production):** Gunicorn
* **Middleware:** ProxyFix (for reverse proxy compatibility)

### Database

* **Engine:** SQLite
* **Access Layer:** Direct SQL queries via `sqlite3`
* **Schema:**

  ```sql id="dbschema"
  users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password TEXT
  )
  ```

---

## 🔐 Authentication Flows

### 1. Local Authentication

* Passwords hashed using `werkzeug.security`
* Validation includes:

  * Regex-based email validation
  * Password strength scoring (length, case, digits, symbols)
* Session stored using Flask secure cookies

---

### 2. OAuth2 (Third-Party Authentication)

#### Google OAuth

* OpenID Connect flow (`openid email profile`)
* Token exchange handled via Authlib
* User info extracted from ID token / userinfo endpoint

#### Facebook OAuth

* OAuth2 flow via Graph API
* Email permission requested
* Fallback handling for missing email

---

## 🔒 Security Considerations

* Password hashing (no plaintext storage)
* Secrets managed via `.env` (dotenv)
* `.gitignore` prevents credential leakage
* Session configuration:

  ```python id="sesscfg"
  SESSION_COOKIE_SECURE = True
  SESSION_COOKIE_HTTPONLY = True
  SESSION_COOKIE_SAMESITE = "None"
  ```
* Reverse proxy handling using `ProxyFix`
* Duplicate user prevention via database constraint
* OAuth credentials stored securely (environment variables)

---

## ⚙️ Configuration & Environment

Environment variables are required for OAuth providers:

```env id="envvars"
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

FACEBOOK_CLIENT_ID=
FACEBOOK_CLIENT_SECRET=

SECRET_KEY=
```

---

## 🚀 Deployment

* Platform: Render
* Server: Gunicorn (`gunicorn app:app`)
* HTTPS enforced (required for OAuth flows)
* Auto-deploy via GitHub integration

### Deployment considerations:

* Free tier uses ephemeral instances (cold starts possible)
* SQLite is sufficient for demo; not recommended for high concurrency

---

## 📁 Project Structure

```id="projstruct"
Login-system/
│
├── app.py                # Application entry point
├── users.db              # SQLite database
├── requirements.txt      # Dependencies
├── .gitignore
│
├── templates/            # Jinja2 templates
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   └── auth.html
│
├── static/               # CSS assets
│   └── style.css
│
└── .env                  # Environment variables (excluded)
```

---

## 📜 Compliance & Data Handling

* Privacy Policy endpoint implemented
* User data deletion route available (`/delete-account`)
* OAuth data limited to:

  * Email
  * Basic profile info

---

## ⚠️ Limitations

* SQLite is not optimized for high concurrency workloads
* Facebook OAuth restricted to development mode without business verification
* No email verification or password reset flow (planned)

---

## 📈 Future Enhancements

* Migration to PostgreSQL (production-grade DB)
* Password reset via email token flow
* Email verification system
* Rate limiting (e.g., login brute-force protection)
* JWT-based authentication for API support
* OAuth account linking (multiple providers per user)
* Containerization (Docker)

---

## 🧪 Local Development

```bash id="runlocal"
git clone https://github.com/philis2-tech/login-system.git
cd login-system

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
python app.py
```

---

## 👨‍💻 Author

**Philis Maruza**

---

## 📄 License

MIT License

---
