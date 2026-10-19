// Visual-only revision. Reuse the approved 277-frame intro and unchanged audio;
// render only the original 2652-frame body from its existing source-frame cache.
const fs = require('node:fs');
const path = require('node:path');
const puppeteer = require('../../../../motion-canvas/node_modules/puppeteer');
const root = path.resolve(__dirname, '../../../..');
const local = path.resolve(__dirname, '../local/credits-v3');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const selected = read(path.join(root, 'shared/publishing/video-production-control.json')).shortsRecurringAuthorization;
if (selected.selectedShort !== 'shorts-zombie-quiet-director' ||
    selected.latestSelection.selectedRevision !== 'zombie-quiet-credits-v3') {
  throw Error('Selection changed');
}
const timing = read(path.resolve(__dirname, '../visual-timing.json'));
const name = 'shorts-zombie-quiet-director-body-credits-v3';
const output = path.join(root, 'shared/output/motion-canvas', name + '.mp4');
if (fs.existsSync(output)) throw Error('Preserve completed render ' + output);
fs.mkdirSync(local, {recursive: true});
const port = Number(process.argv[2] || 9248);
(async () => {
  const browser = await puppeteer.launch({headless: true, args: ['--disable-gpu'], protocolTimeout: 900000});
  try {
    const page = await browser.newPage();
    await page.goto(`http://127.0.0.1:${port}/render-worker.html`);
    await page.waitForFunction(() => typeof renderVideo === 'function');
    const pulse = setInterval(() => page.evaluate(() => window.renderJob?.frame)
      .then(frame => console.log('Frame ' + frame + ' / ' + timing.frames)).catch(() => {}), 15000);
    try {
      await page.evaluate(args => window.renderVideo(args), {
        route: '/src/projects/shorts-zombie-quiet-director/project.ts', name,
        firstFrame: 0, frames: timing.frames, fps: 60,
        width: 1080, height: 1920, exactFrameRange: true,
      });
    } finally {
      clearInterval(pulse);
    }
    const result = await page.evaluate(() => window.renderJob);
    fs.writeFileSync(path.join(local, 'render-execution.json'), JSON.stringify(result, null, 2) + '\n');
    if (!result.done || result.result !== 0 || result.errors.length) throw Error(JSON.stringify(result));
    console.log(JSON.stringify({output, frames: timing.frames, introReusedFrames: 277}));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
