// Verify the local preview really loads and plays the full narration/source mix.
const puppeteer=require('puppeteer'),fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../..');
const fps=Number(process.argv[2]??30);
if(![30,60].includes(fps))throw Error('Preview QA rate must be 30 or 60');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'projects/ai-era-cs-fundamentals/project.json'),'utf8'));
const reportPath=path.join(root,`projects/ai-era-cs-fundamentals/audio/editor-playback-check${fps===60?'-60fps':''}.json`);
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
 try {
  const page=await browser.newPage();await page.setViewport({width:1280,height:900});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`http://localhost:9100/ai-cs-review.html?fps=${fps}`,{waitUntil:'networkidle0',timeout:60000});
  await page.waitForFunction(()=>window.aiReview?.ready&&Number.isFinite(aiReview.player.audio.audioElement.duration),{timeout:60000});
  const loaded=await page.evaluate(()=>({url:aiReview.player.audio.source,duration:aiReview.player.audio.audioElement.duration,timeline:aiReview.player.onDurationChanged.current/aiReview.fps,fps:aiReview.fps}));
  const expectedAudio=path.basename(manifest.paths.editorAudioMix??manifest.paths.audioMix);
  if(!loaded.url.includes(expectedAudio))throw Error(`Wrong audio: ${loaded.url}; expected ${expectedAudio}`);
  if(Math.abs(loaded.duration-manifest.video.durationSeconds)>.1)throw Error('Wrong audio duration');
  if(Math.abs(loaded.timeline-manifest.video.durationSeconds)>.1)throw Error(`Scene duration drift: ${loaded.timeline}`);
  const times=await page.evaluate(()=>aiReview.starts.flatMap((s,i)=>[{scene:i+1,kind:'source',time:s+3},{scene:i+1,kind:'narration',time:s+aiReview.exampleSeconds+3}]));
  const playback=[];
  for(const check of times){
   await page.evaluate(seconds=>{aiReview.player.togglePlayback(false);aiReview.jump(seconds);},check.time);
   await page.waitForFunction(f=>aiReview.rendered===f,{timeout:30000},Math.round(check.time*fps));
   await page.evaluate(()=>{aiReview.player.toggleAudio(true);aiReview.player.setAudioVolume(1);aiReview.player.togglePlayback(true);});
   await page.waitForFunction(t=>aiReview.player.audio.audioElement.currentTime>t+.6,{timeout:15000},check.time);
   const state=await page.evaluate(()=>{const a=aiReview.player.audio.audioElement;return {currentTime:a.currentTime,paused:a.paused,muted:a.muted,volume:a.volume,error:a.error?.message??null,frame:aiReview.rendered};});
   if(state.paused||state.muted||state.volume===0||state.error)throw Error(`Playback failed ${check.scene}: ${JSON.stringify(state)}`);
   playback.push({...check,...state});console.log(`Played ${check.scene} ${check.kind}`);
  }
  const report={checkedAt:new Date().toISOString(),kind:'Programmatic playback check, not subjective listening approval',loaded,playback,errors};
  fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');
  if(errors.length)throw Error(errors.join('\n'));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
