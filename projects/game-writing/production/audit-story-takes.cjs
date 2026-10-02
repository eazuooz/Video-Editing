// Validate newly captured local gameplay without changing its source clock.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const capture=read(path.join(__dirname,'capture-story-takes.json'));
const work=path.join(__dirname,'story-take-review');fs.mkdirSync(work,{recursive:true});
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const previous=fs.existsSync(path.join(__dirname,'story-take-audit.json'))?read(path.join(__dirname,'story-take-audit.json')):null;
const report={pid:process.pid,startedAt:new Date().toISOString(),status:'running',captureReport:'projects/game-writing/production/capture-story-takes.json',takes:previous?.takes||[],directVisualReview:'pending'};
const save=()=>fs.writeFileSync(path.join(__dirname,'story-take-audit.json'),JSON.stringify(report,null,2)+'\n');
function run(args){const r=spawnSync('ffmpeg',args,{encoding:'utf8',windowsHide:true,maxBuffer:2e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r;}
try{save();for(const t of capture.takes.filter(t=>t.status==='finished')){
 const source=path.join(root,t.path);if(hash(source)!==t.sha256)throw Error('Captured take changed: '+t.id);
 const existing=report.takes.find(v=>v.id===t.id&&v.sha256===t.sha256&&v.fullDecode.exitCode===0);
 if(existing){for(const s of existing.samples)if(hash(path.join(root,s.path))!==s.sha256)throw Error('Saved native sample changed');console.log('Preserved completed take audit '+t.id);continue;}
 const decode=run(['-v','error','-xerror','-threads','2','-i',source,'-map','0:v','-f','null','-']);
 const samples=[{name:'first',seconds:Math.min(2,t.seconds/4)},{name:'middle',seconds:t.seconds/2},{name:'last',seconds:t.seconds-.5}];
 for(const a of t.actions.filter(a=>['share-rule','give-companion','rest-companion','recover-seal','feed','detour','confirm-known-rule','present-seal','enter-harbor'].includes(a.action)))samples.push({name:a.action,seconds:Math.min(t.seconds-.3,a.resultSeconds+Math.min(1,a.holdSeconds/2)),action:a.action,line:a.line});
 const files=[];for(const [i,s]of samples.entries()){
 const f=path.join(work,`${t.id}-${String(i).padStart(2,'0')}-${s.name}.png`);
 run(['-v','error','-y','-threads','2','-ss',String(s.seconds),'-i',source,'-frames:v','1',f]);
 files.push({...s,path:path.relative(root,f).replaceAll('\\','/'),sha256:hash(f)});
 }
 report.takes.push({id:t.id,path:t.path,sha256:t.sha256,seconds:t.seconds,fullDecode:{exitCode:decode.status,stderr:decode.stderr},samples:files,sourceClock:t.sourceTimestampAudit,directVisualReview:'pending'});save();console.log(t.id+' decoded and '+files.length+' native samples saved.');
 }report.status='decoded-sampled-awaiting-direct-review';report.finishedAt=new Date().toISOString();save();
}catch(e){report.status='failed';report.error=String(e);save();throw e;}
