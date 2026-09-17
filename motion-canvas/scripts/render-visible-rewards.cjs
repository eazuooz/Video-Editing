// Independent scene QA and deterministic headless rendering. Existing final files are preserved.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),m=require('../../projects/visible-rewards/project.json');
const ts=fs.readFileSync(path.join(root,'motion-canvas/src/projects/visible-rewards/timing.ts'),'utf8');
const nums=name=>JSON.parse('['+ts.match(new RegExp(name+' = \\[([^\\]]+)'))[1].trim().replace(/,$/,'')+']');
const starts=nums('SCENE_STARTS'),durations=nums('SCENE_DURATIONS'),fps=60,frames=Number(ts.match(/TOTAL_FRAMES = (\d+)/)[1]),example=m.editing.exampleSeconds;
const qa=path.join(root,'shared/output/visible-rewards/visual-qa-v1'),out=path.join(root,'shared/output/motion-canvas');fs.mkdirSync(qa,{recursive:true});
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16e6});if(r.status!==0)throw Error(r.stderr);return r.stdout;}
const probe=f=>JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',f]));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,f))).digest('hex');
const protectedPaths=[m.paths.narration,m.paths.captionsKo,m.paths.captionsEn,m.paths.audioMix];
async function main(){
 const before=Object.fromEntries(protectedPaths.map(f=>[f,hash(f)]));
 const browser=await puppeteer.launch({headless:true,protocolTimeout:180000,args:['--autoplay-policy=no-user-gesture-required']}),page=await browser.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto('http://127.0.0.1:9100/visible-rewards-review.html',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.rewardReview?.ready,{timeout:60000});
  const timing=await page.evaluate(()=>({frames:rewardReview.player.playback.duration,scenes:rewardReview.player.playback.scenes.current.map(s=>({name:s.name,start:s.firstFrame,end:s.lastFrame}))}));
  if(timing.frames!==frames||timing.scenes.length!==8)throw Error('Runtime timing mismatch '+JSON.stringify(timing));
  const screens=[];
  for(let i=0;i<8;i++)for(const [part,offset] of [['game-start',3],['game-end',16],['diagram',example+9]]){
   const f=Math.round((starts[i]+offset)*fps);await page.evaluate(f=>rewardReview.jump(f/60),f);await page.waitForFunction(f=>rewardReview.rendered===f,{timeout:60000},f);
   const data=await page.evaluate(()=>rewardReview.stage.finalBuffer.toDataURL('image/png'));const label=`scene${i+1}-${part}`;
   fs.writeFileSync(path.join(qa,label+'.png'),Buffer.from(data.split(',')[1],'base64'));screens.push({label,data});
  }
  await page.evaluate(()=>rewardReview.jump(1));await page.waitForFunction(()=>rewardReview.rendered===60);
  await page.click('#play');await page.waitForFunction(()=>rewardReview.player.audio.audioElement.currentTime>2&&!rewardReview.player.audio.audioElement.paused,{timeout:30000});
  const audio=await page.evaluate(()=>{const a=rewardReview.player.audio.audioElement;rewardReview.player.togglePlayback(false);return {src:a.currentSrc,duration:a.duration,muted:a.muted,volume:a.volume,time:a.currentTime};});
  if(audio.muted||!audio.src.includes('final-mix.wav')||audio.volume<=0)throw Error('Editor mix failed '+JSON.stringify(audio));
  await page.setViewport({width:1440,height:1000});await page.setContent('<body style="margin:0;font:18px sans-serif"><div style="display:grid;grid-template-columns:repeat(3,480px)">'+screens.map(s=>`<div>${s.label}<img width="480" src="${s.data}"></div>`).join('')+'</div>');
  await page.screenshot({path:path.join(qa,'contact.png'),fullPage:true});
  fs.writeFileSync(path.join(qa,'report.json'),JSON.stringify({timing,audio,errors,screens:screens.map(s=>s.label)},null,2));
  if(errors.length)throw Error(errors.join('\n'));console.log('24 visual checks + editor playback captured.');
  if(process.argv.includes('--qa-only'))return;
  const pieces=[];
  for(let i=0;i<8;i++){
   const id=String(i+1).padStart(2,'0'),name='visible-rewards-GRAPHICS-v1-'+id,file=path.join(out,name+'.mp4'),firstFrame=Math.round((starts[i]+example)*fps),count=Math.round((durations[i]-example)*fps);
   let cached=false;
   if(fs.existsSync(file)) {try{cached=Number(probe(file).streams.find(s=>s.codec_type==='video').nb_frames)===count;}catch{}}
   if(!cached){
    if(fs.existsSync(file))fs.renameSync(file,path.join(qa,name+'-partial-'+Date.now()+'.mp4'));
    await page.goto('http://127.0.0.1:9100/render-worker.html',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof renderVideo==='function');
    await page.evaluate(c=>{renderVideo(c).catch(e=>window.renderFailure=String(e.stack??e));},{route:'/src/projects/visible-rewards/project.ts',name,firstFrame,frames:count,fps,width:1920,height:1080});
    let last=-1,changed=Date.now();
    while(true){await new Promise(r=>setTimeout(r,3000));const state=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));if(state.failure||state.errors?.length||errors.length)throw Error(JSON.stringify({state,errors}));if(state.frame!==last){last=state.frame;changed=Date.now();}console.log(`scene${id}: ${last-firstFrame}/${count}`);if(state.done){if(state.result!==0)throw Error('Render cancelled');break;}if(Date.now()-changed>180000)throw Error('Render stalled');}
   }
   const v=probe(file).streams.find(s=>s.codec_type==='video');if(Number(v.nb_frames)!==count)throw Error('Graphic frame mismatch');
   const game=path.join(root,`motion-canvas/src/projects/visible-rewards/assets/gameplay/scene${id}.mp4`),silent=path.join(out,`visible-rewards-GAME-v1-${id}.mp4`);
   const gv=probe(game).streams.find(s=>s.codec_type==='video');if(Number(gv.nb_frames)!==Math.round(example*fps))throw Error('Gameplay frame mismatch '+id);
   run('ffmpeg',['-y','-v','error','-i',game,'-map','0:v','-c','copy','-an',silent]);
   pieces.push({file:silent,frames:Math.round(example*fps)},{file,frames:count});
  }
  const list=path.join(qa,'assembly.ffconcat');fs.writeFileSync(list,'ffconcat version 1.0\n'+pieces.map(p=>`file '${p.file.replaceAll('\\','/')}'\nduration ${(p.frames/fps).toFixed(9)}`).join('\n')+'\n');
  const target=path.join(root,m.paths.videoClean);
  if(fs.existsSync(target))throw Error('Preserving existing final; use a new revision');
  run('ffmpeg',['-n','-v','error','-f','concat','-safe','0','-i',list,'-i',path.join(root,m.paths.audioMix),'-map','0:v','-map','1:a','-c','copy','-movflags','+faststart',target]);
  const p=probe(target),v=p.streams.find(s=>s.codec_type==='video');if(Number(v.nb_frames)!==frames||v.width!==1920||v.height!==1080||Math.abs(Number(v.duration)-frames/fps)>.025)throw Error('Final video verification failed');
  run('ffmpeg',['-v','error','-i',target,'-f','null','-']);
  for(const f of protectedPaths)if(hash(f)!==before[f])throw Error('Protected input changed');
  const audioHash=f=>run('ffmpeg',['-v','error','-i',f,'-map','0:a','-c:a','copy','-f','hash','-hash','sha256','-']).trim();
  if(audioHash(target)!==audioHash(path.join(root,m.paths.audioMix)))throw Error('Audio packets differ');
  fs.writeFileSync(path.join(qa,'render-report.json'),JSON.stringify({target,frames,seconds:frames/fps,fullDecodePassed:true,aacMatchesEditor:true,protectedBefore:before,humanListening:'pending'},null,2));console.log('FINISHED '+target);
 }catch(e){await page.evaluate(()=>window.cancelRender?.()).catch(()=>{});throw e;}finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1});
