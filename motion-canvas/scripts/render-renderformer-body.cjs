// Resumable review render, never a substitute for listening/English/outro approval.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..');
const index=process.argv.indexOf('--pages'),count=index>=0?Number(process.argv[index+1]):88;
if(!Number.isInteger(count)||count<1||count>88)throw Error('Invalid page count');
const tag=count===88?'body-review':`proof-${String(count).padStart(2,'0')}`;
const base=path.join(root,'projects/renderformer-explained/production',tag);
const timing=JSON.parse(fs.readFileSync(path.join(base,'timing.json'),'utf8'));
const projectDir=count===88?'narrated':`proof-${String(count).padStart(2,'0')}`;
function run(command,args){const r=spawnSync(command,args,{cwd:root,windowsHide:true,encoding:'utf8',maxBuffer:16e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;}
const probe=file=>JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file]));
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function checkpoint(value){fs.writeFileSync(path.join(base,'render-progress.json'),JSON.stringify({...value,publishReady:false,updatedAt:new Date().toISOString()},null,2));}
(async()=>{
 const browser=await puppeteer.launch({headless:true,protocolTimeout:240000,args:['--autoplay-policy=no-user-gesture-required']});
 try{
  const page=await browser.newPage();page.on('pageerror',e=>console.error('Browser',e.message));
  await page.goto('http://127.0.0.1:9210/render-worker.html');
  await page.waitForFunction(()=>typeof renderVideo==='function');
  // Test caption wrapping before spending time on a full lecture render.
  const captionFailures=await page.evaluate(captions=>{
   const c=document.createElement('canvas').getContext('2d');c.font="500 44px 'Noto Sans KR', 'Malgun Gothic', sans-serif";
   return captions.filter(cue=>{let n=1,line='';for(const word of cue.ko.split(/\s+/)){const next=line?line+' '+word:word;if(line&&c.measureText(next).width>1540){n++;line=word;}else line=next;}return n>2||cue.end<=cue.start;});
  },timing.captions);
  if(captionFailures.length)throw Error('Invalid caption layout/timing: '+JSON.stringify(captionFailures));
  const nativeCaptions=process.argv.includes('--canvas-captions');
  for(const variant of nativeCaptions?['clean','captioned']:['clean']){
   const final=path.join(base,`renderformer-${variant}-review.mp4`);
   if(fs.existsSync(final)){
    const v=probe(final).streams.find(s=>s.codec_type==='video');
    if(Number(v.nb_frames)!==timing.totalFrames)throw Error('Existing incomplete output: '+final);
    continue;
   }
   const files=[];
   for(let i=0;i<timing.scenes.length;i+=8){
    const group=timing.scenes.slice(i,i+8),first=group[0].firstFrame,frames=group.reduce((n,s)=>n+s.frames,0);
    const name=`renderformer-${tag}-${variant}-${String(i+1).padStart(2,'0')}`;
    const file=path.join(root,'shared/output/motion-canvas',name+'.mp4');files.push(file);
    if(fs.existsSync(file)){
     if(Number(probe(file).streams[0].nb_frames)!==frames)throw Error('Inspect incomplete chunk before resume: '+file);
     continue;
    }
    checkpoint({stage:'rendering',variant,firstPage:i+1,totalPages:count});
    await page.evaluate(config=>{window.renderFailure=null;window.renderJob=null;renderVideo(config).catch(e=>window.renderFailure=String(e.stack||e));},
      {route:`/src/projects/renderformer-explained/full/${projectDir}/${variant==='clean'?'clean':'project'}.ts`,name,firstFrame:first,frames,fps:60,width:1920,height:1080,exactFrameRange:true});
    for(;;){
     await sleep(2000);
     const state=await page.evaluate(()=>({...window.renderJob,failure:window.renderFailure}));
     if(state.failure||state.errors?.length)throw Error(JSON.stringify(state));
     checkpoint({stage:'rendering',variant,firstPage:i+1,frame:state.frame,frames:timing.totalFrames,totalPages:count});
     if(state.done){if(state.result!==0)throw Error(JSON.stringify(state));break;}
    }
    const v=probe(file).streams[0];if(Number(v.nb_frames)!==frames)throw Error(`Rendered chunk frame mismatch: ${file}: expected ${frames}, got ${v.nb_frames}`);
    console.log(`Rendered ${variant} pages ${i+1}..${i+group.length}`,new Date().toISOString());
   }
   const list=path.join(base,`concat-${variant}.txt`);
   fs.writeFileSync(list,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
   run('ffmpeg',['-v','error','-n','-f','concat','-safe','0','-i',list,'-i',path.join(base,'narration-mastered.m4a'),
     '-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',final]);
   const info=probe(final),video=info.streams.find(s=>s.codec_type==='video'),audio=info.streams.find(s=>s.codec_type==='audio');
   if(Number(video.nb_frames)!==timing.totalFrames||!audio||Math.abs(Number(info.format.duration)-timing.duration)>.08)throw Error('Output media mismatch');
   run('ffmpeg',['-v','error','-i',final,'-f','null','-']);
   console.log('Review master ready: '+final);
  }
  if(!nativeCaptions&&count===88&&!fs.existsSync(path.join(base,'renderformer-captioned-review.mp4'))){
   checkpoint({stage:'composing-captions',pages:count,duration:timing.duration});
   run(process.execPath,[path.join(__dirname,'compose-renderformer-captions.cjs')]);
  }
  checkpoint({stage:'body-review-rendered',pages:count,duration:timing.duration,
    pending:['ASR differences and human listening','English subtitle translation','original member screenshot and 10s ending']});
 }finally{await browser.close();}
})().catch(e=>{checkpoint({stage:'failed',error:String(e.stack||e)});console.error(e);process.exitCode=1;});
