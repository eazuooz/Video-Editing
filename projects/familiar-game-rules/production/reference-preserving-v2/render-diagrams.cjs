const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../../..');
const [name='familiar-controls-preflight-v2',count='1440',route='/src/projects/familiar-game-rules/revision-v2/preflight-project.ts']=process.argv.slice(2);
if(!name.startsWith('familiar-controls-'))throw Error('D20 output name required');
const frames=Number(count),out=path.join(root,'projects/familiar-game-rules/production/local/reference-preserving-v2',name);fs.mkdirSync(out,{recursive:true});
const authorization=JSON.parse(fs.readFileSync(path.join(__dirname,'authorization.json')));
const control=JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-production-control.json')));
if(!authorization.fullRevisionAuthorized||control.automaticNextVideoEnabled)throw Error('Check current selected scope');
const state={name,frames,route,startedAt:new Date().toISOString(),status:'running',device:'CPU',foreignProcessesChanged:[]};
const save=()=>fs.writeFileSync(path.join(out,'execution.json'),JSON.stringify(state,null,2)+'\n');save();
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu','--renderer-process-limit=2'],protocolTimeout:600000});try{
 const page=await browser.newPage();await page.goto('http://127.0.0.1:9233/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
 const pulse=setInterval(()=>page.evaluate(()=>renderJob?.frame).then(frame=>{state.frame=frame;save();console.log(frame+'/'+frames);}).catch(()=>{}),20000);
 try{await page.evaluate(p=>renderVideo(p),{route,name,frames,firstFrame:0,fps:60,width:1920,height:1080,exactFrameRange:true});}finally{clearInterval(pulse);}
 const result=await page.evaluate(()=>renderJob);state.result=result;if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
 state.status='rendered-awaiting-pixel-review';state.completedAt=new Date().toISOString();save();
}finally{await browser.close();}})().catch(e=>{state.status='failed';state.error=String(e);save();console.error(e);process.exitCode=1;});
