const Redis = require('ioredis')

const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379'
const redis = new Redis(REDIS_URL)
const fetchImpl = globalThis.fetch ? globalThis.fetch.bind(globalThis) : require('node-fetch')

let yfClient

async function getYfClient() {
  if (!yfClient) {
    const mod = await import('yahoo-finance2')
    yfClient = mod.default || mod
  }
  return yfClient
}

function parsePrice(quote) {
  if (!quote) return null
  return quote.regularMarketPrice || quote.price?.regularMarketPrice || quote.previousClose || null
}

async function fetchIndices() {
  try {
    const yf = await getYfClient()
    const nifty = await yf.quoteSummary('^NSEI')
    const sensex = await yf.quoteSummary('^BSESN')

    const payload = {
      fetched_at: new Date().toISOString(),
      nifty: nifty?.price || null,
      sensex: sensex?.price || null,
    }

    await redis.set('market:latest', JSON.stringify(payload), 'EX', 60 * 5)
    console.log('Cached market indices', payload)

    // also fetch configured tickers and cache per-ticker prices
    const tickersEnv = process.env.MARKET_TICKERS || ''
    const tickers = tickersEnv.split(',').map(t => t.trim()).filter(Boolean)
    for (const t of tickers) {
      try {
        const q = await yf.quote(t)
        const price = parsePrice(q)
        const obj = {
          price,
          fetched_at: new Date().toISOString(),
          source: 'worker',
          ticker: t,
          close: q?.regularMarketPreviousClose || q?.previousClose || null,
        }
        await redis.set(`market:prices:${t}`, JSON.stringify(obj), 'EX', 60 * 5)
      } catch (e) {
        console.warn('failed to fetch ticker', t, e && e.message)
      }
    }

    // if backend snapshot endpoint configured, POST daily snapshot for indices
    const BACKEND_SNAPSHOT_URL = process.env.BACKEND_SNAPSHOT_URL
    const WORKER_SECRET = process.env.MARKET_WORKER_SECRET
    if (BACKEND_SNAPSHOT_URL && WORKER_SECRET) {
      try {
        const body = {
          date: new Date().toISOString().slice(0, 10),
          index_name: 'NIFTY',
          open: nifty?.price?.regularMarketOpen || null,
          high: nifty?.price?.regularMarketDayHigh || null,
          low: nifty?.price?.regularMarketDayLow || null,
          close: nifty?.price?.regularMarketPreviousClose || null,
          metadata: { raw: nifty },
          payload: {
            price: parsePrice(nifty?.price),
            source: 'worker',
            fetched_at: new Date().toISOString(),
          }
        }
        await fetchImpl(BACKEND_SNAPSHOT_URL, { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-market-secret': WORKER_SECRET }, body: JSON.stringify(body) })
      } catch (e) {
        console.warn('failed to post snapshot', e && e.message)
      }
    }
  } catch (err) {
    console.error('market fetch error', err.message || err)
  }
}

async function run() {
  await fetchIndices()
  setInterval(fetchIndices, 1000 * 60 * 3)
}

run().catch(err => {
  console.error(err)
  process.exit(1)
})
