// Finite CPU browser composite. Preview ranges are for layout QA, not delivery.
const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),project=path.dirname(__dirname),slug=path.basename(project),local=path.join(__dirname,'local');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const control=read(path.join(root,'shared/publishing/video-production-control.json'));
const auth=control.scopedBatchAuthorizations?.['explicit-ten-distinctive-shorts-20261025'];
if(auth?.status!=='active'||!auth.slugs.includes(slug)||!auth.fullProductionAuthorized)throw Error('Explicit batch scope is inactive');
const preview=process.argv.includes('--preview'),timing=read(path.join(__dirname,preview?'visual-timing.draft.json':'visual-timing.json'));
const mode=process.argv[2]||'distinctive-ten-v1',firstFrame=Number(process.argv[3]||0),frames=Number(process.argv[4]||timing.frames);
const name=slug+'-'+mode,output=path.join(root,'shared/output/motion-canvas',name+'.mp4');
if(fs.existsSync(output))throw Error('Preserve completed render '+output);
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9265/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
 const pulse=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(f=>console.log('Frame '+f+' / '+(firstFrame+frames))).catch(()=>{}),15000);
 try{await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/'+slug+'/project'+(preview?'-preview':'')+'.ts',name,firstFrame,frames,fps:60,width:1080,height:1920,exactFrameRange:true});}finally{clearInterval(pulse);}
 const result=await page.evaluate(()=>window.renderJob);fs.writeFileSync(path.join(local,'motion-'+mode+'-execution.json'),JSON.stringify(result,null,2)+'\n');
 if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));console.log(JSON.stringify({output,firstFrame,frames,preview}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
