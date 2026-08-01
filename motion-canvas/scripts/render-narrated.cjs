// Drives the actual browser-based render of the "narrated" project end to
// end, so a full render doesn't require manually opening the editor and
// clicking through the UI every time.
//
// Why this exists: Motion Canvas has no official headless/CLI renderer --
// the "Video (FFmpeg)" export only runs from inside a real page connected to
// the Vite dev server over its HMR websocket. This script drives that same
// page with a real (non-headless) Chromium so it gets GPU-accelerated canvas
// rendering -- headless mode falls back to software rendering (swiftshader),
// which measured at under 1 frame/sec here (~12 days for this video) vs.
// ~30+ frames/sec headed.
//
// Usage:
//   1. In one terminal: npm start  (or: npx vite --port 9100)
//   2. In another:       node scripts/render-narrated.cjs [port]

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const port = process.argv[2] || '9100';
const URL = `http://localhost:${port}/src/narrated`;
const OUTPUT = path.resolve(__dirname, '../../shared/output/motion-canvas/jump-physics-narrated.mp4');
const STABLE_CHECKS_REQUIRED = 6; // 6 x 5s = 30s of no growth before declaring done
const POLL_MS = 5000;
const TIMEOUT_MS = 30 * 60 * 1000;

async function main() {
  console.log(`checking dev server at ${URL} ...`);
  try {
    await fetch(`http://localhost:${port}/`);
  } catch {
    console.error(`No dev server on port ${port}. Start it first: npx vite --port ${port}`);
    process.exit(1);
  }

  if (fs.existsSync(OUTPUT)) {
    console.log(`Removing stale output: ${OUTPUT}`);
    fs.unlinkSync(OUTPUT);
  }

  console.log('launching headed chromium (for GPU-accelerated canvas rendering)...');
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--window-size=1600,1000'],
  });
  const page = await browser.newPage();
  await page.setViewport({width: 1600, height: 1000});
  page.on('pageerror', err => console.log('[pageerror]', err.message));

  await page.goto(URL, {waitUntil: 'networkidle0', timeout: 60000});

  console.log('waiting for the Render button...');
  let found = false;
  for (let i = 0; i < 20 && !found; i++) {
    found = await page.evaluate(() =>
      Array.from(document.querySelectorAll('button')).some(b =>
        (b.textContent || '').toUpperCase().includes('RENDER'),
      ),
    );
    if (!found) await new Promise(r => setTimeout(r, 1000));
  }
  if (!found) {
    console.error('Render button never appeared -- is the narrated project loaded correctly?');
    await page.screenshot({path: 'scripts/render-fail.png'});
    await browser.close();
    process.exit(1);
  }

  console.log('clicking Render...');
  await page.evaluate(() => {
    const btn = Array.from(document.querySelectorAll('button')).find(b =>
      (b.textContent || '').toUpperCase().includes('RENDER'),
    );
    btn.click();
  });

  const startedAt = Date.now();
  let stableChecks = 0;
  let lastSize = -1;

  while (true) {
    await new Promise(r => setTimeout(r, POLL_MS));
    const elapsed = Math.round((Date.now() - startedAt) / 1000);
    const size = fs.existsSync(OUTPUT) ? fs.statSync(OUTPUT).size : -1;

    if (size > 0 && size === lastSize) {
      stableChecks++;
    } else {
      stableChecks = 0;
    }
    lastSize = size;

    console.log(`[${elapsed}s] size=${size} stable=${stableChecks}/${STABLE_CHECKS_REQUIRED}`);

    if (stableChecks >= STABLE_CHECKS_REQUIRED) {
      console.log(`DONE: ${OUTPUT} (${size} bytes) after ${elapsed}s`);
      break;
    }
    if (Date.now() - startedAt > TIMEOUT_MS) {
      console.error(`TIMEOUT after ${TIMEOUT_MS / 1000}s`);
      await page.screenshot({path: 'scripts/render-timeout.png'});
      break;
    }
  }

  await browser.close();
}

main().catch(e => {
  console.error('FATAL', e);
  process.exit(1);
});
