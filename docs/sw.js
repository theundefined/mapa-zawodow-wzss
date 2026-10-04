// Service worker: pozwala zainstalować stronę jako aplikację i działać offline
// z ostatnio pobranymi danymi. Przy zmianie listy APP_SHELL podbij wersję cache.
const CACHE = 'wzss-mapa-v1';
const APP_SHELL = [
    './',
    'competitions.json',
    'manifest.webmanifest',
    'icons/icon-192.png',
    'icons/favicon-32.png',
    'https://unpkg.com/leaflet@1.7.1/dist/leaflet.css',
    'https://unpkg.com/leaflet@1.7.1/dist/leaflet.js',
];

self.addEventListener('install', event => {
    event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(APP_SHELL)));
    self.skipWaiting();
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    const req = event.request;
    if (req.method !== 'GET') return;
    const url = new URL(req.url);

    // Kafelki OSM nie są cache'owane (polityka OSM + rozmiar) — zwykłe żądanie sieciowe.
    if (url.hostname.endsWith('tile.openstreetmap.org')) return;

    // Biblioteki z CDN (wersjonowane) — najpierw cache.
    if (url.hostname === 'unpkg.com') {
        event.respondWith(caches.match(req).then(hit => hit || fetchAndCache(req)));
        return;
    }

    // Własne pliki (strona, dane, kalendarze) — najpierw sieć, by dane były świeże; offline z cache.
    if (url.origin === self.location.origin) {
        event.respondWith(
            fetchAndCache(req).catch(() =>
                caches.match(req, { ignoreSearch: true })
                    .then(hit => hit || (req.mode === 'navigate' ? caches.match('./') : Response.error()))
            )
        );
    }
});

function fetchAndCache(req) {
    return fetch(req).then(res => {
        if (res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then(cache => cache.put(req, copy));
        }
        return res;
    });
}
