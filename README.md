# CIAP Platform (Team B)

CIAP is a creator influence and analytics platform built as a multi-service system combining a **NestJS API**, a **Next.js frontend**, and a **Python-based analytics engine**. Each service is independently structured but designed to work as a unified system.

---

## Architecture Overview

- **Backend API** – NestJS + TypeScript service  
  Handles authentication, core business logic, PostgreSQL database access via Drizzle ORM, and API documentation.  
  Swagger documentation available at: **/api-docs**  
  → [backend/README.md](backend/README.md)

- **Frontend App** – Next.js + React  
  UI layer with Tailwind CSS, state management, and data visualization components.  
  → [frontend/README.md](frontend/README.md)

- **ML / Analytics Engine** – Python 3  
  Responsible for analytics pipelines, adapters, reporting workflows, and CLI-based execution.  
  → [ML/README.md](ML/README.md)

---

## Getting Started

1. Backend setup and API documentation → [backend/README.md](backend/README.md)  
2. Frontend setup and UI workflow → [frontend/README.md](frontend/README.md)  
3. Analytics engine usage and CLI tools → [ML/README.md](ML/README.md)

---

## Deployment / Environments

- **Frontend (Vercel)**  
  https://30-cycle-hackathon-team-b.vercel.app

- **Backend API**  
  https://p01--ciap-apis--fh4qwyd5rbmr.code.run  
  Swagger docs: https://p01--ciap-apis--fh4qwyd5rbmr.code.run/api-docs

- **Queue Monitoring (Bull Board / Redis UI)**  
  https://p01--redis-bullboard--fh4qwyd5rbmr.code.run  

  **Credentials:**
  - Username: `Admin `
  - Password: `Admin123`

---

## Notes

- Service-specific implementation details should remain in their respective module READMEs to avoid duplication.
- Cross-service architecture decisions or shared contracts can be documented here if they grow in importance.
- Keep environment URLs and credentials updated and rotate them when necessary.