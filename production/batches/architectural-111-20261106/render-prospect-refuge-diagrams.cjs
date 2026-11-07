/* Exact06.02 silent crop worker. Called only by run-prospect-refuge-diagrams.py under its
 * singleton/lease. This module is inert when imported by CPU contract tests. */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawn, spawnSync} = require('node:child_process');
const {pathToFileURL} = require('node:url');
const ROOT = path.resolve(__dirname, '../../..');
const MOTION = path.join(ROOT, 'motion-canvas');
const MEDIA = 'C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-06-02';
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const save = (p, value) => {const t = `${p}.${process.pid}.tmp`; fs.writeFileSync(t, JSON.stringify(value, null, 2) + '\n'); fs.renameSync(t, p);};
const under = (p, root) => {const rel = path.relative(path.resolve(root), path.resolve(p)); return !!rel && !rel.startsWith('..') && !path.isAbsolute(rel);};

function validateJob(job, jobPath, allowExisting = false) {
  if (job.schemaVersion !== '06-02-mc-render-job-v1' || job.topicId !== '06.02'
    || !['p04', 'p25'].includes(job.segment)) throw Error('Wrong scoped crop job');
  const c = job.contract;
  if (!c || c.width !== 1080 || c.height !== 900 || c.fps !== 60 || c.audio !== false
    || c.alpha !== false || !Number.isInteger(c.frames) || c.frames < 6) throw Error('Exact opaque silent1080x900/60 crop required');
  if (!under(job.attempt, path.join(MEDIA, 'mc-render-attempts'))
    || path.resolve(jobPath) !== path.join(path.resolve(job.attempt), 'job.json')) throw Error('Job path outside owned immutable attempt');
  if (!/^[a-f0-9]{64}$/.test(job.fingerprint)) throw Error('Fingerprint required');
  if (path.resolve(job.output) !== path.join(path.resolve(job.attempt), `${job.segment}.silent.mp4`)) throw Error('Unsafe output');
  if (!allowExisting && fs.existsSync(job.output)) throw Error('Preserve existing output; never delete stale output');
  for (const pin of job.inputPins) if (!/^[a-f0-9]{64}$/.test(pin.sha256) || sha(pin.path) !== pin.sha256) throw Error(`Input changed: ${pin.path}`);
  if (job.variables.segment !== job.segment || job.variables.timingMode !== 'authored-cue-frames'
    || job.variables.segmentFrames !== c.frames) throw Error('Actual authored frame binding missing');
  const map = job.variables.phaseFrameMap;
  if (!Array.isArray(map) || map.length < 4 || map[0].frame !== 0 || map[0].phase !== 0 || map.at(-1).frame !== c.frames - 1 || map.at(-1).phase !== 1
    || map.some((p, i) => !Number.isInteger(p.frame) || !Number.isFinite(p.phase) || p.phase < 0 || p.phase > 1
      || i > 0 && (p.frame <= map[i - 1].frame || p.phase <= map[i - 1].phase))) throw Error('Invalid authored phase map');
  if (JSON.stringify(job.stagedSources.map(s => s.name)) !== JSON.stringify(['project.ts', 'refuge-relationships.tsx'])
    || job.stagedSources.some(s => path.resolve(s.path) !== path.join(MOTION, 'src/projects/shorts-leveldesign-06-02', s.name))
    || path.resolve(job.font.path) !== path.resolve('C:/Windows/Fonts/NotoSansKR-VF.ttf')) throw Error('Only exact owned source/font may be staged');
  const pinnedPaths = new Set(job.inputPins.map(p => path.resolve(p.path)));
  if ([...job.stagedSources.map(s => s.path), job.font.path].some(p => !pinnedPaths.has(path.resolve(p)))) throw Error('Mandatory staged source/font pins missing');
  return job;
}


function leaseMatches(job, record) {
  const x = job.lifecycle;
  return x && typeof x.token === 'string' && x.token.length > 0 && Number.isInteger(x.parent?.pid)
    && Number.isFinite(x.parent.createTime) && x.parent.createTime > 0
    && x.protocol === 'architectural111-06-02-mc-crop-v1' && x.owner === 'architectural-111-06-02-mc-crop'
    && record.protocol === x.protocol && record.owner === x.owner && record.token === x.token
    && record.pid === x.parent.pid && record.createTime === x.parent.createTime
    && record.fingerprint === job.fingerprint
    && path.resolve(record.output) === path.resolve(job.attempt);
}
function verifyLease(job) {
  if (!job.lifecycle || path.resolve(job.lifecycle.leasePath) !== path.join(ROOT, 'shared/output/GPU_HANDOFF.json')) throw Error('Exact shared owned lease required');
  const record = JSON.parse(fs.readFileSync(job.lifecycle.leasePath, 'utf8'));
  if (!leaseMatches(job, record)) throw Error('Owned renderer lease/parent identity changed');
  try {process.kill(record.pid, 0);} catch {throw Error('Owned renderer coordinator is not live');}
}

function pngDimensions(data) {
  const b = Buffer.isBuffer(data) ? data : Buffer.from(data.split(',')[1], 'base64');
  if (b.length < 24 || b.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a'
    || b.subarray(12, 16).toString() !== 'IHDR') throw Error('PNG payload required');
  return {buffer: b, width: b.readUInt32BE(16), height: b.readUInt32BE(20)};
}

function workerPage(job) {
  // Public Renderer/Exporter API plus pinned local bootstrap. No editor UI,
  // default settings plugin, FFmpeg server plugin or ~/.motion-canvas writes.
  const vars = JSON.stringify(job.variables).replaceAll('<', '\\u003c');
  const settings = JSON.stringify(job.contract);
  return `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:'Noto Sans KR';src:url('/NotoSansKR-VF.ttf');font-style:normal;font-weight:100 900}body{margin:0;background:#000}
</style></head><body><script type="module">
import config from './project.ts';
import {Renderer, Vector2, MetaFile, MetaField, bootstrap} from '@motion-canvas/core';
const contract=${settings};
class OwnedExporter {
 static id='yamyam/06-02-owned-png'; static displayName='06.02 finite silent crop';
 static async create(){return new OwnedExporter()}; static meta(){return new MetaField('options',{})};
 async handleFrame(canvas,frame,sceneFrame,sceneName,signal){
  if(signal.aborted)throw Error('Owned render aborted');
  await window.__ownedFrame(canvas.toDataURL('image/png'),frame,sceneFrame,sceneName);
 }
 async stop(result){window.__ownedResult=result;}
}
const versions=${JSON.stringify(job.versions)};
const project=bootstrap('06-02-owned-'+${JSON.stringify(job.segment)},versions,
 [{name:'yamyam-06-02-owned-exporter',exporters:()=>[OwnedExporter]}],
 {...config,audio:undefined,variables:${vars}},new MetaFile('owned-project',false),new MetaFile('owned-settings',false));
project.meta.shared.size.set(new Vector2(1080,900));
project.meta.shared.background.set('#000000');
project.meta.shared.range.set([0,contract.frames/60]);
project.meta.shared.audioOffset.set(0);
project.meta.rendering.fps.set(60); project.meta.rendering.resolutionScale.set(1);
project.meta.rendering.exporter.set({name:OwnedExporter.id,options:{}});
project.logger.onLogged.subscribe(e=>{if(e.level==='error')window.__ownedErrors.push(String(e.message));});
window.__ownedErrors=[];window.__ownedResult=null;
await document.fonts.load('700 46px "Noto Sans KR"');await document.fonts.ready;
window.__ownedReady=true;
window.__ownedRun=async()=>{
 const renderer=new Renderer(project); window.__ownedAbort=()=>renderer.abort();
 renderer.onFinished.subscribe(r=>window.__ownedResult=r);
 // Renderer includes both endpoints; quarter-frame inset defeats ceil round-up.
 const range=[0,(contract.frames-1.25)/60];
 const actual={...project.meta.getFullRenderingSettings(),name:'owned06-02',range,
  fps:60,size:new Vector2(1080,900),resolutionScale:1,colorSpace:'srgb',background:'#000000',
  exporter:{name:OwnedExporter.id,options:{}}};
 window.__ownedActualSettings={...actual,size:{x:actual.size.x,y:actual.size.y}};
 await renderer.render(actual);
 if(window.__ownedResult!==0 || window.__ownedErrors.length)throw Error(JSON.stringify({result:window.__ownedResult,errors:window.__ownedErrors}));
 return {settings:window.__ownedActualSettings,projectMeta:project.meta.serialize(),result:window.__ownedResult};
};
</script></body></html>`;
}

function run(command, args, maxBuffer = 32e6) {
  const p = spawnSync(command, args, {encoding: 'utf8', windowsHide: true, maxBuffer});
  if (p.status !== 0) throw Error(p.stderr || String(p.error || `${command} exited${p.status}`));
  return p.stdout;
}

async function main(jobPath, expectedJobSHA) {
  if (!jobPath) throw Error('Pass exact owned job.json; no default render');
  if (!/^[a-f0-9]{64}$/.test(expectedJobSHA || '') || sha(jobPath) !== expectedJobSHA) throw Error('Exact parent-pinned job bytes required');
  const job = validateJob(JSON.parse(fs.readFileSync(jobPath, 'utf8')), jobPath);
  verifyLease(job);
  const attempt = path.resolve(job.attempt), staged = path.join(attempt, 'staged');
  fs.mkdirSync(staged); // exclusive fresh attempt; no rm/rmdir or overwrite.
  for (const source of job.stagedSources) fs.copyFileSync(source.path, path.join(staged, source.name), fs.constants.COPYFILE_EXCL);
  fs.copyFileSync(job.font.path, path.join(staged, 'NotoSansKR-VF.ttf'), fs.constants.COPYFILE_EXCL);
  fs.writeFileSync(path.join(staged, 'worker.html'), workerPage(job), {flag: 'wx'});
  const {createServer} = await import(pathToFileURL(path.join(MOTION, 'node_modules/vite/dist/node/index.js')).href);
  const {metaPlugin} = require(path.join(MOTION, 'node_modules/@motion-canvas/vite-plugin/lib/partials/meta.js'));
  const {scenesPlugin} = require(path.join(MOTION, 'node_modules/@motion-canvas/vite-plugin/lib/partials/scenes.js'));
  const {webglPlugin} = require(path.join(MOTION, 'node_modules/@motion-canvas/vite-plugin/lib/partials/webgl.js'));
  const puppeteer = require(path.join(MOTION, 'node_modules/puppeteer'));
  let server, browser, encoder, encoderClosed = false, encoderDone;
  let frames = 0, actual, error = null;
  const framePins = [], diagnostics = [];
  try {
    server = await createServer({configFile: false, root: staged, cacheDir: path.join(attempt, 'vite-cache'),
      plugins: [metaPlugin(), scenesPlugin(), webglPlugin()],
      esbuild: {jsx: 'automatic', jsxImportSource: '@motion-canvas/2d/lib'},
      resolve: {alias: ['core', '2d'].map(k => ({find: `@motion-canvas/${k}`, replacement: path.join(MOTION, `node_modules/@motion-canvas/${k}`)}))},
      optimizeDeps: {entries: [path.join(staged, 'project.ts')], exclude: ['preact', 'preact/*', '@preact/signals']},
      server: {host: '127.0.0.1', port: 0, strictPort: true, fs: {allow: [staged, path.join(MOTION, 'node_modules')]}},
    });
    await server.listen();
    const address = server.httpServer.address();
    browser = await puppeteer.launch({headless: true, userDataDir: path.join(attempt, 'chromium-profile'),
      protocolTimeout: 45 * 60 * 1000,
      args: ['--disable-gpu', '--use-gl=angle', '--use-angle=swiftshader', '--disable-background-networking', '--no-first-run', '--no-default-browser-check']});
    save(path.join(attempt, 'owned-child-details.json'), {nodePid: process.pid, browserPid: browser.process()?.pid, attempt});
    const page = await browser.newPage();
    await page.setRequestInterception(true);
    page.on('request', req => {const u = new URL(req.url()); if (u.hostname === '127.0.0.1' || ['data:', 'blob:'].includes(u.protocol)) req.continue(); else req.abort();});
    page.on('pageerror', e => diagnostics.push(String(e.message)));
    const sampleFrames = new Set([0, job.contract.frames - 1, ...job.cueFrames.map(c => c.frame)]);
    await page.exposeFunction('__ownedFrame', async (payload, frame, sceneFrame, sceneName) => {
      if (frame !== frames || frame >= job.contract.frames) throw Error(`Unexpected exported frame${frame}; expected${frames}`);
      const png = pngDimensions(payload);
      if (png.width !== 1080 || png.height !== 900) throw Error('Actual canvas dimensions differ');
      if (!encoder || encoderClosed) throw Error('Encoder not live');
      await new Promise((resolve, reject) => encoder.stdin.write(png.buffer, e => e ? reject(e) : resolve()));
      if (sampleFrames.has(frame)) {
        const sample = path.join(attempt, `frame-${String(frame).padStart(6, '0')}.png`);
        fs.writeFileSync(sample, png.buffer, {flag: 'wx'});
        framePins.push({frame, sceneFrame, sceneName, path: sample, sha256: sha(sample)});
      }
      frames++;
    });
    await page.goto(`http://127.0.0.1:${address.port}/worker.html`, {waitUntil: 'domcontentloaded', timeout: 90000});
    await page.waitForFunction(() => window.__ownedReady, {timeout: 60000});
    if (diagnostics.length) throw Error(diagnostics.join('\n'));
    encoder = spawn(job.ffmpeg, ['-hide_banner', '-loglevel', 'error', '-f', 'image2pipe', '-vcodec', 'png', '-framerate', '60', '-i', 'pipe:0', '-an',
      '-frames:v', String(job.contract.frames), '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-threads', '2', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-n', job.output], {windowsHide: true});
    const encodeLog = fs.createWriteStream(path.join(attempt, 'encoder.stderr.log'), {flags: 'wx'});
    encoder.stderr.pipe(encodeLog);
    encoderDone = new Promise((resolve, reject) => {encoder.once('error', reject); encoder.once('close', code => {encoderClosed = true; code === 0 ? resolve() : reject(Error(`Owned encoder exited${code}`));});});
    // Keep rejection observed even if SDK fails before it awaits encoderDone.
    encoderDone.catch(() => {});
    actual = await page.evaluate(() => window.__ownedRun());
    encoder.stdin.end(); await encoderDone;
    if (frames !== job.contract.frames || diagnostics.length) throw Error('Wrong frame count or browser diagnostic');
  } catch (e) {error = e;} finally {
    if (browser) await browser.close();
    if (server) await server.close();
    if (encoder && !encoderClosed) {
      encoder.stdin.end();
      await Promise.race([encoderDone.catch(() => {}), new Promise(r => setTimeout(r, 10000))]);
      if (!encoderClosed) {encoder.kill(); await encoderDone.catch(() => {});}
    }
  }
  if (error) {save(path.join(attempt, 'failed.json'), {complete: false, error: String(error.stack || error), frames, framePins, actual, diagnostics}); throw error;}
  validateJob(job, jobPath, true);
  if (sha(jobPath) !== expectedJobSHA) throw Error('Parent-pinned job changed during rendering');
  for (const pin of job.inputPins) if (sha(pin.path) !== pin.sha256) throw Error(`Input changed during render: ${pin.path}`);
  const probe = JSON.parse(run(job.ffprobe, ['-v', 'error', '-count_frames', '-show_streams', '-of', 'json', job.output]));
  const videos = probe.streams.filter(s => s.codec_type === 'video');
  if (videos.length !== 1 || probe.streams.some(s => s.codec_type === 'audio')) throw Error('One silent video stream required');
  const v = videos[0];
  if (v.width !== 1080 || v.height !== 900 || v.r_frame_rate !== '60/1' || Number(v.nb_read_frames) !== job.contract.frames || v.pix_fmt !== 'yuv420p') throw Error('Encoded crop differs from contract');
  run(job.ffmpeg, ['-v', 'error', '-i', job.output, '-f', 'null', '-']);
  const pts = JSON.parse(run(job.ffprobe, ['-v', 'error', '-select_streams', 'v:0', '-show_frames', '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', job.output])).frames.map(f => Number(f.best_effort_timestamp_time));
  if (pts.length !== frames || pts.some((p, i) => !Number.isFinite(p) || Math.abs(p - i / 60) > 0.000002 || i > 0 && p <= pts[i - 1])) throw Error('Encoded PTS clock differs');
  const metaFiles = fs.readdirSync(staged).filter(n => n.endsWith('.meta')).map(name => ({path: path.join(staged, name), sha256: sha(path.join(staged, name))}));
  save(path.join(attempt, 'render-manifest.json'), {schemaVersion: '06-02-mc-crop-render-v1', topicId: '06.02', segment: job.segment, fingerprint: job.fingerprint,
    complete: true, contract: job.contract, actualSdk: actual, stagedMetaFiles: metaFiles, output: {path: job.output, sha256: sha(job.output)},
    inputPins: job.inputPins, framePins, encoded: {width: v.width, height: v.height, fps: v.r_frame_rate, frames, pixFmt: v.pix_fmt, audioStreams: 0, fullDecodePassed: true, ptsStrictlyIncreasing: true},
    actualVisualReview: false, humanApproval: false, finalMovieComplete: false});
}

module.exports = {validateJob, pngDimensions, workerPage, under, leaseMatches};
if (require.main === module) main(process.argv[2], process.argv[3]).catch(e => {console.error(e.stack || e); process.exitCode = 1;});
