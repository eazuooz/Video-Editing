// Safe local render: headless Renderer API, unique outputs, explicit completion,
// verified frame count/audio, and no deletion or replacement of published files.
// node scripts/render-review.cjs <slug> [seconds | full] [port]
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const puppeteer = require('puppeteer');
const [slug, length = 'full', port = '9100'] = process.argv.slice(2);
if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug ?? '')) throw Error('Invalid project slug');
const root = path.resolve(__dirname, '../..');
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'projects', slug, 'project.json'), 'utf8'));
if (manifest.slug !== slug) throw Error('Manifest slug mismatch');
const motionRoot = path.join(root, 'motion-canvas');
const route = '/' + path.relative(motionRoot, path.resolve(root, manifest.paths.motionCanvasProject)).replaceAll('\\', '/');
if (!route.startsWith('/src/projects/') || route.includes('..')) throw Error('Unsafe project route');
const {fps, width, height} = manifest.video;
const seconds = length === 'full' ? manifest.video.durationSeconds : Number(length);
if (!Number.isFinite(seconds) || seconds <= 0 || seconds > manifest.video.durationSeconds) throw Error('Invalid render length');
const frames = Math.round(seconds * fps), duration = frames / fps;
const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+Z$/, 'Z');
const name = `${slug}-tts-review-${length === 'full' ? 'full' : `${seconds}s`}-${stamp}`;
const outputDir = path.join(root, 'shared/output/motion-canvas');
const visualName = `${name}-visual`;
const visual = path.join(outputDir, `${visualName}.mp4`);
const output = path.join(outputDir, `${name}.mp4`);
const audio = path.resolve(root, manifest.paths.audioMix);
const captions = [manifest.paths.captionsKo, manifest.paths.captionsEn];
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root, file))).digest('hex');
const before = Object.fromEntries([...captions, manifest.paths.audioMix].map(p => [p, hash(p)]));
if ([visual, output].some(fs.existsSync)) throw Error('Unique output already exists');
function execute(cmd, args) {
  const r = spawnSync(cmd, args, {cwd: root, encoding: 'utf8', windowsHide: true, maxBuffer: 8 * 1024 * 1024});
  if (r.status !== 0) throw Error(`${cmd}: ${r.stderr}`);
  return r.stdout;
}
const probe = file => JSON.parse(execute('ffprobe', ['-v','error','-show_streams','-show_format','-of','json',file]));
async function main() {
  const base = `http://localhost:${port}`;
  if (!(await fetch(`${base}/render-worker.html`)).ok) throw Error('Start the Vite dev server first');
  const browser = await puppeteer.launch({headless: true, protocolTimeout: 120000, args: ['--autoplay-policy=no-user-gesture-required']});
  const page = await browser.newPage();
  const pageErrors = [];
  page.on('pageerror', e => pageErrors.push(e.message));
  const started = Date.now();
  let lastFrame = -1, lastProgress = started, finalState;
  try {
    await page.goto(`${base}/render-worker.html`, {waitUntil: 'networkidle0', timeout: 60000});
    await page.waitForFunction(() => typeof window.renderVideo === 'function');
    await page.evaluate(config => {
      window.renderVideo(config).catch(error => window.renderFailure = String(error.stack ?? error));
    }, {route, name: visualName, frames, fps, width, height});
    console.log(`Rendering ${name}: ${width}x${height} ${fps}fps, ${frames} frames, audio=${audio}`);
    while (true) {
      await new Promise(resolve => setTimeout(resolve, 5000));
      const state = await page.evaluate(() => ({...window.renderJob, failure: window.renderFailure}));
      if (state.failure || pageErrors.length || state.errors?.length) throw Error(JSON.stringify({state, pageErrors}));
      if (state.frame !== lastFrame) { lastFrame = state.frame; lastProgress = Date.now(); }
      const elapsed = (Date.now() - started) / 1000;
      console.log(JSON.stringify({frame: state.frame, frames, percent: +(100 * state.frame / frames).toFixed(1), elapsed: Math.round(elapsed), renderFps: +(state.frame / elapsed).toFixed(1)}));
      if (state.done) { finalState = state; break; }
      if (Date.now() - lastProgress > 180000 || elapsed > 7200) throw Error('Render stalled/timed out');
    }
    if (finalState.result !== 0) throw Error(`Renderer result=${finalState.result}`);
  } finally {
    if (!finalState) {
      try {
        await page.evaluate(() => window.cancelRender?.());
        await page.waitForFunction(() => window.renderJob?.done || window.renderFailure, {timeout: 15000});
      } catch (_) { /* Preserve the original error; do not kill unrelated jobs. */ }
    }
    await browser.close();
  }
  const visualInfo = probe(visual), video = visualInfo.streams.find(s => s.codec_type === 'video');
  if (Number(video?.nb_frames) !== frames || video.width !== width || video.height !== height) throw Error(`Unexpected render: ${JSON.stringify(video)}`);
  execute('ffmpeg', ['-hide_banner','-v','warning','-n','-i',visual,'-i',audio,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-t',String(duration),'-movflags','+faststart',output]);
  const info = probe(output), audioStream = info.streams.find(s => s.codec_type === 'audio');
  if (!audioStream || Math.abs(Number(info.format.duration)-duration) > .08) throw Error('Audio missing or duration mismatch');
  execute('ffmpeg', ['-hide_banner','-v','error','-i',output,'-f','null','-']);
  for (const [file, expected] of Object.entries(before)) if (hash(file) !== expected) throw Error(`Input changed during render: ${file}`);
  const report = {createdAt: new Date().toISOString(),scriptRevision:manifest.scriptRevision,kind:`Narration review: ${manifest.audio.mixStatus}; not publish-ready`,publishReady:false,output:path.relative(root,output).replaceAll('\\','/'),visual:path.relative(root,visual).replaceAll('\\','/'),duration,frames,fps,width,height,renderSeconds:(Date.now()-started)/1000,audioSource:manifest.paths.audioMix,inputsSha256:before,renderer:finalState,streams:info.streams.map(({codec_type,codec_name,duration,nb_frames,sample_rate,channels,avg_frame_rate})=>({codec_type,codec_name,duration,nb_frames,sample_rate,channels,avg_frame_rate})),fullDecodePassed:true};
  fs.writeFileSync(output.replace(/\.mp4$/,'.json'),JSON.stringify(report,null,2)+'\n');
  console.log(`DONE: ${output}`);
  console.log(`Original audio and KO/EN SRT unchanged. Visual intermediate retained. Mix status: ${manifest.audio.mixStatus}; not a publish-ready final.`);
}
if (slug === 'ai-era-cs-fundamentals' && length === 'full') {
  // A long single browser session became unresponsive during the first full
  // render. Keep short samples here; full AI-CS jobs use fresh 60s workers.
  const child = spawnSync(process.execPath, [path.join(__dirname, 'resume-ai-cs-render.cjs'), 'new', port], {cwd: motionRoot, stdio: 'inherit', windowsHide: true});
  if (child.error) console.error(child.error);
  process.exitCode = child.status ?? 1;
} else {
  main().catch(error => {console.error(error); process.exitCode = 1;});
}
