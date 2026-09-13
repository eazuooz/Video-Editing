// Recover a validated visual prefix; render the remaining timeline in fresh,
// short-lived browser workers. Scene time remains absolute, never restarted.
// node scripts/resume-ai-cs-render.cjs <new | repo-relative-prefix.mp4> [port]
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'shared/output/motion-canvas');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'projects/ai-era-cs-fundamentals/project.json'),'utf8'));
const fresh=(process.argv[2]??'new')==='new',port=process.argv[3]??'9100';
if(!/^\d+$/.test(port))throw Error('Invalid port');
const prefix=fresh?null:path.resolve(root,process.argv[2]);
if(prefix&&(!prefix.startsWith(out+path.sep)||!prefix.endsWith('-visual.mp4')))throw Error('Expected the recovered visual-only prefix');
const stamp=new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d+Z$/,'Z');
const base=fresh?`${manifest.slug}-tts-review-full-${stamp}`:path.basename(prefix).replace(/-visual\.mp4$/,'');
const output=path.join(out,`${base}.mp4`),visual=path.join(out,`${base}-assembled-visual.mp4`);
const cache=path.join(root,'shared/output/ai-cs-media-cache',`${base}-resume`);
fs.mkdirSync(cache,{recursive:true});
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(path.resolve(root,file))).digest('hex');
const inputs=Object.fromEntries([manifest.paths.audioMix,manifest.paths.captionsKo,manifest.paths.captionsEn].map(p=>[p,hash(p)]));
const {fps,width,height}=manifest.video,total=Math.round(manifest.video.durationSeconds*fps);
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:8*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stdout;}
const probe=file=>JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',file]));
function check(file,expected){const p=probe(file),v=p.streams.find(s=>s.codec_type==='video');if(!v||v.width!==width||v.height!==height||v.avg_frame_rate!==`${fps}/1`||expected!==undefined&&+v.nb_frames!==expected)throw Error(`Invalid part ${file}`);return +v.nb_frames;}
async function main(){
 if(fs.existsSync(output)||fs.existsSync(visual))throw Error('Output exists; refuse replacement');
 let cursor=prefix?check(prefix):0;if(cursor<0||cursor>=total)throw Error('Unexpected prefix duration');
 if(prefix)run('ffmpeg',['-hide_banner','-v','error','-i',prefix,'-f','null','-']);
 const inputRecord=path.join(cache,'inputs.json');
 if(fs.existsSync(inputRecord)&&JSON.stringify(JSON.parse(fs.readFileSync(inputRecord,'utf8')))!==JSON.stringify(inputs))throw Error('Inputs changed since checkpoint; render a new job');
 fs.writeFileSync(inputRecord,JSON.stringify(inputs,null,2)+'\n');
 const parts=prefix?[prefix]:[],results=[];
 console.log(`Preserved ${cursor} frames (${cursor/fps}s). Resume exact frame ${cursor}/${total}.`);
 while(cursor<total){
  const frames=Math.min(60*fps,total-cursor),name=`${base}-part-${String(cursor).padStart(6,'0')}`;
  const file=path.join(out,`${name}.mp4`);
  if(fs.existsSync(file)){check(file,frames);console.log(`Reuse verified part ${cursor}`);}
  else{
   console.log(`Rendering frames ${cursor}..${cursor+frames-1}`);
   // The render Promise can run longer than the protocol timeout. Start it
   // without awaiting its return in the page, then poll progress separately.
   await renderPart(cursor,frames,name);
   check(file,frames);
  }
  parts.push(file);results.push({firstFrame:cursor,frames,file:path.relative(root,file).replaceAll('\\','/')});cursor+=frames;
  fs.writeFileSync(path.join(cache,'checkpoint.json'),JSON.stringify({cursor,total,parts,results},null,2));
  console.log(`CHECKPOINT ${cursor}/${total} (${(cursor/total*100).toFixed(1)}%)`);
 }
 const concat=path.join(cache,'parts.txt');
 fs.writeFileSync(concat,parts.map(p=>`file '${p.replaceAll('\\','/').replaceAll("'","'\\''")}'`).join('\n')+'\n');
 run('ffmpeg',['-hide_banner','-v','error','-n','-f','concat','-safe','0','-i',concat,'-c','copy','-movflags','+faststart',visual]);check(visual,total);
 run('ffmpeg',['-hide_banner','-v','error','-n','-i',visual,'-i',path.join(root,manifest.paths.audioMix),'-map','0:v:0','-map','1:a:0','-c','copy','-t',String(total/fps),'-movflags','+faststart',output]);
 const info=probe(output);if(!info.streams.some(s=>s.codec_type==='audio')||Math.abs(+info.format.duration-total/fps)>.05)throw Error('Audio/duration validation failed');
 run('ffmpeg',['-hide_banner','-v','error','-i',output,'-f','null','-']);
 for(const[p,h]of Object.entries(inputs))if(hash(p)!==h)throw Error(`Input changed: ${p}`);
 fs.writeFileSync(output.replace(/\.mp4$/,'.json'),JSON.stringify({createdAt:new Date().toISOString(),scriptRevision:manifest.scriptRevision,kind:`Narration review: ${manifest.audio.mixStatus}; not publish-ready`,duration:total/fps,frames:total,fps,width,height,output:path.relative(root,output).replaceAll('\\','/'),recoveredPrefix:prefix?path.relative(root,prefix).replaceAll('\\','/'):null,parts:results,inputsSha256:inputs,fullDecodePassed:true},null,2)+'\n');
 console.log(`DONE: ${output}`);
}
async function renderPart(firstFrame,frames,name){
 const browser=await puppeteer.launch({headless:true,protocolTimeout:20000,args:['--autoplay-policy=no-user-gesture-required']});
 const page=await browser.newPage();let failure,finished=false;
 page.on('error',e=>failure=`Worker crashed: ${e.message}`);page.on('pageerror',e=>failure=e.message);
 try{
  await page.goto(`http://localhost:${port}/render-worker.html`,{waitUntil:'networkidle0',timeout:60000});
  await page.waitForFunction(()=>typeof window.renderVideo==='function');
  await page.evaluate(c=>{window.renderVideo(c).catch(e=>window.renderFailure=String(e.stack??e));},{route:'/src/projects/ai-era-cs-fundamentals/project.ts',name,frames,fps,width,height,firstFrame});
  let last=-1,lastChanged=Date.now();
  while(true){
   await new Promise(r=>setTimeout(r,5000));
   if(failure)throw Error(failure);
   const state=await page.evaluate(()=>({...window.renderJob,failure:window.renderFailure}));
   if(state.failure||state.errors?.length)throw Error(JSON.stringify(state));
   if(state.frame!==last){last=state.frame;lastChanged=Date.now();}
   console.log(JSON.stringify({frame:state.frame,total,percent:+(state.frame/total*100).toFixed(1),partStart:firstFrame}));
   if(state.done){if(state.result!==0)throw Error(`Renderer ${state.result}`);finished=true;break;}
   if(Date.now()-lastChanged>60000)throw Error('Part stalled');
  }
 }finally{
  if(!finished){try{await page.evaluate(()=>window.cancelRender?.());await page.waitForFunction(()=>window.renderJob?.done,{timeout:10000});}catch(_){}}
  await browser.close();
 }
}
main().catch(e=>{console.error(e);process.exitCode=1;});
