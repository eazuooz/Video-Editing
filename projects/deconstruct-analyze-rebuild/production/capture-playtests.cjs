// Offline canvas export of the project's own playable experiments.
const fs=require('node:fs'),path=require('node:path'),{spawn,spawnSync}=require('node:child_process');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),dest=path.join(root,'shared/assets/deconstruct-analyze-rebuild/playtests-v3');
async function capture(mode){
 const output=path.join(dest,mode+'.mp4');if(fs.existsSync(output))throw Error('Preserve existing export '+output);
 const browser=await puppeteer.launch({headless:true});
 try{
  const page=await browser.newPage();await page.setViewport({width:1920,height:1080});
  await page.goto('file:///'+path.join(__dirname,'prototype/index.html').replaceAll('\\','/')+'?mode='+mode);
  await page.evaluate(()=>window.recording=true);await page.evaluate(()=>document.fonts.ready);
  const ff=spawn('ffmpeg',['-v','error','-n','-f','image2pipe','-framerate','60','-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','90000',output],{windowsHide:true,stdio:['pipe','ignore','pipe']});
  let error='';ff.stderr.on('data',s=>error+=s);const done=new Promise((resolve,reject)=>ff.on('exit',c=>c===0?resolve():reject(Error(error))));
  let downSpace=false,downRight=false;
  for(let frame=0;frame<2700;frame++){
   const t=frame/60,trial=Math.floor(t/4.8),local=t%4.8;
   const right=mode==='variants'?local>1.72&&local<3.47:local>.35&&local<3.5;
   const jumpTimes=[.82,.48,.97,.75,.43,.89,.52,.93,.79,.67];
   const space=mode==='variants'?local>1.93&&local<2.06:local>jumpTimes[trial]&&local<jumpTimes[trial]+.15;
   await page.evaluate(t=>window.captureStep(t),t);
   if(right!==downRight){await page.keyboard[right?'down':'up']('ArrowRight');downRight=right;}
   if(space!==downSpace){await page.keyboard[space?'down':'up']('Space');downSpace=space;}
   const jpg=await page.evaluate(t=>{window.captureStep(t);return document.querySelector('canvas').toDataURL('image/jpeg',.93).split(',')[1];},t);
   if(!ff.stdin.write(Buffer.from(jpg,'base64')))await new Promise(r=>ff.stdin.once('drain',r));
   if(frame%600===0)console.log(mode,frame+'/2700');
  }
  const evidence=await page.evaluate(()=>({input:window.inputLog,sounds:window.soundLog,outcomes:window.outcomeLog}));
  fs.writeFileSync(path.join(__dirname,mode+'-v3-input-log.json'),JSON.stringify({kind:'real-playable-prototype-keyboard-capture',fps:60,seconds:45,...evidence},null,2)+'\n');
  ff.stdin.end();await done;
 }finally{await browser.close();}
}
(async()=>{fs.mkdirSync(dest,{recursive:true});for(const mode of (process.argv[2]?[process.argv[2]]:['landing','retry','variants','observe']))await capture(mode);})().catch(e=>{console.error(e);process.exitCode=1;});
