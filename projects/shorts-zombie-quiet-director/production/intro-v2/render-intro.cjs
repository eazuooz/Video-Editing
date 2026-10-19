const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../../..'),local=path.resolve(__dirname,'../local/intro-v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const selected=read(path.join(root,'shared/publishing/video-production-control.json')).shortsRecurringAuthorization;
if(selected.selectedShort!=='shorts-zombie-quiet-director'||selected.latestSelection.selectedRevision!=='zombie-quiet-intro-v2')throw Error('Selection changed');
const timing=read(path.join(__dirname,'timing.json')),name='shorts-zombie-quiet-director-intro-v2';
if(fs.existsSync(path.join(root,'shared/output/motion-canvas',name+'.mp4')))throw Error('Preserve completed intro');
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9248/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/shorts-zombie-quiet-director-intro-v2/project.ts',name,firstFrame:0,frames:timing.introFrames,fps:60,width:1080,height:1920,exactFrameRange:true});const result=await page.evaluate(()=>window.renderJob);fs.writeFileSync(path.join(local,'render-execution.json'),JSON.stringify(result,null,2)+'\n');if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));console.log(JSON.stringify({frames:timing.introFrames,seconds:timing.introSeconds}));}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
