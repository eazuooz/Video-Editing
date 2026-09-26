const fs=require('node:fs'),path=require('node:path'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),work=path.join(root,'projects/small-window-game-design/production/full-v2');
(async()=>{
  const plan=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8'));
  const browser=await puppeteer.launch({headless:true,protocolTimeout:600000});
  try{
    const page=await browser.newPage();await page.goto('http://127.0.0.1:9210/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
    const progress=setInterval(()=>page.evaluate(()=>renderJob.frame).then(f=>console.log(`Diagram frame ${f}/${plan.diagramFrames}`)).catch(()=>{}),20000);
    try{await page.evaluate(frames=>renderVideo({route:'/src/projects/small-window-game-design/full/diagram-project.ts',name:'small-window-diagram-reel-v2',frames,fps:60,width:1920,height:1080,exactFrameRange:true}),plan.diagramFrames);}finally{clearInterval(progress);}
    const result=await page.evaluate(()=>renderJob);fs.writeFileSync(path.join(work,'render-result.json'),JSON.stringify(result,null,2));
    if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
