/** D22 CPU-only Motion Canvas export. No service or render starts on import. */
const fs = require('node:fs');
const path = require('node:path');
const ROOT = path.resolve(__dirname, '../../../..');
const MC = path.join(ROOT, 'motion-canvas');
const LOCAL = path.join(ROOT, 'projects/similar-game-design/production/local/reference-preserving-v2');
const PHYSICAL = 'C:/Users/1/.codex/video-production/similar-game-design/reference-preserving-v2';
const PREFIX = '/src/projects/similar-game-design/revision-v2/';
const ROUTES = new Set([PREFIX + 'preflight-project.ts', PREFIX + 'production-project.ts', PREFIX + 'patch-v4-project.ts']);

async function main(argv = process.argv.slice(2)) {
  if (argv.includes('--help')) {
    console.log('node render-diagrams.cjs <similar-game-design-name> <exactFrames> [D22projectRoute] [firstFrame=0]');
    console.log('Start the isolated Vite config on127.0.0.1:9254 separately. CPU only; no service/GPU/process changes.');
    return;
  }
  const [name = 'similar-game-design-preflight-v2', count = '2160', route = PREFIX + 'preflight-project.ts', first = '0'] = argv;
  const frames = Number(count), firstFrame = Number(first);
  if (!/^similar-game-design-[a-z0-9-]+$/.test(name) || !ROUTES.has(route)) throw Error('Only exact D22 output names and its explicit isolated project routes are allowed');
  if (!Number.isSafeInteger(frames) || frames < 1 || !Number.isSafeInteger(firstFrame) || firstFrame < 0) throw Error('Positive exact frame count and nonnegative integer firstFrame required');
  const authorizationPath = path.join(__dirname, 'authorization.json');
  const approval = JSON.parse(fs.readFileSync(authorizationPath, 'utf8'));
  const control = JSON.parse(fs.readFileSync(path.join(ROOT, 'shared/publishing/video-production-control.json'), 'utf8'));
  if (approval.slug !== 'similar-game-design' || approval.revision !== 'reference-preserving-v2' || approval.fullProductionAuthorized !== true || approval.automaticNextVideo !== false) throw Error('Current exact D22 user-backed authorization required');
  if (control.automaticNextVideoEnabled !== false) throw Error('Preserve the one-video boundary');
  const routing = JSON.parse(fs.readFileSync(path.join(__dirname, 'storage-routing.json'), 'utf8'));
  const same = (a, b) => path.resolve(a).toLowerCase() === path.resolve(b).toLowerCase();
  if (!same(routing.logicalRoot, LOCAL) || !same(routing.physicalRoot, PHYSICAL) || JSON.stringify(routing.allowedOutputSubdirectories) !== JSON.stringify(['edit', 'rendered'])) throw Error('Only the exact D22 edit/rendered storage routes are authorized');
  const rendered = path.resolve(PHYSICAL, 'rendered');
  if (!same(fs.realpathSync.native(path.join(LOCAL, 'rendered')), rendered) || !same(fs.realpathSync.native(rendered), rendered)) throw Error('Root must create the exact D rendered -> C rendered junction before exporting');
  const output = path.join(rendered, name + '.mp4');
  const evidence = path.join(rendered, 'executions', name);
  const confined = target => {
    let ancestor = target;
    while (!fs.existsSync(ancestor)) {
      const parent = path.dirname(ancestor);
      if (parent === ancestor) throw Error('No existing storage ancestor');
      ancestor = parent;
    }
    const resolved = path.resolve(fs.realpathSync.native(ancestor), path.relative(ancestor, target));
    const difference = path.relative(rendered, resolved);
    if (difference.startsWith('..') || path.isAbsolute(difference)) throw Error('Nested storage path escapes exact D22 rendered root');
  };
  confined(output); confined(evidence);
  const receipt = path.join(evidence, 'execution.json');
  if (fs.existsSync(output) || fs.existsSync(receipt)) throw Error('Preserve existing output; select a new versioned render name');
  fs.mkdirSync(evidence, {recursive: true});
  const state = {name, frames, firstFrame, route, output: path.relative(ROOT, path.join(LOCAL, 'rendered', name + '.mp4')).replaceAll('\\', '/'),
    startedAt: new Date().toISOString(), status: 'running', width: 1920, height: 1080, fps: 60,
    device: 'headless Chromium CPU (--disable-gpu)', observedSharedSelection: control.selectedVideo,
    authorizationPath: path.relative(ROOT, authorizationPath).replaceAll('\\', '/'),
    foreignProcessesChanged: [], visualPixelReview: 'pending'};
  const save = () => fs.writeFileSync(receipt, JSON.stringify(state, null, 2) + '\n');
  save();
  const puppeteer = require(path.join(MC, 'node_modules/puppeteer'));
  const browser = await puppeteer.launch({headless: true,
    args: ['--disable-gpu', '--renderer-process-limit=2'], protocolTimeout: 600000});
  try {
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:9254/render-worker.html');
    await page.waitForFunction(() => typeof renderVideo === 'function');
    const pulse = setInterval(() => page.evaluate(() => window.renderJob?.frame).then(frame => {
      state.frame = frame; save(); console.log(`${frame}/${firstFrame + frames}`);
    }).catch(() => {}), 20000);
    try {
      await page.evaluate(job => window.renderVideo(job), {route, name, frames, firstFrame,
        fps: 60, width: 1920, height: 1080, exactFrameRange: true});
    } finally {clearInterval(pulse);}
    state.result = await page.evaluate(() => window.renderJob);
    if (!state.result.done || state.result.result !== 0 || state.result.errors.length || !fs.existsSync(output)) throw Error('The exact CPU render did not complete: ' + JSON.stringify(state.result));
    state.status = 'rendered-awaiting-structural-and-pixel-review'; state.completedAt = new Date().toISOString(); save();
  } catch (error) {state.status = 'failed'; state.error = String(error); save(); throw error;}
  finally {await browser.close();}
}

module.exports = {main, ROUTES};
if (require.main === module) main().catch(error => {console.error(error); process.exitCode = 1;});
