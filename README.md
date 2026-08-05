<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=32&duration=3000&pause=1000&color=0EA5E9&center=true&vCenter=true&width=600&lines=SmartInbox;AI-Powered+Inbox+Event+Tracker;Never+Miss+a+Deadline+Again" alt="Typing SVG" />

### Built by [Balaji A](https://github.com/yashvanthbalaji)

<p>
  <a href="https://smart-inbox-frontend.onrender.com"><img src="https://img.shields.io/badge/🚀_Live_App-Visit_Now-0EA5E9?style=for-the-badge" /></a>
  <a href="https://smart-inbox-r65r.onrender.com/api/health"><img src="https://img.shields.io/badge/API-Live-22C55E?style=for-the-badge" /></a>
</p>

<p>
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/Gemini_AI-Gemma_%2F_Flash--Lite-8E75B2?style=flat-square&logo=googlegemini&logoColor=white" />
  <img src="https://img.shields.io/badge/Deployed_on-Render-46E3B7?style=flat-square&logo=render&logoColor=white" />
</p>

**SmartInbox reads your Gmail, uses AI to pull out every meeting, exam, deadline, and interview buried in your emails, and puts it all in one place — a live dashboard, a calendar, or a self-updating Google Sheet. No manual entry, ever.**

[**🔗 Try it live →**](https://smart-inbox-frontend.onrender.com)

</div>

---

## 🎯 The Problem

Students miss real opportunities — interview calls, exam notices, registration deadlines — because they're buried three scrolls deep in a cluttered inbox. SmartInbox fixes that by reading your Gmail automatically, every 15 minutes, and surfacing what actually matters.

## ✨ What It Does

| | |
|---|---|
| 🔐 **One-click Google login** | No passwords stored — secure OAuth2, revoke access anytime |
| 🤖 **AI-powered extraction** | Gemini reads email content and pulls structured events: title, date, time, type, location |
| 📅 **Live dashboard + calendar** | Filterable table view and a full month calendar, both real-time |
| 🔄 **Fully automated** | A background scheduler polls Gmail every 15 minutes — zero manual effort, even while you sleep |
| 📊 **Google Sheets sync** | Prefer a spreadsheet? Events auto-sync to a live Sheet with dropdowns and auto-flagged overdue deadlines |
| 📄 **One-click PDF export** | Download your full event list, styled and ready to share |
| 📱 **PWA-ready** | Add to your phone's home screen — works like a native app |

---

## 🏗️ How It Works

```
┌─────────────────┐        ┌──────────────────┐        ┌─────────────────────┐
│  React Frontend  │───────▶│   Flask REST API   │───────▶│  Gmail · Gemini AI    │
│  (Vite, Router)  │  JWT   │  (JWT + OAuth2)     │        │  Google Sheets · DB   │
└─────────────────┘        └──────────────────┘        └─────────────────────┘
```

**Every 15 minutes, in the background, for every connected user:**

1. **Fetch** — Gmail API pulls new emails matching relevance keywords (free-tier, zero AI cost)
2. **Extract** — Unprocessed emails get batched into a *single* Gemini call (not one per email) to save quota
3. **Fallback** — If the primary model (Gemma) fails validation, it automatically retries on a secondary model (Gemini Flash-Lite) — the app never silently drops an email
4. **Store & Sync** — Structured events land in PostgreSQL and sync to the user's Google Sheet
5. **Serve** — Dashboard, calendar, and Sheet all reflect the update, no user action required

## 🧠 Engineering Decisions Worth Knowing About

- **Quota-aware AI pipeline**: batching + a two-tier model fallback (Gemma 1,500 req/day → Gemini Flash-Lite 500 req/day) means the app is architected to comfortably support 50+ concurrent users on entirely free-tier AI quota — without batching, that same load would exhaust a single model's daily limit in under an hour.
- **SPA-safe OAuth2**: Flask issues short-lived JWTs after the OAuth handshake and hands them to the React SPA via a redirect — cross-origin session cookies, `SameSite`/`Secure` flags, and `ProxyFix` middleware were all tuned specifically to survive Render's proxy layer in production, not just work on localhost.
- **Zero-downtime background jobs**: APScheduler runs inside the same process as the web server, guarded against duplicate instantiation across gunicorn workers — with automatic retry-limiting so a single unparseable email can't loop forever and leak memory.
- **Resilient by default**: every external call (Gmail, Gemini, Sheets) is wrapped so one user's failure, or one bad email, never takes down the whole polling cycle for everyone else.

## 🛠️ Tech Stack

**Frontend** — React 18 · Vite · React Router · Axios · Plain CSS (custom design system, no framework)
**Backend** — Python 3.11 · Flask 3.0 (REST API) · SQLAlchemy · Flask-Migrate · Flask-JWT-Extended · Authlib
**Database** — PostgreSQL
**AI** — Google Gemini API (Gemma 4 31B primary, Gemini 3.1 Flash-Lite fallback)
**Background Jobs** — APScheduler
**Integrations** — Gmail API · Google Sheets API · ReportLab (PDF)
**Deployment** — Render.com (Web Service + Static Site), cron-job.org (uptime ping)

## 🖥️ Screenshots

<div align="center">
<i>Add screenshots here: landing page, dashboard with real events, calendar view, Google Sheet sync</i>
</div>

## 🚀 Live Links

- **App**: [smart-inbox-frontend.onrender.com](https://smart-inbox-frontend.onrender.com)
- **API health check**: [smart-inbox-r65r.onrender.com/api/health](https://smart-inbox-r65r.onrender.com/api/health)

> Hosted on Render's free tier — first load after inactivity may take a few seconds to wake up.

## 📂 Project Structure

```
smartinbox/
├── backend/          Flask REST API, JWT auth, OAuth2, AI pipeline, scheduler
│   ├── routes/       /api/auth, /api/events, /api/fetch, /api/sheet
│   ├── services/      gmail_service, gemini_service, sheets_service, scheduler_jobs
│   └── models.py     User, UserProfile, RawEmail, ExtractedEvent
└── frontend/         React SPA
    ├── pages/         Dashboard, Calendar, Profile, Google Sheet
    └── components/    EventTable, EventFilters, Navbar, EventModal
```

## ⚙️ Running Locally

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in your own keys
flask db upgrade
python app.py

# Frontend
cd frontend
npm install
npm run dev
```

You'll need your own Google Cloud OAuth credentials and a Gemini API key — see `.env.example` in `backend/` for the full list.

---

<div align="center">

**Built end-to-end — OAuth, AI, background automation, and deployment — as a full-stack portfolio project.**

⭐ If this is useful or interesting, a star is appreciated!

</div>