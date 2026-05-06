# CIAP Frontend (Creator Influence & Analytics Platform)

Welcome to the high-fidelity frontend repository for **CIAP**, a production-grade analytics and discovery engine built to empower the creator economy. This application delivers a tactile, "Modern Studio" experience with a focus on real-time data visualization, seamless authentication, and creator-centric workflows.

## 📌 User Review Required
> [!IMPORTANT]
> Ensure `NEXT_PUBLIC_API_URL` is correctly pointed to your running NestJS backend (typically `http://localhost:3000`) in your `.env.local` file.

## Table Of Contents
- [Important Notes](#important-notes)
- [Built With](#built-with)
- [Design Philosophy](#design-philosophy)
- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Testing](#testing)

---

## Important Notes
*   **Next.js 16 (App Router)**: This project utilizes the latest Next.js 16 features, including Server Components and advanced route groups.
*   **Zustand for State**: Global auth state and user sessions are managed via Zustand with persistent hydration support.
*   **TanStack Query**: All API interactions are handled via `@tanstack/react-query` v5 for robust caching and optimistic updates.
*   **Hydration Caution**: Due to the heavy use of client-side metrics and animations, ensure proper use of the `ProtectedRoute` and `AuthGuard` components.

## Built With
| Technology | Version | Purpose |
| :--- | :--- | :--- |
| **Next.js** | 16.2.x | Framework (App Router) |
| **React** | 19.x | UI Library |
| **Tailwind CSS** | 4.x | Styling (v4 engine) |
| **TanStack Query**| 5.x | Data Fetching & Caching |
| **Framer Motion** | 12.x | Layout Animations |
| **Zustand** | 5.x | State Management |
| **Recharts** | 3.x | Data Visualization |
| **Phosphor Icons**| 2.x | Professional Iconography |

## Design Philosophy: "Modern Studio"
CIAP follows a strict **Retro-Modern** design language:
*   **Tactile UI**: Bold 2px black borders and hard pop-shadows for a physical, "magazine-style" feel.
*   **Vibrant Palettes**: Curated pastel backgrounds (Blue, Pink, Green, Purple) that distinguish different data sectors.
*   **Responsive Precision**: Seamless navigation across mobile and desktop with a focus on high-density data visualization.
*   **Modern Typography**: Utilizes `Bricolage Grotesque` and `Outfit` for an editorial, high-impact reading experience.

## Features
### 🔐 Authentication & Security
- **OAuth Integration**: Seamless onboarding with Google/YouTube.
- **Session Management**: Secure JWT-based auth with automatic token refreshing via backend synchronization.
- **Protected Routes**: Granular access control for Creators, SMEs, and Admins.

### 📊 Creator Studio Hub
- **Real-Time Analytics**: Direct integration with YouTube metrics (views, subscribers, engagement).
- **Influence DNA**: Visual representation of market impact and growth velocity.
- **Responsive Dashboard**: High-fidelity charts using Recharts for performance tracking.

### 🔍 Market Discovery (SME)
- **Creator Search**: Powerful discovery engine for brands to find verified talent.
- **Metric Cards**: Tactile, data-dense cards showing "Influence Scores" and audience insights.

## Project Structure
```text
src/
├── app/                  # App Router logic: (auth), (protected), layout
├── components/           # UI Components
│   ├── layout/           # Sidebar, Header, MobileNav, AuthGuard
│   └── ui/               # Atomic components (Buttons, Skeleton, Cards)
├── lib/                  # Core logic
│   ├── api/              # Axios instance and TanStack Query hooks
│   ├── auth/             # Zustand stores for authentication
│   └── utils/            # Styling utilities (cn, clsx)
├── public/               # Static assets and brand illustrations
└── styles/               # Global CSS and Tailwind 4 configuration
```

## Quick Start
1. **Clone & Install**:
   ```bash
   pnpm install
   ```
2. **Environment Setup**:
   ```bash
   cp .env.example .env.local
   ```
3. **Run Development Server**:
   ```bash
   pnpm dev
   ```
   *Application will be available at `http://localhost:4000`*

## Environment Configuration
Create a `.env.local` file with the following:
```env
NEXT_PUBLIC_API_URL=http://localhost:3000
NEXT_PUBLIC_APP_URL=http://localhost:4000
# Add OAuth keys if needed for specific client-side callbacks
```

## Testing
- **Linting**: `pnpm run lint`
- **Typecheck**: `pnpm run typecheck`
- **Production Build**: `pnpm run build`

---
Built with passion by **Team B** for the CIAP Platform. 🚀
