const fs=require('node:fs'),path=require('node:path'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),work=path.join(root,'projects/one-button-game-design/production/final-v2');
(async()=>{
 const browser=await puppeteer.launch({headless:true});let result;
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9210/render-worker.html');
  result=await page.evaluate(async()=>{
   const results=[];
   for(const name of ['game-01.mp4','game-02.mp4','game-03.mp4','game-04.mp4','game-05.mp4','game-06.mp4','game-07.mp4','final-mix-v2.m4a']){
    const el=document.createElement(name.endsWith('m4a')?'audio':'video');el.muted=true;el.src='/src/projects/one-button-game-design/assets/'+name;
    await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(Error('Media timeout: '+name)),12000);el.onloadeddata=()=>{clearTimeout(timer);resolve();};el.onerror=()=>{clearTimeout(timer);reject(Error('Media decoder error: '+name));};document.body.append(el);el.load();});
    await el.play();await new Promise(resolve=>setTimeout(resolve,250));
    results.push({name,duration:el.duration,decoded:el.readyState>=2,playbackAdvanced:el.currentTime>0});el.pause();el.remove();
   }
   return {results,allDecoded:results.every(r=>r.decoded&&r.playbackAdvanced)};
  });
 }finally{await browser.close();}
 fs.writeFileSync(path.join(work,'editor-playback-qa.json'),JSON.stringify(result,null,2));if(!result.allDecoded)throw Error('Editor media playback failed');console.log(JSON.stringify(result));
})().catch(e=>{console.error(e);process.exitCode=1;});
