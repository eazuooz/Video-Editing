// Repository-source rendering only; no external platform or browser UI actions.
const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const version=process.argv[2]||'v1';
if(!/^v\d+$/.test(version))throw Error('Numbered version required');
const work=path.join(__dirname,'lookdev-'+version),statePath=path.join(work,'execution.json');
if(fs.existsSync(work))throw Error('Preserve prior lookdev work');
fs.mkdirSync(work);
const state={pid:process.pid,startedAt:new Date().toISOString(),status:'running',gpuJobs:0,silentLookdev:true,finalNarratedVideo:false,frames:3360,fps:60,port:9218};
const save=()=>fs.writeFileSync(statePath,JSON.stringify(state,null,2)+'\n');save();
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});
 try{
  const page=await browser.newPage();await page.goto('http://127.0.0.1:9218/render-worker.html');
  await page.waitForFunction(()=>typeof renderVideo==='function');
  const pulse=setInterval(()=>page.evaluate(()=>renderJob?.frame).then(frame=>{state.frame=frame;save();console.log('Silent layout frame '+frame+'/3360');}).catch(()=>{}),20000);
  try{await page.evaluate(version=>renderVideo({route:'/src/projects/game-reward-planning/lookdev-project.ts',name:'game-reward-planning-lookdev-'+version,frames:3360,fps:60,width:1920,height:1080,exactFrameRange:true}),version);}finally{clearInterval(pulse);}
  const result=await page.evaluate(()=>renderJob);
  fs.writeFileSync(path.join(work,'render-result.json'),JSON.stringify({...state,renderMode:'headless-source-renderer-disabled-gpu',...result},null,2)+'\n');
  if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
  state.status='finished-awaiting-direct-layout-review';state.endedAt=new Date().toISOString();state.exitCode=0;save();
 }finally{await browser.close();}
})().catch(error=>{state.status='failed';state.error=String(error);state.exitCode=1;state.endedAt=new Date().toISOString();save();console.error(error);process.exitCode=1;});
