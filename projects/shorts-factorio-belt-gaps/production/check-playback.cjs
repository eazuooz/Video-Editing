// Local authored review-page playback, not external browser/account automation.
const fs=require('node:fs'), path=require('node:path'), {pathToFileURL}=require('node:url'), crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const puppeteer=require(path.join(root,'motion-canvas/node_modules/puppeteer'));
const manifest=JSON.parse(fs.readFileSync(path.join(__dirname,'../project.json'),'utf8'));
const dir=fs.realpathSync(path.join(__dirname,'..',manifest.currentFinalDirectory));
(async()=>{
  const out=path.join(dir,'automated-playback'); fs.mkdirSync(out,{recursive:true});
  if(fs.existsSync(path.join(out,'result.json')))throw Error('Preserve prior playback record.');
  const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:120000});
  try{
    const page=await browser.newPage();await page.setViewport({width:375,height:820,deviceScaleFactor:1});
    const errors=[];page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(pathToFileURL(path.join(dir,'index.html')).href,{waitUntil:'networkidle0'});
    await page.waitForSelector('video');
    const before=await page.evaluate(async()=>{const v=document.querySelector('video');v.muted=true;v.playbackRate=1;await v.play();return {currentTime:v.currentTime,width:v.videoWidth,height:v.videoHeight,duration:v.duration};});
    const shots=[];
    for(const t of [1,8,17,21,29,36,44.5,46]){
      await page.waitForFunction(t=>document.querySelector('video').currentTime>=t,{timeout:65000},t);
      const time=await page.evaluate(()=>document.querySelector('video').currentTime);
      const file=path.join(out,'mobile-'+t+'.png'); await (await page.$('video')).screenshot({path:file}); shots.push({requested:t,currentTime:time,path:file});
    }
    await page.waitForFunction(()=>document.querySelector('video').ended,{timeout:10000});
    const after=await page.evaluate(()=>{const v=document.querySelector('video');const q=v.getVideoPlaybackQuality();return {ended:v.ended,currentTime:v.currentTime,error:v.error&&{code:v.error.code,message:v.error.message},totalVideoFrames:q.totalVideoFrames,droppedVideoFrames:q.droppedVideoFrames,playbackRate:v.playbackRate};});
    if(!after.ended||after.error||errors.length||after.totalVideoFrames<2700)throw Error(JSON.stringify({after,errors}));
    const masterSha256=crypto.createHash('sha256').update(fs.readFileSync(path.join(dir,'captioned.mp4'))).digest('hex');
    fs.writeFileSync(path.join(out,'result.json'),JSON.stringify({status:'automated-realtime-playback-pass',masterSha256,viewport:{width:375,height:820},before,after,shots,errors,muted:true,actualHumanListening:false,actualFullHumanViewing:false},null,2)+'\n',{flag:'wx'});
    console.log(JSON.stringify({after,shots:shots.length,report:path.join(out,'result.json')}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
