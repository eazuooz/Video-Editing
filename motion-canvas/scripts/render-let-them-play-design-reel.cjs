// QA and rendering of our local Motion Canvas app. --qa-only skips encoding.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),manifest=require('../../projects/let-them-play/project.json');
const fps=manifest.video.fps,seconds=manifest.editing.exampleSeconds,count=manifest.video.sceneCount,frames=Math.round(seconds*count*fps);
const stamp=new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d+Z$/,'Z'),name='let-them-play-DESIGN-25D-SILENT-'+stamp;
const output=path.join(root,'shared/output/motion-canvas',name+'.mp4'),qa=path.join(root,'shared/output/let-them-play/design-reel',stamp);
async function main(){
 fs.mkdirSync(qa,{recursive:true});if(fs.existsSync(output))throw Error('Output already exists');
 const browser=await puppeteer.launch({headless:true,protocolTimeout:120000});const errors=[];let state,timing;
 try{
  const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:9100/let-them-play-design-reel.html',{waitUntil:'networkidle0',timeout:60000});
  await page.waitForFunction(()=>window.designReel?.ready,{timeout:60000});
  timing=await page.evaluate(()=>({duration:designReel.player.playback.duration,starts:designReel.starts,scenes:designReel.player.playback.scenes.current.map(s=>({name:s.name,firstFrame:s.firstFrame,lastFrame:s.lastFrame}))}));
  console.log(JSON.stringify(timing));
  if(timing.duration!==frames)throw Error('Runtime duration '+timing.duration+' expected '+frames);
  if(timing.scenes.length!==count||timing.scenes.some((s,i)=>s.firstFrame!==i*seconds*fps||s.lastFrame!==(i+1)*seconds*fps))throw Error('Scene boundaries do not match the manifest');
  const images=[];
  for(let i=0;i<count;i++)for(const fraction of [.25,.72]){
   const t=seconds*(i+fraction);
   await page.evaluate(t=>designReel.jump(t),t);await page.waitForFunction(f=>designReel.rendered===f,{timeout:30000},Math.round(t*fps));
   const data=await page.evaluate(()=>designReel.stage.finalBuffer.toDataURL('image/png'));
   const label='scene'+String(i+1).padStart(2,'0')+'-'+fraction;
   fs.writeFileSync(path.join(qa,label+'.png'),Buffer.from(data.split(',')[1],'base64'));images.push({label,data});console.log(label);
  }
  await page.setViewport({width:1440,height:1000,deviceScaleFactor:1});
  await page.setContent('<body style="margin:0;background:#ddd"><div style="display:grid;grid-template-columns:repeat(2,720px)">'+images.map(x=>'<div><b>'+x.label+'</b><img width="720" src="'+x.data+'"></div>').join('')+'</div></body>');
  await page.screenshot({path:path.join(qa,'contact-sheet.png'),fullPage:true});
  fs.writeFileSync(path.join(qa,'qa.json'),JSON.stringify({timing,errors,frames,publishReady:false},null,2));
  if(errors.length)throw Error(errors.join('\n'));
  if(process.argv.includes('--qa-only')){console.log('QA: '+qa);return}
  await page.goto('http://localhost:9100/render-worker.html',{waitUntil:'networkidle0'});
  await page.waitForFunction(()=>typeof window.renderVideo==='function');
  await page.evaluate(config=>{window.renderVideo(config).catch(e=>window.renderFailure=String(e.stack??e))},{route:'/src/projects/let-them-play/design-reel/project.ts',name,frames,fps,width:1920,height:1080});
  const start=Date.now();let last=-1,lastChange=start;
  while(true){
   await new Promise(r=>setTimeout(r,3000));state=await page.evaluate(()=>({...window.renderJob,failure:window.renderFailure}));
   if(!Number.isFinite(state.frame)||state.failure||state.errors?.length||errors.length)throw Error(JSON.stringify({state,errors}));
   if(state.frame!==last){lastChange=Date.now();last=state.frame}
   console.log(state.frame+'/'+frames);if(state.done)break;
   if(Date.now()-start>900000||Date.now()-lastChange>120000)throw Error('Render timeout');
  }
  if(state.result!==0)throw Error('Render failed '+state.result);
 }finally{await browser.close()}
 const probe=spawnSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',output],{encoding:'utf8',windowsHide:true});if(probe.status!==0)throw Error(probe.stderr);
 const info=JSON.parse(probe.stdout),v=info.streams.find(s=>s.codec_type==='video');
 if(v.width!==1920||v.height!==1080||Number(v.nb_frames)!==frames||Math.abs(Number(info.format.duration)-seconds*count)>.001||info.streams.some(s=>s.codec_type==='audio'))throw Error('Wrong media format');
 const decode=spawnSync('ffmpeg',['-v','error','-i',output,'-f','null','-'],{encoding:'utf8',windowsHide:true});if(decode.status!==0)throw Error(decode.stderr);
 const report={output,qa,duration:seconds*count,width:1920,height:1080,fps,frames,kind:'silent 8-scene 2.5D opening-design comparisons',fullDecodePassed:true,mainTimelineSeconds:468,publishReady:false};
 fs.writeFileSync(output.replace(/\.mp4$/,'.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
}
main().catch(e=>{console.error(e);process.exitCode=1});
