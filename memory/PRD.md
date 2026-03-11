# Family Hub - Product Requirements Document

## Overview
Self-hosted family organization app. Single Docker container with embedded MongoDB.

## Tech Stack
- **Frontend:** React 18, Tailwind CSS (dark mode), Shadcn UI, Recharts, @zxing/library
- **Backend:** FastAPI (18 modular routers), Python 3.11, pywebpush, BeautifulSoup4
- **Database:** MongoDB 7.0 (embedded in Docker), motor 3.7.1 + pymongo 4.9+
- **Real-time:** WebSocket via FastAPI
- **Offline:** Service Worker (cache-first static, network-first API)
- **Push:** Web Push Protocol via pywebpush + VAPID keys
- **AI:** Emergent LLM (GPT-4o-mini) + OpenAI fallback

## All Implemented Features

### Core Modules (Full CRUD)
- [x] Calendar (+ Google Calendar sync)
- [x] Shopping List, Tasks, Notes, Grocery List, Contacts
- [x] Budget Tracker with charts + summary
- [x] Meal Planner, Recipe Box (+ URL import)
- [x] Pantry (barcode scanner + web lookup)
- [x] Chores + Rewards + Leaderboard (gamified)

### Real-time, Push & Offline
- [x] WebSocket real-time updates across family
- [x] Push notifications on ALL module changes (pywebpush + VAPID)
- [x] Service Worker offline caching
- [x] PWA installable

### AI
- [x] AI meal suggestions from pantry (prioritizes expiring items, avoids recent meals)
- [x] Emergent LLM / OpenAI GPT-4o-mini

### Data Management
- [x] Full JSON export + CSV per module
- [x] Data import/restore (merge mode — duplicates skipped)
- [x] QR code for mobile setup

### UI/UX
- [x] Dark mode toggle (persisted)
- [x] Mobile responsive
- [x] Role-based access (Owner > Parent > Member > Child)

### Admin / Server Management (Merged into Owner Settings)
- [x] Server status dashboard (Backend, Database, SMTP, OpenAI, Google)
- [x] SMTP email configuration + test connection
- [x] Google Calendar API configuration
- [x] OpenAI API key configuration
- [x] Server config (JWT secret, CORS, DB name)
- [x] Server log viewer (backend, frontend, error logs)
- [x] Server restart capability
- [x] All admin features gated to Owner role only (403 for non-owners)

## Docker
- Single container: MongoDB + FastAPI
- Supervisor manages all processes
- Backend runs from `/app/backend` directory
- Port: 8001 (app)
- HEALTHCHECK on `/api/health`

## Code Architecture
```
/app/backend/
├── server.py, database.py, auth.py
├── models/schemas.py
├── services/push.py
└── routers/ (admin, auth, family, calendar, shopping, tasks, chores,
    notes, budget, meals, recipes, grocery, contacts, pantry,
    settings, suggestions, utilities, websocket)
```

## Key API Endpoints
- `/api/admin/*` — Owner-only server management (status, config, logs, reboot)
- `/api/auth/*` — Registration, login, PIN login
- `/api/family/*` — Family CRUD, member management
- `/api/calendar/*`, `/api/shopping/*`, etc. — Module CRUD
- `/api/ws` — WebSocket
- `/api/notifications/*` — Push subscriptions
- `/api/export/*`, `/api/import/*` — Data backup/restore

## Removed
- [x] admin_portal.py (separate Flask/FastAPI admin on port 8050) — MERGED into main app
- [x] Port 8050 exposure in Dockerfile
- [x] Separate admin supervisor config

## Backlog
- [ ] Recurring chores automation
- [ ] Multi-family hub support
- [ ] Enhance AI Meal Suggestions with dietary restrictions
- [ ] More granular dark mode theme controls
- [ ] CSS refactoring (dark mode overrides → Tailwind dark: variants)
