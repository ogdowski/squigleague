# Herald Frontend - Alpine.js SPA

Frontend service for the Herald blind list exchange system.

## What is Herald Frontend?

The Herald frontend is a **lightweight Alpine.js single-page application (SPA)** that provides the user interface for the Herald list exchange system. It communicates with the backend via JSON API calls.

## Architecture

Herald uses a **frontend/backend separation**:

- **Frontend (this service)**: Alpine.js SPA serving static HTML/JS/CSS
- **Backend**: FastAPI JSON API (see `../herald/`)
- **Communication**: Frontend calls backend at `/api/herald/*` endpoints
- **Nginx**: Routes `/api/*` to backend, everything else to this service

## Tech Stack

- **Framework**: Alpine.js (lightweight reactive framework)
- **Styling**: TailwindCSS via CDN
- **Deployment**: Nginx static file server in Docker container
- **No build step**: Pure HTML/JS/CSS, no compilation required

## Files

```
frontend/
├── index.html      # Home page (create exchange)
├── view.html       # Exchange view page (submit response + reveal)
├── style.css       # Global styles
├── nginx.conf      # Nginx configuration for static serving
└── Dockerfile      # Container definition
```

## How It Works

### 1. Create Exchange (index.html)
- User pastes army list
- Frontend POSTs to `/api/herald/exchange/create`
- Backend returns `{id, hash_a, url}`
- Frontend displays URL and hash for Player A

### 2. View Exchange (view.html)
- User opens URL with exchange ID
- Frontend GETs `/api/herald/exchange/{id}`
- If incomplete: Shows hash proof + form for Player B
- If complete: Shows both lists with timestamps

### 3. Submit Response
- Player B submits their list
- Frontend POSTs to `/api/herald/exchange/{id}/respond`
- Backend returns complete exchange
- Frontend displays both lists

### 4. Polling
- While waiting for Player B, Player A's page polls `/api/herald/exchange/{id}/status`
- When `complete: true`, page auto-refreshes to show both lists

## Development

The frontend is typically run via Docker Compose alongside the backend:

```bash
# From project root
just dev              # Starts both backend and frontend

# Frontend is served at: http://localhost:8000
# - / → index.html
# - /view/{id} → view.html (rewritten by nginx)
```

### Testing Frontend Changes

```bash
# Start services
just dev

# Open browser
open http://localhost:8000

# Test flow:
# 1. Create exchange
# 2. Copy URL
# 3. Open URL in incognito/private window (simulate Player B)
# 4. Submit response
# 5. Verify both lists appear in both windows
```

### Local Development (Without Docker)

If you want to work on the frontend without Docker:

```bash
# Start backend only
cd herald
uvicorn main:app --reload --port 8001

# Serve frontend with any static server
cd frontend
python3 -m http.server 8002

# Open browser: http://localhost:8002
# Note: Update API calls in HTML to point to http://localhost:8001
```

## Docker Image

Built as a multi-arch image (amd64/arm64):
- **Image**: `ogdowski/private:squigleague-frontend-VERSION`
- **Base**: nginx:alpine
- **Size**: ~50MB (just nginx + static files)

Build and push:
```bash
# From project root
just push  # Builds and pushes both backend and frontend
```

## Nginx Configuration

The frontend uses a custom nginx config (`nginx.conf`):

```nginx
# Serve static files
location / {
    root /usr/share/nginx/html;
    try_files $uri $uri/ =404;
}

# Rewrite /view/{id} to /view.html
location ~ ^/view/([a-z\-0-9]+)$ {
    try_files /view.html =404;
}
```

This allows clean URLs like `/view/crimson-captain-charges-7a2f` instead of `/view.html?id=...`.

## API Integration

The frontend calls these backend endpoints:

- `POST /api/herald/exchange/create` - Create new exchange
- `GET /api/herald/exchange/{id}` - Get exchange data
- `POST /api/herald/exchange/{id}/respond` - Submit Player B's list
- `GET /api/herald/exchange/{id}/status` - Poll for completion
- `GET /api/herald/stats` - Get system stats (for footer version)

All API calls are relative paths (`/api/herald/...`) which nginx routes to the backend service.

## Dynamic Version

The footer version is fetched dynamically from the backend:

```javascript
fetch('/api/herald/stats')
  .then(r => r.json())
  .then(data => {
    document.getElementById('version').textContent = data.version;
  });
```

This ensures the frontend always displays the correct backend version without hardcoding.

## Production

In production, this service:
- Serves static files via nginx
- Is completely stateless
- Can be cached/CDN'd
- Scales independently of backend
- Updates require only a container restart (no build step)

## Future Enhancements

- Add loading spinners for better UX
- Add error messages for failed API calls
- Add copy-to-clipboard feedback
- Add animations for list reveals
- Add dark mode toggle
- Add PWA support for offline viewing

## License

Part of Squig League ecosystem.
Copyright © 2025 Ariel Ogdowski. All Rights Reserved.
