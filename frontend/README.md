# Smart Home Organizer - Frontend Prototype

A clickable, interactive prototype of the Smart Home Organizer web application built with **Next.js 16+** and **Tailwind CSS**.

## 🎯 Current Sprint Features

### ✅ Implemented
- **Authentication**: Login page with demo credentials and session management
- **Dashboard**: Main interface with activities, reminders, and quick stats
- **Activity Logging**: Modal form to log activities (food, mood, play, sleep, other)
- **Today's View**: 
  - Activities list with timestamps and type icons
  - Upcoming reminders with times
  - Quick stats (activity count, reminders, children)
- **Navigation**: Placeholder menu for Calendar, Grocery List, and Settings
- **Responsive Design**: Works seamlessly on mobile, tablet, and desktop

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup & Run

```bash
# Install dependencies (if not already done)
npm install

# Start development server
npm run dev
```

Open **http://localhost:3000** in your browser. You'll be redirected to the login page.

### Demo Credentials
```
Email: demo@example.com
Password: password123
```

## 📁 Project Structure

```
frontend/
├── app/
│   ├── login/
│   │   └── page.tsx          # Login page with form
│   ├── dashboard/
│   │   └── page.tsx          # Main dashboard (protected)
│   ├── lib/
│   │   └── mockData.ts       # Mock data (activities, reminders, groceries)
│   ├── globals.css           # Global styles
│   ├── layout.tsx            # Root layout wrapper
│   └── page.tsx              # Root (redirects to /login)
├── public/                   # Static assets
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

## 🎨 UI/UX Highlights

- **Login Page**: Gradient blue background, clean form layout, demo credentials hint
- **Dashboard**: Two-column responsive layout with sidebar on desktop
- **Activity Cards**: Icon + child name + description + timestamp + edit button
- **Reminder Panel**: Yellow-highlighted reminder cards with time
- **Modal**: Clean form for logging new activities with dropdowns
- **Interactive**: All buttons, forms, and navigation elements are functional

## 💬 Walkthrough

### 1. **Login Page** (`/login`)
- Email and password inputs
- Form validation (basic)
- Demo credentials displayed
- Simulated login (stores user in localStorage)
- Redirects to dashboard on success

### 2. **Dashboard** (`/dashboard`)
- **Header**: Welcome message + current date + Sign Out button
- **Main Content**:
  - "Log New Activity" button
  - Today's Activities section (scrollable list)
- **Sidebar** (right panel):
  - Today's Reminders
  - Quick Stats (cards)
  - Navigation Menu

### 3. **Activity Modal**
- Child selector (Emma, Liam)
- Activity type dropdown with emoji icons
- Description textarea
- Cancel/Save buttons
- Real-time list updates after save

## 🔧 Available Commands

```bash
# Development server (auto-reload)
npm run dev

# Production build
npm run build

# Start production server
npm start

# Lint code
npm run lint
```

## 📝 Mock Data

Located in `app/lib/mockData.ts`:
- **Activities**: 4 sample entries (food, mood, play, food)
- **Reminders**: 3 upcoming reminders (calendar, recurring, grocery)
- **Icon Mapping**: Activity type → emoji icons

Mock data persists during the session in component state.

## 🔐 Session Management

- User info stored in **localStorage** under key `user`
- Cleared on sign out
- Dashboard checks for user on mount; redirects to login if missing

## 🎯 Next Steps

### This Sprint ✅
- [x] Login page
- [x] Dashboard layout
- [x] Activity logging form
- [x] Reminders display
- [x] Mock data integration

### Future Sprints
- [ ] Backend API integration (replace mock data)
- [ ] Real JWT authentication
- [ ] Calendar view
- [ ] Grocery list management
- [ ] User profile/settings
- [ ] Google Calendar sync
- [ ] WhatsApp integration
- [ ] Error boundaries & loading states
- [ ] Unit & E2E tests

## 📱 Notes

- **Thin Frontend Philosophy**: Minimal business logic. API endpoints will handle validation, auth, and data processing.
- **TypeScript**: Full type safety throughout
- **Tailwind CSS**: Utility-first styling for rapid prototyping
- **No State Management Library Yet**: Using React hooks for prototype; will add Context/Redux as complexity grows
- **Responsive**: Mobile-first design; works on all screen sizes

## 🐛 Known Limitations (Prototype Only)

- Authentication is simulated (no real backend)
- Data persists only in-memory during session
- No error handling for network requests
- Edit activity button non-functional (placeholder)
- Calendar, Grocery, Settings pages not yet implemented

## 📚 Tech Stack

- **Framework**: Next.js 16+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: React Hooks (local)
- **Storage**: localStorage (session only)
