const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),dir=path.join(root,'shared/output/ai-game-development-human-craft/unity-sample');
const name='ai-human-craft-unity-sample-v1',output=path.join(root,'shared/output/motion-canvas',name+'.mp4');
const render=process.argv.includes('--render');
const samples=[0,90,210,280,310,335,337,370,430,650,659,660,770,938,966,995,997,1010,1170,1319,1320,1460,1559];
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:16e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;};
async function main(){
 const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required'],protocolTimeout:180000});
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto('http://127.0.0.1:9198/ai-unity-sample.html',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.sampleReview?.ready,{timeout:60000});
  const timeline=await page.evaluate(()=>({frames:sampleReview.player.playback.duration,scenes:sampleReview.player.playback.scenes.current.map(s=>({name:s.name,firstFrame:s.firstFrame,lastFrame:s.lastFrame}))}));
  for(const frame of samples){
   await page.evaluate(f=>sampleReview.player.requestSeek(f),frame);
   await page.waitForFunction(f=>sampleReview.rendered===f,{timeout:30000},frame);
   const data=await page.evaluate(()=>sampleReview.stage.finalBuffer.toDataURL('image/png'));
   fs.writeFileSync(path.join(dir,`composite-${String(frame).padStart(4,'0')}.png`),Buffer.from(data.split(',')[1],'base64'));
  }
  if(errors.length)throw Error(errors.join('\n'));
  const report={kind:'silent-Unity-animation-with-Motion-Canvas-composite',timeline,preflightFrames:samples,wholeVideoComplete:false,errors};
  fs.writeFileSync(path.join(dir,'composite-review.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(timeline));
  if(!render)return;
  if(fs.existsSync(output))throw Error('Preserve existing output');
  await page.goto('http://127.0.0.1:9198/render-worker.html',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof renderVideo==='function');
  await page.evaluate(c=>{renderVideo(c).catch(e=>window.renderFailure=String(e.stack||e));},{route:'/src/projects/ai-game-development-human-craft/unity-sample/project.ts',name,frames:1560,fps:60,width:1920,height:1080,exactFrameRange:true});
  let last=-1,lastChange=Date.now();
  while(true){await new Promise(r=>setTimeout(r,1500));const s=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));if(s.failure||s.errors.length)throw Error(JSON.stringify(s));if(s.frame!==last){last=s.frame;lastChange=Date.now();console.log(`frame ${last}/1560`);}if(s.done){if(s.result!==0)throw Error('Exporter failed');break;}if(Date.now()-lastChange>120000)throw Error('Render stalled');}
  const probe=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',output]));const v=probe.streams.find(s=>s.codec_type==='video');
  if(+v.nb_frames!==1560||v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1')throw Error('Unexpected output');
  run('ffmpeg',['-v','error','-i',output,'-f','null','-']);
  const pts=JSON.parse(run('ffprobe',['-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',output])).frames.map(f=>+f.best_effort_timestamp_time);
  if(pts.length!==1560||pts.some((x,i)=>i&&x<=pts[i-1]))throw Error('PTS mismatch');
  report.encoded={output,frames:pts.length,duration:+probe.format.duration,width:v.width,height:v.height,fps:v.r_frame_rate,fullDecodePassed:true,ptsStrictlyIncreasing:true,sha256:crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex')};
  fs.writeFileSync(path.join(dir,'composite-review.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report.encoded));
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
