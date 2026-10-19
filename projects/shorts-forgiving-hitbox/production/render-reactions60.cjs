// Finite selected visual revision; never overwrite prior approved media.
const fs=require('node:fs'),path=require('node:path');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),local=path.join(__dirname,'local/fairness-60s-reactions-v1');
const control=JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-production-control.json'),'utf8')).shortsRecurringAuthorization;
if(control.selectedShort!=='shorts-forgiving-hitbox'||control.latestSelection.selectedRevision!=='fairness-60s-reactions-v1')throw Error('Selected revision changed');
const mode=process.argv[2]||'full-v1',firstFrame=Number(process.argv[3]||0),frames=Number(process.argv[4]||(mode.startsWith('preview')?420:3600));
const name='shorts-forgiving-hitbox-reactions60-'+mode,output=path.join(root,'shared/output/motion-canvas',name+'.mp4');
if(fs.existsSync(output))throw Error('Preserve completed render '+output);
fs.mkdirSync(local,{recursive:true});
(async()=>{const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
 try{
  const page=await browser.newPage();await page.goto('http://127.0.0.1:9246/render-worker.html');await page.waitForFunction(()=>typeof renderVideo==='function');
  const pulse=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(f=>console.log('Frame '+f+' / '+(firstFrame+frames))).catch(()=>{}),15000);
  try{await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/shorts-forgiving-hitbox-reactions60/project.ts',name,firstFrame,frames,fps:60,width:1080,height:1920,exactFrameRange:true});}finally{clearInterval(pulse);}
  const result=await page.evaluate(()=>window.renderJob);fs.writeFileSync(path.join(local,'motion-'+mode+'-execution.json'),JSON.stringify(result,null,2)+'\n');
  if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
  console.log(JSON.stringify({output,firstFrame,frames,result:result.result}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
