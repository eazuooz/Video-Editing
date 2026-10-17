// Inspect actual speech-aligned captions on the planned deepest diagram state.
// One-frame samples are layout evidence, not full moving-output approval.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const puppeteer=require('../../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../../..'),local=path.join(root,'projects/making-game-sequels/production/local/reference-preserving-v2');
const plan=JSON.parse(fs.readFileSync(path.join(__dirname,'edit-plan.json'),'utf8'));
const layout=JSON.parse(fs.readFileSync(path.join(local,'edit/caption-layout.json'),'utf8'));
if(plan.timing!=='measured-and-asr-aligned')throw Error('Current aligned narration is required');
const control=JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-production-control.json'),'utf8'));
if(control.selectedVideo!=='making-game-sequels')throw Error('Selected video changed');
const out=path.join(local,'preflight-current-captions');fs.mkdirSync(out,{recursive:true});
const picks=[];
for(const c of plan.cuts.filter(x=>x.kind==='explanation')){
 const cues=layout.rows.filter(q=>(q.start+q.end)*30>=c.startFrame&&(q.start+q.end)*30<c.endFrame);
 if(!cues.length)throw Error('No current caption in '+c.id);
 const deepest=cues.at(-1),widest=cues.reduce((a,b)=>a.width>=b.width?a:b);
 for(const q of [deepest,...(widest.cue===deepest.cue?[]:[widest])]){
  const globalFrame=Math.round((q.start+q.end)*30);
  picks.push({cut:c.id,visual:c.visual,cue:q.cue,text:q.text,globalFrame,mcFrame:c.mcStartFrame+globalFrame-c.startFrame});
 }
}
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});try{
 const page=await browser.newPage();await page.goto('http://127.0.0.1:9231/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
 for(const p of picks){
  const name='sequel-caption-preflight-'+p.cut+'-'+p.cue;
  await page.evaluate(options=>renderVideo(options),{route:'/src/projects/making-game-sequels/revision-v2/production-project.ts',name,frames:1,firstFrame:p.mcFrame,fps:60,width:1920,height:1080,exactFrameRange:true});
  const r=await page.evaluate(()=>renderJob);if(!r.done||r.result!==0||r.errors.length)throw Error(JSON.stringify(r));
  const vf=`setpts=PTS+${p.globalFrame/60}/TB,ass=projects/making-game-sequels/production/local/reference-preserving-v2/edit/captions.ko.ass,setpts=PTS-STARTPTS`;
  p.file=path.join(out,name+'.png');
  cp.execFileSync('ffmpeg',['-v','error','-y','-i',path.join(root,'shared/output/motion-canvas',name+'.mp4'),'-vf',vf,'-frames:v','1',p.file],{cwd:root});
  console.log(p.cut+' cue'+p.cue);
 }
 fs.writeFileSync(path.join(out,'index.json'),JSON.stringify({status:'pending-direct-layout-review',scope:'current caption text at exact planned times; moving output not approved',samples:picks},null,2)+'\n');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
