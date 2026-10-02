// Own code-only explanation preview. CPU/software browser; no final master.
const fs=require('node:fs'),path=require('node:path'),puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});
 try{
 const page=await browser.newPage();await page.goto('http://127.0.0.1:9210/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
 const pulse=setInterval(()=>page.evaluate(()=>renderJob?.frame).then(f=>console.log(`Explanation draft frame ${f}/1440`)).catch(()=>{}),20000);
 try{await page.evaluate(()=>renderVideo({route:'/src/projects/game-writing/lookdev-project.ts',name:'game-writing-explanation-lookdev-v3',frames:1440,fps:30,width:1920,height:1080,exactFrameRange:true}));}finally{clearInterval(pulse)}
 const result=await page.evaluate(()=>renderJob);fs.writeFileSync(path.join(__dirname,'lookdev-render-result-v3.json'),JSON.stringify({...result,classification:'code-only 48-second visual draft, not completed narrated video'},null,2)+'\n');
 if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
 console.log('Explanation-only draft rendered; final narration/gameplay/render QA remain pending.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
