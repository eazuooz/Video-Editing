// Finite local visual renderer. Imports do not launch a server or media job.
const fs = require('node:fs'), path = require('node:path'), cp = require('node:child_process'), crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..'), batchId = 'tech-ten-shorts-20261030', revision = 'tech-ten-v1';
const python = path.join(root, 'qwen3-tts/.venv/Scripts/python.exe');
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const hash = async file => {const h = crypto.createHash('sha256');for await (const b of fs.createReadStream(file))h.update(b);return h.digest('hex');};

function guard(slug) {
  const code = 'import sys;sys.path.insert(0,sys.argv[1]);from scoped_context import make_context;c=make_context(sys.argv[2]);c["guard"]();c["assert_no_game_apps"]()';
  cp.execFileSync(python, ['-B', '-X', 'utf8', '-c', code, __dirname, slug],
    {cwd: root, stdio: 'pipe', windowsHide: true, env: {...process.env, PYTHONDONTWRITEBYTECODE: '1'}});
}

async function scope() {
  try {const result = await fetch('http://127.0.0.1:9284/__yamyam_production_scope', {signal: AbortSignal.timeout(2000)});
    if (!result.ok) throw Error('Foreign server on renderer port.'); return await result.json();
  } catch (error) {if (error.cause?.code === 'ECONNREFUSED') return undefined; throw error;}
}

async function main() {
  const [slug, name, firstArg = '0', countArg] = process.argv.slice(2);
  const batch = read(path.join(__dirname, 'batch.json'));
  if (!batch.projects.some(p => p.slug === slug)) throw Error('Select an exact current batch project.');
  if (!/^[a-z0-9][a-z0-9-]{1,160}$/.test(name || '')) throw Error('Use a unique safe render name.');
  guard(slug);
  const production = path.join(root, 'projects', slug, 'production'), local = path.join(production, 'local');
  const timing = read(path.join(production, 'visual-timing.json'));
  if (JSON.stringify(timing) !== JSON.stringify(read(path.join(local, 'visual-timing.json')))
      || timing.revision !== revision || timing.previewOnly !== false || timing.fps !== 60)
    throw Error('The current final-PCM timeline differs between renderer and mixer.');
  const firstFrame = Number(firstArg), frames = countArg === undefined ? timing.frames - firstFrame : Number(countArg);
  if (!Number.isInteger(firstFrame) || !Number.isInteger(frames) || firstFrame < 0 || frames < 1 || firstFrame + frames > timing.frames)
    throw Error('Frame range exceeds selected version.');
  const owned = 'C:/Users/1/Videos/YamyamProduction/' + batchId + '/' + slug;
  const outputRoot = owned + '/local/motion-canvas-output', output = path.join(outputRoot, name + '.mp4');
  const receipt = path.join(local, name + '-render.json');
  if (fs.existsSync(output) || fs.existsSync(receipt)) throw Error('Previous render or attempt is preserved. Version before retry.');
  let server, browser, stream;
  try {
    let current = await scope();
    if (!current) {
      fs.mkdirSync(path.join(local, 'server-logs'), {recursive: true});
      const log = path.join(local, 'server-logs', 'vite-' + new Date().toISOString().replace(/[:.]/g, '-') + '.log');
      stream = fs.openSync(log, 'wx');
      server = cp.spawn(process.execPath, ['node_modules/vite/bin/vite.js', '--config', 'src/projects/' + batchId + '/vite.config.ts'],
        {cwd: path.join(root, 'motion-canvas'), windowsHide: true, stdio: ['ignore', stream, stream], env: {...process.env, YAMYAM_TECH_TEN_SLUG: slug}});
      for (let i = 0; i < 60 && !current; i++) {if (server.exitCode !== null) throw Error('Owned Vite server failed; see ' + log); await delay(500);current = await scope();}
    }
    if (!current || current.batchId !== batchId || current.slug !== slug || current.revision !== revision || current.output !== outputRoot)
      throw Error('Port 9284 belongs to a different scope. Preserve it and stop.');
    guard(slug);
    const puppeteer = require(path.join(root, 'motion-canvas/node_modules/puppeteer'));
    browser = await puppeteer.launch({headless: true, args: ['--disable-gpu'], protocolTimeout: 900000});
    const page = await browser.newPage();
    await page.goto('http://127.0.0.1:9284/render-worker.html');
    await page.waitForFunction(() => typeof renderVideo === 'function');
    const pulse = setInterval(() => page.evaluate(() => window.renderJob?.frame).then(frame => console.log('Frame ' + frame)).catch(() => {}), 15000);
    try {await page.evaluate(args => window.renderVideo(args), {route: '/src/projects/' + batchId + '/entries/' + slug + '/project.ts', name, firstFrame, frames, fps: 60, width: 1080, height: 1920, exactFrameRange: true});}
    finally {clearInterval(pulse);}
    const result = await page.evaluate(() => window.renderJob);
    const record = {...result, batchId, slug, revision, output, firstFrame, frames, fullCurrentTimeline: firstFrame === 0 && frames === timing.frames,
      timingSha256: await hash(path.join(production, 'visual-timing.json')), configSha256: await hash(path.join(production, 'visual-config.json')),
      outputSha256: fs.existsSync(output) ? await hash(output) : null};
    fs.writeFileSync(receipt, JSON.stringify(record, null, 2) + '\n', {flag: 'wx'});
    if (!result.done || result.result !== 0 || result.errors.length || !fs.existsSync(output)) throw Error(JSON.stringify(record));
    console.log(JSON.stringify({output, receipt, frames}));
  } finally {
    if (browser) await browser.close();
    // This is exclusively the process spawned by this invocation, never an existing server.
    if (server && server.exitCode === null) {server.kill();await delay(200);}
    if (stream !== undefined) fs.closeSync(stream);
  }
}

if (require.main === module) main().catch(error => {console.error(error);process.exitCode = 1;});
