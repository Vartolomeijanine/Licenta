# Color Analysis Frontend

Local React + Vite frontend for the Color Analysis app.

Quick start

1. Install dependencies

```bash
cd frontend
npm install
```

2. Run dev server

```bash
npm run dev
```

3. Open http://localhost:5173

Configuration

- By default the frontend calls the API at `http://localhost:8000`.
- To change the backend base URL, set the `VITE_API_BASE` environment variable before running Vite. Example (Windows PowerShell):

```powershell
$Env:VITE_API_BASE = "http://localhost:8000"
npm run dev
```

Notes

- Authentication uses JWT: login `POST /api/token/` (handled by `src/api/authApi.js`).
- Uploads are sent as multipart/form-data to `POST /api/coloranalysis/analyze/`.
- The backend currently returns mock seasons; connect your AI pipeline to `backend/coloranalysis/views.py` to replace the mock.

TODOs

- Add GET `/api/coloranalysis/<id>/` detail endpoint on the backend for direct result fetching (frontend currently fetches history and finds the item by id).
