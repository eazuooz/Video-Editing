const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),rel='production/research/game-lighting-history/local/cache-spatial-proof-v1',dir=path.join(root,rel),qa=path.join(dir,'qa');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const plan=read('projects/game-lighting-history-03/production/cache-spatial-proof-plan-v1.json'),execution=read('production/research/game-lighting-history/local/current-render-execution-v1.json');
if(execution.status!=='complete'||execution.exitCode!==0||!execution.command.includes('cache-project-v1.mp4'))throw Error('Actual cache exporter completion missing');
if(fs.existsSync(path.join(qa,'extraction.json')))throw Error('Existing extraction preserved');
for(const p of plan.modelInputs)if(sha(path.join(root,p.path))!==p.sha256)throw Error('Model input changed');
const ffmpeg=path.join(root,'motion-canvas/node_modules/@ffmpeg-installer/win32-x64/ffmpeg.exe'),ffprobe='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
function run(exe,args){const r=spawnSync(exe,args,{encoding:'utf8',windowsHide:true,maxBuffer:32*1024*1024});if(r.status!==0)throw Error(r.stderr);return{command:[exe,...args],exitCode:r.status,stdout:r.stdout,stderr:r.stderr};}
fs.mkdirSync(qa,{recursive:true});const video=path.join(dir,'cache-models.mp4');fs.copyFileSync(path.join(root,'production/research/game-lighting-history/local/black-proof-v3/cache-project-v1.mp4'),video);
const pr=run(ffprobe,['-v','error','-count_frames','-show_entries','stream=codec_type,codec_name,width,height,r_frame_rate,time_base,duration,nb_frames,nb_read_frames','-of','json',video]),probe=JSON.parse(pr.stdout),v=probe.streams[0];
if(v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1'||v.time_base!=='1/90000')throw Error('Unexpected format');
const decode=run(ffmpeg,['-hide_banner','-v','error','-threads','2','-i',video,'-f','null','NUL']);
const frames=[];for(let i=0;i<6;i++)for(const[t,pose]of[[.4,'before'],[1.5,'middle'],[2.8,'after']])frames.push({frame:Math.round((i*3+t)*60),paragraph:i+1,pose});
const extraction=run(ffmpeg,['-hide_banner','-v','error','-threads','2','-i',video,'-vf',`select='${frames.map(f=>`eq(n,${f.frame})`).join('+')}'`,'-vsync','0','-threads','2',path.join(qa,'frame-%03d.png')]);
frames.forEach((f,i)=>{f.path=`${rel}/qa/frame-${String(i+1).padStart(3,'0')}.png`;f.sha256=sha(path.join(root,f.path));});
const boards=[];for(let i=0;i<3;i++){const out=path.join(qa,`board-${String(i+1).padStart(2,'0')}.png`);run(ffmpeg,['-hide_banner','-v','error','-threads','2','-start_number',String(i*6+1),'-i',path.join(qa,'frame-%03d.png'),'-vf','scale=960:540,tile=2x3:nb_frames=6','-frames:v','1','-threads','2',out]);boards.push({path:path.relative(root,out).replaceAll('\\','/'),sha256:sha(out),directlyViewed:false,frameIndices:[i*6+1,i*6+6]});}
const record={createdAt:new Date().toISOString(),scope:plan.scope,video:{path:`${rel}/cache-models.mp4`,sha256:sha(video),probe},modelInputs:plan.modelInputs,exporter:execution,wholeDecode:decode,probeCommand:pr.command,plannedFrames:1080,observedFrames:Number(v.nb_read_frames),extractionCommand:extraction.command,frames,boards,modelMotionProofReviewed:false,fullEpisodeApproved:false,narrationTimed:false,actualFootageQuotaSeconds:0,localOnly:true};
fs.writeFileSync(path.join(qa,'extraction.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({record:`${rel}/qa/extraction.json`,frames:18,boards:3,observedFrames:record.observedFrames,wholeDecode:decode.exitCode}));
