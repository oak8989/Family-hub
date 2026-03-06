# Family Hub - Product Requirements Document

## Overview
Family Hub is a fully self-contained, self-hosted family organization app with role-based access control. It runs as a single Docker container with MongoDB embedded.

## Latest Update (December 2025)
- **E2E Testing Completed**: All 90 backend tests passing (100% success rate)
- **Bug Fixes Applied**: Fixed duplicate `/api/api/` prefix in ChoresPage.jsx and SettingsPage.jsx
- **Owner Role Protection**: Verified fixed - owner cannot change their own role
- **All Modules Verified**: Calendar, Shopping, Tasks, Chores, Rewards, Notes, Budget, Meals, Recipes, Grocery, Contacts, Pantry, Suggestions

## Original Requirements
- Shared Calendar, Shopping List, Task List, Notes, Budget Tracker
- Meal Planner, Recipe Box, Grocery List, Contact Book
- Pantry Tracker with barcode scanner, Meal Suggestions
- Gamified Chore Chart with rewards
- User roles: Owner, Parent, Family Member, Child
- Auto-generated PINs for quick access
- Self-hostable with Docker
- Mobile-friendly (PWA)

## Implemented Features

### Authentication & User Management
- [x] Email/password registration and login
- [x] Family PIN login (6 digits, auto-generated)
- [x] Personal PIN login (4 digits, auto-generated)
- [x] Role-based permissions (Owner > Parent > Member > Child)
- [x] Add family members without email (just name + role)
- [x] Invite by email (requires SMTP configuration)

### Core Modules
- [x] Calendar with event management
- [x] Shopping List with categories
- [x] Tasks with assignment to family members
- [x] Notes with color coding
- [x] Budget with income/expense tracking and Recharts visualization
- [x] Meal Planner
- [x] Recipe Box
- [x] Grocery List
- [x] Contacts
- [x] Pantry with barcode scanner
- [x] Meal Suggestions based on pantry

### Gamification
- [x] Chores with difficulty levels (Easy/Medium/Hard)
- [x] Points awarded on chore completion
- [x] Rewards system with point redemption
- [x] Family leaderboard

### Admin Features
- [x] Settings page with tabs (Family, Modules, Integrations, Server)
- [x] Module enable/disable per role
- [x] Family name editing
- [x] PIN regeneration
- [x] Google Calendar sync (optional)

### Removed Features
- [x] Photo Gallery (removed per user request)
- [x] Messaging (removed per user request)

## Technical Stack
- **Frontend:** React 18, Tailwind CSS, Shadcn UI, Recharts
- **Backend:** FastAPI, Python 3.11
- **Database:** MongoDB 7.0 (embedded in Docker)
- **Process Manager:** Supervisor
- **Container:** Single self-contained Docker image

## Permission Matrix

| Action | Owner | Parent | Member | Child |
|--------|:-----:|:------:|:------:|:-----:|
| View all modules | ✅ | ✅ | ✅ | ✅* |
| Add/edit content | ✅ | ✅ | ✅ | ❌ |
| Add family members | ✅ | ✅ | ❌ | ❌ |
| Change settings | ✅ | ✅ | ❌ | ❌ |
| Server configuration | ✅ | ❌ | ❌ | ❌ |

*Module visibility configurable by admins

## Deployment
- Single Docker command: `docker run -p 8001:8001 ghcr.io/oak8989/family-hub`
- Docker Compose available for production
- Health check endpoint: `/api/health`
- Data persisted in `/data/db` volume

## Future Enhancements (Backlog)
- [ ] Real-time WebSocket updates
- [ ] Push notifications
- [ ] Data export/backup UI
- [ ] Recurring chores automation
- [ ] Dark mode
- [ ] Recipe import from URL
