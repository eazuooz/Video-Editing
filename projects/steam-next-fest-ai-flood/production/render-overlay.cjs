// Render the transparent overlay project to a PNG sequence through the Motion
// Canvas editor (image-sequence exporter in project.meta). Starts its own Vite
// server on a private port and stops it afterwards.
// Usage: node projects/steam-next-fest-ai-flood/production/render-overlay.cjs [expectedFrames]
const {spawn} = require('child_process');
const fs = require('fs');
const path = require('path');
const R = path.resolve(__dirname, '../../..');
const MC = path.join(R, 'motion-canvas');
const puppeteer = require(path.join(MC, 'node_modules/puppeteer'));
const OUT = path.join(R, 'shared/output/motion-canvas/steam-next-fest-ai-flood-overlay');
const expected = Number(process.argv[2] || 0);
const port = 9123;
const sleep = ms => new Promise(r => setTimeout(r, ms));
function countFrames() { if (!fs.existsSync(OUT)) return 0; return fs.readdirSync(OUT).filter(f => f.endsWith('.png')).length; }
async function main() {
  if (fs.existsSync(OUT)) fs.rmSync(OUT, {recursive: true, force: true});
  const vite = spawn(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['vite', '--port', String(port), '--strictPort'], {cwd: MC, stdio: ['ignore', 'pipe', 'pipe'], shell: process.platform === 'win32'});
  vite.stdout.on('data', () => {}); vite.stderr.on('data', () => {});
  let ready = false;
  for (let i = 0; i < 240 && !ready; i++) { try { const r = await fetch(`http://localhost:${port}/`); ready = r.ok; } catch (e) {} if (!ready) await sleep(1000); }
  if (!ready) { vite.kill(); throw new Error('vite did not start'); }
  const browser = await puppeteer.launch({headless: false, args: ['--window-size=1600,1000']});
  const page = await browser.newPage(); await page.setViewport({width: 1600, height: 1000});
  page.on('pageerror', e => console.log('[pageerror]', e.message));
  await page.goto(`http://localhost:${port}/src/projects/steam-next-fest-ai-flood/project`, {waitUntil: 'domcontentloaded', timeout: 120000});
  await page.waitForFunction(() => Array.from(document.querySelectorAll('button')).some(b => (b.textContent || '').toUpperCase().includes('RENDER')), {timeout: 60000});
  await sleep(2000);
  await page.evaluate(() => { const b = Array.from(document.querySelectorAll('button')).find(x => (x.textContent || '').toUpperCase().includes('RENDER')); b.click(); });
  const started = Date.now(); let last = -1, stable = 0;
  while (true) {
    await sleep(5000); const n = countFrames(); const el = Math.round((Date.now() - started) / 1000);
    if (n !== last) { console.log(`${el}s frames=${n}`); last = n; stable = 0; } else stable++;
    if (expected && n >= expected && stable >= 2) break;
    if (!expected && n > 0 && stable >= 8) break;
    if (el > 4 * 3600) throw new Error('render timeout');
  }
  await browser.close(); vite.kill();
  console.log('done frames', countFrames(), 'at', OUT);
}
main().catch(e => { console.error(e); process.exit(1); });
