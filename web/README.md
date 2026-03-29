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

---

## Extending the Dashboard

### Adding a new tab
1. Create `web/src/lib/MyTab.svelte` — use `data` prop (metrics snapshot shape)
2. Import it in `App.svelte` and add a tab button: `<button onclick={() => activeTab = 'mytab'}>My Tab</button>`
3. Add `{#if activeTab === 'mytab'}<MyTab {data} />{/if}` to the main content area
4. Re-run `npm run build` to confirm no type errors

### Extending the sidecar API
1. Add a new route to `web/server.py` inside `create_app()`
2. Add tests to `tests/test_web_server.py` — target ≥80% coverage
3. Update `web/src/lib/api.js` with a new `fetch` helper
