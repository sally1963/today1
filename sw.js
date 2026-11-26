/* 오늘의 1위 — 서비스 워커 (앱 설치·오프라인 보기)
   화면 파일은 저장해 두고 바로 열고, 순위 데이터는 항상 최신을 먼저 받아 옵니다.
   화면 코드를 바꿔 올릴 때는 아래 VERSION 숫자를 올려 주세요. */
const VERSION = "v2-2026-11-26";
const SHELL = "shell-" + VERSION;
const DATA = "data-" + VERSION;
const FONT = "fonts";
const SHELL_FILES = [
  "./", "index.html", "about.html", "privacy.html", "posts/", "manifest.webmanifest",
  "site.config.js", "assets/doc.css", "assets/doc.js",
  "i18n/source.js", "i18n/en.js", "i18n/zh.js", "i18n/ja.js", "i18n/es.js", "i18n/fr.js", "i18n/ru.js",
  "icons/icon-192.png", "icons/icon-512.png", "icons/apple-touch-icon.png", "icons/favicon-32.png"
];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_FILES)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(
    keys.filter(k => ![SHELL, DATA, FONT].includes(k)).map(k => caches.delete(k))
  )).then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // 글꼴: 한 번 받으면 저장해 두고 재사용
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    e.respondWith(caches.open(FONT).then(async c => {
      const hit = await c.match(req); if (hit) return hit;
      const res = await fetch(req); if (res.ok || res.type === "opaque") c.put(req, res.clone()); return res;
    }));
    return;
  }
  if (url.origin !== location.origin) return; // 유튜브·광고 등 외부는 그대로

  // 순위·조회수·해설 데이터와 해설 글: 최신 먼저, 안 되면 저장본
  if (/\/data\/|\/posts\//.test(url.pathname)) {
    e.respondWith(fetch(req).then(res => {
      if (res.ok) caches.open(DATA).then(c => c.put(req, res.clone()));
      return res;
    }).catch(() => caches.match(req, { ignoreSearch: true })));
    return;
  }

  // 화면 파일: 저장본을 바로 보여 주고 뒤에서 새로 받아 둠
  e.respondWith(caches.match(req, { ignoreSearch: true }).then(hit => {
    const net = fetch(req).then(res => {
      if (res.ok) caches.open(SHELL).then(c => c.put(req, res.clone()));
      return res;
    }).catch(() => hit || caches.match("index.html"));
    return hit || net;
  }));
});
