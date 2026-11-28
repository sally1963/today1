// 유튜브 실시간 조회수를 받아 data/live.js 로 저장합니다.
// 실행: YOUTUBE_API_KEY=키 node scripts/update-live.mjs
// GitHub Actions가 약 30분마다 실행하며, 키는 저장소 Secrets에만 있어 방문자에게 노출되지 않습니다.
// 1회 실행에 쓰는 API 한도: 영상 50개당 1단위 + 채널 1단위 + 인기 급상승 2단위 ≈ 5~6단위 (하루 무료 10,000단위)
import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const KEY = process.env.YOUTUBE_API_KEY;
const DRY = process.argv.includes("--dry");
const API = "https://www.googleapis.com/youtube/v3/";
const VID = /^[A-Za-z0-9_-]{11}$/;
const CH = /^UC[A-Za-z0-9_-]{22}$/;

const src = await readFile(path.join(root, "data/rankings.js"), "utf8");
const start = src.indexOf("window.RANKINGS=") + "window.RANKINGS=".length;
const json = src.slice(start, src.lastIndexOf("}") + 1);
const D = JSON.parse(json);

const videos = new Set(), channels = new Set();
for (const key of Object.keys(D)) {
  for (const blk of [D[key].daily, D[key].total, D[key].daily?.extra, D[key].total?.extra]) {
    for (const it of blk?.items || []) {
      const id = String(it[3]);
      if (VID.test(id)) videos.add(id);
      else if (id.startsWith("u:") && CH.test(id.slice(2))) channels.add(id.slice(2));
    }
  }
}
console.log(`영상 ${videos.size}개, 채널 ${channels.size}개`);
if (DRY) process.exit(0);
if (!KEY) { console.log("::notice::YOUTUBE_API_KEY가 아직 없어 실시간 조회수 갱신을 건너뜁니다. 저장소 Settings → Secrets → Actions에 등록하면 자동으로 시작됩니다."); process.exit(0); }

const get = async (p, params) => {
  const q = new URLSearchParams({ ...params, key: KEY });
  const r = await fetch(API + p + "?" + q);
  const j = await r.json();
  if (!r.ok) throw new Error(j.error?.message || `HTTP ${r.status}`);
  return j;
};
const chunk = (a, n) => Array.from({ length: Math.ceil(a.length / n) }, (_, i) => a.slice(i * n, i * n + n));

const out = { updated: new Date().toISOString(), videos: {}, channels: {}, trending: { kr: [], global: [] } };
for (const c of chunk([...videos], 50)) {
  const j = await get("videos", { part: "statistics", id: c.join(",") });
  for (const v of j.items || []) out.videos[v.id] = Number(v.statistics.viewCount);
}
for (const c of chunk([...channels], 50)) {
  const j = await get("channels", { part: "statistics", id: c.join(",") });
  for (const v of j.items || []) out.channels[v.id] = Number(v.statistics.viewCount);
}
for (const [k, region] of [["kr", "KR"], ["global", "US"]]) {
  const j = await get("videos", { part: "snippet,statistics", chart: "mostPopular", regionCode: region, maxResults: 10 });
  out.trending[k] = (j.items || []).map(v => [v.snippet.title, v.snippet.channelTitle, Number(v.statistics.viewCount), v.id]);
}
await writeFile(path.join(root, "data/live.js"),
  "/* 서버(GitHub Actions)가 자동으로 덮어쓰는 파일입니다. 직접 고치지 마세요. */\nwindow.LIVE=" + JSON.stringify(out) + ";\n");
console.log(`저장 완료: 영상 ${Object.keys(out.videos).length}, 채널 ${Object.keys(out.channels).length}, 인기 급상승 ${out.trending.kr.length}/${out.trending.global.length}`);
