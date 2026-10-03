// Local source-render worker, never a YouTube Studio UI controller.
const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const work=path.join(__dirname,'final-v1'),plan=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8'));
if(!plan.finalSourceTimingApproved||!plan.explanationReelFrames)throw Error('Install exact reviewed compiled timing first');
if(fs.existsSync(path.join(work,'explanation-render-result.json')))throw Error('Review existing render rather than duplicate it');
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9214/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
  const pulse=setInterval(()=>page.evaluate(()=>renderJob?.frame).then(frame=>console.log(`Measured explanation reel ${frame}/${plan.explanationReelFrames}`)).catch(()=>{}),20000);
  try{await page.evaluate(frames=>renderVideo({route:'/src/projects/motion-sickness-games/explanation-project.ts',name:'motion-sickness-games-explanation-reel',frames,fps:60,width:1920,height:1080,exactFrameRange:true}),plan.explanationReelFrames);}finally{clearInterval(pulse);}
  const result=await page.evaluate(()=>renderJob);fs.writeFileSync(path.join(work,'explanation-render-result.json'),JSON.stringify({createdAt:new Date().toISOString(),pid:process.pid,renderMode:'headless-source-worker-disabled-gpu',frames:plan.explanationReelFrames,finalVideo:false,captionPixelReview:'pending',...result},null,2)+'\n');if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
