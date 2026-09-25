// Render the shared membership thank-you outro on its own for review (silent picture).
// Start the Vite dev server first, then: node scripts/render-membership-outro.cjs [port]
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const puppeteer = require('puppeteer');

const port = process.argv[2] || '9100';
const root = path.resolve(__dirname, '../..');
const fps = 60, width = 1920, height = 1080, seconds = 10, frames = seconds * fps;
const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+Z$/, 'Z');
const name = `membership-outro-preview-${stamp}`;
const output = path.join(root, 'shared/output/motion-canvas', `${name}.mp4`);
const route = '/src/shared/membership/preview/project.ts';

async function main() {
  const base = `http://localhost:${port}`;
  if (!(await fetch(`${base}/render-worker.html`)).ok) throw Error('Start the Vite dev server first');
  const browser = await puppeteer.launch({headless: true, protocolTimeout: 120000});
  const page = await browser.newPage();
  const pageErrors = [];
  page.on('pageerror', e => pageErrors.push(e.message));
  try {
    await page.goto(`${base}/render-worker.html`, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForFunction(() => typeof window.renderVideo === 'function');
    await page.evaluate(config => {
      window.renderVideo(config).catch(error => window.renderFailure = String(error.stack ?? error));
    }, {route, name, frames, fps, width, height});
    const started = Date.now();
    while (true) {
      await new Promise(resolve => setTimeout(resolve, 2000));
      const state = await page.evaluate(() => ({...window.renderJob, failure: window.renderFailure}));
      if (state.failure || pageErrors.length || state.errors?.length) throw Error(JSON.stringify({state, pageErrors}));
      console.log(`frame ${state.frame}/${frames}`);
      if (state.done) {
        if (state.result !== 0) throw Error(`Renderer result=${state.result}`);
        break;
      }
      if (Date.now() - started > 600000) throw Error('Render timed out');
    }
  } finally {
    await browser.close();
  }
  const probe = spawnSync('ffprobe', ['-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
    'stream=width,height,nb_read_frames', '-of', 'json', output], {encoding: 'utf8'});
  const video = JSON.parse(probe.stdout).streams[0];
  if (Number(video.nb_read_frames) !== frames || video.width !== width || video.height !== height) {
    throw Error(`Unexpected render: ${JSON.stringify(video)}`);
  }
  console.log(`DONE: ${path.relative(root, output)} (${frames} frames)`);
}

main().catch(error => { console.error(error); process.exitCode = 1; });
