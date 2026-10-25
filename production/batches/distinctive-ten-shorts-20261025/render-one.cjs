// Scoped CPU Motion Canvas renderer; outputs on the verified C: media volume.
const fs=require('node:fs'),path=require('node:path');
const R=path.resolve(__dirname,'../../..');
const puppeteer=require(path.join(R,'motion-canvas/node_modules/puppeteer'));
const [slug,name,first='0',count='1']=process.argv.slice(2);
const batch=JSON.parse(fs.readFileSync(path.join(__dirname,'batch.json'),'utf8'));
if(!batch.projects.some(r=>r.slug===slug))throw Error('Outside explicit batch');
const control=JSON.parse(fs.readFileSync(path.join(R,'shared/publishing/video-production-control.json'),'utf8'));
const authorization=control.scopedBatchAuthorizations?.['explicit-ten-distinctive-shorts-20261025'];
if(authorization?.status!=='active'||!authorization?.fullProductionAuthorized)throw Error('Scope changed');
if(!/^[a-z0-9][a-z0-9-]+$/.test(name||''))throw Error('Use a safe unique render name');
const project=path.join(R,'projects',slug);
const timing=JSON.parse(fs.readFileSync(path.join(project,'production/visual-timing.json'),'utf8'));
if(!Number.isInteger(Number(first))||!Number.isInteger(Number(count))||Number(first)<0||Number(count)<1||Number(first)+Number(count)>timing.frames)throw Error('Frame range outside this version');
const nested={'shorts-d2r-ultrawide-ai-range':'ultrawide','shorts-d2r-loot-grass-clearance':'grass','shorts-d2-modular-sprite-equipment':'sprites'};
const route=nested[slug]?'/src/projects/diablo-tricks-shorts-20261025/'+nested[slug]+'/project.ts':'/src/projects/'+slug+'/project.ts';
const output=path.join('C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025/motion-canvas-output',name+'.mp4');
if(fs.existsSync(output))throw Error('Preserve successful render');
if(Number(count)>300&&timing.previewOnly)throw Error('Full render requires actual narration timing');
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
 try{const page=await browser.newPage();await page.goto('http://127.0.0.1:9267/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
  const timer=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(x=>console.log('Frame '+x)).catch(()=>{}),15000);
  try{await page.evaluate(a=>window.renderVideo(a),{route,name,firstFrame:Number(first),frames:Number(count),fps:60,width:1080,height:1920,exactFrameRange:true});}finally{clearInterval(timer);}
  const result=await page.evaluate(()=>window.renderJob);fs.writeFileSync(path.join(project,'production/local',name+'-render.json'),JSON.stringify({...result,output},null,2)+'\n');
  if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));console.log(output);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
