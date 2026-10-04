// Native source pixels plus every cut-aware actual caption. No final encoding.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn}=require('node:child_process');
const {createCanvas,loadImage,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:[path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]}));
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun Gothic');
const revision=process.argv.includes('--reviewed-v3')?'v3':process.argv.includes('--reviewed-v2')?'v2':'v1';
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1'),dest=path.join(work,'source-layout-review-'+revision);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),rel=p=>path.relative(root,p).replaceAll('\\','/'),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(fs.existsSync(path.join(dest,'index.json')))throw Error('Inspect existing review instead of rerunning.');
fs.mkdirSync(dest,{recursive:true});
const plan=read(path.join(work,'plan.json')),layout=read(path.join(work,'caption-layout-qa.json')),samples=[],processes=[];
const previous=revision==='v1'?null:read(path.join(work,`source-layout-review-${revision==='v3'?'v2':'v1'}/index.json`));
const earlier=revision==='v3'?read(path.join(work,'source-layout-review-v1/index.json')):null;
if(revision!=='v1'&&read(path.join(work,'cut-selection.json')).sourceLayoutRevision!==revision)throw Error('Current reviewed source revision required.');
for(const c of plan.cuts){for(const [role,n]of [['first',0],['middle',Math.floor(c.frames/2)],['last',c.frames-1]])samples.push({kind:'cut',id:c.id,cut:c.id,scene:c.scene,role,offsetFrame:n,time:c.timelineStart+n/60});}
for(const [i,q]of layout.cues.entries())if(q.cut){const c=plan.cuts.find(c=>c.id===q.cut),n=Math.min(c.frames-1,Math.max(0,Math.floor(((q.start+q.end)/2-c.timelineStart)*60)));samples.push({kind:'cue',id:q.cue,segment:i,cut:c.id,scene:c.scene,role:'cut-aware-midpoint',offsetFrame:n,time:c.timelineStart+n/60});}
const qpath=path.join(root,'production/batches/sakurai-planning-game-design/queue.json'),stateFile=path.join(dest,'execution.json');
function save(status,child=null){const state={pid:process.pid,status,updatedAt:new Date().toISOString(),child,processes,index:rel(path.join(dest,'index.json')),allCutsApproved:false};fs.writeFileSync(stateFile,JSON.stringify(state,null,2)+'\n');const q=read(qpath),item=q.items.find(i=>i.slug==='hierarchical-game-outlines');item.execution.sourceLayoutInspection=state;item.execution.activeTasks=status==='source-layout-preview-running'?[{kind:'cpu-native-source-caption-inspection',pid:process.pid,childPid:child?.pid??null,state:rel(stateFile)}]:[];item.execution.status=status;item.updatedAt=state.updatedAt;fs.writeFileSync(qpath,JSON.stringify(q,null,2)+'\n');}
save('source-layout-preview-running');
async function run(command,args,log,cut){await new Promise((resolve,reject)=>{const fd=fs.openSync(log,'w'),child=spawn(command,args,{cwd:root,stdio:['ignore',fd,fd],windowsHide:true});save('source-layout-preview-running',{pid:child.pid,cut:cut.id,log:rel(log),command,args});child.on('error',reject);child.on('exit',code=>{fs.closeSync(fd);processes.push({cut:cut.id,pid:child.pid,exitCode:code,log:rel(log),command:[command,...args]});if(code===0)resolve();else reject(Error('Native extraction failed '+cut.id+':'+code));});});}
(async()=>{
 for(const [ix,c]of plan.cuts.entries()){
  const group=samples.filter(s=>s.cut===c.id),points=[...new Set(group.map(s=>s.offsetFrame))].sort((a,b)=>a-b),d=path.join(dest,'native-'+c.id);fs.mkdirSync(d,{recursive:true});
  const oldNatives=points.map(n=>previous?.samples.find(s=>Math.abs(s.sourceTime-(c.sourceIn+n/60))<1e-6)??earlier?.samples.find(s=>Math.abs(s.sourceTime-(c.sourceIn+n/60))<1e-6));
  const reuse=revision!=='v1'&&oldNatives.every(s=>s&&fs.existsSync(path.join(root,s.nativeFile)));
  if(reuse){
   points.forEach((n,i)=>fs.copyFileSync(path.join(root,oldNatives[i].nativeFile),path.join(d,`frame-${String(i+1).padStart(3,'0')}.jpg`)));
   processes.push({cut:c.id,status:'exact-native-PTS-reused',sourceTimes:points.map(n=>c.sourceIn+n/60),previousIndex:`source-layout-review-${revision==='v3'?'v2':'v1'}/index.json`,previousNativeFiles:oldNatives.map(s=>s.nativeFile)});
  }else{
   const log=path.join(dest,'native-'+c.id+'.log'),vf=`select='${points.map(n=>`eq(n,${n})`).join('+')}',showinfo,crop=1376:774:0:0`;
   await run('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe',['-hide_banner','-threads','1','-ss',String(c.sourceIn),'-t',String(c.seconds),'-i',path.join(root,c.file),'-map','0:v:0','-an','-vf',vf,'-frames:v',String(points.length),'-fps_mode','vfr','-q:v','2',path.join(d,'frame-%03d.jpg')],log,c);
   const stderr=fs.readFileSync(log,'utf8'),pts=[...stderr.matchAll(/\bpts_time:([0-9.]+)/g)].map(m=>+m[1]);if(pts.length!==points.length||pts.some((p,i)=>Math.abs(p-points[i]/60)>1/60))throw Error('Native PTS mismatch '+c.id);
  }
  for(const s of group){
   const native=path.join(d,`frame-${String(points.indexOf(s.offsetFrame)+1).padStart(3,'0')}.jpg`),canvas=createCanvas(1920,1080),x=canvas.getContext('2d'),pixels=await loadImage(native);
   if(c.composition?.mode==='same-game-background-with-complete-borderless-source'){
    x.filter='blur(18px)';x.drawImage(pixels,-25,-25,1970,1130);x.filter='none';
    x.drawImage(pixels,...c.composition.foreground);
   }else{x.drawImage(pixels,0,0,1920,1080);}
   // Top-left strip ends above the observed control logo; constructor header stays clear.
   const label='Two Point Museum · 공식 시연 / 추가 콘텐츠 미리보기 (2026)';x.font='22px Malgun Gothic';x.textBaseline='top';const w=x.measureText(label).width;x.fillStyle='rgba(255,255,255,.92)';x.fillRect(12,3,w+14,33);x.fillStyle='#073c32';x.fillText(label,19,7);
   const active=s.kind==='cue'?layout.cues[s.segment]:layout.cues.find(q=>q.cut===c.id&&s.time>=q.start&&s.time<q.end);
   if(active){x.fillStyle='#073c32';x.fillRect(active.x+14,active.y+14,active.width,active.height);x.fillStyle='white';x.fillRect(active.x,active.y,active.width,active.height);x.strokeStyle='#161b18';x.lineWidth=3;x.strokeRect(active.x,active.y,active.width,active.height);x.font='48px Malgun Gothic';x.textAlign='center';x.textBaseline='middle';x.fillStyle='#080b09';active.lines.forEach((line,n)=>x.fillText(line,960,active.y+42+n*62));}
   const file=path.join(dest,`${s.kind}-${s.id}-${s.kind==='cue'?s.segment:s.role}.png`);fs.writeFileSync(file,canvas.toBuffer('image/png'));s.path=rel(file);s.nativeFile=rel(native);s.sourceTime=c.sourceIn+s.offsetFrame/60;s.caption=active?.lines??[];s.sha256=sha(file);
  }
  if(ix%7===0)console.log(`Native source/caption group ${ix+1}/${plan.cuts.length}`);
 }
 const pages=[];for(const kind of ['cut','cue']){const rows=samples.filter(s=>s.kind===kind);for(let begin=0;begin<rows.length;begin+=12){const batch=rows.slice(begin,begin+12),canvas=createCanvas(1920,Math.ceil(batch.length/3)*397),x=canvas.getContext('2d');x.fillStyle='white';x.fillRect(0,0,canvas.width,canvas.height);for(const [i,s]of batch.entries()){const l=i%3*640,t=Math.floor(i/3)*397;x.drawImage(await loadImage(path.join(root,s.path)),l,t+31,640,360);x.fillStyle='#111';x.font='19px Malgun Gothic';x.fillText(`${s.kind} ${s.id} ${s.role} · scene${s.scene}/cut${s.cut}@${s.sourceTime.toFixed(3)}`,l+5,t+23);}const f=path.join(dest,`${kind}-contact-${String(Math.floor(begin/12)+1).padStart(2,'0')}.jpg`);fs.writeFileSync(f,canvas.toBuffer('image/jpeg'));pages.push(rel(f));}}
 fs.writeFileSync(path.join(dest,'index.json'),JSON.stringify({createdAt:new Date().toISOString(),sourceBoundarySamples:plan.cuts.length*3,actualCaptionSegments:layout.cues.filter(c=>c.cut).length,samples,pages,processes,selectionSha256:sha(path.join(work,'cut-selection.json')),layoutSha256:sha(path.join(work,'caption-layout-qa.json')),nativePtsChecked:true,status:'pending-direct-action-and-every-actual-cue-pixel-review',finalVideoApproved:false},null,2)+'\n');save('source-layout-previews-ready-pending-direct-review');console.log(JSON.stringify({views:samples.length,pages:pages.length,approval:false}));
})().catch(e=>{save('source-layout-inspection-failed');console.error(e);process.exitCode=1;});
