// Research-only original captions. Never copy/translate these into a new script.
const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const root = path.resolve(__dirname, '../../../..');
const base = 'production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons';
const local = base + '/research-local';
const write = (p, v) => fs.writeFileSync(path.join(root, p), JSON.stringify(v, null, 2) + '\n');
fs.mkdirSync(path.join(root, local), {recursive: true});
const exclusion = '/' + local + '/';
const excludePath = path.join(root, '.git/info/exclude');
if (!fs.readFileSync(excludePath, 'utf8').split(/\r?\n/).includes(exclusion)) fs.appendFileSync(excludePath, '\n' + exclusion + '\n');
const state = {slug: 'avoid-game-comparisons', sourceVideoId: 'gYuvggptkDM', purpose: 'Full concept research before content/Studio duplicate decision; captions local only.', startedAt: new Date().toISOString(), pid: process.pid, gpuJobs: 0, newNarrationCreated: false, newSceneCreated: false, duplicateDecision: 'pending', browserObservations: [{tab: '33', operation: 'bind existing source research tab', result: 'DOM snapshot timeout'}, {tab: '27', operation: 'navigate stable channel-content tab to supplied original URL', result: 'command timeout; navigation not confirmed; previous saved reward proofs remain valid'}]};
const python = 'D:/Github/Video-Editing/qwen3-tts/.venv/Scripts/python.exe';
const args = ['-m', 'yt_dlp', '--no-playlist', '--skip-download', '--write-subs', '--write-auto-subs', '--sub-langs', 'en,ja', '--sub-format', 'json3', '--js-runtimes', 'node:C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe', '--retries', '2', '--socket-timeout', '20', '-o', path.join(root, local, '%(id)s.%(ext)s'), 'https://www.youtube.com/watch?v=gYuvggptkDM'];
state.command = {exe: python, args};
const fd = fs.openSync(path.join(root, local, 'acquisition.log'), 'a');
const child = cp.spawn(python, args, {cwd: root, windowsHide: true, stdio: ['ignore', fd, fd]});
state.childPid = child.pid; state.status = 'research-captions-running';
function save() {
  state.updatedAt = new Date().toISOString(); write(base + '/source-concept-acquisition.json', state);
  const qp = 'production/batches/sakurai-planning-game-design/queue.json';
  const q = JSON.parse(fs.readFileSync(path.join(root, qp), 'utf8'));
  const item = q.items.find(x => x.slug === state.slug);
  if (!item || item.videoId) throw Error('Candidate assignment changed; preserve produced files.');
  item.status = 'in-progress'; item.stage = 'preflight-full-content-Studio-review';
  item.execution = {observedAt: state.updatedAt, phase: 'pre-production-original-concept-research', pid: state.pid, childPid: state.childPid, sessionId: state.sessionId || null, status: state.status, gpuSynthesisJobs: 0, renderJobs: 0, uploads: 0, log: local + '/acquisition.log', state: base + '/source-concept-acquisition.json', activeTasks: state.status.endsWith('running') ? [{kind: 'original-concept-captions', pid: state.childPid}] : [], newNarrationCreated: false, newSceneCreated: false};
  item.nextAction = 'Read the entire source concept, all likely overlapping KO/EN scripts and current Studio matches/IDs before recording distinct and passing --check. No script/TTS/scene creation before that gate. Thumbnail follow-ups remain nonblocking.';
  q.currentSlug = state.slug; q.progress.inProgress = 1; q.progress.queued = 12; q.updatedAt = state.updatedAt; write(qp, q);
}
save(); console.log(JSON.stringify({pid: state.pid, childPid: child.pid, status: state.status, log: local + '/acquisition.log'}));
child.once('error', e => {state.error = String(e); state.status = 'research-captions-failed'; save(); fs.closeSync(fd); process.exitCode = 1;});
child.once('exit', code => {state.exitCode = code; state.status = code === 0 ? 'research-captions-acquired-awaiting-full-read' : 'research-captions-failed'; state.endedAt = new Date().toISOString(); save(); fs.closeSync(fd); console.log(JSON.stringify({status: state.status, exitCode: code})); process.exitCode = code || 0;});
