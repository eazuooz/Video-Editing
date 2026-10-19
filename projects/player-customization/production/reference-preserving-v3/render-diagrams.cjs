const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../../..');
const [name='customization-preflight-v3',count='1440',route='/src/projects/player-customization/revision-v3/preflight-project.ts']=process.argv.slice(2);
if(!/^customization-[a-z0-9-]+$/.test(name))throw Error('D21 scoped output name required');
if(!route.startsWith('/src/projects/player-customization/revision-v3/'))throw Error('D21 route required');
const frames=Number(count);if(!Number.isSafeInteger(frames)||frames<1)throw Error('Positive exact frame count required');
const out=path.join(root,'projects/player-customization/production/local/reference-preserving-v3',name);fs.mkdirSync(out,{recursive:true});
const authorization=JSON.parse(fs.readFileSync(path.join(__dirname,'authorization.json')));
const control=JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-production-control.json')));
if(authorization.slug!=='player-customization'||!authorization.fullProductionAuthorized||authorization.automaticNextVideo!==false||control.automaticNextVideoEnabled)throw Error('Check current selected scope');
const state={name,frames,route,startedAt:new Date().toISOString(),status:'running',device:'CPU',observedSharedSelection:control.selectedVideo,foreignProcessesChanged:[]};
const save=()=>fs.writeFileSync(path.join(out,'execution.json'),JSON.stringify(state,null,2)+'\n');save();
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu','--renderer-process-limit=2'],protocolTimeout:600000});try{
 const page=await browser.newPage();await page.goto('http://127.0.0.1:9241/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
 const pulse=setInterval(()=>page.evaluate(()=>renderJob?.frame).then(frame=>{state.frame=frame;save();console.log(frame+'/'+frames);}).catch(()=>{}),20000);
 try{await page.evaluate(p=>renderVideo(p),{route,name,frames,firstFrame:0,fps:60,width:1920,height:1080,exactFrameRange:true});}finally{clearInterval(pulse);}
 const result=await page.evaluate(()=>renderJob);state.result=result;if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
 state.status='rendered-awaiting-pixel-review';state.completedAt=new Date().toISOString();save();
}finally{await browser.close();}})().catch(e=>{state.status='failed';state.error=String(e);save();console.error(e);process.exitCode=1;});
