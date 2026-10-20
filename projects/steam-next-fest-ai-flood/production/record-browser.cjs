// Record our own browser screens (Steam store/search/hub, public report pages)
// with the MIT-licensed "AI warning for Steam" extension loaded from source.
// Usage: node projects/steam-next-fest-ai-flood/production/record-browser.cjs [shotId ...]
// Output: projects/steam-next-fest-ai-flood/production/local/recordings/<shot>.webm (+ .json)
const puppeteer = require('../../../motion-canvas/node_modules/puppeteer');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const R = path.resolve(__dirname, '../../..');
const P = path.join(R, 'projects/steam-next-fest-ai-flood');
const EXT = path.join(P, 'production/local/ext/aiwarningforsteam');
const OUT = path.join(P, 'production/local/recordings');
fs.mkdirSync(OUT, {recursive: true});
const W = 1920, H = 1080;
const sleep = ms => new Promise(r => setTimeout(r, ms));
const sha = f => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');

async function smoothScroll(page, totalPx, stepPx = 6, delayMs = 16) {
  // Mouse-wheel scrolling survives client-side reloads better than evaluate().
  await page.mouse.move(W / 2, H / 2);
  for (let y = 0; y < totalPx; y += stepPx) {
    try { await page.mouse.wheel({deltaY: stepPx}); } catch (e) { await sleep(300); }
    await sleep(delayMs);
  }
}
async function settle(page) {
  await page.waitForNetworkIdle({idleTime: 1200, timeout: 20000}).catch(() => {});
  await sleep(1500);
}
async function hasDisclosure(page) {
  return page.evaluate(() => /AI Generated Content Disclosure|AI 생성 콘텐츠 공개|AI 생성 콘텐츠/i.test(document.body.innerText));
}
async function dismissSteamOverlays(page) {
  // Age gate / cookie dialog if present; keep platform UI otherwise.
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button, a')).find(b => /Accept all|모두 수락|Reject all|모두 거부/i.test(b.textContent || ''));
    if (btn && /Reject|거부/i.test(btn.textContent)) btn.click();
  }).catch(() => {});
}

const SHOTS = {
  // S01 hero: newest demos search with the extension blurring disclosed games
  'search-demos-blur': {url: 'https://store.steampowered.com/search/?category1=10&sort_by=Released_DESC&ndl=1', ext: true,
    run: async page => { await sleep(2500); await smoothScroll(page, 2600, 5, 16); await sleep(1500); }},
  'search-demos-hide': {url: 'https://store.steampowered.com/search/?category1=10&sort_by=Released_DESC&ndl=1', ext: true,
    run: async page => { await sleep(2000);
      await page.evaluate(() => { const o = Array.from(document.querySelectorAll('.tab_filter_control_row, .tab_filter_control')).find(e => /Hide games with AI disclosure/i.test(e.textContent||'')); if (o) o.click(); });
      await sleep(2000); await smoothScroll(page, 1800, 5, 16); await sleep(1500); }},
  'search-demos-plain': {url: 'https://store.steampowered.com/search/?category1=10&sort_by=Released_DESC&ndl=1', ext: false,
    run: async page => { await sleep(2500); await smoothScroll(page, 2600, 5, 16); await sleep(1000); }},
  // S02/S05 hub random mode and charts
  'hub-random': {url: 'https://store.steampowered.com/sale/nextfest', ext: false,
    run: async page => { await sleep(4000); await smoothScroll(page, 3200, 5, 16); await sleep(1500); }},
  'hub-charts': {url: 'https://store.steampowered.com/sale/nextfest', ext: false,
    run: async page => { await sleep(3500);
      await page.evaluate(() => { const t = Array.from(document.querySelectorAll('a, div, span')).find(e => (e.textContent||'').trim() === 'CHARTS'); if (t) t.click(); });
      await sleep(3500); await smoothScroll(page, 2400, 5, 16); await sleep(1500); }},
  // S03 store page: popup then scroll to the disclosure at the bottom (app id filled at run time)
  'store-disclosure': {url: 'https://store.steampowered.com/search/?category1=10&sort_by=Released_DESC&ndl=1', ext: true, firstDisclosed: true,
    run: async page => { await sleep(3500);
      await page.evaluate(() => { const c = document.querySelector('.aiwarning_close, [class*=aiwarning] button'); if (c) c.click(); });
      await sleep(1200); const h = await page.evaluate(() => document.body.scrollHeight); await smoothScroll(page, h, 8, 12); await sleep(3000); }},
  // S04 16-tile test: open the first 16 demo tiles on the hub and detect disclosures
  'hub-16-click': {url: 'https://store.steampowered.com/sale/nextfest', ext: true, special: 'sixteen'},
  // public report / article pages
  'gdc-report': {url: 'https://gdconf.com/article/gdc-2026-state-of-the-game-industry-reveals-impact-of-layoffs-generative-ai-and-more/', ext: false,
    run: async page => { await sleep(3000); await smoothScroll(page, 3600, 6, 16); await sleep(1500); }},
  'aftermath-list': {url: 'https://aftermath.site/video-games-no-ai/', ext: false,
    run: async page => { await sleep(3000); await smoothScroll(page, 5000, 8, 16); await sleep(1500); }},
  'curator-noai': {url: 'https://store.steampowered.com/curator/45186708-No-AI/', ext: false,
    run: async page => { await sleep(3000); await smoothScroll(page, 2000, 5, 16); await sleep(1500); }},
  'itch-tag': {url: 'https://itch.io/games/tag-no-ai', ext: false,
    run: async page => { await sleep(3000); await smoothScroll(page, 2000, 5, 16); await sleep(1500); }},
  'search-needle': {url: 'https://store.steampowered.com/search/?term=needle+in+a+haystack&ndl=1', ext: false,
    run: async page => { await sleep(3000); await smoothScroll(page, 1800, 5, 16); await sleep(2000); }},
  'gdco-prices': {url: 'https://newsletter.gamediscover.co/p/are-steam-game-prices-dropping-and', ext: false,
    run: async page => { await sleep(3500); await smoothScroll(page, 3000, 6, 16); await sleep(1500); }},
  'mp1st-budgets': {url: 'https://mp1st.com/news/game-development-costs-on-steam-exceed-27-billion', ext: false,
    run: async page => { await sleep(3500); await smoothScroll(page, 2200, 6, 16); await sleep(1500); }},
  'gamemeca': {url: 'https://www.gamemeca.com/en/view.php?gid=1782071', ext: false,
    run: async page => { await sleep(3500); await smoothScroll(page, 3000, 6, 16); await sleep(1500); }},
  'kotaku-needle': {url: 'https://kotaku.com/devs-behind-needle-in-a-haystack-clone-complain-their-clone-has-been-cloned-by-vibe-coder-2000747284', ext: false,
    run: async page => { await sleep(3500); await smoothScroll(page, 3000, 6, 16); await sleep(1500); }},
  'crimson-desert': {url: 'https://store.steampowered.com/search/?term=Crimson+Desert&ndl=1', ext: true, firstResult: true,
    run: async page => { await sleep(3500);
      await page.evaluate(() => { const c = document.querySelector('.aiwarning_close, [class*=aiwarning] button'); if (c) c.click(); });
      await sleep(1000); const h = await page.evaluate(() => document.body.scrollHeight); await smoothScroll(page, h, 10, 12); await sleep(3000); }},
  'reflux-store': {url: 'https://store.steampowered.com/search/?term=Drunken+Goddess+Reflux&ndl=1', ext: false, firstResult: true,
    run: async page => { await sleep(3000); await smoothScroll(page, 1200, 5, 16); await sleep(2000); }},
  'steamdb-releases': {url: 'https://steamdb.info/stats/releases/', ext: false,
    run: async page => { await sleep(5000); await smoothScroll(page, 2000, 6, 16); await sleep(1500); }},
  'price-70': {url: process.env.PRICE_URL || 'https://store.steampowered.com/search/?sort_by=Released_DESC&maxprice=70&ndl=1&filter=topsellers', ext: false,
    run: async page => { await sleep(3000); await smoothScroll(page, 1200, 5, 16); await sleep(1500); }},
};

async function sixteen(page, meta) {
  await sleep(4000);
  const links = await page.evaluate(() => Array.from(document.querySelectorAll('a[href*="/app/"]')).map(a => a.href).filter((v, i, s) => s.indexOf(v) === i).slice(0, 16));
  meta.tiles = [];
  for (const [i, href] of links.entries()) {
    await page.goto(href, {waitUntil: 'domcontentloaded', timeout: 60000}).catch(() => {});
    await sleep(2500);
    const disclosed = await hasDisclosure(page);
    const popup = await page.evaluate(() => !!document.querySelector('[class*=aiwarning]'));
    meta.tiles.push({index: i + 1, url: href, disclosed, extensionPopup: popup, title: await page.title()});
    await sleep(1000);
  }
  meta.disclosedCount = meta.tiles.filter(t => t.disclosed).length;
}

async function main() {
  const wanted = process.argv.slice(2);
  const ids = wanted.length ? wanted : Object.keys(SHOTS);
  for (const id of ids) {
    const shot = SHOTS[id]; if (!shot) throw new Error('unknown shot ' + id);
    const args = [`--window-size=${W},${H + 100}`, '--hide-scrollbars', '--lang=ko-KR', '--force-device-scale-factor=1', '--no-first-run', '--disable-infobars'];
    if (shot.ext) args.push(`--disable-extensions-except=${EXT}`, `--load-extension=${EXT}`);
    const browser = await puppeteer.launch({headless: false, args, defaultViewport: {width: W, height: H}});
    const page = (await browser.pages())[0] || await browser.newPage();
    await page.setViewport({width: W, height: H, deviceScaleFactor: 1});
    const meta = {shot: id, url: shot.url, extension: shot.ext, startedAt: new Date().toISOString(), width: W, height: H};
    const file = path.join(OUT, id + '.webm');
    await page.goto(shot.url, {waitUntil: 'domcontentloaded', timeout: 90000});
    await settle(page);
    await dismissSteamOverlays(page);
    if (shot.firstResult || shot.firstDisclosed) {
      await sleep(2500);
      const sel = shot.firstDisclosed ? '#search_resultsRows a.search_result_row.aiwarning_hasdisclosure' : '#search_resultsRows a.search_result_row';
      let href = null;
      if (shot.firstDisclosed) {
        // Prefer a disclosed demo already observed by the 16-tile test; otherwise scroll so the extension checks rows.
        const tiles = path.join(OUT, 'hub-16-click.json');
        if (fs.existsSync(tiles)) { const t = JSON.parse(fs.readFileSync(tiles, 'utf8')).tiles || []; const d = t.find(x => x.disclosed); if (d) href = d.url; }
        if (!href) { await smoothScroll(page, 1600, 8, 10); await sleep(6000); await page.evaluate(() => window.scrollTo(0, 0)); await sleep(1500); }
      }
      for (let i = 0; i < 25 && !href; i++) {
        href = await page.evaluate(s => { const a = document.querySelector(s); if (a) return a.href; const t = Array.from(document.querySelectorAll('#search_resultsRows a.search_result_row')).find(r => /AI Generated Content Disclosure found/i.test(r.textContent || '')); return t ? t.href : null; }, sel);
        if (!href) await sleep(1000);
      }
      if (!href) throw new Error('no result for ' + id);
      meta.pickedFromSearch = href;
      await page.goto(href, {waitUntil: 'domcontentloaded', timeout: 90000});
      await settle(page);
      // age gate: pick a birth year and continue
      await page.evaluate(() => { const y = document.querySelector('#ageYear'); if (y) { y.value = '1990'; const b = document.querySelector('#view_product_page_btn'); if (b) b.click(); } }).catch(() => {});
      await settle(page);
    }
    meta.urlAfterLoad = page.url();
    const recorder = await page.screencast({path: file, fps: 60});
    try {
      if (shot.special === 'sixteen') await sixteen(page, meta); else await shot.run(page);
    } finally {
      await recorder.stop();
    }
    meta.finishedAt = new Date().toISOString();
    meta.disclosureOnPage = await hasDisclosure(page).catch(() => null);
    meta.pageTitle = await page.title();
    meta.sha256 = sha(file); meta.bytes = fs.statSync(file).size;
    fs.writeFileSync(path.join(OUT, id + '.json'), JSON.stringify(meta, null, 2) + '\n');
    console.log(id, meta.bytes, 'bytes', meta.disclosedCount !== undefined ? `disclosed ${meta.disclosedCount}/16` : '');
    await browser.close();
  }
}
main().catch(e => { console.error(e); process.exit(1); });
