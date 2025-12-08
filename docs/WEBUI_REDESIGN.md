# WebUI Redesign - Chatty Style

## 📋 Overview

The WebUI has been completely redesigned in the style of the Chatty bot, featuring a clean, modern Telegram-like interface with four main sections: Chat, Profile, Saved, and Settings.

## 🎨 Design Philosophy

The new design follows the Chatty bot's approach:
- **Clean and minimal** - Focus on content, not clutter
- **Mobile-first** - Responsive design that works on all devices
- **Telegram-inspired** - Familiar interface for Telegram users
- **Modern aesthetics** - Smooth animations and transitions

## 📱 Main Sections

### 1. Chat (Dashboard)
**Route:** `/dashboard`

**Features:**
- Real-time chat interface with Honzík
- Voice message recording (hold to record)
- Text input option
- Message history with audio playback
- Score indicators (✅ correctness percentage)
- Streak and stars display in header
- Quick action buttons (Menu, Help, Commands)

**UI Elements:**
- Header with bot avatar and stats
- Scrollable message area
- Message bubbles (blue for user, white for assistant)
- Audio player controls
- Input bar with mic button

### 2. Profile
**Route:** `/dashboard/profile`

**Features:**
- User avatar and info card
- Key stats dashboard:
  - Current streak 🔥
  - Total stars ⭐
  - Messages today
- Detailed statistics:
  - Total messages
  - Average correctness
  - Words learned
  - Longest streak
- Czech level indicator with progress bar
- Achievements section with badges:
  - Week Warrior (7 day streak)
  - Chatty (50+ messages)
  - Star Collector (100+ stars)
  - Word Master (25+ words)

### 3. Saved
**Route:** `/dashboard/saved`

**Features:**
- Search bar for filtering words
- Word count display
- Export to Anki button
- Word cards showing:
  - Czech word with phonetics
  - Translation
  - Context sentence
  - Review count
  - Date added
- Action buttons:
  - 🔊 Pronounce (text-to-speech)
  - ✅ Mark as reviewed
  - 🗑️ Delete

**Empty State:**
- Friendly message
- CTA to start practicing

### 4. Settings
**Route:** `/dashboard/settings`

**Tabs:**

#### Learning Tab
1. **Czech Level**
   - Začátečník (Beginner)
   - Středně pokročilý (Intermediate)
   - Pokročilý (Advanced)
   - Rodilý (Native)

2. **Correction Level**
   - Minimální - Only critical mistakes
   - Vyvážený - Important mistakes with explanations
   - Detailní - All mistakes corrected

3. **Conversation Style**
   - Přátelský 😊 - Casual and supportive
   - Učitel 👨‍🏫 - More corrections and tips
   - Kamarád 🍺 - Like chatting with a friend

#### Voice Tab
1. **Voice Speed**
   - Velmi pomalu (Very Slow)
   - Pomalu (Slow)
   - Normálně (Normal)
   - Rodilý (Native Speed)

2. **Notifications**
   - Toggle for daily practice reminders

#### Account Tab
- User information display (read-only)
- Logout button

## 🎯 Navigation

### Desktop (md and up)
- **Vertical sidebar** on the left (80px width)
- Icon + label for each section
- Fixed position
- Active state highlighting

### Mobile
- **Bottom navigation bar**
- Icon + label for each section
- Fixed at bottom
- Active state highlighting

**Navigation Items:**
1. 💬 Chat
2. 👤 Profile
3. 🔖 Saved
4. ⚙️ Settings

## 🎨 Color Scheme

### Primary Colors
- **Blue**: #3B82F6 (Primary actions, user messages)
- **White**: #FFFFFF (Background, assistant messages)
- **Gray**: #F9FAFB (Page background)

### Accent Colors
- **Orange**: #F97316 (Streak, fire emoji)
- **Yellow**: #EAB308 (Stars, achievements)
- **Green**: #22C55E (Success, correctness)
- **Purple**: #A855F7 (Words learned)
- **Red**: #EF4444 (Danger actions)

### Text Colors
- **Primary**: #111827
- **Secondary**: #6B7280
- **Muted**: #9CA3AF

## 🧩 Components Created

### New Components
1. **`Navigation`** (`components/ui/navigation.tsx`)
   - Responsive navigation component
   - Desktop sidebar / Mobile bottom bar
   - Active state management

2. **`Tabs`** (`components/ui/tabs.tsx`)
   - Radix UI tabs implementation
   - Styled for Settings page

### Updated Components
- **Dashboard Layout** - Added navigation
- **Dashboard Page** - Redesigned in Chatty style
- All pages follow consistent design patterns

## 📦 Dependencies

Already in `package.json`:
```json
{
  "@radix-ui/react-tabs": "^1.0.4",
  "@tanstack/react-query": "^5.28.0",
  "lucide-react": "^0.365.0",
  "tailwindcss": "^3.4.0",
  "next": "^14.2.15"
}
```

## 🚀 Key Features

### Chat Interface
- **Hold-to-record voice messages** (like Telegram)
- Real-time message display
- Audio playback controls
- Correctness score badges
- Streak and stars in header

### Responsive Design
- Mobile-first approach
- Adapts to all screen sizes
- Touch-friendly controls
- Smooth transitions

### User Experience
- **Fast navigation** between sections
- **Instant feedback** on actions
- **Loading states** for async operations
- **Empty states** with helpful CTAs
- **Error handling** with user-friendly messages

## 🎭 Animations

### Custom Animations
```css
.animate-fade-in {
  animation: fadeIn 0.3s ease-in-out;
}
```

### Transitions
- Smooth hover effects
- Button press animations
- Page transitions
- Modal animations

## 📱 Mobile Optimizations

1. **Bottom Navigation**
   - Easy thumb access
   - Clear active states
   - Icon + label for clarity

2. **Touch Targets**
   - Minimum 44px touch areas
   - Adequate spacing between elements

3. **Viewport Management**
   - `pb-20` padding to account for bottom nav
   - Full-height chat interface

## 🔧 Technical Implementation

### State Management
- **Zustand** for auth state
- **React Query** for server state
- Local state for UI interactions

### API Integration
All pages connect to existing backend endpoints:
- `/api/v1/stats/me` - User statistics
- `/api/v1/users/me/settings` - User settings
- `/api/v1/words` - Saved words
- `/api/v1/web/lessons/history` - Message history

### Type Safety
Full TypeScript implementation with proper types for:
- User data
- Settings
- Statistics
- Messages
- Saved words

## 📝 Usage Examples

### Voice Recording
```typescript
const startRecording = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  const mediaRecorder = new MediaRecorder(stream)
  // ... recording logic
}
```

### Settings Update
```typescript
const updateSettingsMutation = useMutation({
  mutationFn: (newSettings) =>
    apiClient.patch("/api/v1/users/me/settings", newSettings),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["user-settings"] })
  },
})
```

## 🎯 Next Steps

### Potential Enhancements
1. **Real-time audio playback** for Honzík's responses
2. **Voice message waveform visualization**
3. **Offline support** with service workers
4. **Push notifications** for daily reminders
5. **Dark mode** support
6. **Animations** for streak achievements
7. **Social sharing** of achievements
8. **Anki export** functionality for saved words

### Performance Optimizations
1. Virtual scrolling for long message lists
2. Image optimization with Next.js Image
3. Code splitting for faster initial load
4. Lazy loading of components
5. Caching strategies for static content

## 📚 File Structure

```
frontend/
├── app/
│   ├── dashboard/
│   │   ├── layout.tsx          # Main layout with navigation
│   │   ├── page.tsx            # Chat interface
│   │   ├── profile/
│   │   │   └── page.tsx        # Profile page
│   │   ├── saved/
│   │   │   └── page.tsx        # Saved words
│   │   └── settings/
│   │       └── page.tsx        # Settings
│   ├── globals.css             # Enhanced with Chatty styles
│   └── layout.tsx
├── components/
│   ├── ui/
│   │   ├── navigation.tsx      # NEW: Navigation component
│   │   ├── tabs.tsx            # NEW: Tabs component
│   │   ├── button.tsx
│   │   └── card.tsx
│   └── features/
│       ├── ProgressChart.tsx
│       ├── RecentLessons.tsx
│       └── StatsCard.tsx
└── lib/
    ├── api-client.ts
    ├── auth-store.ts
    └── types.ts
```

## 🎨 Design Tokens

### Spacing
- Base: 4px (0.25rem)
- Icons: 16-24px
- Touch targets: 44px minimum
- Container max-width: 672px (max-w-2xl)

### Border Radius
- Small: 8px (rounded-lg)
- Medium: 12px (rounded-xl)
- Large: 16px (rounded-2xl)
- Full: 9999px (rounded-full)

### Shadows
- Small: `shadow-sm`
- Medium: `shadow-md`
- Large: `shadow-lg`

## ✅ Browser Support

- Chrome/Edge 90+
- Safari 14+
- Firefox 88+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📄 License

This redesign follows the same license as the main Mluv.Me project.

---

**Redesigned with ❤️ in the style of Chatty bot**
