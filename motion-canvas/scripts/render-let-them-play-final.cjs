// Local Motion Canvas runtime QA and full render; the approved AAC is packet-copied afterwards.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),time=require('../src/projects/let-them-play/timeline.generated.json');
if(!time.voiceAligned||time.creditsFrames!==0)throw Error('Measured timing with description-only credits required');
const fps=time.fps,frames=time.totalFrames,name='let-them-play-V4-PICTURE-20260914',out=path.join(root,'shared/output/motion-canvas',name+'.mp4'),qa=path.join(root,'shared/output/let-them-play/final-visual-qa');
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stdout;}
async function main(){
 fs.mkdirSync(qa,{recursive:true});const browser=await puppeteer.launch({headless:true,protocolTimeout:180000,args:['--autoplay-policy=no-user-gesture-required']}),errors=[];let timing;
 try{
  const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:9100/let-them-play-review.html',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.thirdReview?.ready,{timeout:60000});
  timing=await page.evaluate(()=>({duration:thirdReview.player.playback.duration,scenes:thirdReview.player.playback.scenes.current.map(s=>({name:s.name,firstFrame:s.firstFrame,lastFrame:s.lastFrame}))}));
  if(timing.duration!==frames||timing.scenes.length!==8)throw Error('Wrong runtime '+JSON.stringify(timing));
  for(let i=0;i<8;i++)if(timing.scenes[i].firstFrame!==time.scenes[i].startFrame||timing.scenes[i].lastFrame!==time.scenes[i].startFrame+time.scenes[i].frames)throw Error('Scene boundary mismatch');
  const images=[];
  for(let i=0;i<8;i++)for(let k=0;k<3;k++){
   const frame=time.scenes[i].startFrame+Math.round(time.scenes[i].segmentFrames*(k+.58));
   await page.evaluate(f=>thirdReview.jump(f/60),frame);await page.waitForFunction(f=>thirdReview.rendered===f,{timeout:60000},frame);
   const data=await page.evaluate(()=>thirdReview.stage.finalBuffer.toDataURL('image/png')),label=`scene${i+1}-part${k+1}`;
   fs.writeFileSync(path.join(qa,label+'.png'),Buffer.from(data.split(',')[1],'base64'));images.push({label,data});
  }
  await page.evaluate(()=>thirdReview.jump(1));
  await page.waitForFunction(()=>thirdReview.rendered===60,{timeout:60000});
  await page.waitForFunction(()=>thirdReview.player.audio.onDataChanged.current?.absoluteMax>0,{timeout:60000});
  await page.click('#play');
  await page.waitForFunction(()=>thirdReview.player.audio.audioElement.currentTime>2&&!thirdReview.player.audio.audioElement.paused,{timeout:30000});
  const editorAudio=await page.evaluate(()=>{const a=thirdReview.player.audio,el=a.audioElement;thirdReview.player.togglePlayback(false);return {src:el.currentSrc,seconds:el.duration,playhead:el.currentTime,muted:el.muted,volume:el.volume,waveformPeak:a.onDataChanged.current.absoluteMax};});
  if(editorAudio.muted||editorAudio.volume<=0||!editorAudio.src.includes('final-mix.wav')||Math.abs(editorAudio.seconds-frames/fps)>.05)throw Error('Editor audio failed '+JSON.stringify(editorAudio));
  await page.setViewport({width:1440,height:1000});await page.setContent('<body style="margin:0;background:#ddd"><div style="display:grid;grid-template-columns:repeat(3,480px)">'+images.map(x=>`<div>${x.label}<img width="480" src="${x.data}"></div>`).join('')+'</div></body>');
  await page.screenshot({path:path.join(qa,'contact.png'),fullPage:true});
  fs.writeFileSync(path.join(qa,'report.json'),JSON.stringify({timing,editorAudio,errors,screens:images.map(x=>x.label)},null,2));
  if(errors.length)throw Error(errors.join('\n'));
  console.log('24-point visual QA captured');if(process.argv.includes('--qa-only'))return;
  await page.goto('http://localhost:9100/render-worker.html',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof renderVideo==='function');
  await page.evaluate(c=>{renderVideo(c).catch(e=>window.renderFailure=String(e.stack??e));},{route:'/src/projects/let-them-play/project.ts',name,frames,fps,width:1920,height:1080});
  let last=-1,lastChange=Date.now();const start=Date.now();
  while(true){await new Promise(r=>setTimeout(r,5000));const s=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));
   if(s.failure||s.errors?.length||errors.length)throw Error(JSON.stringify({s,errors}));
   if(s.frame!==last){last=s.frame;lastChange=Date.now();}console.log(`${s.frame}/${frames}`);
   if(s.done){if(s.result!==0)throw Error('Render result '+s.result);break;}
   if(Date.now()-lastChange>180000||Date.now()-start>3600000)throw Error('Render stalled');
  }
 }catch(error){
  for(const page of await browser.pages())await page.evaluate(()=>window.cancelRender?.()).catch(()=>{});
  await new Promise(resolve=>setTimeout(resolve,1000));throw error;
 }finally{await browser.close();}
 const info=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',out]));const v=info.streams.find(s=>s.codec_type==='video');
 if(v.width!==1920||v.height!==1080||Number(v.nb_frames)!==frames)throw Error('Invalid picture stream');
 const m=require('../../projects/let-them-play/project.json'),target=path.join(root,m.paths.videoClean),aac=path.join(root,m.paths.audioMix);
 run('ffmpeg',['-y','-v','error','-i',out,'-i',aac,'-map','0:v','-map','1:a','-c','copy','-t',String(frames/fps),'-movflags','+faststart',target]);
 run('ffmpeg',['-v','error','-i',target,'-f','null','-']);
 const hash=f=>run('ffmpeg',['-v','error','-i',f,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).trim();
 if(hash(target)!==hash(aac))throw Error('AAC packets differ from editor master');
 fs.writeFileSync(path.join(qa,'render-report.json'),JSON.stringify({target,frames,seconds:frames/fps,fullDecodePassed:true,aacPacketsMatch:true,humanListeningApproval:'pending'},null,2));console.log('Finished '+target);
}
main().catch(e=>{console.error(e);process.exitCode=1});
