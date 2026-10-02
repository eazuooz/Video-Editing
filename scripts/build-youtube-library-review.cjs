const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const puppeteer = require(path.join(root, 'motion-canvas', 'node_modules', 'puppeteer'));
const outputRoot = path.join(root, 'output', 'youtube-library-refresh');
const report = JSON.parse(fs.readFileSync(path.join(outputRoot, 'changes.json'), 'utf8'));

const grouped = new Map();
for (const change of report.changes) {
  const id = change.primaryPlaylist.id;
  if (!grouped.has(id)) grouped.set(id, []);
  grouped.get(id).push(change);
}

function escapeHtml(value) {
  return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;');
}

function relativeThumbnail(change) {
  return `thumbnails/${path.basename(change.thumbnailPath)}`;
}

const allCards = report.changes.map((change) => `
<article>
  <img loading="lazy" src="${relativeThumbnail(change)}" alt="${escapeHtml(change.headline)}">
  <h2>${escapeHtml(change.proposedTitle)}</h2>
  <p><strong>${escapeHtml(change.category)}</strong> · ${escapeHtml(change.id)}</p>
  <details><summary>설명 상단 추가문</summary><pre>${escapeHtml(change.descriptionIntro)}</pre></details>
</article>`).join('');

const indexHtml = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>얌얌코딩 라이브러리 리뉴얼</title><style>
body{margin:0;background:#f5f7fb;color:#111827;font-family:'Noto Sans KR','Malgun Gothic',sans-serif}header{position:sticky;top:0;z-index:2;padding:18px 28px;background:rgba(255,255,255,.94);border-bottom:1px solid #dbe1ea}h1{margin:0;font-size:26px}header p{margin:6px 0 0;color:#5b6473}.grid{padding:24px;display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}article{background:#fff;border-radius:16px;box-shadow:0 8px 24px rgba(15,23,42,.1);overflow:hidden;padding-bottom:16px}img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover}h2{font-size:18px;line-height:1.35;margin:14px 16px 8px}p,details{margin:0 16px;color:#5b6473;font-size:14px}pre{white-space:pre-wrap;color:#222;background:#f5f6f8;padding:12px;border-radius:10px}
</style></head><body><header><h1>유튜브 라이브러리 리뉴얼 — ${report.count}개</h1><p>C++ 기초 문법 / C++ 자료구조 및 기초 알고리즘 제외 · 재생목록별 배경색·환경 적용</p></header><main class="grid">${allCards}</main></body></html>`;
fs.writeFileSync(path.join(outputRoot, 'index.html'), indexHtml, 'utf8');

const sampleCards = [];
for (const changes of grouped.values()) {
  const picks = [changes[0], changes[Math.floor(changes.length / 2)], changes.at(-1)].filter(Boolean);
  const unique = [...new Map(picks.map((change) => [change.id, change])).values()];
  for (const change of unique) {
    sampleCards.push(`<article><img src="${relativeThumbnail(change)}"><div><b>${escapeHtml(change.category)}</b><span>${escapeHtml(change.headline)}</span></div></article>`);
  }
}
const sampleHtml = `<!doctype html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box}body{margin:0;padding:18px;background:#111827;font-family:'Noto Sans KR','Malgun Gothic',sans-serif}.grid{display:grid;grid-template-columns:repeat(3,400px);gap:14px}article{background:#fff;border-radius:10px;overflow:hidden}img{display:block;width:400px;height:225px;object-fit:cover}div{padding:8px 10px 10px;display:flex;flex-direction:column;gap:2px}b{font-size:12px;color:#6b7280}span{font-size:14px;font-weight:800;color:#111827;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
</style></head><body><main class="grid">${sampleCards.join('')}</main></body></html>`;
const samplePath = path.join(outputRoot, 'sample-contact.html');
fs.writeFileSync(samplePath, sampleHtml, 'utf8');

(async () => {
  const browser = await puppeteer.launch({headless: true});
  const page = await browser.newPage();
  await page.setViewport({width: 1280, height: 900, deviceScaleFactor: 1});
  await page.goto(`file:///${samplePath.replaceAll('\\', '/')}`, {waitUntil: 'networkidle0'});
  await page.screenshot({path: path.join(outputRoot, 'sample-contact.png'), fullPage: true});
  await browser.close();
  console.log(JSON.stringify({index: path.join(outputRoot, 'index.html'), sample: path.join(outputRoot, 'sample-contact.png'), sampleCount: sampleCards.length}, null, 2));
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
