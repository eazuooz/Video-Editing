// Render editable explanation ranges with Motion Canvas; retain native source
// motion in FFmpeg. Both routes use the same MC source-credit layout.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),slug='ai-game-development-human-craft';
const manifest=JSON.parse(fs.readFileSync(path.join(root,'projects',slug,'project.json'),'utf8'));
const version=manifest.revision?.id||'v1';
const project=path.join(root,'motion-canvas/src/projects',slug),out=path.join(root,manifest.revision?.workDir||`shared/output/${slug}`,'composite');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{windowsHide:true,encoding:'utf8',maxBuffer:64e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;};
const encode=['-an','-c:v','h264_nvenc','-preset','p5','-cq','17','-pix_fmt','yuv420p','-r','60','-video_track_timescale','15360','-movflags','+faststart'];
const control=()=>{const c=read(path.join(root,'shared/publishing/video-production-control.json'));if(c.selectedVideo!==slug||!c.newProductionAuthorization.fullProductionAuthorized)throw Error('Selection changed');};
const data=read(path.join(project,'scene-data.json')),actual=read(path.join(project,'actual-footage.json'));
const ids=process.argv.find(a=>a.startsWith('--scenes='))?.split('=')[1].split(',')||data.scenes.map(s=>s.id);
const fingerprintBase={sceneKitHash:hash(path.join(project,'scene-kit.tsx')),mediaHash:hash(path.join(project,'media.json'))};
const jsonHash=value=>crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');
let fingerprint;
function compatible(previous,id){
 if(JSON.stringify(previous)===JSON.stringify(fingerprint))return true;
 // Captions are burned separately. The clean-scene routes never set the
 // captions=1 query, so a proven caption-data-only correction changes no
 // pixels here. Keep the exact prior input rather than rerendering the scene.
 const captionProof=path.join(out,'../caption-data-compatibility.json');
 if(fs.existsSync(captionProof)){
  const proof=read(captionProof),before=path.join(root,proof.beforeSceneDataFile);
  if(proof.sceneKitHash===fingerprint.sceneKitHash&&fs.existsSync(before)&&hash(before)===proof.beforeSceneDataFileSha256
     &&Object.keys(fingerprint).every(k=>k==='sceneDataHash'||previous[k]===fingerprint[k])){
   const a={...read(before).scenes.find(s=>s.id===id)},b={...data.scenes.find(s=>s.id===id)};
   delete a.start;delete b.start;
   if(jsonHash(a)===previous.sceneDataHash&&jsonHash(b)===fingerprint.sceneDataHash){
    delete a.captions;delete b.captions;
    if(JSON.stringify(a)===JSON.stringify(b))return true;
   }
  }
 }
 const file=path.join(out,'../scene-kit-compatibility.json');if(!fs.existsSync(file))return false;
 const config=read(file),steps=config.steps||[{...config,beforeSourcePath:`shared/output/${slug}/composite/17/timing-v2/scene-kit.before.tsx`}];
 let currentHash=previous.sceneKitHash;
 for(const c of steps){
  if(c.oldKitSha256!==currentHash)continue;
  if(id===c.onlyAffectedScene)return false;
  const before=path.join(root,c.beforeSourcePath);if(!fs.existsSync(before)||hash(before)!==c.oldKitSha256)return false;
  const old=fs.readFileSync(before,'utf8');if(old.split(c.oldExpression).length!==2)return false;
  const changed=old.replace(c.oldExpression,c.newExpression);
  if(crypto.createHash('sha256').update(changed).digest('hex')!==c.newKitSha256)return false;
  currentHash=c.newKitSha256;
 }
 if(currentHash!==fingerprint.sceneKitHash)return false;
 return Object.keys(fingerprint).every(k=>k==='sceneKitHash'||previous[k]===fingerprint[k]);
}
async function main(){
 control();if(data.timingStatus!=='measured-narration'||data.captionTimingStatus!=='asr-aligned')throw Error('Unmeasured timeline');
 const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required'],protocolTimeout:180000});
 const page=await browser.newPage();page.on('pageerror',e=>console.error(e));
 try{for(const id of ids){
  control();const s=data.scenes.find(s=>s.id===id),frames=Math.round(s.duration*60),dir=path.join(out,id);fs.mkdirSync(dir,{recursive:true});
  // Each project renders a scene-local clock. Absolute assembly start does
  // not affect its pixels; local paragraphs/captions/cuts and duration do.
  const localScene={...s};delete localScene.start;
  fingerprint={...fingerprintBase,sceneDataHash:jsonHash(localScene),actualFootageHash:jsonHash(actual.cuts.filter(c=>c.scene===id)),scope:'scene-local-v2'};
  const movie=path.join(root,`shared/output/motion-canvas/ai-craft-scene-${id}-${version}.mp4`),receipt=path.join(dir,'render.json');
  if(fs.existsSync(movie)){const r=read(receipt);if(!compatible(r.fingerprint,id)||r.encoded.sha256!==hash(movie))throw Error('Changed existing scene '+id);console.log('Reuse '+id);continue;}
  const cuts=actual.cuts.filter(c=>c.scene===id).sort((a,b)=>a.startFrame-b.startFrame),parts=[];let cursor=0;
  for(const cut of cuts){if(cut.startFrame>cursor)parts.push({kind:'explanation',start:cursor,end:cut.startFrame});parts.push({kind:'actual',start:cut.startFrame,end:cut.endFrame,cut});cursor=cut.endFrame;}
  if(cursor<frames)parts.push({kind:'explanation',start:cursor,end:frames});
  const outputs=[];
  for(const [i,part] of parts.entries()){
   const name=`ai-craft-part-${id}-${String(i).padStart(2,'0')}-${version}`,count=part.end-part.start;
   const target=path.join(root,'shared/output/motion-canvas',name+'.mp4'),record=path.join(dir,name+'.json');
   const inputs={fingerprint,part};
   if(fs.existsSync(target)){if(!fs.existsSync(record)||JSON.stringify(read(record).inputs)!==JSON.stringify(inputs)||read(record).sha256!==hash(target))throw Error('Incomplete/changed part '+name);outputs.push(target);continue;}
   if(part.kind==='actual'){
    await page.goto(`http://127.0.0.1:9199/ai-production.html?scene=${id}&actualOverlay=1`,{waitUntil:'domcontentloaded'});
    await page.waitForFunction(()=>window.sampleReview?.ready,{timeout:60000});
    const f=Math.floor((part.start+part.end)/2);await page.evaluate(f=>sampleReview.player.requestSeek(f),f);await page.waitForFunction(f=>sampleReview.rendered===f,{timeout:60000},f);
    const png=await page.evaluate(()=>sampleReview.stage.finalBuffer.toDataURL('image/png'));const overlay=path.join(dir,`credit-${part.cut.id}.png`);fs.writeFileSync(overlay,Buffer.from(png.split(',')[1],'base64'));
    run('ffmpeg',['-v','error','-n','-i',path.join(root,part.cut.path),'-i',overlay,'-filter_complex','[0:v][1:v]overlay=0:0:format=auto,format=yuv420p','-frames:v',String(count),...encode,target]);
   }else{
    await page.goto('http://127.0.0.1:9199/render-worker.html?skipActual=1',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof renderVideo==='function');
    await page.evaluate(c=>{renderVideo(c).catch(e=>window.renderFailure=String(e.stack||e));},{route:`/src/projects/${slug}/scenes/${id}/project.ts`,name,firstFrame:part.start,frames:count,fps:60,width:1920,height:1080,exactFrameRange:true});
    let last=-1,changed=Date.now(),logged=0;
    while(true){await new Promise(r=>setTimeout(r,1000));const st=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));if(st.failure||st.errors.length)throw Error(JSON.stringify(st));if(st.frame!==last){last=st.frame;changed=Date.now();}if(Date.now()-logged>20000){console.log(`${name} ${last}/${part.end}`);logged=Date.now();}if(st.done){if(st.result!==0)throw Error('Exporter failed');break;}if(Date.now()-changed>180000)throw Error('Render stalled');}
   }
   const v=readProbe(target);if(+v.nb_frames!==count)throw Error(`Frame mismatch ${name} ${v.nb_frames}/${count}`);
   fs.writeFileSync(record,JSON.stringify({inputs,frames:count,sha256:hash(target)},null,2));outputs.push(target);console.log(`Completed ${name} ${count}f`);
  }
  const list=path.join(dir,'parts.ffconcat');fs.writeFileSync(list,'ffconcat version 1.0\n'+outputs.map(p=>`file '${p.replaceAll('\\','/')}'`).join('\n')+'\n');
  run('ffmpeg',['-v','error','-n','-f','concat','-safe','0','-i',list,'-frames:v',String(frames),...encode,movie]);
  const v=readProbe(movie);if(+v.nb_frames!==frames||v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1')throw Error('Scene integrity');
  run('ffmpeg',['-v','error','-i',movie,'-f','null','-']);
  fs.writeFileSync(receipt,JSON.stringify({scene:id,frames,fingerprint,parts,timingStatus:data.timingStatus,visualReview:'pending-final-encoded-motion/caption-review',encoded:{path:path.relative(root,movie).replaceAll('\\','/'),frames,sha256:hash(movie),decode:'pass'}},null,2)+'\n');console.log(`SCENE ${id} COMPLETE`);
 }}finally{await browser.close();}
}
function readProbe(p){return JSON.parse(run('ffprobe',['-v','error','-show_streams','-of','json',p])).streams.find(s=>s.codec_type==='video');}
main().catch(e=>{console.error(e);process.exitCode=1;});
