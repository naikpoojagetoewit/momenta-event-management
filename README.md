# Momenta – AI-Powered Event Management and Booking System

**Creating Moments That Matter**

A full-stack Flask event management platform with separate portals for Clients,
Admins, Event Managers and Team Members — booking, service selection, a live
budget calculator, simulated online payments, PDF invoices, and progress tracking.

---

## 1. Requirements

- Python 3.10+
- pip
- (Optional) PostgreSQL 13+ — the project runs on **SQLite by default**, so
  you don't need PostgreSQL installed just to try it out.

## 2. Quick Start (VS Code)

```bash
# 1. Open this folder in VS Code
# 2. Open a terminal (Ctrl+`) and run:

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# 3. Copy the environment file
cp .env.example .env        # Windows: copy .env.example .env

# 4. Seed the database with demo data (users, events, services, sample bookings)
python seed.py

# 5. Run the app
python run.py
```

Open **http://127.0.0.1:5000** in your browser.

## 3. Demo Logins (created by seed.py)

| Role          | Email                | Password    |
|---------------|-----------------------|-------------|
| Admin         | admin@momenta.com     | admin123    |
| Event Manager | manager@momenta.com   | manager123  |
| Team Member   | team@momenta.com      | team123     |
| Client        | client@momenta.com    | client123   |

You can also register a new client account from the **Register** page.

## 4. Switching to PostgreSQL

By default `SQLALCHEMY_DATABASE_URI` falls back to a local `momenta.db`
SQLite file so the project runs with zero setup. To use PostgreSQL instead:

1. Create a database: `createdb momenta_db` (or via pgAdmin)
2. In `.env`, uncomment and edit:
   ```
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/momenta_db
   ```
3. Re-run `python seed.py` to create tables and demo data in Postgres.

## 5. Project Structure

```
momenta/
├── app/
│   ├── __init__.py          # App factory, blueprint registration
│   ├── config.py             # Config (DB, mail, Razorpay keys)
│   ├── extensions.py         # Flask extensions (db, login, mail, migrate)
│   ├── models.py             # All SQLAlchemy models (Users, Bookings, etc.)
│   ├── auth/                 # Register / Login / Forgot password
│   ├── main/                 # Public site: home, about, services, events, gallery, contact
│   ├── client/                # Client dashboard, booking flow, payments, invoices, feedback
│   ├── admin/                 # Admin dashboard, user/event/service/booking/team management
│   ├── manager/                # Event Manager dashboard & event coordination
│   ├── team/                    # Team Member dashboard & task updates
│   ├── utils/                    # Budget calculator, PDF invoices, email, decorators
│   ├── static/                    # CSS, JS, uploads, generated invoices
│   └── templates/                  # Jinja2 templates (Bootstrap 5)
├── seed.py                    # Populates demo data
├── run.py                     # App entry point
├── requirements.txt
├── .env.example
└── README.md
```

## 6. Feature Notes / What's Implemented

- **Auth**: registration, login, logout, forgot/reset password (session-based via Flask-Login).
- **Client**: profile management, multi-step event booking with service selection,
  a **live AJAX budget calculator** (exact total + an AI-style suggested budget range),
  simulated payment flow (UPI/Card/Net Banking), booking tracking, booking history,
  **PDF invoice download** (ReportLab), and post-event star-rating feedback.
- **Admin**: dashboard with stats + Chart.js revenue/popularity charts, full CRUD
  for users, events, services, team members, booking approval/rejection and
  event-manager assignment, daily/monthly/annual revenue reports.
- **Event Manager**: view assigned events, update event stage (Planning → ... →
  Event Completed), assign tasks to team members.
- **Team Member**: view assigned tasks, update task status, upload proof photos,
  mark attendance.
- **Emails**: registration/booking/payment/status-update emails are sent via
  Flask-Mail if SMTP credentials are set in `.env`; otherwise they're safely
  logged to the console instead of failing (`MAIL_SUPPRESS_SEND`).
- **Payments**: a simulated gateway is used out of the box so you can test the
  full flow with zero configuration. Swap in real Razorpay Checkout using the
  `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` in `.env` for production use.
- **AI Budget Prediction**: `app/utils/budget.py` computes the exact live total
  from selected services, plus a weighted "AI suggested range" based on event
  type, guest count and number of services — the lightweight equivalent of the
  Linear Regression / Random Forest estimate described in the spec, with no
  heavy ML dependency required to run the project instantly.

### Intentionally simplified for a runnable v1
A few advanced items from the spec (real-time chat, QR-code verification,
full ML model training pipeline) are stubbed or simplified so the project
installs and runs cleanly out of the box. The architecture (blueprints,
models, utils) is set up so each can be extended without restructuring:
- Real-time chat → add a `chat` blueprint + Flask-SocketIO.
- QR codes → `pip install qrcode` and generate one per booking in `utils/`.
- Heavier ML budget model → train a scikit-learn model offline and load it
  in `utils/budget.py` in place of `predict_budget_ai()`.

## 7. Common Issues

- **"ModuleNotFoundError"** → make sure your virtual environment is activated
  and `pip install -r requirements.txt` completed without errors.
- **psycopg2 install fails** → you likely don't need PostgreSQL; just leave
  `DATABASE_URL` unset in `.env` to use SQLite.
- **Port already in use** → change the port in `run.py` (`app.run(port=5001)`).

---

Momenta · Creating Moments That Matter
