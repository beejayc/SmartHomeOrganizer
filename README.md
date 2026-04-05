# Smart Home Organizer

A web and mobile application for families to track and manage daily activities, organize grocery lists, and stay synchronized across devices.

## 🎯 Project Goals

**Smart Home Organizer** helps busy families keep track of their kids' daily lives in one place:

- 📋 **Activity Logging**: Log food intake, moods, playdates, and sleep schedules for each child
- 📅 **Calendar Sync**: Automatic synchronization with Google Calendar for family events
- 🛒 **Grocery Management**: Organize multi-store shopping lists efficiently
- 🔔 **Smart Reminders**: Daily reminders for activities, meals, and appointments
- 💬 **Multi-Channel Input**: Accept information via WhatsApp, email, and web interface
- 🤖 **AI-Powered**: Voice transcription and intelligent message parsing (local LLM)
- 🔐 **Security First**: End-to-end encryption and secure authentication from day one

**Users**: Parents, caregivers, and nannies managing family routines.

---

## 🚀 Getting Started

### For Sprint 1: Frontend Prototype

Start here to see what we're building:

👉 **[PROTOTYPE_GUIDE.md](./PROTOTYPE_GUIDE.md)** — Interactive web prototype walkthrough

```bash
cd frontend
npm run dev
# Open http://localhost:3000
```

**Demo Credentials:**
- Email: `demo@example.com`
- Password: `password123`

---

## 📦 Project Structure

```
smart-home-organizer/
├── README.md                    # This file
├── CLAUDE.md                    # Development guidelines & tech stack
├── PROTOTYPE_GUIDE.md           # Sprint 1 frontend prototype
├── frontend/                    # React/Next.js web app (Sprint 1)
│   ├── app/
│   │   ├── login/              # Login page
│   │   ├── dashboard/          # Main dashboard
│   │   └── lib/mockData.ts     # Mock data for prototype
│   └── README.md
├── backend/                     # FastAPI server (Coming Sprint 2)
├── mobile/                      # React Native app (Future)
├── docker-compose.yml           # Local development setup (Coming)
└── .env.example                 # Environment template (Coming)
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **[CLAUDE.md](./CLAUDE.md)** | Development setup, architecture, tech stack, common commands |
| **[PROTOTYPE_GUIDE.md](./PROTOTYPE_GUIDE.md)** | Interactive frontend prototype guide for Sprint 1 |
| **[frontend/README.md](./frontend/README.md)** | Frontend-specific technical documentation |

---

## 🛠 Tech Stack

### Frontend (Sprint 1 - In Progress)
- **Framework**: Next.js 16+ (React)
- **Styling**: Tailwind CSS
- **Language**: TypeScript
- **State**: React Hooks

### Backend (Sprint 2 - Planning)
- **Framework**: Python FastAPI
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis
- **AI/ML**: OpenAI Whisper (transcription), Local LLM (parsing)

### Deployment
- **Docker Compose** for local development & production
- **Nginx** reverse proxy with SSL/HTTPS
- **PostgreSQL** on Ubuntu host with automated backups

---

## 👥 Team

- **2 Engineers** (Backend + Frontend)
- **1 PM** (Non-technical, focuses on product direction)

### Working Philosophy
- ⚡ **Speed & pragmatism** over perfection
- 🔙 **Backend-first** — Keep frontend thin, logic in APIs
- 🔒 **Security first** — Auth & encryption from day one
- 🎨 **Simple UX** — Intuitive, no hidden workflows

---

## 🎯 Sprint Roadmap

### ✅ Sprint 1: Frontend Prototype (Current)
- [x] Login page with authentication form
- [x] Dashboard with activity logging
- [x] Today's activities and reminders view
- [x] Interactive activity logging modal
- [x] Responsive design (mobile, tablet, desktop)
- [x] Mock data integration

### 🔄 Sprint 2: Backend & API (Planning)
- [ ] FastAPI setup with PostgreSQL
- [ ] User authentication endpoints
- [ ] Activity logging endpoints
- [ ] Calendar sync with Google Calendar API
- [ ] Task queue with Redis
- [ ] Integration with WhatsApp Bridge

### 🚀 Sprint 3+: Advanced Features
- [ ] Voice transcription (Whisper)
- [ ] AI-powered message parsing
- [ ] Grocery list management
- [ ] Mobile app (React Native)
- [ ] Push notifications & reminders
- [ ] Google Keep integration

---

## 🏃 Quick Start

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend - coming soon)
- PostgreSQL 16 (for backend - coming soon)
- Docker & Docker Compose (optional, for full stack)

### Run Frontend Prototype Now

```bash
cd frontend
npm install  # (Already done during setup)
npm run dev
```

Open **http://localhost:3000** and login with demo credentials.

### View Development Guidelines

```bash
# Read setup, commands, architecture, security checklist
cat CLAUDE.md
```

---

## ✨ Key Features (End Goal)

### Activity Logging
- Log food, moods, play, sleep for each child
- Timestamps and activity types with emoji icons
- Edit and delete capabilities

### Smart Reminders
- Daily recurring reminders (meals, activities)
- One-time event reminders
- Email, SMS, and push notifications

### Calendar Integration
- Sync family events from Google Calendar
- Create events from within app
- Parse calendar invites from email

### Grocery Management
- Multi-store shopping lists
- Cross-family collaboration
- Cost tracking (future)

### Multi-Channel Input
- WhatsApp voice and text messages
- Email forwarding and parsing
- Web interface
- Voice transcription with local Whisper

### Security & Privacy
- Password-based authentication
- Data encryption at rest and in transit
- HTTPS-only communication
- No storing secrets in code

---

## 🔐 Security First

Before any feature ships, we verify:
- ✅ Passwords hashed (bcrypt or similar)
- ✅ HTTPS only (no HTTP)
- ✅ SQL injection prevention (ORM)
- ✅ CORS properly configured
- ✅ Secrets in environment variables
- ✅ API rate limiting
- ✅ Input validation on all endpoints
- ✅ Database backups automated

---

## 📖 How to Contribute

1. **Review current work**: Check [PROTOTYPE_GUIDE.md](./PROTOTYPE_GUIDE.md)
2. **Read development guide**: See [CLAUDE.md](./CLAUDE.md) for setup & commands
3. **Run the prototype**: `cd frontend && npm run dev`
4. **Send feedback**: Comment on features, UX, and next priorities

---

## 📞 Questions?

- 🏗️ **Architecture questions?** → See [CLAUDE.md](./CLAUDE.md)
- 🎨 **Frontend prototype questions?** → See [PROTOTYPE_GUIDE.md](./PROTOTYPE_GUIDE.md)
- 💻 **Tech stack details?** → See [CLAUDE.md](./CLAUDE.md)

---

## 📅 Status

- **Project**: Early stage, ready to build
- **Sprint 1**: Frontend prototype ✅ Complete
- **Next**: Backend API development
- **Last Updated**: 2026-04-05
