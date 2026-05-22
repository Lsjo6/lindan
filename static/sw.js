const CACHE = "ld-v2";

self.addEventListener("install", e => {
    e.waitUntil(
        caches.open(CACHE).then(c => c.addAll(["/", "/static/manifest.json"]))
    );
    self.skipWaiting();
});

self.addEventListener("fetch", e => {
    // API 请求不缓存
    if (e.request.url.includes("/api/")) return;
    e.respondWith(
        caches.match(e.request).then(r => r || fetch(e.request))
    );
});
