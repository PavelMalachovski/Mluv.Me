# 🎨 WebUI Redesign - Chatty Style

## 🎯 What's New

The Mluv.Me WebUI has been completely redesigned to match the style of the Chatty bot, featuring a modern, Telegram-inspired interface.

## 🚀 Quick Start

```bash
cd frontend
npm install
npm run dev
```

Visit: `http://localhost:3000`

## 📱 Main Features

### 1. **Chat Interface** (`/dashboard`)
- Telegram-like chat bubbles
- Voice recording (hold to record)
- Real-time message history
- Audio playback controls
- Streak & stars display

### 2. **Profile** (`/dashboard/profile`)
- User stats dashboard
- Achievement badges
- Learning progress
- Czech level indicator

### 3. **Saved Words** (`/dashboard/saved`)
- Searchable vocabulary list
- Pronunciation feature
- Review tracking
- Export to Anki (coming soon)

### 4. **Settings** (`/dashboard/settings`)
Three tabs with full customization:
- **Learning**: Level, corrections, conversation style
- **Voice**: Speed and notifications
- **Account**: User info and logout

## 🎨 Design Highlights

- **Mobile-first** responsive design
- **Bottom navigation** on mobile
- **Sidebar navigation** on desktop
- **Smooth animations** and transitions
- **Clean, modern UI** inspired by Telegram

## 🏗️ New Components

```
components/ui/
├── navigation.tsx    # Main navigation component
└── tabs.tsx          # Settings tabs

app/dashboard/
├── layout.tsx        # Layout with navigation
├── page.tsx          # Chat interface
├── profile/page.tsx  # Profile page
├── saved/page.tsx    # Saved words
└── settings/page.tsx # Settings
```

## 🎨 Color Scheme

- **Primary Blue**: `#3B82F6` - Actions, user messages
- **White**: `#FFFFFF` - Background, cards
- **Gray**: `#F9FAFB` - Page background
- **Accent colors**: Orange (streak), Yellow (stars), Green (success)

## 📦 Tech Stack

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Radix UI** - Accessible components
- **React Query** - Server state
- **Zustand** - Client state
- **Lucide React** - Icons

## 🔧 Key Integrations

All features connect to existing backend API:
- User stats and profile
- Message history
- Saved words CRUD
- Settings management
- Authentication

## 📱 Responsive Breakpoints

```css
sm: 640px   /* Small devices */
md: 768px   /* Medium devices - sidebar appears */
lg: 1024px  /* Large devices */
xl: 1280px  /* Extra large */
```

## 🎭 Animations

Custom animations in `globals.css`:
- Fade in for page transitions
- Ripple effect for buttons
- Smooth hover states
- Custom scrollbar

## 🌐 Navigation Flow

```
/dashboard (Chat)
    ├── /dashboard/profile (Stats & achievements)
    ├── /dashboard/saved (Vocabulary)
    └── /dashboard/settings (Preferences)
```

## 📝 Usage

### Voice Recording
Press and hold the microphone button to record. Release to send.

### Settings Update
Changes are saved automatically when you select an option.

### Word Search
Type in the search bar to filter your saved words instantly.

## 🎯 Design Principles

1. **Simplicity** - Clean, uncluttered interface
2. **Familiarity** - Telegram-like patterns
3. **Accessibility** - WCAG 2.1 compliant
4. **Performance** - Fast, responsive interactions
5. **Mobile-first** - Optimized for touch

## 🔮 Future Enhancements

- [ ] Dark mode support
- [ ] Audio waveform visualization
- [ ] Offline mode with PWA
- [ ] Push notifications
- [ ] Social sharing
- [ ] Anki export
- [ ] Advanced analytics

## 📚 Documentation

See `/docs/WEBUI_REDESIGN.md` for detailed documentation.

## 🐛 Known Issues

None currently - this is a fresh redesign!

## 🤝 Contributing

Follow the existing code style and component patterns.

## 📄 License

Same as main Mluv.Me project.

---

**Na zdraví! 🍺🇨🇿**
