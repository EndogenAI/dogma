import fixtureData from '../assets/fixture.json';

let _isOffline = true;

export function isOffline() { return _isOffline; }

export async function getSnapshot() {
  try {
    const resp = await fetch('http://localhost:8000/api/metrics');
    if (!resp.ok) throw new Error('fetch failed');
    _isOffline = false;
    return resp.json();
  } catch {
    return fixtureData;
  }
}

export function subscribeStream(onData, onError) {
  const es = new EventSource('http://localhost:8000/api/metrics/stream');
  es.onopen = () => { _isOffline = false; };
  es.onmessage = (e) => { onData(JSON.parse(e.data)); };
  es.onerror = onError;
  return () => es.close(); // returns unsubscribe fn
}
