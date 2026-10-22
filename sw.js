const CACHE='radar-v1';const ASSETS=['./','./index.html','./assets/styles.css','./assets/app.js','./assets/icon.svg','./manifest.webmanifest'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)));self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k!==CACHE).map(k=>caches.delete(k)))));self.clients.claim()});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;const u=new URL(e.request.url);if(u.origin!==self.location.origin)return;
if(u.pathname.endsWith('/news.json')){e.respondWith(fetch(e.request).then(r=>{if(r.ok){const copy=r.clone();caches.open(CACHE).then(c=>c.put('./news.json',copy))}return r}).catch(()=>caches.match('./news.json')));return}
e.respondWith(fetch(e.request).catch(()=>caches.match(e.request)))});
