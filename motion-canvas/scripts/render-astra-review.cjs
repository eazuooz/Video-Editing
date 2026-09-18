// Local-only picture review. Source permissions, narration and music remain pending.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),plan=require('../../projects/gpt-astra-showcase/planning/edit-plan.json');
const manifest=require('../../projects/gpt-astra-showcase/project.json');
const port=process.argv.find(x=>/^\d{4,5}$/.test(x))||'9101';
const qaOnly=process.argv.includes('--qa-only');
const version=plan.version;
const base=path.join(root,'projects/gpt-astra-showcase/review');fs.mkdirSync(base,{recursive:true});
const finalAudioReady=manifest.paths.editorAudioMix&&fs.existsSync(path.join(root,manifest.paths.editorAudioMix));
const qa=path.join(base,`qa-v${version}${finalAudioReady?'-narrated':''}`);fs.mkdirSync(qa,{recursive:true});
const output=path.join(root,'shared/output/motion-canvas');
const target=path.join(base,`astra-picture-review-v${version}.mp4`);
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;}
const probe=f=>JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',f]));
const frames=plan.durationSeconds*60,seconds=s=>s.cuts.reduce((n,c)=>n+c.out-c.in,0);
const starts=[];let time=0;for(const s of plan.scenes){starts.push(time);time+=s.duration;}
async function main(){
  if(!qaOnly&&fs.existsSync(target))throw Error('Existing review preserved; make a new revision before replacing it.');
  const browser=await puppeteer.launch({headless:true,protocolTimeout:180000,args:['--autoplay-policy=no-user-gesture-required']}),page=await browser.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));let active=false;
  try{
    await page.goto(`http://127.0.0.1:${port}/astra-review.html`,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForFunction(()=>window.astraReview?.ready,{timeout:60000});
    const timing=await page.evaluate(()=>({frames:astraReview.player.playback.duration,scenes:astraReview.player.playback.scenes.current.map(s=>({name:s.name,start:s.firstFrame,end:s.lastFrame}))}));
    if(timing.frames!==frames||timing.scenes.length!==10)throw Error('Runtime timing mismatch '+JSON.stringify(timing));
    const screens=[];
    for(let i=0;i<plan.scenes.length;i++){
      const example=seconds(plan.scenes[i]);
      const remaining=plan.scenes[i].duration-example;
      const offsets=example?[['example',3],...(remaining>0?[['explanation',example+Math.min(2,remaining*.6)]]:[['example-end',example-.1]])]:[['explanation',4]];
      for(const [part,offset] of offsets){
        const f=Math.round((starts[i]+offset)*60);await page.evaluate(f=>astraReview.jump(f/60),f);await page.waitForFunction(f=>astraReview.rendered===f,{timeout:60000},f);
        const data=await page.evaluate(()=>astraReview.stage.finalBuffer.toDataURL('image/png')),label=`scene${plan.scenes[i].id}-${part}`;
        fs.writeFileSync(path.join(qa,label+'.png'),Buffer.from(data.split(',')[1],'base64'));screens.push({label,data});
      }
    }
    await page.evaluate(()=>astraReview.jump(20));await page.waitForFunction(()=>astraReview.rendered===1200);
    await page.click('#play');await page.waitForFunction(()=>!astraReview.player.audio.audioElement.paused&&astraReview.player.audio.audioElement.currentTime>20.1,{timeout:30000});
    const audio=await page.evaluate(()=>{const a=astraReview.player.audio.audioElement;astraReview.player.togglePlayback(false);return{src:a.currentSrc,duration:a.duration,muted:a.muted,volume:a.volume,time:a.currentTime};});
    const expectedAudio=finalAudioReady?path.basename(manifest.paths.editorAudioMix):`review-source-only-v${version}.wav`;
    if(audio.muted||audio.volume<=0||!audio.src.includes(expectedAudio))throw Error('Review audio not connected: '+expectedAudio);
    await page.setViewport({width:1440,height:1000});await page.setContent('<body style="margin:0;font:18px sans-serif"><div style="display:grid;grid-template-columns:repeat(3,480px)">'+screens.map(s=>`<div>${s.label}<img width="480" src="${s.data}"></div>`).join('')+'</div>');await page.screenshot({path:path.join(qa,'contact.png'),fullPage:true});
    fs.writeFileSync(path.join(qa,'report.json'),JSON.stringify({publishReady:false,timing,audio,errors,screens:screens.map(s=>s.label)},null,2));
    if(errors.length)throw Error(errors.join('\n'));console.log('QA: '+screens.length+' scene views and '+expectedAudio+' editor audio captured.');
    if(qaOnly)return;
    const pieces=[];
    for(let i=0;i<plan.scenes.length;i++){
      const scene=plan.scenes[i],example=seconds(scene),count=Math.round((scene.duration-example)*60),firstFrame=Math.round((starts[i]+example)*60);
      if(example)pieces.push(path.join(root,`motion-canvas/src/projects/gpt-astra-showcase/assets/examples/scene${scene.id}.mp4`));
      if(count===0)continue;
      const name=`astra-review-v${version}-graphics-${scene.id}`,file=path.join(output,name+'.mp4');
      if(fs.existsSync(file)&&Number(probe(file).streams[0].nb_frames)!==count)throw Error('Partial render exists: '+file);
      if(!fs.existsSync(file)){
        await page.goto(`http://127.0.0.1:${port}/render-worker.html`,{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof renderVideo==='function');
        await page.evaluate(c=>{renderVideo(c).catch(e=>window.renderFailure=String(e.stack??e));},{route:'/src/projects/gpt-astra-showcase/project.ts',name,firstFrame,frames:count,fps:60,width:1920,height:1080});active=true;
        let last=-1,changed=Date.now();
        while(true){await new Promise(r=>setTimeout(r,3000));const state=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));if(state.failure||state.errors?.length||errors.length)throw Error(JSON.stringify({state,errors}));if(state.frame!==last){last=state.frame;changed=Date.now();}console.log(`scene${scene.id}: ${last-firstFrame}/${count}`);if(state.done){if(state.result!==0)throw Error('Renderer failed');active=false;break;}if(Date.now()-changed>180000)throw Error('Render stalled');}
      }
      if(Number(probe(file).streams[0].nb_frames)!==count)throw Error('Wrong graphic frame count');pieces.push(file);
    }
    const list=path.join(base,`review-v${version}.ffconcat`);fs.writeFileSync(list,'ffconcat version 1.0\n'+pieces.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n')+'\n');
    run('ffmpeg',['-v','error','-n','-f','concat','-safe','0','-i',list,'-i',path.join(root,`motion-canvas/src/projects/gpt-astra-showcase/assets/review-source-only-v${version}.wav`),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',target]);
    const info=probe(target),video=info.streams.find(s=>s.codec_type==='video');
    if(Number(video.nb_frames)!==frames||Math.abs(+info.format.duration-plan.durationSeconds)>.06)throw Error('Review duration or frame count mismatch');
    run('ffmpeg',['-v','error','-i',target,'-f','null','-']);
    fs.writeFileSync(path.join(base,`render-report-v${version}.json`),JSON.stringify({publishReady:false,kind:'picture-review-source-only-no-tts-no-bgm',target,frames,duration:+info.format.duration,width:video.width,height:video.height,fullDecodePassed:true,rights:'pending',humanFullWatch:'pending'},null,2));
    console.log('DONE (internal picture review, NOT final): '+target);
  }finally{if(active)await page.evaluate(()=>window.cancelRender?.()).catch(()=>{});await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
