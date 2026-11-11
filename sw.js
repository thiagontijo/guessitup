// Guessitup Arena: keeps the app shell available offline. Network first, cache as fallback.
const CACHE = 'arena-v1';
const SHELL = ['./', './index.html', './manifest.webmanifest', './fonts/bsd-800.woff2', './icons/icon-192.png', './icons/icon-180.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  // Live scores and anything from another site go straight to the network.
  if (e.request.method !== 'GET' || url.origin !== self.location.origin) return;
  const key = url.origin + url.pathname; // ignore cache-busting query strings
  e.respondWith(
    fetch(e.request, { cache: 'no-store' })
      .then((res) => {
        if (res.ok) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(key, copy));
        }
        return res;
      })
      .catch(() => caches.match(key).then((hit) => hit || caches.match('./index.html')))
  );
});
