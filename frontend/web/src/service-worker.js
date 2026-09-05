// Service Worker cho Khai Tâm Huyền Học (Tử Vi & Xem Bói AI)
// Quản lý bộ nhớ đệm ngoại tuyến (Offline Caching) bằng Workbox

const CACHE_NAMES = {
  static: 'khaitam-static-v2',
  api: 'khaitam-api-v2',
};

const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.svg',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
];

// Nạp Workbox từ Google CDN
try {
  importScripts('https://storage.googleapis.com/workbox-cdn/releases/7.0.0/workbox-sw.js');
} catch (e) {
  console.warn('Không thể tải Workbox CDN từ mạng:', e);
}

// 1. Kích hoạt và dọn dẹp các cache phiên bản cũ
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAMES.static && key !== CACHE_NAMES.api) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

if (self.workbox) {
  workbox.setConfig({ debug: false });
  workbox.core.skipWaiting();
  workbox.core.clientsClaim();

  // Nạp sẵn tài nguyên cốt lõi khi cài đặt
  self.addEventListener('install', (event) => {
    event.waitUntil(
      caches.open(CACHE_NAMES.static).then((cache) => {
        return cache.addAll(PRECACHE_ASSETS);
      })
    );
  });

  // A. Chiến lược Cache-First cho tài nguyên tĩnh (JS, CSS, Font, Image, Icons)
  workbox.routing.registerRoute(
    ({ request, url }) =>
      request.destination === 'script' ||
      request.destination === 'style' ||
      request.destination === 'font' ||
      request.destination === 'image' ||
      url.pathname.endsWith('.js') ||
      url.pathname.endsWith('.css') ||
      url.pathname.endsWith('.woff2') ||
      url.pathname.endsWith('.woff') ||
      url.pathname.endsWith('.png') ||
      url.pathname.endsWith('.svg') ||
      url.hostname.includes('fonts.googleapis.com') ||
      url.hostname.includes('fonts.gstatic.com'),
    new workbox.strategies.CacheFirst({
      cacheName: CACHE_NAMES.static,
      plugins: [
        new workbox.expiration.ExpirationPlugin({
          maxEntries: 120,
          maxAgeSeconds: 30 * 24 * 60 * 60, // 30 ngày
        }),
      ],
    })
  );

  // B. Chiến lược Network-First với Fallback Cache cho API GET /tu-vi và /bat-tu
  // Đã xem 1 lần thì có thể xem lại khi mất mạng, gắn cờ header X-From-Cache: 1
  workbox.routing.registerRoute(
    ({ request, url }) =>
      request.method === 'GET' &&
      (url.pathname.includes('/tu-vi') || url.pathname.includes('/bat-tu')),
    new workbox.strategies.NetworkFirst({
      cacheName: CACHE_NAMES.api,
      networkTimeoutSeconds: 4,
      plugins: [
        new workbox.expiration.ExpirationPlugin({
          maxEntries: 40,
          maxAgeSeconds: 7 * 24 * 60 * 60, // 7 ngày
        }),
        {
          cachedResponseWillBeUsed: async ({ cachedResponse }) => {
            if (!cachedResponse) return null;
            const headers = new Headers(cachedResponse.headers);
            headers.set('X-From-Cache', '1');
            return new Response(cachedResponse.body, {
              status: cachedResponse.status,
              statusText: cachedResponse.statusText,
              headers: headers,
            });
          },
        },
      ],
    })
  );

  // C. Tuyệt đối KHÔNG cache bất kỳ request POST, PUT, DELETE (đăng nhập, gieo quẻ, chat, upload)
  workbox.routing.registerRoute(
    ({ request }) => ['POST', 'PUT', 'DELETE', 'PATCH'].includes(request.method),
    new workbox.strategies.NetworkOnly()
  );

  // D. Xử lý điều hướng SPA (fallback về index.html khi ngoại tuyến)
  workbox.routing.registerRoute(
    ({ request }) => request.mode === 'navigate',
    async ({ request }) => {
      try {
        return await fetch(request);
      } catch {
        return (await caches.match('/index.html')) || (await caches.match('/'));
      }
    }
  );
} else {
  // Fallback Vanilla Service Worker dự phòng khi Workbox CDN không tải được
  self.addEventListener('install', (event) => {
    event.waitUntil(
      caches.open(CACHE_NAMES.static).then((cache) => cache.addAll(PRECACHE_ASSETS)).then(() => self.skipWaiting())
    );
  });

  self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    if (request.method !== 'GET') return;

    if (url.pathname.startsWith('/tu-vi') || url.pathname.startsWith('/bat-tu')) {
      event.respondWith(
        fetch(request)
          .then((networkResponse) => {
            if (networkResponse.ok) {
              const resClone = networkResponse.clone();
              caches.open(CACHE_NAMES.api).then((cache) => cache.put(request, resClone));
            }
            return networkResponse;
          })
          .catch(async () => {
            const cachedResponse = await caches.match(request);
            if (cachedResponse) {
              const headers = new Headers(cachedResponse.headers);
              headers.append('X-From-Cache', '1');
              return new Response(cachedResponse.body, {
                status: cachedResponse.status,
                statusText: cachedResponse.statusText,
                headers: headers,
              });
            }
            return new Response(
              JSON.stringify({
                thanh_cong: false,
                loi: 'Bạn đang ngoại tuyến và chưa có bản lưu cho lá số này.',
                du_lieu: null,
              }),
              {
                status: 503,
                headers: { 'Content-Type': 'application/json' },
              }
            );
          })
      );
      return;
    }

    if (
      request.destination === 'script' ||
      request.destination === 'style' ||
      request.destination === 'font' ||
      request.destination === 'image' ||
      url.pathname.endsWith('.js') ||
      url.pathname.endsWith('.css') ||
      url.pathname.endsWith('.svg') ||
      url.pathname.endsWith('.png') ||
      url.hostname.includes('fonts.googleapis.com') ||
      url.hostname.includes('fonts.gstatic.com')
    ) {
      event.respondWith(
        caches.match(request).then((cachedResponse) => {
          if (cachedResponse) return cachedResponse;
          return fetch(request).then((networkResponse) => {
            if (networkResponse.ok) {
              const resClone = networkResponse.clone();
              caches.open(CACHE_NAMES.static).then((cache) => cache.put(request, resClone));
            }
            return networkResponse;
          });
        })
      );
      return;
    }

    if (request.mode === 'navigate') {
      event.respondWith(
        fetch(request).catch(() => caches.match('/index.html'))
      );
    }
  });
}
