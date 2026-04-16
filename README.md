# ciap-mvp-b
The CIAP-MVP Git repository for Team B.
- Edit as neccesary ,commit to main only when absolutely neccesary
- containerize your apps, keep clear and concise commit e.g `git commit -m feat: your-commit`
- Ensure you use separate ports to prevent race conditions e.g backend uses `localhost:3000` frontend should use `localhost:4000`

## What is this repo

- `backend/` contains the NestJS API (auth, users, sessions, etc.)
- `frontend/` contains the client app
- `ML/` contains ML-related work

## Backend usage (for frontend & ML)

Quick path to get the API running locally so you can call it from the frontend.

### 1) Start the API

```bash
cd backend
pnpm install
cp .env.example .env
pnpm run db:migrate
pnpm run start:dev
```

Defaults:

- API base: http://localhost:3000
- Swagger docs: http://localhost:3000/api-docs
- Health check: http://localhost:3000/health

### 2) Configure frontend

Point your frontend API base URL to `http://localhost:3000`.

If the frontend needs auth flows, see the API docs in [backend/README.md](backend/README.md) for routes and JWT/OAuth details.

### 3) Common endpoints

- `POST /auth/signup`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/verify`

For the full list and schemas, use Swagger at `/api-docs`.

### 4) Need sample data?

```bash
pnpm run db:seed
```

### 5) Notes

- Uses `pnpm` only.
- Access tokens use `ES256`; refresh tokens use `ES512`.

## More docs

- Backend setup and usage: [backend/README.md](backend/README.md)
- Backend structure: [backend/docs/project-structure.md](backend/docs/project-structure.md)
