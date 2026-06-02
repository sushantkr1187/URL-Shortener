# URL-Shortener

A lightweight URL shortening service built with **Flask** and **PostgreSQL**. Paste a long URL, generate a compact short link, and share it instantly.

## 🌐 Live Demo

**Website:** https://url-shortener-rplo.onrender.com/

**Demo Video:**

![Demo](assets/demo.gif)

---

## ✨ Features

- Generate short URLs instantly
- Automatic redirection to original URLs
- Clean and responsive user interface
- Random unique short code generation
- PostgreSQL database integration
- Automatic timestamp recording
- Persistent cloud-hosted database
- Deployed and accessible through the web

---

## 🛠️ Tech Stack

### Backend
- Python
- Flask
- PostgreSQL
- Psycopg

### Frontend
- HTML5
- CSS3
- Jinja2 Templates

### Deployment
- Gunicorn
- Render

---

## 📂 Project Structure

```text
url_shortener/
│
├── assets/
│   ├── demo.gif
│   ├── home.png
│   └── result.png
│
├── static/
│   └── logo.png
│
├── templates/
│   ├── index.html
│   └── result.html
│
├── LICENSE
├── README.md
├── app.py
├── procfile
└── requirements.txt
```

---

## 🚀 How It Works

1. User enters a URL.
2. The application generates a unique short code.
3. The URL mapping is stored in PostgreSQL.
4. A timestamp is automatically recorded.
5. A shortened URL is returned.
6. Visiting the shortened URL redirects the user to the original destination.

---

## ⚙️ Database Schema

```sql
CREATE TABLE IF NOT EXISTS urls (
    short_code TEXT PRIMARY KEY,
    original_url TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚙️ Local Installation

### Clone the Repository

```bash
git clone <repository-url>
cd <repository-folder>
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create PostgreSQL Database

```sql
CREATE DATABASE urlshortener;
```

### Configure Environment Variables

Set a `DATABASE_URL` environment variable.

Example:

```text
postgresql://username:password@localhost:5432/urlshortener
```

### Run the Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

in your browser.

---

## Important Note

When running locally, the generated short URL may appear in the form:

```text
https://url-shortener-rplo.onrender.com/<code>
```

Since your local Flask server is running on your machine, replace the domain with:

```text
http://127.0.0.1:5000/<code>
```

Example:

```text
Generated:
https://url-shortener-rplo.onrender.com/abc123

Open locally:
http://127.0.0.1:5000/abc123
```

This occurs because the application is currently configured to generate shortened URLs using the deployed Render domain. When testing locally, replace the domain with your local Flask server address.
---
## 📸 Screenshots

### Home Page

![Home Page](assets/home.png)

### Generated Short URL

![Generated URL](assets/result.png)

---

## 🎯 Learning Outcomes

This project was built to learn and practice:

- Flask routing
- Dynamic URLs
- HTML forms
- Jinja2 templating
- PostgreSQL database operations
- Database connectivity using Psycopg
- CRUD fundamentals
- Environment variables and configuration management
- Cloud database integration
- Web application deployment
- GitHub and Render workflows

---

## 🔮 Future Improvements

- Click tracking
- URL analytics dashboard
- Custom short codes
- URL expiration dates
- REST API support
- User accounts and authentication

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Sushant Kumar Kushwaha**

GitHub: https://github.com/sushantkr1187

If you found this project useful, consider giving it a ⭐ on GitHub.
