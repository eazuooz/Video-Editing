const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../../..');
const args=process.argv.slice(2),name=args[0]||'avoid-comparisons-preflight-v2',firstFrame=Number(args[1]||4200),frames=Number(args[2]||480),route=args[3]||'/src/projects/avoid-game-comparisons/revision-v2/project.ts';
const out=path.join(root,'projects/avoid-game-comparisons/production/local/reference-preserving-v2',name);fs.mkdirSync(out,{recursive:true});
const state={name,firstFrame,frames,route,startedAt:new Date().toISOString(),status:'running'};
const save=()=>fs.writeFileSync(path.join(out,'execution.json'),JSON.stringify(state,null,2)+'\n');save();
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:600000});try{
 const page=await browser.newPage();await page.goto('http://127.0.0.1:9231/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
 const pulse=setInterval(()=>page.evaluate(()=>renderJob?.frame).then(frame=>{state.frame=frame;save();console.log(frame+'/'+(firstFrame+frames));}).catch(()=>{}),20000);
 try{await page.evaluate(p=>renderVideo(p),{route,name,frames,firstFrame,fps:60,width:1920,height:1080,exactFrameRange:true});}finally{clearInterval(pulse);}
 const result=await page.evaluate(()=>renderJob);state.result=result;if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
 state.status='rendered-awaiting-pixel-review';state.completedAt=new Date().toISOString();save();
}finally{await browser.close();}})().catch(e=>{state.status='failed';state.error=String(e);save();console.error(e);process.exitCode=1;});
