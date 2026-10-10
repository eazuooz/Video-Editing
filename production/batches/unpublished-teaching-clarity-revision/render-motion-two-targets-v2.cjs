// Execute the actual authored JSX geometry with the established CPU adapter.
// This renders only two held visual targets; no audio, source gameplay or UI.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),os=require('node:os'),{spawn,execFileSync}=require('node:child_process'),{once}=require('node:events');
const ROOT=path.resolve(__dirname,'../../..'),MC=path.join(ROOT,'motion-canvas');
const R=path.join(ROOT,'projects/motion-sickness-games/production/revision-teaching-clarity-v1');
const OUT=path.join(ROOT,'shared/output/unpublished-teaching-clarity-revision/motion/two-target-repair-v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const rel=p=>path.relative(ROOT,p).replaceAll('\\','/');
const save=(p,o)=>{fs.writeFileSync(p+'.writing',JSON.stringify(o,null,2)+'\n');fs.renameSync(p+'.writing',p);};
const resource=read(path.resolve(ROOT,process.argv[2]));
if(Date.now()-Date.parse(resource.observedAt)>240000||resource.ownHeavyCpuJobs!==0||resource.cpuLoadPercent>=85||resource.freePhysicalMemoryKiB<=8000000)throw Error('Fresh available resources required');
execFileSync(process.execPath,['scripts/review-video-duplicates.cjs','motion-sickness-games','--check'],{cwd:ROOT,stdio:'inherit'});
const plan=read(path.join(R,'targeted-visual-repair-plan-v2.json'));
for(const v of plan.sources)if(sha(path.join(ROOT,v.source))!==v.sha256)throw Error('Target source changed');
for(const v of read(path.join(R,'narration-tts-waiting-v1.json')).protectedInputs)if(sha(path.join(ROOT,v.path))!==v.sha256)throw Error('Protected input changed');
if(fs.existsSync(OUT))throw Error('Preserve existing execution/output');
fs.mkdirSync(OUT,{recursive:true});
try{os.setPriority(0,os.constants.priority.PRIORITY_BELOW_NORMAL);}catch{}
const ts=require(path.join(MC,'node_modules/typescript'));
const {createCanvas,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules']}));
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun Gothic');GlobalFonts.registerFromPath('C:/Windows/Fonts/malgunbd.ttf','Malgun Gothic Bold');
const adapter=path.join(ROOT,'production/batches/visual-depth-revision/render-depth-cpu.cjs');
let code=fs.readFileSync(adapter,'utf8');code=code.slice(code.indexOf('let time=0;class Node'),code.indexOf('const state='));
const oldCore="if(spec==='@motion-canvas/core')return {linear:x=>x,createSignal:()=>function(value,duration){if(arguments.length===0)return time;return(function*(){yield {duration};})();}};";
if(!code.includes(oldCore))throw Error('Adapter dependency changed');
code=code.replace("return {Node,Txt,Line,Rect,Circle,View2D}","return {Node,Txt,Line,Rect,Circle,View2D,makeScene2D:f=>f}");
code=code.replace(oldCore,`if(spec==='@motion-canvas/core')return {linear:x=>x,createSignal:initial=>{let target=initial,duration=0,start=0;return function(value,seconds){if(arguments.length===0)return initial+(target-initial)*Math.max(0,Math.min(1,duration?(time-start)/duration:0));return(function*(){target=value;duration=seconds;start=time;yield {duration};})();};}};`);
const adapterContext={MC,path,fs,ts,vm,Math,Error,console};
vm.runInNewContext(code+'\nthis.adapterApi={load,draw,View2D,setTime:v=>time=v};',adapterContext,{filename:adapter});
const api=adapterContext.adapterApi,canvas=createCanvas(1920,1080),ctx=canvas.getContext('2d');
const statePath=path.join(R,'two-target-render-execution-v2.json');if(fs.existsSync(statePath))throw Error('Execution already exists');
const state={schemaVersion:1,status:'rendering-only-two-held-targets',startedAt:new Date().toISOString(),pid:process.pid,commandLine:process.argv,cwd:process.cwd(),resource,renderer:'Exact authored Motion Canvas JSX through CPU Canvas adapter with linear signals matching target and duration',adapterPath:rel(adapter),adapterSha256:sha(adapter),cpuThreads:2,gpuJobs:0,pcmOrAudioOrCaptionsOrGameplayChanged:false,completed:[],actualExitCode:null,allFinalPixelsApproved:false};
const checkpoint=()=>{state.updatedAt=new Date().toISOString();save(statePath,state);};checkpoint();
const ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';
(async()=>{
 for(const row of plan.sources){
  const src=path.join(ROOT,row.source),dest=path.join(OUT,`scene-${row.id}.mp4`);api.setTime(0);const view=new api.View2D();const factory=api.load(src).default;factory(view).next();
  const args=['-hide_banner','-loglevel','warning','-f','rawvideo','-pix_fmt','rgba','-s','1920x1080','-r','60','-i','pipe:0','-an','-c:v','libx264','-threads','2','-filter_threads','1','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',dest];
  const p=spawn(ff,args,{windowsHide:true});const log=fs.createWriteStream(path.join(OUT,`scene-${row.id}.ffmpeg.log`));p.stderr.pipe(log);p.stdin.on('error',()=>{});const done=once(p,'close');
  state.activeScene=row.id;state.ffmpegPid=p.pid;state.actualCommand=[ff,...args];checkpoint();
  const samples=new Set([0,row.frames-1,...Array.from({length:Math.ceil(row.frames/60)},(_,i)=>i*60),...(row.id==='02'?[643,1114,1657,1681,1705,1728,1729,1760,1850,2100]:[1,15,150,300])]);
  for(let f=0;f<row.frames;f++){
   api.setTime(f/60);ctx.fillStyle=view.color||'#fff';ctx.fillRect(0,0,1920,1080);ctx.save();ctx.translate(960,540);view.children.forEach(n=>api.draw(ctx,n));ctx.restore();
   if(samples.has(f))fs.writeFileSync(path.join(OUT,`scene-${row.id}-frame-${String(f).padStart(5,'0')}.png`),canvas.toBuffer('image/png'));
   if(!p.stdin.write(canvas.data()))await once(p.stdin,'drain');
   if(f%120===0){state.frame=f;checkpoint();}
  }
  p.stdin.end();const [exit]=await done;log.end();state.completed.push({id:row.id,frames:row.frames,path:rel(dest),sha256:sha(dest),source:row.source,sourceSha256:row.sha256,actualFfmpegExitCode:exit});checkpoint();if(exit!==0)throw Error('FFmpeg target failed');
  console.log(JSON.stringify({scene:row.id,frames:row.frames,actualFfmpegExitCode:exit}));
 }
 state.status='rendered-two-targets-pending-current-captioned-pixels';state.endedAt=new Date().toISOString();state.actualExitCode=0;checkpoint();
})().catch(e=>{state.status='failed';state.error=String(e);state.actualExitCode=1;checkpoint();console.error(e);process.exitCode=1;});
