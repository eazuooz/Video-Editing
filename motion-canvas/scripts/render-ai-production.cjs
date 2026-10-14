const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');const puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),slug='ai-game-development-human-craft';
const project=path.join(root,'motion-canvas/src/projects',slug),out=path.join(root,'shared/output',slug,'composite');fs.mkdirSync(out,{recursive:true});
const ids=(process.argv.find(a=>a.startsWith('--scenes='))||'--scenes=01').split('=')[1].split(',');
const render=process.argv.includes('--render'),captions=process.argv.includes('--captions');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:128e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;};
async function main(){
 const control=JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-production-control.json'),'utf8').replace(/^\uFEFF/,''));
 if(control.selectedVideo!==slug||!control.newProductionAuthorization.fullProductionAuthorized)throw Error('Selected production authorization changed');
 const d=JSON.parse(fs.readFileSync(path.join(project,'scene-data.json'),'utf8'));
 if(render&&d.timingStatus!=='measured-narration')throw Error('Final render requires measured narration timing.');
 if((render||captions)&&d.captionTimingStatus!=='asr-aligned')throw Error('Actual ASR-aligned captions must be prepared first.');
 const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required'],protocolTimeout:180000});
 const page=await browser.newPage();let errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{for(const id of ids){
  if(JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-production-control.json'),'utf8').replace(/^\uFEFF/,'')).selectedVideo!==slug)throw Error('Selection changed; stopped at scene boundary');
  const s=d.scenes.find(s=>s.id===id);if(!s)throw Error('Unknown scene');
  const frames=Math.round(s.duration*60),dir=path.join(out,id);fs.mkdirSync(dir,{recursive:true});
  await page.goto(`http://127.0.0.1:9199/ai-production.html?scene=${id}${captions?'&captions=1':''}`,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.sampleReview?.ready,{timeout:60000});
  const extraPath=process.argv.find(a=>a.startsWith('--extra-samples='))?.split('=')[1];
  const extra=extraPath?(JSON.parse(fs.readFileSync(path.resolve(root,extraPath),'utf8'))[id]||[]):[];
  const samples=[...new Set([0,...s.paragraphs.map(p=>Math.min(frames-1,Math.round((p.start+Math.min(1,(p.end-p.start)/2))*60))),...extra,frames-1])].filter(f=>f>=0&&f<frames).sort((a,b)=>a-b);
  for(const f of samples){
   await page.evaluate(f=>sampleReview.player.requestSeek(f),f);
   await page.waitForFunction(f=>sampleReview.rendered===f,{timeout:45000},f);
   const png=await page.evaluate(()=>sampleReview.stage.finalBuffer.toDataURL('image/png'));
   fs.writeFileSync(path.join(dir,`${captions?'caption-':''}frame-${String(f).padStart(6,'0')}.png`),Buffer.from(png.split(',')[1],'base64'));
  }
  const logged=await page.evaluate(()=>window.reviewErrors);if(errors.length||logged.length)throw Error(JSON.stringify([...errors,...logged]));
  const report={scene:id,timingStatus:d.timingStatus,frames,samples,captionPreflight:captions,visualHumanOrAgentReview:'pending',sceneDataHash:sha(path.join(project,'scene-data.json')),sceneKitHash:sha(path.join(project,'scene-kit.tsx')),mediaHash:sha(path.join(project,'media.json'))};
  fs.writeFileSync(path.join(dir,'preflight.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({scene:id,frames,samples:samples.length}));
  if(!render)continue;
  const media=JSON.parse(fs.readFileSync(path.join(project,'media.json'),'utf8'));
  if(s.mode==='unity'&&!media.unity[id]?.video)throw Error('Missing actual Unity capture '+id);
  if(s.mode==='footage'&&!media.footage[id]?.length)throw Error('Missing source footage '+id);
  const name=`ai-craft-scene-${id}-v1`,movie=path.join(root,'shared/output/motion-canvas',name+'.mp4');
  if(fs.existsSync(movie))throw Error('Existing render requires explicit hash-based reuse or a new version: '+movie);
  await page.goto('http://127.0.0.1:9199/render-worker.html',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof renderVideo==='function');
  await page.evaluate(c=>{renderVideo(c).catch(e=>window.renderFailure=String(e.stack||e));},{route:`/src/projects/${slug}/scenes/${id}/project.ts`,name,frames,fps:60,width:1920,height:1080,exactFrameRange:true});
  let last=-1,changed=Date.now(),loggedAt=0;
  while(true){await new Promise(r=>setTimeout(r,1500));const state=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));if(state.failure||state.errors.length)throw Error(JSON.stringify(state));if(state.frame!==last){last=state.frame;changed=Date.now();if(Date.now()-loggedAt>15000){console.log(`${id}: ${last}/${frames}`);loggedAt=Date.now();}}if(state.done){if(state.result!==0)throw Error('Exporter failure');break;}if(Date.now()-changed>180000)throw Error('Render stalled');}
  const probe=JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',movie]));const v=probe.streams.find(x=>x.codec_type==='video');if(+v.nb_frames!==frames||v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1')throw Error('Frame or geometry mismatch');
  run('ffmpeg',['-v','error','-i',movie,'-f','null','-']);
  report.encoded={path:path.relative(root,movie).replaceAll('\\','/'),frames,sha256:sha(movie),decode:'pass'};fs.writeFileSync(path.join(dir,'render.json'),JSON.stringify(report,null,2)+'\n');
 }}finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
