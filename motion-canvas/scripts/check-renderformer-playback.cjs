const fs=require('node:fs'),path=require('node:path'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..');
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
 try{
  const page=await browser.newPage();
  page.on('pageerror',e=>console.error('Page error:',e.message));
  page.on('response',r=>{if(r.status()>=400)console.error(r.status(),r.url());});
  await page.goto('http://127.0.0.1:9210/renderformer-full.html');
  await page.waitForFunction(()=>Boolean(document.querySelector('video').getAttribute('src')));
  const variant=process.argv.includes('--captioned')?'captioned':'clean';
  await page.select('#variant',variant);
  try {await page.waitForFunction(()=>document.querySelector('video').readyState>=2,{timeout:15000});}
  catch(e){console.error(await page.evaluate(()=>{const v=document.querySelector('video');return {src:v.currentSrc,error:v.error?.message,ready:v.readyState,status:document.querySelector('#status').textContent};}));throw e;}
  const results=await page.evaluate(async()=>{
   const v=document.querySelector('video'),context=new AudioContext();await context.resume();
   const source=context.createMediaElementSource(v),a=context.createAnalyser();source.connect(a);a.connect(context.destination);a.fftSize=2048;
   let results=[];
   for(const time of [3,1205,2602]){
    v.pause();const ready=new Promise(r=>v.addEventListener('seeked',r,{once:true}));v.currentTime=time;await ready;await v.play();
    let maxRms=0;const values=new Float32Array(a.fftSize);
    for(let i=0;i<12;i++){await new Promise(r=>setTimeout(r,100));a.getFloatTimeDomainData(values);maxRms=Math.max(maxRms,Math.sqrt(values.reduce((n,x)=>n+x*x,0)/values.length));}
    results.push({time,playedTo:v.currentTime,maxRms,muted:v.muted,readyState:v.readyState});
   }
   v.pause();return {duration:v.duration,videoWidth:v.videoWidth,videoHeight:v.videoHeight,results};
  });
  if(results.results.some(r=>r.maxRms<.002||r.playedTo<r.time+.5))throw Error(JSON.stringify(results));
  fs.writeFileSync(path.join(root,`projects/renderformer-explained/production/body-review/browser-playback${variant==='captioned'?'-captioned':''}.json`),JSON.stringify({...results,variant,note:'Objective signal/playback check, not human listening approval.'},null,2));
  console.log(JSON.stringify(results));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
