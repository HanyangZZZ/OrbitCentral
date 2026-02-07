# FBLC Cross-Platform App

## Overview
- Frontend: Vue 3 + Vite + Capacitor
- Backend: Django (API only)
- Communication: Axios via REST API

## Frontend Setup
From the workspace root:

1) Install dependencies
- `cd frontend`
- `npm install`

2) Run the dev server
- `npm run dev`

The frontend uses a Vite dev proxy for `/api` by default. Override with `VITE_API_BASE_URL` in `.env` if needed.

## Backend Setup
From the workspace root:

1) Install dependencies
- `cd backend`
- `/Users/hanyangzhuo/Documents/FBLC/.venv/bin/python -m pip install -r requirements.txt`

2) Run the server
- `/Users/hanyangzhuo/Documents/FBLC/.venv/bin/python manage.py migrate`
- `/Users/hanyangzhuo/Documents/FBLC/.venv/bin/python manage.py runserver`

The API endpoint is available at `http://localhost:8000/api/items/`.

### Verify frontend ↔ backend connection
1) Start the backend and frontend servers.
2) Use the "Add item" form in the UI.
3) The new item should appear immediately after refresh.

### Web portal (Django admin)
1) Run migrations (already applied).
2) Create a superuser if needed:
	- `/Users/hanyangzhuo/Documents/FBLC/.venv/bin/python manage.py createsuperuser`
3) Start the server and open `http://localhost:8000/admin`.

### Backend tests
- `/Users/hanyangzhuo/Documents/FBLC/.venv/bin/python manage.py test`

### Frontend tests (Capacitor checks)
From `frontend/`:
- `npm test`

What it covers:
- Validates `capacitor.config.json` exists and contains required fields for cross-platform builds.
- Backend API tests include GET/POST and validation errors.

## Capacitor
After building the frontend:
- `npm run build`
- `npm run cap:init`
- `npm run cap:add:ios` or `npm run cap:add:android`
- `npm run cap:sync`

## Notes
- CORS is enabled for all origins in development.
- Replace the example data in the backend with your real data source.
