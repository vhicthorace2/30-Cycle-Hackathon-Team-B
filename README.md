# CIAP Platform (Creator Intelligence & Analytics Platform)

Welcome to the **CIAP Platform**, a high-fidelity analytics and discovery engine built to empower the creator economy. CIAP bridges the gap between raw data and actionable intelligence, providing a production-grade experience for both creators and brands.

## 🚀 Key Features

### For Creators (Studio Hub)
*   **Real-Time Analytics**: Direct integration with YouTube Analytics API to show live subscriber counts, views, and engagement.
*   **Influence DNA**: A proprietary scoring system that calculates your market impact based on audience loyalty, growth velocity, and sentiment.
*   **Identity Management**: Centralized profile and avatar management with global synchronization across the platform.

### For SMEs & Brands (Market Discovery)
*   **Talent Hub**: A powerful search and discovery engine to find verified creators across multiple niches.
*   **Data-Backed Recruitment**: View real audience metrics and "Influence Scores" before initiating partnerships.
*   **Network Overview**: Track the aggregate reach and ROI of your entire creator network from a single dashboard.

## 🎨 Design Philosophy: "Modern Studio"
CIAP follows a strict **Retro-Modern** design language:
*   **Tactile UI**: Bold 2px black borders and hard pop-shadows for a physical, "magazine-style" feel.
*   **Vibrant Palettes**: Curated pastel backgrounds (Blue, Pink, Green, Purple) that distinguish different data sectors.
*   **Responsive Precision**: Seamless navigation across mobile and desktop with a focus on high-density data visualization.
*   **Modern Typography**: Utilizes `Bricolage Grotesque` for an editorial, high-impact reading experience.

## 🛠 Tech Stack

*   **Frontend**: Next.js 16 (App Router), TypeScript, Tailwind CSS 4, Framer Motion.
*   **Backend**: NestJS, PostgreSQL, Drizzle ORM, Redis for caching.
*   **Integrations**: Google/YouTube Data API v3, Instagram Graph API.

## 📂 Project Structure

```text
frontend/
├── app/                  # App Router: (protected) dashboard, market, settings
├── components/           # UI Components: layout (Sidebar, Header), shared (MetricCards)
├── lib/                  # Logic: API hooks (TanStack Query), Auth state (Zustand)
└── public/               # Assets: Modern illustrations and brand assets
```

## ⚙️ Quick Start

1.  **Installation**: `pnpm install`
2.  **Config**: Set `NEXT_PUBLIC_API_URL` in `.env.local`.
3.  **Launch**: `pnpm dev`

---
Built with passion for the creator economy. 🚀
