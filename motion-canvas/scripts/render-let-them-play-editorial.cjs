const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),qa=path.join(root,'shared/output/let-them-play/editorial-sample-qa');
const name='let-them-play-EDITORIAL-25D-SAMPLE-picture',picture=path.join(root,'shared/output/motion-canvas',name+'.mp4');
const output=path.join(root,'shared/output/motion-canvas/let-them-play-EDITORIAL-25D-SAMPLE.mp4');
const onlyQa=process.argv.includes('--qa-only');
function run(tool,args){const r=spawnSync(tool,args,{encoding:'utf8',windowsHide:true,maxBuffer:24*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stdout;}
async function main(){
 fs.mkdirSync(qa,{recursive:true});
 if(!process.argv.includes('--mux-only')){
 const browser=await puppeteer.launch({headless:true,protocolTimeout:120000});const errors=[];
 try{
  const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:9100/let-them-play-editorial.html',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.editorialReview?.ready,{timeout:60000});
  await page.evaluate(()=>document.fonts.ready);
  const frames=await page.evaluate(()=>editorialReview.player.playback.duration);if(frames!==2382)throw Error('Runtime frames: '+frames);
  for(const sec of [1,6,13,18,19.7,21,27,34,39.5]){
   await page.evaluate(t=>editorialReview.jump(t),sec);await page.waitForFunction(f=>editorialReview.rendered===f,{timeout:30000},Math.round(sec*60));
   const data=await page.evaluate(()=>editorialReview.stage.finalBuffer.toDataURL('image/png').split(',')[1]);fs.writeFileSync(path.join(qa,'t-'+sec+'.png'),Buffer.from(data,'base64'));
  }
  await page.evaluate(()=>editorialReview.jump(1));await page.click('#play');
  await page.waitForFunction(()=>editorialReview.player.audio.audioElement.currentTime>2,{timeout:15000});
  const audio=await page.evaluate(()=>{const a=editorialReview.player.audio.audioElement;editorialReview.player.togglePlayback(false);return {currentTime:a.currentTime,duration:a.duration,muted:a.muted,volume:a.volume,paused:a.paused,readyState:a.readyState,src:a.currentSrc}});
  if(audio.muted||audio.volume<=0||audio.readyState<2||Math.abs(audio.duration-39.7)>.03)throw Error('Audio playback failed '+JSON.stringify(audio));
  if(errors.length)throw Error(errors.join('\n'));
  fs.writeFileSync(path.join(qa,'live-review.json'),JSON.stringify({frames,audio,errors,visuallyReviewed:false},null,2));
  if(onlyQa){console.log(JSON.stringify({qa,frames,audio}));return;}
  await page.goto('http://localhost:9100/render-worker.html',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof window.renderVideo==='function');
  await page.evaluate(config=>{window.renderVideo(config).catch(e=>window.renderFailure=String(e.stack??e))},{route:'/src/projects/let-them-play/editorial-sample/project.ts',name,frames:2382,fps:60,width:1920,height:1080});
  const start=Date.now();let state;
  while(true){
   await new Promise(r=>setTimeout(r,2000));state=await page.evaluate(()=>({...window.renderJob,failure:window.renderFailure}));
   if(state.failure||state.errors?.length||errors.length)throw Error(JSON.stringify({state,errors}));
   console.log(state.frame+'/2382');if(state.done)break;if(Date.now()-start>300000)throw Error('Render timeout');
  }
  if(state.result!==0)throw Error('Render failed '+JSON.stringify(state));
 }catch(e){for(const p of await browser.pages())await p.evaluate(()=>window.cancelRender?.()).catch(()=>{});throw e;}finally{await browser.close()}
 }
 const sample=path.join(root,'motion-canvas/src/projects/let-them-play/editorial-sample/assets/sample-mix.wav');
 run('ffmpeg',['-y','-v','error','-i',picture,'-i',sample,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','39.7','-movflags','+faststart',output]);
 const info=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',output]));const v=info.streams.find(s=>s.codec_type==='video'),a=info.streams.find(s=>s.codec_type==='audio');
 if(v.width!==1920||v.height!==1080||Number(v.nb_frames)!==2382||Math.abs(Number(info.format.duration)-39.7)>.025||!a)throw Error('Wrong output properties');
 run('ffmpeg',['-v','error','-i',output,'-f','null','-']);
 for(const sec of [13,34])run('ffmpeg',['-y','-v','error','-ss',String(sec),'-i',output,'-frames:v','1',path.join(qa,'final-'+sec+'.png')]);
 const report={output,picture,qa,width:1920,height:1080,fps:60,frames:2382,duration:39.7,audio:'existing Korean narration gain x1.1 + approved Discovery',fullDecodePassed:true,fullVisualReplaced:false,sampleApproval:'pending'};
 fs.writeFileSync(path.join(qa,'render-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1});
