# Family Hub - Product Requirements Document

## Overview
Self-hosted family organization app. Single Docker container with embedded MongoDB.

## Tech Stack
- **Frontend:** React 18, Tailwind CSS (dark mode), Shadcn UI, Recharts, @zxing/library
- **Backend:** FastAPI (17 modular routers), Python 3.11, pywebpush, BeautifulSoup4
- **Database:** MongoDB 7.0 (embedded in Docker)
- **Real-time:** WebSocket via FastAPI
- **Offline:** Service Worker (cache-first static, network-first API)
- **Push:** Web Push Protocol via pywebpush + VAPID keys
- **AI:** Emergent LLM (GPT-4o-mini) + OpenAI fallback
- **Admin:** FastAPI session-based auth (port 8050)

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

### Admin
- [x] Admin Portal (port 8050, session-based login)
- [x] SMTP, Google Calendar, OpenAI, server config

## Docker
- Single container: MongoDB + FastAPI + Admin Portal
- Supervisor manages all processes
- Backend runs from `/app/backend` directory
- Ports: 8001 (app), 8050 (admin)
- HEALTHCHECK on `/api/health`

## Code Architecture
```
/app/backend/
├── server.py, database.py, auth.py, admin_portal.py
├── models/schemas.py
└── routers/ (auth, family, calendar, shopping, tasks, chores,
    notes, budget, meals, recipes, grocery, contacts, pantry,
    settings, suggestions, utilities, websocket)
```

## Backlog
- [ ] Recurring chores automation
- [ ] Multi-family hub support
