// Isolated narrated preview: sample every scene, then render and mux the same editor mix.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const versionArg=process.argv.find(v=>v.startsWith('--version='))||'--version=1';
const version=Number(versionArg.split('=')[1]);if(![1,2].includes(version))throw Error('Use --version=1 or --version=2');
const captionSample=process.argv.includes('--caption-sample'),captioned=process.argv.includes('--captioned'),hasCaptions=captionSample||captioned;
if(hasCaptions&&version!==2)throw Error('Boxed captions require --version=2');
if(captionSample&&captioned)throw Error('Choose sample or full captions, not both');
const folder=captionSample?'caption-sample':captioned?'preview-v2-captioned':version===1?'preview':`preview-v${version}`;
const stem=captionSample?'game-dev-career-caption-sample-v2':`game-dev-career-preview-v${version}${captioned?'-captioned':''}`;
const root=path.resolve(__dirname,'../..'),base=path.join(root,'projects/game-dev-career/preview',version===1?'':`v${version}`,captionSample?'captions':captioned?'captioned':''),assets=path.join(root,`motion-canvas/src/projects/game-dev-career/${captioned?'preview-v2':folder}/assets`);
const fullTiming=require(`../src/projects/game-dev-career/${hasCaptions?'preview-v2':folder}/timing.generated.json`);
const timing=captionSample?{...fullTiming,scenes:fullTiming.scenes.slice(0,1),duration:fullTiming.scenes[0].duration,totalFrames:fullTiming.scenes[0].frames}:fullTiming;
const port=process.argv.find(v=>/^\d{4,5}$/.test(v))||'9191',qaOnly=process.argv.includes('--qa-only');
const qa=path.join(base,`qa-v${version}`);fs.mkdirSync(qa,{recursive:true});
const final=path.join(base,`${stem}.mp4`);
const picture=path.join(root,`shared/output/motion-canvas/${stem}-picture.mp4`);
function run(cmd,args){const p=spawnSync(cmd,args,{cwd:root,windowsHide:true,encoding:'utf8',maxBuffer:32e6});if(p.status!==0)throw Error(p.stderr||p.error);return p.stdout;}
const probe=file=>JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file]));
async function main(){
  const browser=await puppeteer.launch({headless:true,protocolTimeout:180000,args:['--autoplay-policy=no-user-gesture-required']}),page=await browser.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));let rendering=false;
  try{
    await page.setViewport({width:1440,height:1000});
    await page.goto(`http://127.0.0.1:${port}/career-preview.html?v=${version}${captionSample?'&captions=sample':captioned?'&captions=full':''}`,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(()=>window.careerReview?.ready||document.querySelector('#status')?.textContent.startsWith('로딩 실패'),{timeout:60000});
    const startupFailure=await page.evaluate(()=>window.careerReview?.ready?null:document.querySelector('#status')?.textContent);
    if(startupFailure)throw Error(startupFailure);
    const runtime=await page.evaluate(()=>({frames:careerReview.player.playback.duration,scenes:careerReview.player.playback.scenes.current.map(s=>({name:s.name,start:s.firstFrame,end:s.lastFrame}))}));
    if(runtime.frames!==timing.totalFrames||runtime.scenes.length!==timing.scenes.length)throw Error('Timeline mismatch '+JSON.stringify({runtime,expected:timing.totalFrames}));
    const captionLayout=hasCaptions?await page.evaluate(cues=>{
      const c=document.createElement('canvas').getContext('2d');c.font="500 48px 'Noto Sans KR', 'Malgun Gothic', sans-serif";
      return cues.map(cue=>{const lines=[];let line='';for(const word of cue.ko.trim().split(/\s+/)){const next=line?line+' '+word:word;if(line&&c.measureText(next).width>1570){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);return{text:cue.ko,lines,width:Math.ceil(Math.max(...lines.map(l=>c.measureText(l).width)))+44,height:lines.length*62+22};});
    },fullTiming.captions.filter(c=>c.start<timing.duration)):[];
    if(captionLayout.some(c=>c.lines.length>2||c.width>1640||540+430+c.height/2+14>=1080))throw Error('Caption safe area exceeded');
    const images=[];
    for(const s of timing.scenes){
      for(const fraction of (hasCaptions?s.cues.map(c=>(c.start+c.end)/2/s.duration):[.25,.75])){
        const frame=s.firstFrame+Math.round(s.frames*fraction);
        await page.evaluate(t=>careerReview.jump(t),frame/60);
        await page.waitForFunction(f=>careerReview.rendered===f,{timeout:30000},frame);
        const data=await page.evaluate(()=>careerReview.stage.finalBuffer.toDataURL('image/png'));
        const label=hasCaptions?`scene${s.id}-caption-${frame}`:`scene${s.id}-${fraction===.25?'early':'late'}`;
        fs.writeFileSync(path.join(qa,label+'.png'),Buffer.from(data.split(',')[1],'base64'));images.push({label,data});
      }
    }
    await page.evaluate(()=>careerReview.jump(1));await page.waitForFunction(()=>careerReview.rendered===60);
    await page.click('#play');await page.waitForFunction(()=>!careerReview.player.audio.audioElement.paused&&careerReview.player.audio.audioElement.currentTime>1.2,{timeout:30000});
    const audio=await page.evaluate(()=>{const a=careerReview.player.audio.audioElement;careerReview.player.togglePlayback(false);return{src:a.currentSrc,duration:a.duration,time:a.currentTime,muted:a.muted,volume:a.volume};});
    if(audio.muted||audio.volume<=0||!audio.src.includes(`preview-mix-v${version}.wav`))throw Error('Editor audio not audible '+JSON.stringify(audio));
    await page.setContent('<body style="margin:0;font:18px sans-serif"><div style="display:grid;grid-template-columns:repeat(3,480px)">'+images.map(s=>`<div>${s.label}<img width="480" src="${s.data}"></div>`).join('')+'</div>');
    await page.screenshot({path:path.join(qa,'contact.png'),fullPage:true});
    fs.writeFileSync(path.join(qa,'report.json'),JSON.stringify({runtime,audio,captionLayout,errors},null,2));
    if(errors.length)throw Error(errors.join('\n'));
    console.log(`QA passed: ${timing.scenes.length} scenes, ${images.length} views, active unmuted editor audio.`);
    if(qaOnly)return;
    if(fs.existsSync(final))throw Error('Existing delivered preview preserved. Use a new revision.');
    if(fs.existsSync(picture)&&Number(probe(picture).streams[0].nb_frames)!==timing.totalFrames)throw Error('Incomplete earlier picture render: '+picture);
    if(!fs.existsSync(picture)){
      await page.goto(`http://127.0.0.1:${port}/render-worker.html`,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof renderVideo==='function');
      await page.evaluate(config=>{renderVideo(config).catch(e=>window.renderFailure=String(e.stack??e));},{route:`/src/projects/game-dev-career/${folder}/project.ts`,name:`${stem}-picture`,frames:timing.totalFrames,fps:60,width:1920,height:1080});rendering=true;
      let last=-1,change=Date.now();
      while(true){
        await new Promise(resolve=>setTimeout(resolve,3000));const state=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));
        if(state.failure||state.errors?.length||errors.length)throw Error(JSON.stringify({state,errors}));
        if(state.frame!==last){last=state.frame;change=Date.now();}
        console.log(`Render ${last}/${timing.totalFrames}`);
        if(state.done){if(state.result!==0)throw Error('Render failed');rendering=false;break;}
        if(Date.now()-change>180000)throw Error('Render stalled');
      }
    }
    run('ffmpeg',['-v','error','-n','-i',picture,'-i',path.join(assets,`preview-mix-v${version}.m4a`),'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',final]);
    const info=probe(final),v=info.streams.find(s=>s.codec_type==='video'),a=info.streams.find(s=>s.codec_type==='audio');
    if(Number(v.nb_frames)!==timing.totalFrames||Math.abs(+info.format.duration-timing.duration)>.08||!a)throw Error('Final media mismatch');
    run('ffmpeg',['-v','error','-i',final,'-f','null','-']);
    fs.writeFileSync(path.join(base,'render-report.json'),JSON.stringify({kind:'narrated-design-preview-not-full-episode',width:v.width,height:v.height,fps:v.r_frame_rate,frames:+v.nb_frames,duration:+info.format.duration,audioCodec:a.codec_name,bytes:+info.format.size,fullDecodePassed:true,sourceFootageIncluded:false,humanApproval:false},null,2));
    console.log('DELIVERED: '+final);
  }finally{if(rendering)await page.evaluate(()=>window.cancelRender?.()).catch(()=>{});await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
