# Market Worker

Simple Node worker that fetches Sensex (^BSESN) and Nifty (^NSEI) via `yahoo-finance2` and caches results in Redis under `market:latest`.

Run locally:

```bash
cd market-worker
npm install
REDIS_URL=redis://localhost:6379 node index.js
```

Notes:
- This is a lightweight scaffold. Add retry/backoff, error logging, and daily snapshot persistence to Postgres as needed.
