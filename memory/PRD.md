# Family Hub - Product Requirements Document

## Original Problem Statement
Build a full-stack, self-hostable application for families called "Family Hub" with shared calendar, shopping list, task list, shared notes, budget tracker, meal planner, recipe box, grocery list, contact book, pantry tracker, chore system with gamification, and more.

## Tech Stack
- **Frontend:** React, Tailwind CSS, Shadcn UI, Axios, Recharts, PWA (Service Workers)
- **Backend:** FastAPI (modular), MongoDB (embedded), WebSockets, pywebpush, httpx
- **Auth:** JWT (72h expiration, rate-limited endpoints)
- **DevOps:** Docker, Supervisor

## Core Features (All Implemented)
- Shared Calendar (with Google Calendar sync)
- Shopping List, Task List (assignable), Shared Notes
- Budget Tracker (with visualization charts)
- Meal Planner (with AI suggestions), Recipe Box (with URL import)
- Quick Grocery List, Contact Book
- Pantry Tracker with barcode scanner + Bulk Scan mode
- Chore System with gamification & rewards + claim history
- Settings with user management (Owner, Parent, Member, Child roles)
- Dark Mode, PWA offline support, push notifications
- Data export/import, QR code setup
- Email invites with pending invite management
- Password change, owner reset, and **forgot password with email reset link**
- **Server URL configuration** in admin panel
- **Security hardening**: JWT expiration, rate limiting, dynamic config, no stale secrets

## Completed Features (Latest Session - March 2026)
### Batch 1: UI/UX Enhancements
- Quantity Placeholder "0": Shopping, Grocery, Pantry quantity inputs show placeholder "0"
- Bulk Pantry Scanning: Full-screen bulk scanning mode with continuous barcode scanning and batch save

### Batch 2: Security & Cleanup
- **Server URL Setting**: New field in Settings > Server to set public-facing URL (used in emails)
- **Forgot Password**: Full flow — link on login page, email with reset link (itsdangerous token), /reset-password page
- **Removed Self-Hosted Server**: Cleaned login page — removed custom server config, setCustomServer, getCustomServer, testServerConnection
- **Bloat Removal**: Removed stale module-level vars (SMTP_*, GOOGLE_*) from auth.py, removed /app/backend_test.py, /app/test_result.md, /app/tests/, made suggestions.py use dynamic env lookups
- **Security Hardening**: JWT 72h expiration, rate limiting (10/5min on login/register/forgot-password), random JWT_SECRET fallback, itsdangerous for reset tokens, email enumeration prevention

## Key API Endpoints
- `POST /api/auth/forgot-password` - Request password reset email (NEW)
- `POST /api/auth/reset-password-token` - Reset password with token (NEW)
- `POST /api/admin/config/server` - Save server config including server_url (UPDATED)
- `POST /api/pantry/bulk-add` - Bulk add pantry items
- Full CRUD for: shopping, grocery, pantry, tasks, notes, budget, meals, recipes, contacts, calendar, chores, rewards
- `/api/admin/*` - Server management (Owner only)

## Database Collections
- users, families, family_settings
- shopping_items, grocery_items, pantry_items
- tasks, notes, calendar_events
- budget_entries, meal_plans, recipes
- contacts, chores, rewards, reward_claims
- push_subscriptions

## Integrations
- Emergent LLM Key / emergentintegrations (AI Meal Suggestions)
- OpenAI GPT (fallback for self-hosted)
- Emergent-managed Google Auth (Calendar sync)
- pywebpush (push notifications)

## Critical Notes
- motor==3.4.0 and pymongo<4.7 pinned in requirements.txt (Docker crash prevention)
- Backend uses dynamic config pattern for SMTP/Google/OpenAI settings
- All backend routes prefixed with /api
- JWT tokens expire after 72 hours
- Rate limiting: 10 attempts per 5 minutes on auth endpoints

## Upcoming / Future Tasks
- P2: Enhanced AI Meal Suggestions (dietary restrictions, recent meals)
- P2: More granular dark mode theme controls
- P3: Refactor App.css dark mode overrides to Tailwind dark: variants
