# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# SmartHome AI — WhatsApp-Integrated Family Management Platform

## Current Status

**Sprint 1 (In Progress):** Frontend prototype—interactive clickable UI with login, dashboard, activity logging, and mock data. **Backend and WhatsApp integration coming in Sprint 2.**

**Last Updated:** 2026-04-06

---

## Quick Start

```bash
cd frontend
npm install  # (if needed)
npm run dev
# Open http://localhost:3000 → Login: demo@example.com / password123
```

---

## Architecture Overview

### Current (Sprint 1)
- **Frontend**: Next.js 16 app (React 19, TypeScript, Tailwind CSS)
- **Mock Data**: All data in `frontend/app/lib/mockData.ts` (activities, reminders, groceries)
- **Session**: localStorage for demo auth; no real backend
- **Structure**: Two pages (login, dashboard) with modular component logic

### Planned (Sprint 2+)
- **Backend**: FastAPI (Python) with PostgreSQL, Redis
- **WhatsApp Integration**: WhatsApp Bridge Go server → FastAPI webhooks
- **AI Pipeline**: Local Whisper (transcription) + Local LLM (parsing/synthesis)
- **Data Flow**: WhatsApp messages → AI processing → database → frontend API calls

---

## Frontend Architecture

### Key Files
- `frontend/app/login/page.tsx` — Login form with session management
- `frontend/app/dashboard/page.tsx` — Main UI: activities, reminders, stats
- `frontend/app/lib/mockData.ts` — All mock activities, reminders, groceries; **edit here to test UI changes**
- `frontend/app/globals.css` — Global Tailwind styles
- `frontend/tailwind.config.ts` — Tailwind configuration
- `frontend/tsconfig.json` — TypeScript settings (strict mode enabled)

### Design Philosophy
- **Thin Frontend**: Minimal business logic. UI is a presentation layer.
- **Mock-Driven Dev**: All state in mockData.ts during prototype phase.
- **Backend-Ready**: Once APIs exist, replace mockData imports with fetch() calls.
- **Responsive**: Mobile-first design; works on all screen sizes.

### Next.js 16 Important Notes
**This version has breaking changes from Next.js 14/15.** Key differences:
- App Router is the default (no Pages Router)
- React 19 has new hooks and features
- Layout system works differently
- Before adding dependencies or changing config, check `node_modules/next/dist/docs/` for current patterns

See `frontend/AGENTS.md` for additional Next.js 16 guidance.

---

## Common Commands

### Frontend Development
```bash
cd frontend

# Development server (auto-reload on file changes)
npm run dev

# Production build
npm run build

# Start production server (requires build first)
npm start

# Lint code
npm run lint

# (No tests yet - will add in Sprint 2)
```

### Git Workflow
```bash
git status                          # Check changes
git add <file>                      # Stage specific files
git commit -m "Clear message"       # Create commit
git log --oneline -10               # View recent commits
```

---

## Project Structure

```
smart-home-organizer/
├── frontend/                        # React/Next.js 16 prototype (Sprint 1)
│   ├── app/
│   │   ├── login/page.tsx          # Login page
│   │   ├── dashboard/page.tsx      # Main dashboard
│   │   ├── lib/mockData.ts         # ⭐ Edit this to test UI changes
│   │   ├── layout.tsx              # Root layout
│   │   ├── globals.css             # Global styles
│   │   └── page.tsx                # Root (redirects to login)
│   ├── public/                     # Static assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── README.md                   # Frontend-specific docs
│   └── AGENTS.md                   # Next.js 16 breaking changes
├── backend/                        # Empty (Sprint 2)
├── docs/
│   └── prd.md                      # Product requirements
├── PROTOTYPE_GUIDE.md              # Interactive prototype walkthrough
├── README.md                       # Main project README
└── CLAUDE.md                       # This file
```

---

## Key Workflows

### Adding a New Activity Type
1. Add icon/emoji mapping to `mockData.ts` → `activityTypeIcons`
2. Add to dropdown options in `dashboard/page.tsx`
3. Save test activity to see it populate the list

### Changing Dashboard Layout
1. Edit `dashboard/page.tsx` (layout is in JSX; Tailwind classes for styling)
2. Run `npm run dev` to see changes live
3. Tailwind intellisense will suggest classes in your editor

### Testing New Reminder
1. Add to `mockData.ts` → `reminders` array
2. Restart dev server or save file to trigger reload
3. Reminders appear in right sidebar under "Today's Reminders"

### Preparing for Backend Integration
Replace mockData calls with API:
```typescript
// Before (current)
const { activities } = mockData;

// After (Sprint 2)
const [activities, setActivities] = useState([]);
useEffect(() => {
  fetch('/api/activities').then(r => r.json()).then(setActivities);
}, []);
```

---

## Styling & Typography

- **Framework**: Tailwind CSS v4 (utility-first)
- **Colors**: Blue gradients (login), white/gray dashboard
- **Icons**: Emoji-based (🍽️ food, 😊 mood, 🎮 play, etc.) in `mockData.ts`
- **Fonts**: System stack (no custom fonts added yet)
- **Responsive**: `sm:`, `md:`, `lg:` breakpoints for mobile-first design

---

## Dependencies

### Current (Sprint 1)
| Package | Version | Purpose |
|---------|---------|---------|
| `next` | 16.2.2 | Framework (App Router, React 19) |
| `react` | 19.2.4 | UI library |
| `tailwindcss` | 4 | Styling |
| `typescript` | 5 | Type safety |
| `eslint` | 9 | Linting |

### Coming (Sprint 2)
- `fastapi` (Python backend)
- `sqlalchemy`, `alembic` (database ORM + migrations)
- `pydantic` (validation)
- `python-jose` (JWT auth)
- `redis` (task queue)

---

## Sprint Roadmap

### ✅ Sprint 1: Frontend Prototype
- [x] Login page with session management
- [x] Dashboard with activities, reminders, stats
- [x] Activity logging modal
- [x] Mock data integration
- [x] Responsive design

### 🔄 Sprint 2: Backend & Integration
- [ ] FastAPI setup with PostgreSQL
- [ ] User auth endpoints (JWT)
- [ ] Activity logging endpoints
- [ ] Google Calendar API integration
- [ ] WhatsApp Bridge webhook handler
- [ ] Replace mock data with API calls
- [ ] Background task queue (Redis)

### 🚀 Sprint 3+: Advanced Features
- [ ] Voice transcription (local Whisper)
- [ ] AI parsing (local LLM)
- [ ] Grocery list management
- [ ] Nutrition synthesis
- [ ] Daily briefing generation
- [ ] Mobile app (React Native)

---

## Team & Working Philosophy

**Team**: 2 engineers (backend + frontend) + 1 PM (product)

**Principles**:
- ⚡ **Speed & pragmatism** over perfection
- 🔙 **Backend-first logic** — Keep frontend thin
- 🔒 **Security by default** — Auth & encryption from day one
- 🎨 **Simple UX** — Intuitive, no hidden workflows

---

## How to Contribute

### For Frontend Work
1. Run `npm run dev` and make changes to `app/` files
2. Test in browser at http://localhost:3000
3. Lint code before commit: `npm run lint`
4. Commit with clear message (reference sprint/feature)

### For Backend Work (Sprint 2)
1. Follow the backend template in `/backend` (will be scaffolded)
2. Create FastAPI endpoints matching the mockData structure
3. Document APIs in docstrings
4. Write unit tests in `tests/` directory
5. Integration tests against real PostgreSQL test DB

### For Design/UX Feedback
- Test the prototype: `npm run dev`
- Check `PROTOTYPE_GUIDE.md` for interactive walkthrough
- File feedback on component styling, layout, or missing pages

---

## Security Notes

**Current (Prototype Only)**:
- Auth is simulated (no real passwords hashed)
- Session stored in localStorage (not secure)
- No HTTPS; runs on localhost

**Before Production (Sprint 2)**:
- [ ] Passwords hashed (bcrypt)
- [ ] HTTPS only (Nginx reverse proxy)
- [ ] JWT tokens in secure HttpOnly cookies
- [ ] CORS properly configured (frontend origin only)
- [ ] Secrets in environment variables (never in code)
- [ ] API rate limiting (prevent brute force)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] Database backups automated

---

## Debugging

### Dev Server Not Starting
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

### Linter Errors
```bash
cd frontend
npm run lint  # Shows errors
# Fix manually or use editor's "Quick Fix" if available
```

### Mock Data Not Updating
- Ensure `mockData.ts` is imported correctly
- Restart dev server if file changes don't appear
- Check browser console (F12) for errors

### TypeScript Errors
- Check `tsconfig.json` (strict mode is on)
- Hover over error in editor to see type hint
- Run `tsc --noEmit` to check all files

---

## Deployment

**Local Development**: `npm run dev` on your machine

**Production Build**: 
```bash
npm run build
npm start
```

**Docker** (coming in Sprint 2 with backend):
```bash
docker-compose up -d
```

---

## References

- **Project Overview**: See `README.md`
- **Sprint 1 Prototype Details**: See `PROTOTYPE_GUIDE.md`
- **Frontend Tech Details**: See `frontend/README.md`
- **Product Requirements**: See `docs/prd.md`
- **Next.js 16 Notes**: See `frontend/AGENTS.md`

---

## Questions?

- 🏗️ **Architecture?** → Check this file
- 📱 **Frontend walkthrough?** → See `PROTOTYPE_GUIDE.md`
- 💻 **Frontend tech details?** → See `frontend/README.md`
- 📋 **Product goals?** → See `docs/prd.md`
- 🚀 **Sprint planning?** → See README.md "Sprint Roadmap"