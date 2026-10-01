// Render the local code artifact in its isolated Motion Canvas worker.
const fs=require('node:fs'),path=require('node:path'),puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),lookdev=process.argv.includes('--lookdev');
const work=path.join(__dirname,process.env.COUNTING_REVISION||'final-v1');fs.mkdirSync(work,{recursive:true});
(async()=>{
 const plan=lookdev?null:JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8'));
 const frames=lookdev?3600:plan.introFrames+plan.diagramFrames+600;
 const browser=await puppeteer.launch({headless:true,protocolTimeout:600000});
 try{
  const page=await browser.newPage();await page.goto('http://127.0.0.1:9210/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
  const progress=setInterval(()=>page.evaluate(()=>renderJob.frame).then(f=>console.log(`Explanation frame ${f}/${frames}`)).catch(()=>{}),20000);
  try{await page.evaluate(({frames,lookdev})=>renderVideo({route:'/src/projects/counting-animation-frames/'+(lookdev?'lookdev-project':'explanation-project')+'.ts',name:lookdev?'counting-animation-frames-lookdev':'counting-animation-frames-explanation-reel',frames,fps:60,width:1920,height:1080,exactFrameRange:true}),{frames,lookdev});}finally{clearInterval(progress);}
  const result=await page.evaluate(()=>renderJob);fs.writeFileSync(path.join(work,lookdev?'lookdev-render-result.json':'render-result.json'),JSON.stringify(result,null,2));
  if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
