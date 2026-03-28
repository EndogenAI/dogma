# MCP Web Dashboard (Phase 2 Scaffold)

This directory hosts the web dashboard scaffold for the dogma MCP observability UI.

## Local Development

1. Install dependencies:

```bash
npm install
```

2. Start both sidecar + frontend:

```bash
uv run python ../scripts/start_dashboard.py
```

3. Optional frontend-only dev server:

```bash
npm run dev
```

4. Quality checks:

```bash
npm run check
npm run build
```

## Architecture Notes (Locked for MVP)

- Scaffold uses `npm init vite web -- --template svelte`.
- CORS remains hardcoded to `http://localhost:5173` in `web/server.py`.
- SSE contract is FastAPI `StreamingResponse` to browser-native `EventSource`.
- Data visualization library is LayerCake; do not add `svelte-chartjs` or `chart.js`.
- Routing is local reactive tab state (`activeTab`), no routing library.
