# RubriCheck — Frontend (React + Vite + Tailwind + TS)

A minimal, production-ready frontend to upload a **rubric (JSON)**, paste an **essay**, call your **/evaluate** API, and render **per-criterion results**.

## Quickstart

```bash
npm install
cp .env.example .env
# edit .env if needed
npm run dev
```

Open http://localhost:5173

## Configure API

Set `VITE_API_BASE_URL` in `.env` (e.g., `https://api.your-domain.com`).  
The app POSTs to `/evaluate` with:
```json
{ "rubric": { ... }, "essayText": "..." }
```

## Rubric JSON shape (simplified)

```jsonc
{
  "id": "essay-v1",
  "title": "Argumentative Essay Rubric",
  "criteria": [
    {
      "id": "thesis",
      "name": "Thesis Statement",
      "weight": 0.25,
      "levels": [
        {"name": "Excellent", "description": "Clear, arguable thesis.", "points": 4},
        {"name": "Good", "description": "Mostly clear thesis.", "points": 3},
        {"name": "Fair", "description": "Unclear or weak.", "points": 2},
        {"name": "Poor", "description": "Missing.", "points": 1}
      ]
    }
  ]
}
```

## Production build
```bash
npm run build
npm run preview
```

## Tech
- React 18 + Vite 5 + TypeScript
- TailwindCSS
- Zustand for lightweight state
- Axios for API
