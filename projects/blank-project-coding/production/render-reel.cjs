const fs=require('node:fs'),path=require('node:path'),puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const work=path.join(__dirname,'final-v1'),plan=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8'));
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});
try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9342/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');const pulse=setInterval(()=>page.evaluate(()=>renderJob?.frame).then(f=>console.log('Explanation frame '+f+'/'+plan.explanationReelFrames)).catch(()=>{}),20000);
try{await page.evaluate(frames=>renderVideo({route:'/src/projects/blank-project-coding/explanation-project.ts',name:'blank-project-coding-explanation-reel',frames,fps:60,width:1920,height:1080,exactFrameRange:true}),plan.explanationReelFrames);}finally{clearInterval(pulse);}
const result=await page.evaluate(()=>renderJob);fs.writeFileSync(path.join(work,'render-result.json'),JSON.stringify(result,null,2)+'\n');if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
