const CACHE = "ld-v50";

self.addEventListener("install", e => {
    e.waitUntil(
        caches.open(CACHE).then(c => c.addAll(["/lindan/static/manifest.json", "/lindan/static/avatar.png", "/lindan/static/icon-192.png", "/lindan/static/icon-512.png"]))
    );
    self.skipWaiting();
});

self.addEventListener("activate", e => {
    e.waitUntil(
        caches.keys().then(keys => Promise.all(
            keys.filter(k => k !== CACHE).map(k => caches.delete(k))
        ))
    );
});

self.addEventListener("fetch", e => {
    // Network-first for HTML — always get latest version
    if(e.request.destination === "document"){
        e.respondWith(
            fetch(e.request).catch(() => caches.match(e.request))
        );
        return;
    }
    // Cache-first for static assets
    e.respondWith(
        caches.match(e.request).then(r => r || fetch(e.request))
    );
});
