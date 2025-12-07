# Mluv.Me Web Frontend

Next.js 14 web application for learning Czech with AI-powered conversations.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Run development server
npm run dev
```

## 📦 Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **UI Components**: Radix UI
- **Charts**: Recharts
- **Icons**: Lucide React

## 🔧 Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_TELEGRAM_BOT_ID=your_bot_id_here
```

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── (auth)/            # Auth pages (login)
│   ├── dashboard/         # Dashboard pages
│   │   ├── page.tsx      # Main dashboard
│   │   └── practice/     # Practice interface
│   ├── layout.tsx        # Root layout
│   └── providers.tsx     # React Query provider
├── components/
│   ├── ui/               # Reusable UI components
│   └── features/         # Feature-specific components
├── lib/
│   ├── api-client.ts     # API client
│   ├── auth-store.ts     # Auth state management
│   ├── types.ts          # TypeScript types
│   └── utils.ts          # Utility functions
└── public/               # Static assets
```

## 🎨 Pages

### Authentication
- `/login` - Telegram Login Widget authentication

### Dashboard
- `/dashboard` - Main dashboard with stats and progress
- `/dashboard/practice` - Practice Czech with Honzík

## 🔐 Authentication Flow

1. User clicks "Login with Telegram"
2. Telegram Login Widget opens
3. User authorizes
4. Backend validates and creates session
5. User redirected to dashboard

## 🚢 Deployment (Vercel)

### Automatic Deployment

1. Connect GitHub repository to Vercel
2. Configure environment variables in Vercel dashboard
3. Deploy automatically on push

### Manual Deployment

```bash
npm install -g vercel
vercel login
vercel --prod
```

### Environment Variables in Vercel

- `NEXT_PUBLIC_API_URL` - Backend API URL (e.g., https://api.mluv.me)
- `NEXT_PUBLIC_TELEGRAM_BOT_ID` - Telegram Bot ID

## 🧪 Scripts

```bash
# Development
npm run dev

# Build
npm run build

# Production
npm start

# Lint
npm run lint
```

## 📚 Key Features

- ✅ Telegram authentication
- ✅ Real-time stats and progress tracking
- ✅ Text-based practice with Honzík
- ✅ Instant feedback and corrections
- ✅ Responsive design
- ✅ Dark mode ready

## 🔗 API Integration

All API calls go through `lib/api-client.ts`:

```typescript
import { apiClient } from '@/lib/api-client'

// Example usage
const data = await apiClient.get('/api/v1/stats/me')
```

## 🎯 Next Steps

- [ ] Add audio recording for practice
- [ ] Implement vocabulary page
- [ ] Add analytics page
- [ ] PWA support
- [ ] Offline mode

## 📄 License

Part of Mluv.Me project
