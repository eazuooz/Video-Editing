const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),stamp=new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d+Z$/,'Z');
const name='let-them-play-2d-vs-25d-SILENT-'+stamp;
const output=path.join(root,'shared/output/motion-canvas',name+'.mp4');
const qa=path.join(root,'shared/output/let-them-play/lookdev',stamp);
async function main(){
 fs.mkdirSync(qa,{recursive:true});if(fs.existsSync(output))throw Error('Output already exists');
 const browser=await puppeteer.launch({headless:true,protocolTimeout:120000});let state;
 try{
  const page=await browser.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:9100/let-them-play-lookdev.html',{waitUntil:'networkidle0',timeout:60000});
  await page.waitForFunction(()=>window.lookdev?.ready,{timeout:60000});
  const frames=await page.evaluate(()=>lookdev.player.playback.duration);if(frames!==720)throw Error('Runtime duration '+frames);
  for(const t of [1,4.8,6,8.5,11.5]){
   await page.evaluate(t=>lookdev.jump(t),t);await page.waitForFunction(f=>lookdev.rendered===f,{timeout:30000},Math.round(t*60));
   const data=await page.evaluate(()=>lookdev.stage.finalBuffer.toDataURL('image/png').split(',')[1]);fs.writeFileSync(path.join(qa,'t-'+t+'.png'),Buffer.from(data,'base64'));
  }
  if(errors.length)throw Error(errors.join('\n'));
  await page.goto('http://localhost:9100/render-worker.html',{waitUntil:'networkidle0'});
  await page.waitForFunction(()=>typeof window.renderVideo==='function');
  await page.evaluate(config=>{window.renderVideo(config).catch(e=>window.renderFailure=String(e.stack??e))},{route:'/src/projects/let-them-play/lookdev/project.ts',name,frames:720,fps:60,width:1920,height:1080});
  const start=Date.now();
  while(true){
   await new Promise(r=>setTimeout(r,2000));state=await page.evaluate(()=>({...window.renderJob,failure:window.renderFailure}));
   if(!Number.isFinite(state.frame)||state.failure||state.errors?.length||errors.length)throw Error(JSON.stringify({state,errors}));
   console.log(state.frame+'/720');if(state.done)break;if(Date.now()-start>180000)throw Error('Render timeout');
  }
  if(state.result!==0)throw Error('Render failed '+state.result);
 }finally{await browser.close()}
 const probe=spawnSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',output],{encoding:'utf8',windowsHide:true});if(probe.status!==0)throw Error(probe.stderr);
 const info=JSON.parse(probe.stdout),v=info.streams.find(s=>s.codec_type==='video');
 if(v.width!==1920||v.height!==1080||Number(v.nb_frames)!==720||Number(info.format.duration)!==12||info.streams.some(s=>s.codec_type==='audio'))throw Error('Wrong media format');
 const decode=spawnSync('ffmpeg',['-v','error','-i',output,'-f','null','-'],{encoding:'utf8',windowsHide:true});if(decode.status!==0)throw Error(decode.stderr);
 const report={output,qa,duration:12,width:1920,height:1080,frames:720,kind:'silent 2D vs 2.5D style comparison',fullDecodePassed:true,mainTimelineChanged:false,publishReady:false};
 fs.writeFileSync(output.replace(/\.mp4$/,'.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1});
