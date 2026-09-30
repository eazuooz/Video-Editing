// Capture real playable prototypes from their canvas; keep actual input logs.
const fs=require('node:fs'),path=require('node:path'),{spawn}=require('node:child_process');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),dest=path.join(root,'shared/assets/one-button-game-design/playtests');
async function capture(mode){
 const output=path.join(dest,mode+'.mp4');if(fs.existsSync(output))throw Error('Preserve existing test: '+output);
 const browser=await puppeteer.launch({headless:true});
 const page=await browser.newPage();await page.setViewport({width:1920,height:1080});
 await page.goto('file:///'+path.join(__dirname,'prototype/index.html').replaceAll('\\','/')+'?mode='+mode);
 await page.evaluate(()=>window.recording=true);await page.evaluate(()=>document.fonts.ready);
 const ff=spawn('ffmpeg',['-v','error','-n','-f','image2pipe','-framerate','60','-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','90000',output],{windowsHide:true,stdio:['pipe','ignore','pipe']});
 let error='';ff.stderr.on('data',s=>error+=s);const done=new Promise((resolve,reject)=>ff.on('exit',code=>code===0?resolve():reject(Error(error))));
 let wasDown=false;
 try{
  for(let frame=0;frame<2400;frame++){
   const t=frame/60,trial=Math.floor(t/8),local=t%8;
   const interval=[.24,.18,.13,.2,.16][trial];
   const isDown=mode==='mash'?local>.35&&local<4.8&&(local%interval)<interval*.38:local>1&&local<[2.1,2.9,2.5,3.2,2.7][trial];
   await page.evaluate(t=>window.captureStep(t),t);
   if(isDown!==wasDown){await page.keyboard[isDown?'down':'up']('Space');wasDown=isDown;}
   const jpg=await page.evaluate(t=>{window.captureStep(t);return document.querySelector('canvas').toDataURL('image/jpeg',.93).split(',')[1]},t);
   if(!ff.stdin.write(Buffer.from(jpg,'base64')))await new Promise(r=>ff.stdin.once('drain',r));
   if(frame%600===0)console.log(mode,frame+'/2400');
  }
  fs.writeFileSync(path.join(__dirname,mode+'-input-log.json'),JSON.stringify({kind:'actual-playable-prototype-input-capture',fps:60,seconds:40,events:await page.evaluate(()=>window.inputLog)},null,2)+'\n');
  ff.stdin.end();await done;
 }finally{await browser.close();}
}
(async()=>{fs.mkdirSync(dest,{recursive:true});for(const mode of ['mash','charge'])await capture(mode)})().catch(e=>{console.error(e);process.exitCode=1});
