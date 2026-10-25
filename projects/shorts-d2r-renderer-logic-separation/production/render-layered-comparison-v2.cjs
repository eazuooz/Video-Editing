// One explicitly requested local-only revision. No old finite batch is resumed.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const P=path.resolve(__dirname,'..'),R=path.resolve(P,'../..');
const puppeteer=require(path.join(R,'motion-canvas/node_modules/puppeteer'));
const [name,first='0',count='2620']=process.argv.slice(2);
const slug='shorts-d2r-renderer-logic-separation';
if(path.basename(P)!==slug||!/^d2layers-v2-[a-z0-9-]+$/.test(name||''))throw Error('Wrong local revision/name');
const timing=JSON.parse(fs.readFileSync(path.join(__dirname,'layered-comparison-v2.json'),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(timing.frames!==2620||timing.revision!=='layered-comparison-v2')throw Error('Timing changed');
if(hash(path.join(__dirname,'local/audio-v1/voice/narration.wav'))!=='9809f48b8a8dfbf0fc20c80e3f6c2acd4d7d8020ec1a3e69962e122f328d96be')throw Error('Preserve approved PCM');
if(!Number.isInteger(+first)||!Number.isInteger(+count)||+first<0||+count<1||+first+(+count)>2620)throw Error('Invalid range');
const output=path.join('C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025/motion-canvas-output',name+'.mp4');
if(fs.existsSync(output))throw Error('Preserve previous render');
// Read the current control for the receipt; do not activate or edit any old queue.
const controlHash=hash(path.join(R,'shared/publishing/video-production-control.json'));
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:900000});
 try{
  const page=await browser.newPage();await page.goto('http://127.0.0.1:9267/render-worker.html');
  await page.waitForFunction(()=>typeof renderVideo==='function');
  const timer=setInterval(()=>page.evaluate(()=>window.renderJob?.frame).then(x=>console.log('Frame '+x)).catch(()=>{}),15000);
  try{await page.evaluate(a=>window.renderVideo(a),{route:'/src/projects/'+slug+'/project.ts',name,firstFrame:+first,frames:+count,fps:60,width:1080,height:1920,exactFrameRange:true});}
  finally{clearInterval(timer);}
  const result=await page.evaluate(()=>window.renderJob);
  const receipt={...result,output,controlHash,renderer:'Motion Canvas CPU Chromium (--disable-gpu) + ffmpeg exporter',sourceHash:hash(path.join(R,'motion-canvas/src/projects/'+slug+'/layered-comparison-v2.tsx')),timingHash:hash(path.join(__dirname,'layered-comparison-v2.json')),pcmHash:hash(path.join(__dirname,'local/audio-v1/voice/narration.wav'))};
  fs.writeFileSync(path.join(__dirname,'local/layered-comparison-v2',name+'-render.json'),JSON.stringify(receipt,null,2)+'\n');
  if(!result.done||result.result!==0||result.errors.length)throw Error(JSON.stringify(result));
  console.log(output);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
