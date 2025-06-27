/// <reference types="@types/serviceworker" />

import { transformJpegXLToBmp } from './transformJpegXLToBmp';

const CACHE_NAME = 'wsh-2024-v1';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24時間

// キャッシュするリソースのパターン
const CACHE_PATTERNS = [
  /\/assets\//,  // 静的アセット
  /\/images\//,  // 画像API
  /\.js$/,       // JavaScriptファイル
  /\.css$/,      // CSSファイル
  /\.woff$/,     // フォントファイル
];

self.addEventListener('install', (ev: ExtendableEvent) => {
  ev.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (ev: ExtendableEvent) => {
  ev.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(cacheName => cacheName !== CACHE_NAME)
          .map(cacheName => caches.delete(cacheName))
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (ev: FetchEvent) => {
  ev.respondWith(onFetch(ev.request));
});

async function onFetch(request: Request): Promise<Response> {
  // キャッシュ可能なリソースかチェック
  const shouldCache = CACHE_PATTERNS.some(pattern => pattern.test(request.url));
  
  if (shouldCache && request.method === 'GET') {
    // キャッシュファーストストラテジー
    const cached = await caches.match(request);
    if (cached) {
      // キャッシュの有効期限をチェック
      const cacheDate = cached.headers.get('sw-cache-date');
      if (cacheDate) {
        const age = Date.now() - parseInt(cacheDate);
        if (age < CACHE_DURATION) {
          return cached;
        }
      }
    }
  }

  // ネットワークリクエスト
  try {
    const res = await fetch(request);
    
    // JPEG XLの変換処理
    if (res.headers.get('Content-Type') === 'image/jxl') {
      const transformedRes = await transformJpegXLToBmp(res);
      
      // 変換済み画像もキャッシュする
      if (shouldCache && res.ok) {
        const cache = await caches.open(CACHE_NAME);
        const responseToCache = transformedRes.clone();
        const headers = new Headers(responseToCache.headers);
        headers.set('sw-cache-date', Date.now().toString());
        const cachedResponse = new Response(responseToCache.body, {
          status: responseToCache.status,
          statusText: responseToCache.statusText,
          headers: headers
        });
        cache.put(request, cachedResponse);
      }
      
      return transformedRes;
    }
    
    // 通常のレスポンスもキャッシュ
    if (shouldCache && res.ok) {
      const cache = await caches.open(CACHE_NAME);
      const responseToCache = res.clone();
      const headers = new Headers(responseToCache.headers);
      headers.set('sw-cache-date', Date.now().toString());
      const cachedResponse = new Response(responseToCache.body, {
        status: responseToCache.status,
        statusText: responseToCache.statusText,
        headers: headers
      });
      cache.put(request, cachedResponse);
    }
    
    return res;
  } catch (error) {
    // ネットワークエラー時はキャッシュから返す
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    throw error;
  }
}