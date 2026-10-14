const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),version=process.argv[2]||'v1';
if(!/^v\d+$/.test(version))throw Error('Explicit proof version required');
const rel=`production/research/game-lighting-history/local/bvh-proof-${version}`,dir=path.join(root,rel),qa=path.join(dir,'qa'),video=path.join(dir,`bvh-proof-${version}.mp4`);
const ffmpeg=path.join(root,'motion-canvas/node_modules/@ffmpeg-installer/win32-x64/ffmpeg.exe'),ffprobe='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function run(exe,args){const r=spawnSync(exe,args,{encoding:'utf8',windowsHide:true,maxBuffer:16*1024*1024});if(r.status!==0)throw Error(r.stderr);return{command:[exe,...args],exitCode:r.status,stdout:r.stdout,stderr:r.stderr};}
if(fs.existsSync(path.join(qa,'extraction.json')))throw Error('Completed extraction preserved');
fs.mkdirSync(qa,{recursive:true});
const probeRun=run(ffprobe,['-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=codec_name,width,height,r_frame_rate,time_base,duration,nb_frames,nb_read_frames','-of','json',video]);
const probe=JSON.parse(probeRun.stdout).streams[0];if(probe.width!==1920||probe.height!==1080||probe.r_frame_rate!=='60/1'||probe.time_base!=='1/90000')throw Error('Unexpected format');
const decode=run(ffmpeg,['-hide_banner','-v','error','-threads','2','-i',video,'-f','null','NUL']);
const frames=Array.from({length:8},(_,i)=>[30,90,150].map((v,k)=>({paragraph:i+1,pose:['start','middle','end'][k],frame:i*180+v}))).flat();
const extraction=run(ffmpeg,['-hide_banner','-v','error','-threads','2','-i',video,'-vf',`select='${frames.map(f=>`eq(n,${f.frame})`).join('+')}'`,'-vsync','0','-threads','2',path.join(qa,'frame-%02d.png')]);
frames.forEach((f,i)=>{f.path=`${rel}/qa/frame-${String(i+1).padStart(2,'0')}.png`;f.sha256=sha(path.join(root,f.path));});
const boards=[];for(let i=0;i<4;i++){const out=path.join(qa,`board-${i+1}.png`);run(ffmpeg,['-hide_banner','-v','error','-threads','2','-start_number',String(i*6+1),'-i',path.join(qa,'frame-%02d.png'),'-vf','scale=960:540,tile=2x3:nb_frames=6','-frames:v','1','-threads','2',out]);boards.push({path:`${rel}/qa/board-${i+1}.png`,sha256:sha(out),directlyViewed:false});}
const record={createdAt:new Date().toISOString(),video:{path:`${rel}/bvh-proof-${version}.mp4`,sha256:sha(video),...probe},renderedModel:{path:`${rel}/bvh-model-rendered-snapshot.tsx`,sha256:sha(path.join(dir,'bvh-model-rendered-snapshot.tsx'))},plannedFrames:1440,observedFrames:Number(probe.nb_read_frames),endpointDifference:Number(probe.nb_read_frames)-1440,wholeDecode:decode,probeCommand:probeRun.command,extractionCommand:extraction.command,frames,boards,allProofPixelsReviewed:false,finalNarrationTimed:false,finalRendered:false,localOnly:true};
fs.writeFileSync(path.join(qa,'extraction.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({record:`${rel}/qa/extraction.json`,frames:frames.length,boards:boards.length,observedFrames:record.observedFrames,wholeDecode:decode.exitCode}));
