// Sequential official-source acquisition and CPU decoding. No synthesis or GPU job.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawn, spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '../../../../../');
const base = path.relative(root, __dirname).replaceAll('\\', '/');
const request = JSON.parse(fs.readFileSync(path.join(__dirname, 'request.json'), 'utf8'));
const statePath = path.join(__dirname, 'acquisition.json');
const queuePath = path.join(root, 'production/batches/sakurai-planning-game-design/queue.json');
const media = path.join(root, request.localMediaDirectory);
const stamp = () => new Date().toISOString();
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
async function hashMedia(p) {
  const digest = crypto.createHash('sha256');
  for await (const chunk of fs.createReadStream(p)) digest.update(chunk);
  return digest.digest('hex');
}
function writeJson(p, v) {
  const t = p + '.' + process.pid + '.tmp';
  for (let attempt = 0; attempt < 5; attempt++) {
    try { fs.writeFileSync(t, JSON.stringify(v, null, 2) + '\n'); fs.renameSync(t, p); return; }
    catch (e) { if (attempt === 4) throw e; Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 150); }
  }
}
let previousAttempts = [];
let priorCompletedDecodes = [];
if (fs.existsSync(statePath)) {
  const old = JSON.parse(fs.readFileSync(statePath, 'utf8'));
  if (old.status === 'acquired-decoded-awaiting-direct-action-review') throw Error('Sources already acquired; review them instead.');
  if (old.pid) { let alive = false; try { process.kill(old.pid, 0); alive = true; } catch(e) { if(e.code !== 'ESRCH') throw e; } if(alive) throw Error('Reuse active acquisition PID ' + old.pid); }
  const archive = path.join(__dirname, 'acquisition-attempt-' + old.pid + '.json');
  if (!fs.existsSync(archive)) writeJson(archive, old);
  previousAttempts = [...(old.previousAttempts || []), {pid:old.pid,status:old.status,record:path.relative(root,archive).replaceAll('\\','/')}];
  priorCompletedDecodes = (old.children || []).filter(c => c.kind === 'full-decode' && c.status === 'finished' && c.exitCode === 0).map(c => ({...c, evidenceRecord:path.relative(root,archive).replaceAll('\\','/')}));
}
fs.mkdirSync(media, {recursive: true});
fs.mkdirSync(path.join(__dirname, 'logs'), {recursive: true});
const state = {pid: process.pid, startedAt: stamp(), requestSha256: hash(path.join(__dirname, 'request.json')), status: 'initializing', previousAttempts, children: [], results: [], gpuJobs: 0, narrationCreated: false, actualCutApproval: false};
function save(status) {
  state.status = status; state.updatedAt = stamp(); writeJson(statePath, state);
  const q = JSON.parse(fs.readFileSync(queuePath, 'utf8'));
  const i = q.items.find(x => x.slug === request.slug);
  if (!i || i.videoId) throw Error('Queue assignment no longer matches unproduced subject.');
  i.stage = 'existing-game-source-' + status;
  i.execution = {...i.execution, phase: 'official-existing-game-source-research', status, updatedAt: state.updatedAt, pid: process.pid, state: base + '/acquisition.json', runner: base + '/acquire-official-sources.cjs', children: state.children, activeTasks: state.children.filter(x => x.status === 'running'), noTts: true, noNewProject: !fs.existsSync(path.join(root,'projects',request.slug))};
  i.nextAction = 'Review full decoded official sources and meaningful action intervals/crops before writing independent KO/EN narration. Candidate runtime is not a final60:40 measurement.';
  q.updatedAt = state.updatedAt; writeJson(queuePath, q);
}
async function run(kind, exe, args, source) {
  const log = base + '/logs/' + source.videoId + '-' + kind + '.log';
  const fd = fs.openSync(path.join(root,log),'a');
  const child = spawn(exe,args,{cwd:root,windowsHide:true,stdio:['ignore',fd,fd]});
  const c = {kind, videoId:source.videoId,pid:child.pid,startedAt:stamp(),status:'running',log};
  state.children.push(c); save(kind + '-running');
  console.log(JSON.stringify(c));
  try { await new Promise((resolve,reject) => { child.once('error',reject); child.once('exit',code=>{c.exitCode=code;c.endedAt=stamp();c.status=code===0?'finished':'failed';code===0?resolve():reject(Error(kind+' exit '+code));}); }); }
  finally { fs.closeSync(fd); }
  c.status='finished';c.endedAt=stamp();c.exitCode=0;save(kind+'-finished');
}
(async()=>{
  for (const s of request.sources) {
    const target = path.join(media,s.videoId+'.mp4');
    const info = path.join(media,s.videoId+'.info.json');
    if (!fs.existsSync(target) || !fs.existsSync(info)) await run('download',request.python,['-m','yt_dlp','--no-playlist','--write-info-json','--no-write-thumbnail','--http-chunk-size','1M','--retries','20','--socket-timeout','30','--js-runtimes','node:'+request.node,'--ffmpeg-location',request.ffmpegDirectory,'-f','bv*[height<=1080][vcodec^=avc]+ba[ext=m4a]/b[height<=1080][ext=mp4]/bv*[height<=1080]+ba','--merge-output-format','mp4','-o',path.join(media,'%(id)s.%(ext)s'),s.url],s);
    const m = JSON.parse(fs.readFileSync(info,'utf8'));
    if (m.id!==s.videoId || !s.expectedChannels.includes(m.channel)) throw Error('Official-source owner mismatch: '+s.videoId+' '+m.channel);
    const probe = spawnSync(request.ffprobe,['-v','error','-show_format','-show_streams','-of','json',target],{encoding:'utf8',windowsHide:true});
    if (probe.status!==0) throw Error(probe.stderr || 'Probe failed');
    const data = JSON.parse(probe.stdout);
    const prior = priorCompletedDecodes.find(c => c.videoId === s.videoId && fs.statSync(target).mtimeMs <= Date.parse(c.startedAt) && fs.statSync(info).mtimeMs <= Date.parse(c.startedAt));
    if (prior) {
      state.children.push({...prior, reusedCompletedDecode:true});
      save('full-decode-finished');
    } else {
      await run('full-decode',request.ffmpeg,['-hide_banner','-v','error','-threads','2','-i',target,'-map','0:v:0','-an','-f','null','-'],s);
    }
    const logText=fs.readFileSync(path.join(__dirname,'logs',s.videoId+'-full-decode.log'),'utf8');
    if (logText.trim()) throw Error('Decode emitted diagnostics; inspect before using '+s.videoId);
    state.results.push({videoId:s.videoId,title:m.title,channel:m.channel,channelId:m.channel_id,uploadDate:m.upload_date,webpageUrl:m.webpage_url,localMediaPath:request.localMediaDirectory+'/'+s.videoId+'.mp4',fileBytes:fs.statSync(target).size,fileSha256:await hashMedia(target),format:data.format,streams:data.streams.map(x=>({codec_type:x.codec_type,codec_name:x.codec_name,width:x.width,height:x.height,r_frame_rate:x.r_frame_rate,duration:x.duration,nb_frames:x.nb_frames})),fullDecode:{exitCode:0,diagnostics:0,log:base+'/logs/'+s.videoId+'-full-decode.log',reusedCompletedDecode:!!prior,evidenceRecord:prior?.evidenceRecord},sourceAudioForFinal:'exclude-presenter-and-source-music',directActionReview:'pending',finalPublicRights:'pending'});
    save('source-acquired-decoded');
  }
  save('acquired-decoded-awaiting-direct-action-review');console.log(state.status);
})().catch(e=>{state.error=String(e.stack||e);try{save('failed');}catch(w){console.error(w);}console.error(e);process.exitCode=1;});
