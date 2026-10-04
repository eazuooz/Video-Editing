// One approved-voice synthesis/CPU-ASR pipeline. Other users' jobs are observed only.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawn, spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const base = 'projects/hierarchical-game-outlines/production/';
const statePath = path.join(root, base, 'resource-runner.json');
const queuePath = path.join(root, 'production/batches/sakurai-planning-game-design/queue.json');
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(path.join(root, p))).digest('hex');
const gate = read(base + 'script-source-review.json');
const inputs = [...gate.inputs, {path: base + 'script-source-review.json', sha256: hash(base + 'script-source-review.json')}];
const stamp = () => new Date().toISOString();
function writeJson(filename, value) {
  const temporary = `${filename}.${process.pid}.tmp`;
  for (let attempt = 0; attempt < 5; attempt++) {
    try {
      fs.writeFileSync(temporary, JSON.stringify(value, null, 2) + '\n');
      fs.renameSync(temporary, filename);
      return;
    } catch (error) {
      if (attempt === 4) throw error;
      Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 100);
    }
  }
}
if (fs.existsSync(statePath)) {
  const previous = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  if (previous.pid && previous.pid !== process.pid) {
    let alive = false;
    try { process.kill(previous.pid, 0); alive = true; } catch (error) { if (error.code !== 'ESRCH') throw error; }
    if (alive) throw new Error(`Runner PID ${previous.pid} is alive; reuse it.`);
  }
  if (previous.status === 'tts-asr-ready-for-direct-review') throw new Error('Results already exist. Review them instead of starting another run.');
}
fs.mkdirSync(path.join(root, base, 'logs'), {recursive: true});
const state = {
  pid: process.pid, startedAt: stamp(), status: 'initializing', inputs,
  minimumFreeMiB: 9000, maximumUtilizationPercent: 35,
  stableSamplesRequired: 3, checkIntervalSeconds: 30, children: [],
  logs: {runner: base + 'logs/resource-runner.log', tts: base + 'logs/initial-tts.log', asr: base + 'logs/initial-cpu-asr.log'},
  speechAutomaticallyApproved: false, humanListening: 'pending',
};
function save(status, extra = {}) {
  Object.assign(state, {status, updatedAt: stamp()}, extra);
  writeJson(statePath, state);
  const queue = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
  const item = queue.items.find(x => x.slug === 'hierarchical-game-outlines');
  if (!item || item.status !== 'in-progress') throw new Error('Queue no longer assigns this item to an active production task.');
  item.stage = status; item.updatedAt = state.updatedAt;
  const old = item.execution || {};
  item.execution = {...old, status, updatedAt: state.updatedAt,
    runner: base + 'resource-runner.cjs', state: base + 'resource-runner.json',
    pid: process.pid, logs: state.logs, children: state.children,
    activeTasks: state.children.filter(x => x.status === 'running'),
    noTts: !state.children.some(x => x.kind === 'tts'),
    ttsStarted: state.children.some(x => x.kind === 'tts'),
    ttsComplete: state.children.some(x => x.kind === 'tts' && x.status === 'finished'),
    toolSessionId: state.toolSessionId || old.toolSessionId || null,
  };
  item.nextAction = status === 'tts-asr-ready-for-direct-review'
    ? 'Directly compare all12 current-hash ASR scenes with60 KO/EN paragraphs and endings. Repair only rejected speech, then measure60:40, encode/review actual cuts, author12 MC scenes, mix and both SRTs, render/QA/collect captioned private delivery and per-video Git.'
    : status.startsWith('waiting')
    ? 'Reuse the single live resource-runner; it observes GPU/training without stopping other jobs. No duplicate synthesis. Actual cuts/timing/captions and final media remain pending.'
    : 'Read this runner state and actual child/logs; no automatic speech approval or final media completion implied.';
  queue.updatedAt = state.updatedAt;
  writeJson(queuePath, queue);
}
function verify() {
  for (const input of inputs) if (hash(input.path) !== input.sha256) throw new Error('Reviewed input changed: ' + input.path);
}
function observation() {
  const gpu = spawnSync('nvidia-smi', ['--query-gpu=memory.total,memory.used,utilization.gpu', '--format=csv,noheader,nounits'], {encoding: 'utf8', windowsHide: true});
  if (gpu.status !== 0) throw new Error(gpu.stderr || 'GPU observation failed');
  const [total, used, utilization] = gpu.stdout.trim().split('\n')[0].split(',').map(Number);
  if (![total, used, utilization].every(Number.isFinite)) throw new Error('Invalid GPU observation');
  const snapshot = spawnSync('powershell', ['-NoProfile', '-Command', "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"], {encoding: 'utf8', windowsHide: true});
  if (snapshot.status !== 0) throw new Error(snapshot.stderr || 'Process observation failed');
  const parsed = snapshot.stdout.trim() ? JSON.parse(snapshot.stdout) : [];
  const rows = Array.isArray(parsed) ? parsed : [parsed];
  return {at: stamp(), totalMiB: total, usedMiB: used, freeMiB: total - used,
    utilizationPercent: utilization,
    competingSynthesisPids: rows.filter(x => /render_narration\.py|generate_sample\.py/.test(x.CommandLine || '')).map(x => x.ProcessId),
    observedPythonPids: rows.map(x => x.ProcessId), action: 'Observe only. Never stop unrelated jobs.'};
}
async function waitForGpu() {
  let stable = 0;
  while (stable < state.stableSamplesRequired) {
    verify();
    const measured = observation();
    stable = measured.freeMiB >= state.minimumFreeMiB && measured.utilizationPercent <= state.maximumUtilizationPercent && !measured.competingSynthesisPids.length ? stable + 1 : 0;
    save('waiting-for-free-gpu', {gpuObservation: measured, stableSamples: stable});
    if (stable < state.stableSamplesRequired) await new Promise(resolve => setTimeout(resolve, state.checkIntervalSeconds * 1000));
  }
}
function child(kind, args, log) {
  return new Promise((resolve, reject) => {
    verify();
    const stream = fs.createWriteStream(path.join(root, log), {flags: 'a'});
    const worker = spawn(path.join(root, 'qwen3-tts/.venv/Scripts/python.exe'), ['-u', ...args], {
      cwd: root, windowsHide: true,
      env: {...process.env, PYTHONIOENCODING: 'utf-8', OMP_NUM_THREADS: '2', MKL_NUM_THREADS: '2'},
    });
    const record = {kind, pid: worker.pid, args, log, startedAt: stamp(), status: 'running'};
    state.children.push(record); save(kind + '-running');
    worker.stdout.pipe(stream, {end: false}); worker.stderr.pipe(stream, {end: false});
    worker.on('error', error => {stream.end(); reject(error);});
    worker.on('exit', code => {
      stream.end(); Object.assign(record, {status: code === 0 ? 'finished' : 'failed', exitCode: code, finishedAt: stamp()});
      save(kind + '-finished');
      code === 0 ? resolve() : reject(new Error(`${kind} exited ${code}; inspect ${log}`));
    });
  });
}
(async () => {
  verify();
  const plan = read('projects/hierarchical-game-outlines/planning/action-map.json');
  if (!gate.currentPlanApproved || !gate.sourceObservationReady || gate.actualSelfCreatedGameFootage !== false) throw new Error('Source/editorial gate is incomplete');
  for (const cut of plan.chapters.flatMap(x => x.cuts)) {
    if (!cut.sourceId || cut.take || cut.classification !== 'actual-existing-game-action' || cut.loop || cut.speed !== 1) throw new Error('Nonconforming gameplay bank');
  }
  const preflight = spawnSync(process.execPath, ['scripts/review-video-duplicates.cjs', 'hierarchical-game-outlines', '--check'], {cwd: root, encoding: 'utf8', windowsHide: true});
  if (preflight.status !== 0) throw new Error(preflight.stdout + preflight.stderr);
  console.log(`Hierarchical-game-outlines runner PID ${process.pid}; source-first bilingual script locked, approved voice, no render approval.`);
  save('waiting-for-free-gpu'); await waitForGpu();
  await child('tts', ['qwen3-tts/render_narration.py', '--project', 'hierarchical-game-outlines', '--device', 'cuda:0'], state.logs.tts);
  await child('cpu-asr', ['qwen3-tts/review_project_narration.py', '--project', 'hierarchical-game-outlines', '--device', 'cpu'], state.logs.asr);
  save('tts-asr-ready-for-direct-review', {finishedAt: stamp(), speechAutomaticallyApproved: false});
  console.log('All12 current-hash ASR scenes ready for direct review; do not infer speech or final-video approval.');
})().catch(error => {
  try {save('failed', {failure: String(error), finishedAt: stamp()});} catch (saveError) {console.error(saveError);}
  console.error(error); process.exitCode = 1;
});
