# 🏆 SportsBoard — All Sports, One Board

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?style=for-the-badge&logo=django&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PostgreSQL-Production-316192?style=for-the-badge&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Deployed-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" />
  <img src="https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge" />
</p>

<p align="center">
  <b>A centralized web platform for sports event management, player trials, ticket booking, and live sports news — built for Nepal's local sports community.</b>
</p>

<p align="center">
  🌐 <a href="https://sportsboard.onrender.com"><strong>Live Demo → sportsboard.onrender.com</strong></a>
</p>

---

## 📌 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Screenshots](#-screenshots)
- [Local Setup](#-local-setup)
- [Environment Variables](#-environment-variables)
- [Deployment](#-deployment-on-render)
- [Project Structure](#-project-structure)
- [Future Improvements](#-future-improvements)
- [Contributors](#-contributors)

---

## 📖 About

Sports event information in Nepal is scattered across social media, WhatsApp groups, and physical posters. There is no single platform where players, fans, and organizers can connect reliably.

**SportsBoard** solves this by bringing everything into one place:

- **Organizers** create events, run player trials, sell tickets, and verify gate entry via QR code
- **Players/Users** discover events, apply for trials, book tickets, and pay online via Khalti
- **Admins** control the entire platform — approving organizers, managing users, and monitoring activity

---

## ✨ Features

### Users / Athletes
- Register and log in (email, username, or Google)
- Browse upcoming sports events and schedules
- Apply for player selection trials (multi-step form)
- Book event tickets and pay via **Khalti**
- View booking history and trial application status
- Read latest sports news (Hamro Khelkud feed)

### Organizers
- Multi-step event creation (Identity → Logistics → Matches → Tickets)
- Publish and manage player trial/selection forms
- Review, approve, or reject player applications
- QR code-based gate verification for ticket holders
- View ticket sales and revenue reports

### Admins
- Full user and organizer management
- Approve or reject organizer registration requests
- View and resolve user feedback and reports
- Manage sports categories and system settings

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| Framework | Django 5.2 |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Database | SQLite (local) / PostgreSQL (production) |
| Auth | Django AllAuth + custom role-based auth |
| Payments | Khalti Payment Gateway |
| News Feed | Hamro Khelkud (external feed) |
| Static Files | Whitenoise |
| Deployment | Render |
| Version Control | Git + GitHub |

---



## ⚙️ Local Setup

### Prerequisites

- Python 3.11+
- pip
- Git

### Steps

**1. Clone the repository**

```bash
git clone https://github.com/AnujaLamichhane/SportsBoard.git
cd SportsBoard
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

> Note: `psycopg2-binary` may fail on Windows — this is expected. It is only needed on the Linux production server. All other packages install correctly.

**4. Create your `.env` file**

```bash
cp .env.example .env
```

Fill in your values. See the Environment Variables section below.

**5. Run migrations**

```bash
python manage.py migrate
```

**6. Create a superuser**

```bash
python manage.py createsuperuser
```

**7. Run the development server**

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000`

---

## 🔐 Environment Variables

Create a `.env` file in the root directory. Use `.env.example` as a template.

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` for local, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins (include your Render URL) |
| `DATABASE_URL` | PostgreSQL URL — auto-provided by Render |
| `EMAIL_USER` | Gmail address for sending emails |
| `EMAIL_PASS` | Gmail App Password (not your real Gmail password) |
| `KHALTI_SECRET_KEY` | Khalti payment secret key |
| `SITE_ID` | Django sites framework ID — use `1` for fresh deployments |
| `ACCOUNT_HTTP_PROTOCOL` | `https` for production, `http` for local |

> ⚠️ Never commit your `.env` file. It is listed in `.gitignore`.

---

## ☁️ Deployment on Render

### One-time Setup

**1. Create a Render account** at [render.com](https://render.com)

**2. Create a PostgreSQL database**
- Render dashboard → New → PostgreSQL
- Copy the `DATABASE_URL` it provides

**3. Create a Web Service**
- New → Web Service → Connect your GitHub repo
- Branch: `master`
- Build command:
```
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```
- Start command:
```
gunicorn SportsBoard.wsgi:application
```

**4. Add environment variables**

In Render → your service → Environment tab, add all variables from `.env.example` with your real values.

**5. Create superuser after first deploy**

Render dashboard → your service → Shell tab:
```bash
python manage.py createsuperuser
```

**6. Fix the Site domain for allauth**

```bash
python manage.py shell
```
```python
from django.contrib.sites.models import Site
Site.objects.update_or_create(
    id=1,
    defaults={'domain': 'your-app.onrender.com', 'name': 'SportsBoard'}
)
exit()
```

### Redeployment

Every push to `master` triggers an automatic redeploy on Render.

---

## 📁 Project Structure

```
SportsBoard/
├── SportsBoard/          # Project settings and URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/             # User auth, roles, profiles
├── admin_panel/          # Custom admin dashboard
├── homepage/             # Public homepage and sports categories
├── organizer/            # Event management, trials, gate verification
├── payments/             # Khalti payment integration
├── news/                 # Sports news feed
├── templates/            # Project-level templates
├── static/               # Project-level static files
├── media/                # User-uploaded files
├── requirements.txt
├── Procfile
├── .env.example
└── manage.py
```

---

## 🔮 Future Improvements

- [ ] Mobile app (React Native or Flutter)
- [ ] Real-time match score updates via WebSocket
- [ ] Push notifications for events and trials
- [ ] REST API for third-party integrations
- [ ] Advanced analytics dashboard for organizers
- [ ] Multi-language support (Nepali / English)
- [ ] Map integration for event venues
- [ ] Automated test suite (pytest-django)

---

## 👥 Contributors

| Name | Role |
|---|---|
| [Anuja Lamichhane](https://github.com/AnujaLamichhane) | Developer |
| Alisha Baral | Developer |

Supervised by **Er. Basanta Subedi**, Pokhara Engineering College, affiliated to Pokhara University.

---

## 📄 License

Developed as an academic final year project at **Pokhara Engineering College**.

For use, extension, or collaboration, please contact the contributors via GitHub.

---

<p align="center">Made with ❤️ for Nepal's sports community</p>
