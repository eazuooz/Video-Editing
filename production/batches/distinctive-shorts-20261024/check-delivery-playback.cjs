// Smoke-test the complete local review files in a real 375px browser viewport.
// Muted programmatic playback proves decoding/playability, never human listening.
const fs=require('node:fs'),path=require('node:path');
const R=path.resolve(__dirname,'../../..');
const puppeteer=require(path.join(R,'motion-canvas/node_modules/puppeteer'));
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const slugs=read(path.join(__dirname,'batch.json')).authorization.slugs;
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--disable-gpu','--disable-background-timer-throttling','--disable-renderer-backgrounding','--disable-backgrounding-occluded-windows'],protocolTimeout:180000});
 try{
  const reports=[];
  for(const slug of slugs){
   const d=read(path.join(R,'projects',slug,'production/delivery.json'));
   const page=await browser.newPage();await page.setViewport({width:375,height:900,deviceScaleFactor:1});
   const errors=[];page.on('pageerror',e=>errors.push(String(e)));
   await page.goto('http://127.0.0.1:9265/@fs/'+d.reviewPage.replaceAll('\\','/'),{waitUntil:'domcontentloaded'});
   await page.bringToFront();
   const result=await page.evaluate(async()=>{
    const v=document.querySelector('video');v.muted=true;v.volume=0;
    const log=[],start=performance.now();let timer;
    const completed=new Promise((resolve,reject)=>{
     const timeout=setTimeout(()=>{clearInterval(timer);reject(Error('Whole playback timeout '+JSON.stringify({time:v.currentTime,readyState:v.readyState,paused:v.paused,networkState:v.networkState,samples:log})));},120000);
     v.addEventListener('error',()=>{clearTimeout(timeout);reject(Error('Video error '+v.error?.message));},{once:true});
     v.addEventListener('ended',()=>{clearTimeout(timeout);clearInterval(timer);resolve({ended:true,currentTime:v.currentTime,duration:v.duration,width:v.videoWidth,height:v.videoHeight,elapsedSeconds:(performance.now()-start)/1000,quality:v.getVideoPlaybackQuality().toJSON?.()??{droppedVideoFrames:v.getVideoPlaybackQuality().droppedVideoFrames,totalVideoFrames:v.getVideoPlaybackQuality().totalVideoFrames},samples:log,muted:v.muted});},{once:true});
    });
    timer=setInterval(()=>log.push({time:v.currentTime,readyState:v.readyState,paused:v.paused}),3000);
    await v.play();return await completed;
   });
   if(errors.length||!result.ended||result.width!==1080||result.height!==1920||Math.abs(result.duration-d.durationSeconds)>.05)throw Error(slug+' playback failed '+JSON.stringify({result,errors}));
   await page.close();reports.push({slug,masterSha256:d.files.captioned.sha256,viewport:{width:375,height:900},...result,errors,scope:'Complete normal-speed muted browser playback; not a human visual or audio review.'});
   console.log(JSON.stringify({slug,ended:result.ended,duration:result.duration,quality:result.quality}));
  }
  fs.writeFileSync(path.join(__dirname,'browser-playback-check.json'),JSON.stringify({recordedAt:new Date().toISOString(),status:'pass',reports,humanListening:false},null,2)+'\n');
  console.log(JSON.stringify(reports.map(x=>({slug:x.slug,ended:x.ended,duration:x.duration,quality:x.quality}))));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
