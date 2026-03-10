# Family Hub - Product Requirements Document

## Overview
Family Hub is a fully self-contained, self-hosted family organization app with role-based access control. It runs as a single Docker container with MongoDB embedded.

## Latest Update (March 2026)
- **Backend Refactored**: Monolithic 1652-line server.py split into 16 modular FastAPI router files with separate database.py, auth.py, and models/schemas.py
- **Admin Portal Fixed**: Replaced broken HTTP Basic Auth with session-based form login accessible via web browsers
- **Barcode Scanner Enhanced**: Camera-based scanning auto-closes on detection, product lookup uses Open Food Facts + UPC Item DB fallback, shows product image and Google search link for unknown barcodes
- **Full Regression Test**: 144/144 backend tests passing, all frontend flows verified

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
- [x] Pantry with barcode scanner (camera + manual entry + web search)
- [x] Meal Suggestions based on pantry (simple matching + AI-powered)

### Gamification
- [x] Chores with difficulty levels (Easy/Medium/Hard)
- [x] Points awarded on chore completion
- [x] Rewards system with point redemption
- [x] Family leaderboard

### Admin Features
- [x] Settings page with tabs (Family, Modules, Integrations, Mobile, Backup, Server)
- [x] Module enable/disable per role
- [x] Family name editing
- [x] PIN regeneration
- [x] Google Calendar sync (optional)
- [x] QR Code generation for mobile device setup
- [x] Push notifications toggle
- [x] Data export (Full JSON backup + CSV by module)
- [x] Admin Portal with session-based login (port 8050)

### AI Features
- [x] AI-Powered Meal Suggestions using GPT-4o-mini
- [x] Emergent LLM key (platform) + OpenAI fallback (self-hosted)

### Removed Features
- [x] Photo Gallery (removed per user request)
- [x] Messaging (removed per user request)

## Technical Stack
- **Frontend:** React 18, Tailwind CSS, Shadcn UI, Recharts, @zxing/library
- **Backend:** FastAPI (modular routers), Python 3.11
- **Database:** MongoDB 7.0 (embedded in Docker)
- **AI Integration:** Emergent LLM (GPT-4o-mini) + OpenAI fallback
- **Admin Portal:** FastAPI with session-based auth (port 8050)
- **Process Manager:** Supervisor
- **Container:** Single self-contained Docker image

## Code Architecture (Refactored)
```
/app/backend/
├── server.py           # Slim app init (~80 lines)
├── database.py         # MongoDB connection
├── auth.py             # JWT helpers, roles, permissions, email
├── admin_portal.py     # Admin portal (port 8050)
├── models/
│   └── schemas.py      # All Pydantic models
├── routers/
│   ├── auth.py         # Registration, login, PIN auth
│   ├── family.py       # Family CRUD, members, invites
│   ├── calendar.py     # Calendar + Google Calendar sync
│   ├── shopping.py     # Shopping list CRUD
│   ├── tasks.py        # Tasks CRUD
│   ├── chores.py       # Chores + rewards + leaderboard
│   ├── notes.py        # Notes CRUD
│   ├── budget.py       # Budget CRUD + summary
│   ├── meals.py        # Meal plans CRUD
│   ├── recipes.py      # Recipes CRUD
│   ├── grocery.py      # Grocery list CRUD
│   ├── contacts.py     # Contacts CRUD
│   ├── pantry.py       # Pantry CRUD + barcode lookup
│   ├── settings.py     # Family + server settings
│   ├── suggestions.py  # AI meal suggestions
│   └── utilities.py    # QR code, export, push notifications
└── tests/
    ├── test_family_hub.py
    ├── test_new_features.py
    ├── test_comprehensive_crud.py
    └── test_permissions.py
```

## Future Enhancements (Backlog)
- [ ] Push notification backend logic (Web Push Protocol)
- [ ] AI Meal Suggestions based on actual pantry inventory
- [ ] Data import/restore feature
- [ ] Real-time WebSocket updates
- [ ] Service worker for offline support
- [ ] Recurring chores automation
- [ ] Dark mode
- [ ] Recipe import from URL
