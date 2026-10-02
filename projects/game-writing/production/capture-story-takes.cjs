// Own local artifact only. Real UI inputs and wall-clock screen recording; no source looping/speed change.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process'),{pathToFileURL}=require('node:url');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),asset='shared/assets/game-writing/story-takes-v1';
const statePath=path.join(__dirname,'capture-story-takes.json'),logDir=path.join(root,asset);
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const inputs=['projects/game-writing/playtest/index.html','projects/game-writing/playtest/story-state.cjs'].map(p=>({path:p,sha256:hash(p)}));
const step=(action,hold)=>({action,hold});
const takes=[
 {id:'guard-first',scene:'01',focus:'Guard before board; later read, explicitly share and return',actions:[step('start-skip',1),step('close',.25),step('talk-guard',6),step('ask-seal',6),step('close',.3),step('read-note',7),step('close',.3),step('talk-guard',5),step('share-rule',5),step('close',.3),step('talk-guard',7)],last:'guard.rule-shared'},
 {id:'note-first',scene:'03',focus:'Reading is not sharing; direct knowledge transfer and repeat conversation',actions:[step('start-skip',.8),step('close',.2),step('read-note',7),step('close',.3),step('talk-guard',7),step('share-rule',6),step('close',.3),step('talk-guard',7),step('close',.3),step('read-note',6),step('close',.3),step('talk-guard',7)],last:'guard.rule-shared'},
 {id:'owner-chain',scene:'05',focus:'Visible seal transfers, companion absence, rejected access and recovery',actions:[step('start-skip',.8),step('close',.2),step('take-seal',5),step('close',.3),step('give-companion',6),step('close',.3),step('talk-guard',6),step('close',.3),step('rest-companion',5),step('close',.3),step('talk-guard',7),step('ask-seal',7),step('close',.3),step('recover-seal',6),step('close',.3),step('talk-guard',7)],last:'guard.first'},
 ...['feed','detour'].map(route=>({id:'route-'+route,scene:'07',focus:'Fresh '+route+' input, actual movement/resource result and matching guard dialogue',route,actions:[step('start-skip',.8),step('close',.2),step('road',7),step(route,7),step('close',.3),step('take-seal',4),step('close',.3),step('talk-guard',7),step('present-seal',5),step('enter-harbor',7)],last:'harbor.arrived'})),
 {id:'skip-essential',scene:'09',focus:'Skipped exposition recovered by guard and board, then actual progression',actions:[step('start-skip',2),step('close',.3),step('talk-guard',6),step('ask-rule',7),step('close',.3),step('read-note',7),step('close',.3),step('take-seal',5),step('close',.3),step('talk-guard',5),step('present-seal',4),step('enter-harbor',5)],last:'harbor.arrived'},
 {id:'read-essential',scene:'09',focus:'Read exposition, short confirmation, seal acquisition and progression',actions:[step('start-read',7),step('close',.3),step('talk-guard',6),step('confirm-known-rule',6),step('close',.3),step('take-seal',5),step('close',.3),step('talk-guard',5),step('present-seal',4),step('enter-harbor',6)],last:'harbor.arrived'},
 {id:'verification-standard',scene:'11',focus:'New complete board/item/drive path; every displayed reply reflects actual facts',route:'drive',actions:[step('start-skip',.8),step('close',.2),step('read-note',5),step('close',.3),step('take-seal',4),step('close',.3),step('road',5),step('drive',5),step('close',.3),step('talk-guard',6),step('share-rule',5),step('close',.3),step('talk-guard',5),step('present-seal',5),step('enter-harbor',6)],last:'harbor.arrived'},
 {id:'verification-absent',scene:'11',focus:'New adverse order and absent-owner run, recover and successfully enter',actions:[step('start-skip',.8),step('close',.2),step('take-seal',4),step('close',.3),step('give-companion',5),step('close',.3),step('rest-companion',5),step('close',.3),step('talk-guard',7),step('ask-seal',6),step('close',.3),step('recover-seal',5),step('close',.3),step('talk-guard',6),step('present-seal',5),step('enter-harbor',6)],last:'harbor.arrived'}
];
// Additional narrated observations use fresh takes, not repeated earlier source ranges.
takes.push(
 {id:'observe-question-memory',scene:'13',focus:'Ask an unknown rule, then return and observe the remembered conversation',actions:[step('start-skip',.5),step('close',.2),step('talk-guard',3),step('ask-rule',5),step('close',.2),step('talk-guard',6)],last:'guard.rule-shared'},
 {id:'observe-companion-return',scene:'14',focus:'Owner remains companion; physical return restores the available reply',actions:[step('start-skip',.5),step('close',.2),step('take-seal',1),step('close',.2),step('give-companion',1),step('close',.2),step('rest-companion',2),step('close',.2),step('talk-guard',4),step('close',.2),step('call-companion',4),step('close',.2),step('talk-guard',6)],last:'guard.first'},
 {id:'observe-drive-result',scene:'15',focus:'Fresh third route with movement, then guard acknowledges the actual drive action',route:'drive',actions:[step('start-skip',.5),step('close',.2),step('road',3),step('drive',5),step('close',.2),step('talk-guard',6)],last:'guard.first'},
 {id:'observe-finished-event',scene:'16',focus:'Give seal, close and talk again; completed event is not requested again',actions:[step('start-skip',.5),step('close',.2),step('take-seal',1),step('close',.2),step('talk-guard',3),step('present-seal',4),step('close',.2),step('talk-guard',6),step('enter-harbor',4)],last:'harbor.arrived'}
);
takes.push(
 {id:'verify-unshared-first',scene:'03',focus:'Fresh record-first visit with knowledge still unshared',actions:[step('start-skip',.5),step('close',.2),step('read-note',8),step('close',.2),step('talk-guard',8)],last:'guard.first'},
 {id:'verify-unknown-path',scene:'11',focus:'Fresh skipped opening, guard first, fact recovery and real progress',actions:[step('start-skip',.5),step('close',.2),step('talk-guard',4),step('ask-rule',4),step('close',.2),step('take-seal',3),step('close',.2),step('talk-guard',3),step('present-seal',3),step('enter-harbor',4)],last:'harbor.arrived'},
 {id:'verify-feed-again',scene:'11',focus:'Fresh feeding run for final contrast against the standard drive route',route:'feed',actions:[step('start-skip',.5),step('close',.2),step('road',3),step('feed',4),step('close',.2),step('take-seal',2),step('close',.2),step('talk-guard',4),step('present-seal',3),step('enter-harbor',4)],last:'harbor.arrived'}
);
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const prior=fs.existsSync(statePath)?JSON.parse(fs.readFileSync(statePath,'utf8')):null;
if(prior?.pid&&prior.status==='running')try{process.kill(prior.pid,0);throw Error('An existing story capture is alive.');}catch(e){if(e.code!=='ESRCH')throw e;}
const state={pid:process.pid,startedAt:new Date().toISOString(),status:'running',inputs,sourceTimePolicy:'CDP wall-clock frame timestamps preserved; CFR30 delivery resampling only; no content replay or slow-down',softwareBrowser:true,takes:prior?.takes||[]};
function save(){state.updatedAt=new Date().toISOString();fs.writeFileSync(statePath,JSON.stringify(state,null,2)+'\n');}
async function capture(take){
 const existing=state.takes.find(t=>t.id===take.id&&t.status==='finished');
 if(existing){assert.deepEqual(existing.inputs,inputs,'Captured inputs changed; preserve old take and create a fresh version intentionally.');assert.equal(hash(existing.path),existing.sha256);console.log('Reuse verified completed take '+take.id);return;}
 const attempt=1+state.takes.filter(t=>t.id===take.id).length;
 const out=asset+'/'+take.id+'.mp4',framesDir=path.join(logDir,'frames-'+take.id+'-attempt'+attempt);
 if(fs.existsSync(path.join(root,out)))throw Error('Preserve unverified or partial existing capture '+out+'; inspect before choosing a fresh version.');
 fs.mkdirSync(framesDir,{recursive:true});fs.writeFileSync(path.join(framesDir,'.gitignore'),'*\n');
 const browser=await puppeteer.launch({headless:true,args:['--disable-gpu','--disable-accelerated-2d-canvas'],protocolTimeout:120000});
 const report={id:take.id,attempt,scene:take.scene,focus:take.focus,inputs,path:out,rawFrames:path.relative(root,framesDir).replaceAll('\\','/'),status:'recording',startedAt:new Date().toISOString(),actions:[],pageErrors:[]};state.takes.push(report);save();
 try{
 const page=await browser.newPage();await page.setViewport({width:1920,height:1080,deviceScaleFactor:1});
 page.on('pageerror',e=>report.pageErrors.push(String(e)));
 await page.goto(pathToFileURL(path.join(root,'projects/game-writing/playtest/index.html')).href);await page.evaluate(()=>document.fonts.ready);
 const cdp=await page.createCDPSession(),frames=[];let collect=true;
 cdp.on('Page.screencastFrame',e=>{
  if(collect){const name=String(frames.length).padStart(6,'0')+'.jpg';fs.writeFileSync(path.join(framesDir,name),Buffer.from(e.data,'base64'));frames.push({file:name,timestamp:e.metadata.timestamp,arrivedAt:Date.now()/1000});}
  cdp.send('Page.screencastFrameAck',{sessionId:e.sessionId}).catch(()=>{});
 });
 await cdp.send('Page.startScreencast',{format:'jpeg',quality:94,maxWidth:1920,maxHeight:1080,everyNthFrame:1});
 const started=Date.now();await delay(350);
 for(const s of take.actions){
  const selector=s.action.startsWith('start-')?'#'+s.action:`[data-action="${s.action}"]`;
  await page.waitForSelector(selector,{visible:true});
  const before=await page.evaluate(()=>harborState.events.length),triggerSeconds=(Date.now()-started)/1000;
  await page.click(selector);await page.waitForFunction(n=>harborState.events.length>n,{timeout:10000},before);
  const model=await page.evaluate(()=>harborState),event=model.events.at(-1);assert.equal(event.accepted,true,take.id+' '+s.action);
  report.actions.push({action:s.action,triggerSeconds,resultSeconds:(Date.now()-started)/1000,holdSeconds:s.hold,event,line:model.dialogue?.text||null,choices:model.dialogue?.choices||[],state:{introRead:model.introRead,noteKnown:model.noteKnown,sharedRule:model.sharedRule,sealOwner:model.sealOwner,companionPresent:model.companionPresent,route:model.route,rations:model.rations,minutes:model.minutes,gateOpen:model.gateOpen,arrived:model.arrived}});
  if(s.action==='talk-guard'&&!model.companionPresent&&model.sealOwner==='companion')assert(!model.dialogue.choices.some(c=>c[0]==='present-seal'));
  await delay(s.hold*1000);
 }
 const final=await page.evaluate(()=>harborState);assert.equal(final.lastLineId,take.last);
 if(take.route){assert.equal(final.route,take.route);assert.equal(final.rations,take.route==='feed'?0:1);assert.equal(final.minutes,take.route==='detour'?3:1);}
 await cdp.send('Page.stopScreencast');collect=false;
 assert.deepEqual(report.pageErrors,[]);assert(frames.length>100,'Screencast did not provide actual frames');
 fs.writeFileSync(path.join(framesDir,'source-frame-times.json'),JSON.stringify(frames,null,2)+'\n');
 // CDP occasionally emits an initial untimed frame or a duplicate creation timestamp.
 // Preserve all raw evidence, order by actual creation time and encode each timestamp once.
 const unique=new Map();for(const f of frames)if(Number.isFinite(f.timestamp)&&f.timestamp>0&&!unique.has(f.timestamp))unique.set(f.timestamp,f);
 const valid=[...unique.values()].sort((a,b)=>a.timestamp-b.timestamp);
 report.sourceTimestampAudit={rawFrames:frames.length,uniqueTimedFrames:valid.length,excludedUntimedOrDuplicate:frames.length-valid.length,outOfOrderOrEqual:frames.slice(1).filter((f,i)=>f.timestamp<=frames[i].timestamp).length,manifest:path.relative(root,path.join(framesDir,'source-frame-times.json')).replaceAll('\\','/'),noContentReplay:true};
 save();assert(valid.length/frames.length>.95,'Too many source frames lack unique creation times');
 const deltas=valid.slice(1).map((f,i)=>f.timestamp-valid[i].timestamp);assert(deltas.every(t=>t>0&&Number.isFinite(t)),'Invalid source frame time');
 const elapsed=valid.at(-1).timestamp-valid[0].timestamp,sorted=[...deltas].sort((a,b)=>a-b);
 assert(Math.abs(elapsed-(Date.now()-started)/1000)<1,'Source clock does not match actual recording wall time');
 const concat=['ffconcat version 1.0'];for(let i=0;i<valid.length-1;i++)concat.push(`file '${valid[i].file}'`,`duration ${deltas[i].toFixed(9)}`);concat.push(`file '${valid.at(-1).file}'`);
 fs.writeFileSync(path.join(framesDir,'capture.ffconcat'),concat.join('\n')+'\n');
 const ff=spawnSync('ffmpeg',['-v','error','-n','-threads','2','-f','concat','-safe','0','-i',path.join(framesDir,'capture.ffconcat'),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','30','-fps_mode','cfr','-video_track_timescale','90000',path.join(root,out)],{encoding:'utf8',windowsHide:true,maxBuffer:1024*1024});
 fs.writeFileSync(path.join(framesDir,'encode.log'),ff.stderr||'');if(ff.status!==0)throw Error('Capture encode failed '+ff.stderr);
 const probe=spawnSync('ffprobe',['-v','error','-show_entries','format=duration:stream=width,height,r_frame_rate','-of','json',path.join(root,out)],{encoding:'utf8',windowsHide:true});if(probe.status!==0)throw Error(probe.stderr);
 const media=JSON.parse(probe.stdout);assert(Math.abs(Number(media.format.duration)-elapsed)<.2,'Wall-clock source time was changed');
 Object.assign(report,{status:'finished',finishedAt:new Date().toISOString(),sha256:hash(out),seconds:Number(media.format.duration),wallClockFrameSeconds:elapsed,recordedFrames:frames.length,frameGapMedianSeconds:sorted[Math.floor(sorted.length*.5)],frameGapP99Seconds:sorted[Math.floor(sorted.length*.99)],frameGapMaxSeconds:Math.max(...deltas),media,finalState:{lastLineId:final.lastLineId,route:final.route,rations:final.rations,minutes:final.minutes,sealOwner:final.sealOwner,arrived:final.arrived},assertionsPassed:true,finalCutVisualApproval:false});
 save();console.log(JSON.stringify({take:take.id,seconds:report.seconds,frames:frames.length,p99:report.frameGapP99Seconds,assertionsPassed:true}));
 }catch(e){Object.assign(report,{status:'failed',failure:String(e)});save();throw e;}finally{await browser.close();}
}
(async()=>{fs.mkdirSync(logDir,{recursive:true});save();const selected=process.argv[2];const list=selected==='verification'?takes.filter(t=>t.id.startsWith('verify-')):selected==='additions'?takes.filter(t=>Number(t.scene)>12):selected?takes.filter(t=>t.id===selected):takes;assert(list.length,'Unknown take selection');for(const t of list)await capture(t);state.status=selected?'selected-take-finished':'finished';state.finishedAt=new Date().toISOString();save();console.log('New actual story inputs captured. Final cut selection and all-cue/cut visual review remain pending.');})().catch(e=>{state.status='failed';state.failure=String(e);save();console.error(e);process.exitCode=1;});
