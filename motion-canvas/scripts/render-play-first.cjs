// Render play-first (clean master or boxed Korean caption version) through the headless worker,
// then mux the current mix (final-mix when BGM is approved, otherwise the no-BGM review mix).
// Start the dev server first. Usage: node scripts/render-play-first.cjs [clean|captioned] [port]
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const puppeteer = require('puppeteer');

const [variant = 'clean', port = '9100'] = process.argv.slice(2);
if (!['clean', 'captioned'].includes(variant)) throw Error('variant must be clean or captioned');
const root = path.resolve(__dirname, '../..');
const board = JSON.parse(fs.readFileSync(path.join(root, 'motion-canvas/src/projects/play-first/storyboard.generated.json'), 'utf8'));
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'projects/play-first/project.json'), 'utf8'));
const final = manifest.audio.backgroundMusic.approvalStatus === 'approved';
const mix = path.join(root, 'motion-canvas/src/projects/play-first/assets', final ? 'final-mix.m4a' : 'review-mix-nobgm.m4a');
if (!fs.existsSync(mix)) throw Error(`Mix not found: ${mix}`);
const fps = 60, width = 1920, height = 1080;
const frames = Math.round(board.totalSeconds * fps), duration = frames / fps;
const route = variant === 'clean' ? '/src/projects/play-first/project.ts' : '/src/projects/play-first/captioned.ts';
const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+Z$/, 'Z');
const tag = final ? '' : '-review-nobgm';
const base = `play-first${variant === 'captioned' ? '-subtitled' : ''}${tag}-${stamp}`;
const outDir = path.join(root, 'shared/output/motion-canvas');
const visual = path.join(outDir, `${base}-visual.mp4`);
const output = path.join(outDir, `${base}.mp4`);

const execute = (cmd, args) => {
  const r = spawnSync(cmd, args, {cwd: root, encoding: 'utf8', windowsHide: true, maxBuffer: 16 * 1024 * 1024});
  if (r.status !== 0) throw Error(`${cmd}: ${(r.stderr || '').slice(-2000)}`);
  return r.stdout;
};

async function main() {
  const host = `http://localhost:${port}`;
  if (!(await fetch(`${host}/render-worker.html`)).ok) throw Error('Start the Vite dev server first');
  const browser = await puppeteer.launch({headless: true, protocolTimeout: 180000, args: ['--autoplay-policy=no-user-gesture-required']});
  const page = await browser.newPage();
  const pageErrors = [];
  page.on('pageerror', e => pageErrors.push(e.message));
  const started = Date.now();
  let lastFrame = -1, lastProgress = started;
  try {
    await page.goto(`${host}/render-worker.html`, {waitUntil: 'domcontentloaded', timeout: 60000});
    await page.waitForFunction(() => typeof window.renderVideo === 'function');
    await page.evaluate(config => {
      window.renderVideo(config).catch(error => window.renderFailure = String(error.stack ?? error));
    }, {route, name: `${base}-visual`, frames, fps, width, height});
    console.log(`Rendering ${base}: ${frames} frames`);
    while (true) {
      await new Promise(resolve => setTimeout(resolve, 10000));
      const state = await page.evaluate(() => ({...window.renderJob, failure: window.renderFailure}));
      if (state.failure || pageErrors.length || state.errors?.length) throw Error(JSON.stringify({state, pageErrors}));
      if (state.frame !== lastFrame) { lastFrame = state.frame; lastProgress = Date.now(); }
      console.log(`frame ${state.frame}/${frames} (${Math.round((Date.now() - started) / 1000)}s)`);
      if (state.done) { if (state.result !== 0) throw Error(`Renderer result=${state.result}`); break; }
      if (Date.now() - lastProgress > 300000) throw Error('Render stalled');
    }
  } finally {
    await browser.close();
  }
  execute('ffmpeg', ['-hide_banner', '-v', 'warning', '-n', '-i', visual, '-i', mix, '-map', '0:v:0', '-map', '1:a:0',
    '-c:v', 'copy', '-c:a', 'copy', '-t', String(duration), '-movflags', '+faststart', output]);
  const info = JSON.parse(execute('ffprobe', ['-v', 'error', '-count_frames', '-show_entries',
    'stream=codec_type,nb_read_frames,width,height:format=duration', '-of', 'json', output]));
  const video = info.streams.find(s => s.codec_type === 'video');
  if (Number(video.nb_read_frames) !== frames || !info.streams.some(s => s.codec_type === 'audio')) {
    throw Error(`Unexpected output: ${JSON.stringify(info)}`);
  }
  execute('ffmpeg', ['-hide_banner', '-v', 'error', '-i', output, '-f', 'null', '-']);
  fs.writeFileSync(output.replace(/\.mp4$/, '.json'), JSON.stringify({
    createdAt: new Date().toISOString(), variant, publishReady: false,
    kind: final ? 'final render (human listening pending)' : 'review render without BGM (music choice pending)',
    output: path.relative(root, output).replaceAll('\\', '/'), frames, fps, duration, mix: path.relative(root, mix).replaceAll('\\', '/'),
    renderSeconds: (Date.now() - started) / 1000, fullDecodePassed: true,
  }, null, 2) + '\n');
  console.log(`DONE: ${path.relative(root, output)}`);
}

main().catch(error => { console.error(error); process.exitCode = 1; });
