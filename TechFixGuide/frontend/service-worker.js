/**
 * TechFix Guide — Service Worker
 * Strategy: Stale-While-Revalidate for guides/content
 *           Cache-First for static assets
 *           Network-First for API calls
 */

const CACHE_VERSION   = 'tfg-v1.2';
const STATIC_CACHE    = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE   = `${CACHE_VERSION}-dynamic`;
const API_CACHE       = `${CACHE_VERSION}-api`;

// Assets to pre-cache on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/diagnostic.html',
  '/scripts.html',
  '/guides.html',
  '/style.css',
  '/manifest.json',
  '/assets/icons/icon-192.png',
  '/assets/icons/icon-512.png',
];

// ── Install ───────────────────────────────────────────────────
self.addEventListener('install', event => {
  console.log('[SW] Installing TechFix Guide Service Worker…');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
      .catch(err => console.warn('[SW] Pre-cache error:', err))
  );
});

// ── Activate ──────────────────────────────────────────────────
self.addEventListener('activate', event => {
  console.log('[SW] Activating…');
  event.waitUntil(
    caches.keys().then(cacheNames =>
      Promise.all(
        cacheNames
          .filter(name => name.startsWith('tfg-') && !name.startsWith(CACHE_VERSION))
          .map(name => {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          })
      )
    ).then(() => self.clients.claim())
  );
});

// ── Fetch ─────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET and cross-origin uploads
  if (request.method !== 'GET') return;
  if (url.pathname.startsWith('/uploads/')) return;

  // ① API calls → Network-First (with cache fallback)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstWithCache(request, API_CACHE, 5000));
    return;
  }

  // ② HTML pages → Stale-While-Revalidate
  if (request.headers.get('accept')?.includes('text/html') ||
      url.pathname.endsWith('.html') || url.pathname === '/') {
    event.respondWith(staleWhileRevalidate(request, DYNAMIC_CACHE));
    return;
  }

  // ③ Static assets (CSS, JS, fonts, icons) → Cache-First
  if (
    url.pathname.endsWith('.css') ||
    url.pathname.endsWith('.js')  ||
    url.pathname.endsWith('.png') ||
    url.pathname.endsWith('.jpg') ||
    url.pathname.endsWith('.svg') ||
    url.pathname.endsWith('.woff2') ||
    url.pathname.endsWith('.json')
  ) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  // ④ Everything else → Stale-While-Revalidate
  event.respondWith(staleWhileRevalidate(request, DYNAMIC_CACHE));
});

// ── Strategies ────────────────────────────────────────────────

/**
 * Stale-While-Revalidate:
 * Respond immediately from cache if available,
 * then update the cache from network in the background.
 * Best for guides/content that should be readable offline.
 */
async function staleWhileRevalidate(request, cacheName) {
  const cache     = await caches.open(cacheName);
  const cached    = await cache.match(request);

  const networkFetch = fetch(request)
    .then(response => {
      if (response && response.ok) {
        cache.put(request, response.clone());
      }
      return response;
    })
    .catch(() => null);

  return cached || await networkFetch || offlineFallback(request);
}

/**
 * Cache-First:
 * Serve from cache, only fetch from network if not cached.
 * Best for versioned static assets.
 */
async function cacheFirst(request, cacheName) {
  const cache  = await caches.open(cacheName);
  const cached = await cache.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response && response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return offlineFallback(request);
  }
}

/**
 * Network-First with Cache Fallback:
 * Try network first (with timeout), fall back to cache.
 * Best for API calls that need fresh data.
 */
async function networkFirstWithCache(request, cacheName, timeoutMs = 5000) {
  const cache = await caches.open(cacheName);

  try {
    const controller   = new AbortController();
    const timeout      = setTimeout(() => controller.abort(), timeoutMs);
    const response     = await fetch(request, { signal: controller.signal });
    clearTimeout(timeout);

    if (response && response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await cache.match(request);
    return cached || new Response(
      JSON.stringify({ error: 'offline', message: 'Không có kết nối mạng. Đang dùng dữ liệu đã lưu.' }),
      { headers: { 'Content-Type': 'application/json' }, status: 503 }
    );
  }
}

/**
 * Offline fallback page.
 */
async function offlineFallback(request) {
  const cache = await caches.open(STATIC_CACHE);

  // Return cached index for navigation
  if (request.headers.get('accept')?.includes('text/html')) {
    return await cache.match('/index.html') ||
      new Response('<h1>TechFix Guide — Offline</h1><p>Hãy kết nối lại mạng.</p>', {
        headers: { 'Content-Type': 'text/html' }
      });
  }

  return new Response('Offline', { status: 503 });
}

// ── Background Sync ───────────────────────────────────────────
self.addEventListener('sync', event => {
  if (event.tag === 'sync-diagnostic') {
    console.log('[SW] Background sync: diagnostic');
  }
});

// ── Push Notifications ────────────────────────────────────────
self.addEventListener('push', event => {
  const data = event.data?.json() ?? {};
  event.waitUntil(
    self.registration.showNotification(data.title || 'TechFix Guide', {
      body: data.body || 'Có cập nhật mới từ TechFix Guide.',
      icon: '/assets/icons/icon-192.png',
      badge: '/assets/icons/icon-96.png',
      data: { url: data.url || '/' },
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/')
  );
});
