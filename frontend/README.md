# CIAP Frontend - Team B

A high-performance, production-oriented React interface for the **Creative Influence and Analytics Platform (CIAP)**. Built with Next.js 16, Tailwind CSS 4, and designed for strict scalability, analytics visualization, and PWA reliability.

## Table Of Contents
- [Important Notes](#important-notes)
- [Must Read: Setup And Usage](#must-read-setup-and-usage)
- [Current Scope](#current-scope)
- [Prerequisites](#prerequisites)
- [Built With](#built-with)
- [Features](#features)
- [Quick Start](#quick-start)
- [Environment Setup](#environment-setup)
- [Project Structure](#project-structure)
- [Scripts](#scripts)
- [Contributing](#contributing)

## Important Notes
- Uses **Tailwind CSS 4** for high-performance atomic styling.
- Configured as a **PWA** (Progressive Web App) for offline capability and mobile-first experience.
- Implements strict **TypeScript 5** boundaries across all modules.
- Analytics are rendered via **Recharts** with optimized re-render cycles.

## Must Read: Setup And Usage
1) **Configure Environment**: Set `NEXT_PUBLIC_API_URL` to point to the CIAP Backend.
2) **Package Management**: Use `npm` or `pnpm` consistently.
3) **Commit Messages**: Follow conventional commits (e.g., `feat(ui): add dashboard charts`).

## Current Scope
The current frontend implementation focuses on:
- **Dashboard API Integration**: Consuming CIAP backend endpoints for analytics.
- **Interactive Visualization**: Real-time data plotting for creator performance.
- **Auth Flow UI**: Implementation of Google OAuth and JWT-based session management.
- **PWA Lifecycle**: Offline caching and manifest configuration.

## Prerequisites
- Node.js >= 20.x
- npm / pnpm / yarn
- Active [CIAP Backend](https://github.com/30Cycleltd/ciap-mvp-b) instance for data fetching.

## Built With
| Technology | Version | Purpose |
| :--- | :--- | :--- |
| **Next.js** | 16.x | App Router & Core Framework |
| **Tailwind CSS** | 4.x | Styling & Design System |
| **React** | 19.x | Component Library |
| **Framer Motion** | 12.x | High-performance Micro-animations |
| **Recharts** | 3.x | Analytics & Data Visualization |
| **Lucide React** | 1.x | Icon System |

## Features
- **Modern Dashboard**: Responsive layouts with tenant-aware display logic.
- **Dynamic Charts**: Interactive analytics panels for discovery and performance tracking.
- **Smooth Interaction**: Transitions powered by Framer Motion for a premium feel.
- **PWA Ready**: Mobile-centric manifest and service worker configuration.

## Quick Start
```bash
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the application.

## Project Structure
```text
src/
  app/         # Next.js App Router (Layouts, Pages)
  components/  # Shared UI & Feature-specific components
  lib/         # Utility functions and shared logic
  types/       # Global TypeScript interfaces
public/        # PWA assets and static icons
```

## Scripts
- `npm run dev`: Start development server with Webpack.
- `npm run build`: Production bundle generation.
- `npm run lint`: ESLint static analysis.

## Contributing
Please ensure all UI changes adhere to the CIAP Design System and use Tailwind 4 primitives. Tested and type-safe components are mandatory.
