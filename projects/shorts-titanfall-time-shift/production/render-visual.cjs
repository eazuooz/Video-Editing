// Finite exact-CFR authored composite; old deliveries are never overwritten.
const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),local=path.join(__dirname,'local');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const control=read(path.join(root,'shared/publishing/video-production-control.json'));
if(!control.shortsBatchAuthorization?.slugs.includes('shorts-titanfall-time-shift')||control.shortsBatchAuthorization.status!=='active')throw Error('Batch selection changed');
const timing=read(path.join(__dirname,'visual-timing.json'));
const capture=read(path.join(local,'capture-full-v2/success.json'));
if(!control.shortsBatchAuthorization?.fullProductionAuthorized||capture.frames!==timing.frames)throw Error('Finite native capture incomplete');
const mode=process.argv[2]||'distinctive-v1-full',firstFrame=Number(process.argv[3]||0),frames=Number(process.argv[4]||timing.frames);
const name='shorts-titanfall-time-shift-'+mode,output=path.join(root,'shared/output/motion-canvas',name+'.mp4');
if(fs.existsSync(output))throw Error('Preserve completed render '+output);
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9265/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
 const pulse=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(f=>console.log('Frame '+f+' / '+(firstFrame+frames))).catch(()=>{}),15000);
 try{await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/distinctive-shorts-20261024/titanfall/project.ts',name,firstFrame,frames,fps:60,width:1080,height:1920,exactFrameRange:true});}finally{clearInterval(pulse);}
 const result=await page.evaluate(()=>window.renderJob);fs.writeFileSync(path.join(local,'motion-'+mode+'-execution.json'),JSON.stringify(result,null,2)+'\n');
 if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));console.log(JSON.stringify({output,firstFrame,frames}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
