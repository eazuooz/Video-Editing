const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),base=path.join(root,'projects/renderformer-explained/preview');
const assets=path.join(root,'motion-canvas/src/projects/renderformer-explained/preview/assets');
const timing=require('../src/projects/renderformer-explained/preview/timing.generated.json');
const port=process.argv.find(a=>/^\d{4,5}$/.test(a))||'9210',qaOnly=process.argv.includes('--qa-only');
const qa=path.join(base,'qa'),picture=path.join(root,'shared/output/motion-canvas/renderformer-preview-v1-picture.mp4'),final=path.join(base,process.argv.includes('--mastered')?'renderformer-preview-v1-mastered.mp4':'renderformer-preview-v1.mp4');
fs.mkdirSync(qa,{recursive:true});
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,windowsHide:true,encoding:'utf8',maxBuffer:32e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;}
const probe=f=>JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',f]));
(async()=>{
const browser=await puppeteer.launch({headless:true,protocolTimeout:180000,args:['--autoplay-policy=no-user-gesture-required']}),page=await browser.newPage(),errors=[];
page.on('pageerror',e=>errors.push(e.message));
try{
 await page.setViewport({width:1600,height:1100});
 await page.goto(`http://127.0.0.1:${port}/renderformer-preview.html`,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.lectureReview?.ready,{timeout:60000});
 const runtime=await page.evaluate(()=>({frames:lectureReview.player.playback.duration,scenes:lectureReview.player.playback.scenes.current.map(s=>({name:s.name,start:s.firstFrame,end:s.lastFrame}))}));
 if(runtime.frames!==timing.totalFrames||runtime.scenes.length!==3)throw Error('Timeline mismatch '+JSON.stringify(runtime));
 const layouts=await page.evaluate(cues=>{const c=document.createElement('canvas').getContext('2d');c.font="500 44px 'Noto Sans KR', 'Malgun Gothic', sans-serif";return cues.map(cue=>{const lines=[];let l='';for(const w of cue.ko.split(/\s+/)){let next=l?l+' '+w:w;if(l&&c.measureText(next).width>1540){lines.push(l);l=w;}else l=next;}if(l)lines.push(l);let h=lines.length*58+22;return{ko:cue.ko,lines,top:940-h/2,bottom:940+h/2+14};});},timing.captions);
 if(layouts.some(l=>l.lines.length>2||l.top<860||l.bottom>1060))throw Error('Caption outside safe area '+JSON.stringify(layouts));
 for(let i=0;i<timing.captions.length;i++){
   const cue=timing.captions[i],frame=Math.round((cue.start+cue.end)/2*60);
   await page.evaluate(t=>lectureReview.jump(t),frame/60);await page.waitForFunction(f=>lectureReview.rendered===f,{timeout:30000},frame);
   const image=await page.evaluate(()=>lectureReview.stage.finalBuffer.toDataURL('image/png'));
   fs.writeFileSync(path.join(qa,`cue-${String(i+1).padStart(2,'0')}.png`),Buffer.from(image.split(',')[1],'base64'));
 }
 await page.evaluate(()=>lectureReview.jump(1));await page.waitForFunction(()=>lectureReview.rendered===60);
 await page.click('#play');await page.waitForFunction(()=>!lectureReview.player.audio.audioElement.paused&&lectureReview.player.audio.audioElement.currentTime>1.2,{timeout:15000});
 const audio=await page.evaluate(()=>{const a=lectureReview.player.audio.audioElement;lectureReview.player.togglePlayback(false);return{src:a.currentSrc,duration:a.duration,time:a.currentTime,muted:a.muted,volume:a.volume};});
 if(audio.muted||audio.volume<=0||!audio.src.includes('preview-narration.wav'))throw Error('Editor audio failure');
 if(errors.length)throw Error(errors.join('\n'));
 fs.writeFileSync(path.join(qa,'report.json'),JSON.stringify({runtime,audio,layouts,errors},null,2));
 console.log('QA passed: 3 scenes, 11 cues, audible editor track.');
 if(qaOnly)return;
 if(fs.existsSync(final))throw Error('Existing preview preserved; use a new revision.');
 if(fs.existsSync(picture)&&Number(probe(picture).streams[0].nb_frames)!==timing.totalFrames)throw Error('Incomplete earlier render needs inspection');
 if(!fs.existsSync(picture)){
   await page.goto(`http://127.0.0.1:${port}/render-worker.html`);await page.waitForFunction(()=>typeof renderVideo==='function');
   await page.evaluate(config=>renderVideo(config).catch(e=>window.renderFailure=String(e.stack||e)),{route:'/src/projects/renderformer-explained/preview/project.ts',name:'renderformer-preview-v1-picture',frames:timing.totalFrames,fps:60,width:1920,height:1080});
   const state=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));
   if(state.failure||state.errors.length||state.result!==0||!state.done)throw Error(JSON.stringify(state));
 }
 run('ffmpeg',['-v','error','-n','-i',picture,'-i',path.join(assets,'preview-narration.m4a'),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',final]);
 const info=probe(final),v=info.streams.find(s=>s.codec_type==='video'),a=info.streams.find(s=>s.codec_type==='audio');
 if(Number(v.nb_frames)!==timing.totalFrames||!a||Math.abs(+info.format.duration-timing.duration)>.08)throw Error('Media timing mismatch');
 run('ffmpeg',['-v','error','-i',final,'-f','null','-']);
 fs.writeFileSync(path.join(base,'render-report.json'),JSON.stringify({file:final,kind:'narrated-three-page-preview-not-full-episode',width:v.width,height:v.height,fps:v.r_frame_rate,duration:+info.format.duration,frames:+v.nb_frames,audioCodec:a.codec_name,fullDecodePassed:true,bgmIncluded:false,humanApproval:false},null,2));
 console.log('DELIVERED: '+final);
}finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
