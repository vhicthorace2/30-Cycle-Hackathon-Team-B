# CIAP Platform (Team B)

CIAP is a creator influence and analytics platform that combines a NestJS API, a Next.js client, and a Python analytics engine. This repo keeps each part focused while sharing a single entry point.

## Repo layout

- Backend API: NestJS + TypeScript service with PostgreSQL and Drizzle ORM, auth, and API docs. See [backend/README.md](backend/README.md).
- Frontend app: Next.js + React client with Tailwind CSS, state management, and data visualization. See [frontend/README.md](frontend/README.md).
- ML analytics: Python 3 analytics engine with adapters, reporting, and CLI workflows. See [ML/README.md](ML/README.md).

## Start here

1) Backend setup and API docs: [backend/README.md](backend/README.md)
2) Frontend setup and UI workflow: [frontend/README.md](frontend/README.md)
3) ML engine usage and CLI: [ML/README.md](ML/README.md)

## Notes

- Keep component-specific details in each subfolder README to avoid duplication here.
- Cross-cutting architecture or integration notes can live in a short repo-level doc if needed.
