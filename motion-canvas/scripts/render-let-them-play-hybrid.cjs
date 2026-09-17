// Preserve approved gameplay frames; render only the two original graphic thirds.
// All pieces are 1080p60 H.264; concat explicitly uses frame-measured durations.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),m=require('../../projects/let-them-play/project.json'),t=require('../src/projects/let-them-play/timeline.generated.json');
const output=path.join(root,'shared/output/motion-canvas'),qa=path.join(root,'shared/output/let-them-play/final-visual-qa');
const revision=m.visualRevision??4;
const protectedPaths=[m.paths.audioMix,m.paths.editorAudioMix,m.paths.captionsKo,m.paths.captionsEn,m.paths.timeline,m.paths.script,...t.scenes.map(s=>`motion-canvas/src/projects/let-them-play/assets/broll-archive64/scene${s.id}.mp4`)];
const hashFile=f=>require('node:crypto').createHash('sha256').update(fs.readFileSync(path.join(root,f))).digest('hex');
const protectedBefore=Object.fromEntries(protectedPaths.map(f=>[f,hashFile(f)]));
if(!t.voiceAligned||t.creditsFrames!==0)throw Error('Measured credit-free timeline required');
function visualFiles(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.name==='assets'?[]:e.isDirectory()?visualFiles(path.join(dir,e.name)):/\.(ts|tsx|json|meta)$/.test(e.name)?[path.join(dir,e.name)]:[]);}
const sourceFiles=[...visualFiles(path.join(root,'motion-canvas/src/projects/let-them-play')),path.join(root,'projects/let-them-play/planning/scenes.json'),path.join(root,'motion-canvas/src/styles/research-paper.ts')].sort();
const sourceHash=require('node:crypto').createHash('sha256').update(sourceFiles.map(f=>f+'\n'+fs.readFileSync(f,'utf8')).join('\n')).digest('hex');
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stdout;}
const probe=f=>JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',f]));
function valid(f,frames){if(!fs.existsSync(f))return false;try{const p=probe(f),v=p.streams.find(s=>s.codec_type==='video');return v.width===1920&&v.height===1080&&v.r_frame_rate==='60/1'&&v.time_base==='1/15360'&&Number(v.nb_frames)===frames;}catch{return false;}}
async function main(){
 const visual=JSON.parse(fs.readFileSync(path.join(qa,'report.json'),'utf8'));
 if(visual.errors.length||visual.screens.length!==24||visual.timing.duration!==t.totalFrames||visual.editorAudio.muted)throw Error('Run and inspect 24-point visual/audio QA first');
 const browser=await puppeteer.launch({headless:true,protocolTimeout:180000,args:['--autoplay-policy=no-user-gesture-required']}),page=await browser.newPage(),errors=[],pieces=[];
 page.on('pageerror',e=>errors.push(e.message));
 try{
  for(const s of t.scenes){
   const game=path.join(root,`motion-canvas/src/projects/let-them-play/assets/broll-archive64/scene${s.id}.mp4`),name=`let-them-play-V${revision}-GRAPHICS-${s.id}-20260914`,file=path.join(output,name+'.mp4'),count=s.segmentFrames*2,start=s.startFrame+s.segmentFrames;
   if(!valid(game,s.segmentFrames))throw Error('Invalid measured gameplay '+game);
   const cacheFile=file+'.render.json';let cache={};try{cache=JSON.parse(fs.readFileSync(cacheFile,'utf8'));}catch{}
   if(!valid(file,count)||cache.sourceHash!==sourceHash||cache.startFrame!==start){
    await page.goto('http://localhost:9100/render-worker.html',{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(()=>typeof renderVideo==='function',{timeout:60000});
    await page.evaluate(c=>{renderVideo(c).catch(e=>window.renderFailure=String(e.stack??e));},{route:'/src/projects/let-them-play/project.ts',name,firstFrame:start,frames:count,fps:60,width:1920,height:1080});
    let last=-1,changed=Date.now();
    while(true){
     await new Promise(r=>setTimeout(r,3000));const state=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));
     if(state.failure||state.errors?.length||errors.length)throw Error(JSON.stringify({state,errors}));
     if(state.frame!==last){last=state.frame;changed=Date.now();}console.log(`scene${s.id}: ${Math.max(0,last-start)}/${count}`);
     if(state.done){if(state.result!==0)throw Error('Render cancelled');break;}
     if(Date.now()-changed>180000)throw Error('Render stalled');
    }
    if(!valid(file,count))throw Error('Wrong graphic frame count '+file);
    fs.writeFileSync(cacheFile,JSON.stringify({sourceHash,startFrame:start,frames:count},null,2));
   }
   // Use a uniform single-video-stream layout for the concat demuxer.
   // Original source audio stays in the approved AAC mix and original clip.
   const silentGame=path.join(output,`let-them-play-V${revision}-GAME-${s.id}-20260914.mp4`);
   run('ffmpeg',['-y','-v','error','-i',game,'-map','0:v:0','-c:v','copy','-an','-movflags','+faststart',silentGame]);
   if(!valid(silentGame,s.segmentFrames))throw Error('Invalid source packet copy');
   pieces.push({file:silentGame,source:game,frames:s.segmentFrames},{file,frames:count});
  }
 }catch(e){await page.evaluate(()=>window.cancelRender?.()).catch(()=>{});await new Promise(r=>setTimeout(r,1000));throw e;}
 finally{await browser.close();}
 const list=path.join(qa,'assembly.ffconcat');
 fs.writeFileSync(list,'ffconcat version 1.0\n'+pieces.map(p=>`file '${p.file.replaceAll('\\','/')}'\nduration ${(p.frames/60).toFixed(9)}`).join('\n')+'\n');
 const target=path.join(root,m.paths.videoClean),aac=path.join(root,m.paths.audioMix),temporary=path.join(output,`let-them-play-V${revision}-ASSEMBLED-REVIEW.mp4`);
 run('ffmpeg',['-y','-v','error','-f','concat','-safe','0','-i',list,'-i',aac,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',temporary]);
 if(!valid(temporary,t.totalFrames))throw Error('Invalid assembled frames');
 const p=probe(temporary),v=p.streams.find(s=>s.codec_type==='video');
 if(Math.abs(Number(v.duration)-t.totalFrames/60)>.02)throw Error('Picture duration drift');
 run('ffmpeg',['-v','error','-i',temporary,'-f','null','-']);
 const hash=f=>run('ffmpeg',['-v','error','-i',f,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).trim();
 if(hash(temporary)!==hash(aac))throw Error('AAC packets differ');
 for(const [f,h] of Object.entries(protectedBefore))if(hashFile(f)!==h)throw Error('Protected input changed: '+f);
 const backup=path.join(root,`shared/output/let-them-play/editorial-full-v${revision}/before-editorial.mp4`);
 fs.mkdirSync(path.dirname(backup),{recursive:true});if(!fs.existsSync(backup))fs.copyFileSync(target,backup);
 fs.renameSync(temporary,target);
 fs.writeFileSync(path.join(qa,'render-report.json'),JSON.stringify({target,visualRevision:revision,backup,protectedBefore,protectedInputsUnchanged:true,sourceHash,method:'Original 1080p60 gameplay + Motion Canvas graphic thirds, H.264 packet copy with explicit frame durations',pieces,frames:t.totalFrames,seconds:t.totalFrames/60,fullDecodePassed:true,aacPacketsMatch:true,creditsFrames:0,humanListeningApproval:'pending; scene08 ending review'},null,2));
 console.log('Finished '+target);
}
main().catch(e=>{console.error(e);process.exitCode=1});
