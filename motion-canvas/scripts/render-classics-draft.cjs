// Explicitly silent visual draft. Never presented as a narrated/BGM final.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),slug='choice-driven-classics';
const board=JSON.parse(fs.readFileSync(path.join(root,'projects',slug,'script/storyboard.json'),'utf8'));
const stamp=new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d+Z$/,'Z');
const withBgm=process.argv.includes('--bgm');
const name=`${slug}-SILENT-VISUAL-DRAFT-${stamp}`;
const output=path.join(root,'shared/output/motion-canvas',`${name}.mp4`);
async function main(){
 if(fs.existsSync(output))throw Error('Unique draft output already exists');
 const browser=await puppeteer.launch({headless:true,protocolTimeout:120000});
 const errors=[];let state;
 try{
  const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:9100/render-worker.html',{waitUntil:'networkidle0',timeout:60000});
  await page.waitForFunction(()=>typeof window.renderVideo==='function');
  await page.evaluate(config=>{window.renderVideo(config).catch(e=>window.renderFailure=String(e.stack??e));},{route:`/src/projects/${slug}/project.ts`,name,frames:3600,fps:60,width:1920,height:1080});
  const started=Date.now();let last=-1,changed=started;
  while(true){
   await new Promise(r=>setTimeout(r,3000));
   state=await page.evaluate(()=>({...window.renderJob,failure:window.renderFailure}));
   if(!Number.isFinite(state.frame))throw Error('Render worker reloaded. Do not edit source files during rendering.');
   if(state.failure||state.errors?.length||errors.length)throw Error(JSON.stringify({state,errors}));
   if(state.frame!==last){changed=Date.now();last=state.frame;}
   console.log(`${state.frame}/3600 frames (silent visual draft)`);
   if(state.done)break;
   if(Date.now()-changed>120000||Date.now()-started>600000)throw Error('Draft render stalled');
  }
  if(state.result!==0)throw Error(`Render result ${state.result}`);
 }finally{await browser.close();}
 const p=spawnSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',output],{encoding:'utf8',windowsHide:true});
 if(p.status!==0)throw Error(p.stderr);
 const info=JSON.parse(p.stdout),v=info.streams.find(s=>s.codec_type==='video');
 if(v.width!==1920||v.height!==1080||Number(v.nb_frames)!==3600||Number(info.format.duration)!==60||info.streams.some(s=>s.codec_type==='audio'))throw Error('Draft format mismatch');
 const decoded=spawnSync('ffmpeg',['-hide_banner','-v','error','-i',output,'-f','null','-'],{encoding:'utf8',windowsHide:true});
 if(decoded.status!==0)throw Error(decoded.stderr);
 fs.writeFileSync(output.replace(/\.mp4$/,'.json'),JSON.stringify({output,kind:'silent visual draft',publishReady:false,narrationIncluded:false,bgmIncluded:false,resultScreenApproval:'pending',duration:60,frames:3600,width:1920,height:1080,fullDecodePassed:true,sceneStarts:board.scenes.map(s=>s.start)},null,2));
 console.log(`DONE (SILENT DRAFT): ${output}`);
 if(withBgm){
  const manifest=JSON.parse(fs.readFileSync(path.join(root,'projects',slug,'project.json'),'utf8'));
  if(manifest.audio.backgroundMusic.approvalStatus!=='approved')throw Error('Music not approved');
  const mixed=output.replace('SILENT-VISUAL-DRAFT','BGM-ONLY-REVIEW');
  const r=spawnSync('ffmpeg',['-hide_banner','-v','error','-n','-i',output,'-i',path.join(root,manifest.paths.audioMix),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','copy','-t','60','-movflags','+faststart',mixed],{encoding:'utf8',windowsHide:true});
  if(r.status!==0)throw Error(r.stderr);
  const checked=spawnSync('ffmpeg',['-hide_banner','-v','error','-i',mixed,'-f','null','-'],{encoding:'utf8',windowsHide:true});
  if(checked.status!==0)throw Error(checked.stderr);
  fs.writeFileSync(mixed.replace(/\.mp4$/,'.json'),JSON.stringify({output:mixed,kind:'BGM-only visual review',narrationIncluded:false,bgmIncluded:true,music:'Childhood — Scott Buckley',publishReady:false,duration:60,fullDecodePassed:true},null,2));
  console.log(`DONE (BGM ONLY, NO NARRATION): ${mixed}`);
 }
}
main().catch(e=>{console.error(e);process.exitCode=1;});
