const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),base=path.join(root,'projects/game-dev-career/production'),mc=path.join(root,'motion-canvas/src/projects/game-dev-career');
const timing=require(path.join(mc,'timing.generated.json')),manifest=require(path.join(root,'projects/game-dev-career/project.json'));
const suffix=manifest.production.revision>1?'-v'+manifest.production.revision:'';
const qa=path.join(base,'qa-final'+suffix);fs.mkdirSync(qa,{recursive:true});
const audioMaster=path.join(root,manifest.paths.audioMix);
const qaOnly=process.argv.includes('--qa-only'),renderOnly=process.argv.includes('--render-only'),cleanOnly=process.argv.includes('--clean-only'),captionOnly=process.argv.includes('--caption-only');
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,windowsHide:true,encoding:'utf8',maxBuffer:32e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;}
const probe=file=>JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file]));
async function main(){
 const browser=await puppeteer.launch({headless:true,protocolTimeout:180000,args:['--autoplay-policy=no-user-gesture-required']}),page=await browser.newPage(),errors=[];let rendering=false;
 page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.setViewport({width:1440,height:1050});
  if(!renderOnly){
   await page.goto('http://127.0.0.1:9191/career-final.html',{waitUntil:'domcontentloaded',timeout:60000});
   await page.waitForFunction(()=>window.careerReview?.ready||document.querySelector('#status')?.textContent.startsWith('로딩 실패'),{timeout:60000});
   const runtime=await page.evaluate(()=>({frames:careerReview.player.playback.duration,scenes:careerReview.player.playback.scenes.current.map(s=>({name:s.name,start:s.firstFrame,end:s.lastFrame}))}));
   if(runtime.frames!==timing.totalFrames||runtime.scenes.length!==9)throw Error('Timeline mismatch '+JSON.stringify(runtime));
   await page.evaluate(()=>document.fonts.ready);
   const layout=await page.evaluate(({cues,y})=>{
    const c=document.createElement('canvas').getContext('2d');c.font="500 48px 'Noto Sans KR', 'Malgun Gothic', sans-serif";
    return cues.map(cue=>{let line='';const lines=[];for(const word of cue.ko.split(/\s+/)){const next=line?line+' '+word:word;if(line&&c.measureText(next).width>1570){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);const height=lines.length*62+22;return{text:cue.ko,lines,width:Math.max(...lines.map(l=>c.measureText(l).width))+44,height,bottomMargin:540-y-height/2-14-1.5};});
   },{cues:timing.captions,y:manifest.editing.captionStyle.centerYPx});
   if(layout.some(l=>l.lines.length>2||l.bottomMargin<45||l.width>1640))throw Error('Caption safe area failed');
   const images=[];
   for(const s of timing.scenes){
    const times=[4,14,Math.min(s.duration-2,22),s.duration*.78];
    for(let i=0;i<times.length;i++){
     const frame=s.firstFrame+Math.round(times[i]*60);await page.evaluate(t=>careerReview.jump(t),frame/60);await page.waitForFunction(f=>careerReview.rendered===f,{timeout:40000},frame);
     const data=await page.evaluate(()=>careerReview.stage.finalBuffer.toDataURL('image/png'));const label=`${s.id}-${i+1}`;fs.writeFileSync(path.join(qa,label+'.png'),Buffer.from(data.split(',')[1],'base64'));images.push({label,data});
    }
   }
   await page.evaluate(()=>careerReview.jump(1));await page.waitForFunction(()=>careerReview.rendered===60);await page.click('#play');await page.waitForFunction(()=>!careerReview.player.audio.audioElement.paused&&careerReview.player.audio.audioElement.currentTime>1.4,{timeout:30000});
   const audio=await page.evaluate(()=>{const a=careerReview.player.audio.audioElement;careerReview.player.togglePlayback(false);return{src:a.currentSrc,duration:a.duration,time:a.currentTime,muted:a.muted,volume:a.volume};});
   if(audio.muted||audio.volume<=0||!audio.src.includes(path.basename(manifest.paths.editorAudioMix)))throw Error('Editor audio failed');
   for(let k=0;k<3;k++){
    await page.setContent('<body style="margin:0;font:20px sans-serif"><div style="display:grid;grid-template-columns:repeat(3,480px)">'+images.slice(k*12,k*12+12).map(s=>`<div>${s.label}<img width="480" src="${s.data}"></div>`).join('')+'</div>');
    await page.screenshot({path:path.join(qa,`contact-${k+1}.png`),fullPage:true});
   }
   fs.writeFileSync(path.join(qa,'report.json'),JSON.stringify({runtime,layout,audio,errors},null,2));if(errors.length)throw Error(errors.join('\n'));
   console.log(`QA PASS: 9 scenes / ${layout.length} captions / minimum bottom margin ${Math.min(...layout.map(l=>l.bottomMargin))}px / live audio.`);
  }
  if(qaOnly)return;
  const outputs=captionOnly?['captioned']:cleanOnly?['clean']:['clean','captioned'];
  for(const kind of outputs){
   const clean=kind==='clean',stem='game-dev-career'+suffix+(clean?'':'-subtitled'),name=stem+'-picture',picture=path.join(root,'shared/output/motion-canvas',name+'.mp4'),final=path.join(root,manifest.paths[clean?'videoClean':'videoBurnedCaptions']);
   if(fs.existsSync(final)){const info=probe(final);if(Number(info.streams.find(s=>s.codec_type==='video').nb_frames)!==timing.totalFrames)throw Error('Existing incompatible output preserved');console.log('Already rendered: '+final);continue;}
   if(!fs.existsSync(picture)){
    await page.goto('http://127.0.0.1:9191/render-worker.html',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof renderVideo==='function');
    await page.evaluate(config=>{renderVideo(config).catch(e=>window.renderFailure=String(e.stack??e));},{route:`/src/projects/game-dev-career/${clean?'clean':'project'}.ts`,name,frames:timing.totalFrames,fps:60,width:1920,height:1080});rendering=true;
    let last=-1,change=Date.now();
    while(true){await new Promise(r=>setTimeout(r,3000));const state=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));if(state.failure||state.errors?.length||errors.length)throw Error(JSON.stringify({state,errors}));if(state.frame!==last){last=state.frame;change=Date.now();}console.log(`${kind}: ${last}/${timing.totalFrames}`);if(state.done){if(state.result!==0)throw Error('Render failed');rendering=false;break;}if(Date.now()-change>180000)throw Error('Render stalled');}
   }
   const pv=probe(picture).streams.find(s=>s.codec_type==='video');if(Number(pv.nb_frames)!==timing.totalFrames)throw Error('Incomplete picture preserved: '+picture);
   run('ffmpeg',['-v','error','-n','-i',picture,'-i',audioMaster,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',final]);
   const info=probe(final),v=info.streams.find(s=>s.codec_type==='video'),a=info.streams.find(s=>s.codec_type==='audio');
   if(+v.nb_frames!==timing.totalFrames||Math.abs(+info.format.duration-timing.duration)>.08||!a||v.width!==1920||v.height!==1080)throw Error('Invalid final media');
   run('ffmpeg',['-v','error','-i',final,'-f','null','-']);
   const hash=run('ffmpeg',['-v','error','-i',final,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']);const masterHash=run('ffmpeg',['-v','error','-i',audioMaster,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']);if(hash!==masterHash)throw Error('Audio packet mismatch');
   fs.writeFileSync(path.join(base,`render-${kind}${suffix}.json`),JSON.stringify({file:final,frames:+v.nb_frames,duration:+info.format.duration,fps:v.r_frame_rate,width:v.width,height:v.height,audioCodec:a.codec_name,bytes:+info.format.size,fullDecodePassed:true,audioPacketsIdentical:true,captionY:clean?null:manifest.editing.captionStyle.centerYPx,humanListeningApproval:false},null,2));console.log('DELIVERED '+final);
  }
 }finally{if(rendering)await page.evaluate(()=>window.cancelRender?.()).catch(()=>{});await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
