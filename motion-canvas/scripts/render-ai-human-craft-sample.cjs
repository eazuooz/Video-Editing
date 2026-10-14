// Isolated Motion Canvas renderer. No unrelated project, media or index changes.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..');
const dir=path.join(root,'shared/output/ai-game-development-human-craft/style-sample');fs.mkdirSync(dir,{recursive:true});
const render=process.argv.includes('--render');
const name='ai-human-craft-arrow-sample-v1';
const output=path.join(root,'shared/output/motion-canvas',name+'.mp4');
const run=(cmd,args)=>{const p=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(p.status!==0)throw Error(p.stderr||p.error);return p.stdout;};
async function main(){
 console.log('Launching Motion Canvas render browser');
 const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required'],protocolTimeout:180000,timeout:45000});
 console.log('Render browser ready');
 const page=await browser.newPage(),errors=[];page.on('pageerror',e=>{errors.push(e.message);console.error('Page error:',e.message);});page.on('console',m=>{if(m.type()==='error')console.error('Console:',m.text());});
 try{
  await page.goto('http://127.0.0.1:9197/ai-human-craft-sample.html',{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.sampleReview?.ready,{timeout:45000});
  const timeline=await page.evaluate(()=>({frames:sampleReview.player.playback.duration,scenes:sampleReview.player.playback.scenes.current.map(s=>({name:s.name,firstFrame:s.firstFrame,lastFrame:s.lastFrame}))}));
  const frames=[];
  for(const scene of timeline.scenes){
   for(const ratio of [.12,.38,.64,.9]){
    const frame=Math.round(scene.firstFrame+(scene.lastFrame-scene.firstFrame)*ratio);
    await page.evaluate(f=>sampleReview.player.requestSeek(f),frame);
    await page.waitForFunction(f=>sampleReview.rendered===f,{timeout:30000},frame);
    const data=await page.evaluate(()=>sampleReview.stage.finalBuffer.toDataURL('image/png'));
    const file=path.join(dir,`${scene.name}-${frame}.png`);fs.writeFileSync(file,Buffer.from(data.split(',')[1],'base64'));frames.push({frame,file});
   }
  }
  const captions=['AI에게 골드로 아이템을 구매하는 기능을 만들어 달라고 요청했습니다.','버튼을 누르면 골드가 줄고 아이템이 들어옵니다.','한 번 눌러 봤을 때는 잘 작동합니다.','그런데 골드가 부족하면 어떻게 될까요?','인벤토리가 가득 차 있으면 어떻게 해야 할까요?','버튼을 빠르게 여러 번 누르면 구매가 중복 처리되지는 않을까요?','AI가 요구사항을 읽고, 코드를 수정하고, 테스트를 실행하고, 실패한 부분을 다시 고치도록 구성할 수 있습니다.','AI에게 맡길 일이 많아질수록 무엇을 만들지 구체적으로 설명하고, 결과가 맞는지 판단할 기준을 세우는 일이 필요합니다.'];
  captions[captions.length-1]='바로 여기서 개발자의 이해가 필요합니다.';
  const layout=await page.evaluate(texts=>{const c=document.createElement('canvas').getContext('2d');c.font="500 48px 'Noto Sans KR', 'Malgun Gothic', sans-serif";return texts.map(text=>{const lines=[];let line='';for(const word of text.split(/\s+/)){const next=line?line+' '+word:word;if(line&&c.measureText(next).width>1570){lines.push(line);line=word;}else line=next;}if(line)lines.push(line);return{text,lines,boxBottom:970+(lines.length*62+22)/2+14};});},captions);
  if(layout.some(c=>c.lines.length>2||c.boxBottom>1080))throw Error('Caption overflow');
  if(errors.length)throw Error(errors.join('\n'));
  const report={timeline,frames,captionLayout:layout,errors,kind:'silent-independent-Motion-Canvas-style-sample',unityFootageIncluded:false,wholeVideoComplete:false};
  fs.writeFileSync(path.join(dir,'review.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({timeline,frames:frames.length,captionCheck:'passed'}));
  if(render){
   if(fs.existsSync(output))throw Error('Existing sample preserved. Inspect before choosing a new revision.');
   await page.goto('http://127.0.0.1:9197/render-worker.html',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>typeof renderVideo==='function');
   await page.evaluate(c=>{renderVideo(c).catch(e=>window.renderFailure=String(e.stack??e));},{route:'/src/projects/ai-game-development-human-craft/style-sample/project.ts',name,frames:timeline.frames,fps:60,width:1920,height:1080,exactFrameRange:true});
   let last=-1,changed=Date.now();
   while(true){await new Promise(r=>setTimeout(r,1500));const state=await page.evaluate(()=>({...renderJob,failure:window.renderFailure}));if(state.failure||state.errors.length)throw Error(JSON.stringify(state));if(state.frame!==last){last=state.frame;changed=Date.now();console.log(`frame ${last}/${timeline.frames}`);}if(state.done){if(state.result!==0)throw Error('Exporter failed');break;}if(Date.now()-changed>120000)throw Error('Render stalled');}
   const probe=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',output]));const v=probe.streams.find(s=>s.codec_type==='video');
   if(+v.nb_frames!==timeline.frames||v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1')throw Error('Encoded frame/dimension mismatch '+JSON.stringify(v));
   run('ffmpeg',['-v','error','-i',output,'-f','null','-']);
   report.encoded={output,frames:+v.nb_frames,duration:+probe.format.duration,width:v.width,height:v.height,fps:v.r_frame_rate,fullDecodePassed:true,sha256:crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex')};fs.writeFileSync(path.join(dir,'review.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report.encoded));
  }
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
