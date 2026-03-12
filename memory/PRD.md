# Family Hub - Product Requirements Document

## Overview
Self-hosted family organization app. Single Docker container with embedded MongoDB.

## Tech Stack
- **Frontend:** React 18, Tailwind CSS (dark mode), Shadcn UI, Recharts, @zxing/library
- **Backend:** FastAPI (18 modular routers), Python 3.11, pywebpush, BeautifulSoup4, httpx HTTP/2
- **Database:** MongoDB 7.0 (embedded in Docker), motor 3.7.1 + pymongo 4.9+
- **Real-time:** WebSocket via FastAPI
- **Offline:** Service Worker (cache-first static, network-first API)
- **Push:** Web Push Protocol via pywebpush + VAPID keys
- **AI:** Emergent LLM (GPT-4o-mini) + OpenAI fallback

## All Implemented Features

### Core Modules (Full CRUD)
- [x] Calendar (+ Google Calendar sync via OAuth)
- [x] Shopping List, Tasks, Notes, Grocery List, Contacts
- [x] Budget Tracker with charts + summary
- [x] Meal Planner (+ add missing ingredients to grocery), Recipe Box (+ URL import 7+ sites)
- [x] Pantry (barcode scanner + web lookup + auto-categorization 60+ keywords)
- [x] Chores + Rewards + Leaderboard (gamified, live points from leaderboard)

### Account & Security
- [x] Change password (current + new + confirm, 6-char min)
- [x] Owner/Parent reset member passwords (temp password generation)
- [x] last_login tracking on all login flows
- [x] Pending invite detection (members without last_login show "Pending" badge)
- [x] Remove pending invites (fully deletes unjoined user accounts)

### Google Calendar Integration
- [x] OAuth flow: /api/calendar/google/auth → Google OAuth → callback → token storage
- [x] Dynamic config via get_google_config() (reads os.environ at call time, not stale imports)
- [x] Sync family events to Google Calendar
- [x] Connect/Disconnect/Sync buttons in Settings → Integrations tab
- [x] Setup instructions directing to Server Settings → Google tab

### Admin / Server Management (Owner-only)
- [x] Status dashboard, config panels (SMTP/Google/OpenAI/Server)
- [x] All configs use dynamic os.environ reads (SMTP, Google, OpenAI)
- [x] Test email, log viewer, server restart

### Recipe URL Import (httpx HTTP/2)
- [x] 7+ sites: BBC Good Food, NYT Cooking, Sally's Baking, Pinch of Yum, Minimalist Baker, RecipeTin Eats, Love and Lemons
- [x] JSON-LD parser handles all formats (@type as string/list, @graph, nested images)
- [x] Error response (not blank form) when extraction fails

### Real-time, Push & Offline
- [x] WebSocket, Push notifications, PWA, Dark mode

### Mobile
- [x] Sticky header with z-40, safe-area-inset-top for notched phones
- [x] 44x44px minimum tap targets with active state feedback

## Docker
- Single container: MongoDB + FastAPI, Port: 8001
- motor 3.7.1, httpx[http2], cloudscraper

## Backlog
- [ ] Recurring chores automation
- [ ] Multi-family hub support
- [ ] Enhance AI Meal Suggestions with dietary restrictions
- [ ] More granular dark mode theme controls
- [ ] CSS refactoring (dark mode overrides → Tailwind dark: variants)
