const fs=require('node:fs'),path=require('node:path'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),work=path.join(root,'projects/one-button-game-design/production/final-v2');
(async()=>{
 const plan=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8')),frames=plan.introFrames+plan.diagramFrames+600;
 const browser=await puppeteer.launch({headless:true,protocolTimeout:600000});
 try{
  const page=await browser.newPage();await page.goto('http://127.0.0.1:9210/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
  const progress=setInterval(()=>page.evaluate(()=>renderJob.frame).then(f=>console.log(`Explanation frame ${f}/${frames}`)).catch(()=>{}),20000);
  try{await page.evaluate(frames=>renderVideo({route:'/src/projects/one-button-game-design/explanation-project.ts',name:'one-button-explanation-reel-v2',frames,fps:60,width:1920,height:1080,exactFrameRange:true}),frames);}finally{clearInterval(progress);}
  const result=await page.evaluate(()=>renderJob);fs.writeFileSync(path.join(work,'render-result.json'),JSON.stringify(result,null,2));
  if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
