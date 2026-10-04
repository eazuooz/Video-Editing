// Burn the reviewed fixed-position ASS without regenerating cue layout.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawn,spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const manifestPath=path.join(root,'projects/hierarchical-game-outlines/project.json'),m=read(manifestPath),plan=read(path.join(work,'plan.json'));
const clean=path.join(root,m.paths.videoClean),output=path.join(root,m.paths.videoBurnedCaptions),ass=path.join(work,'captions.ko.ass');
const stateFile=path.join(work,'caption-render-execution.json'),queueFile=path.join(root,'production/batches/sakurai-planning-game-design/queue.json');
if(fs.existsSync(output)||fs.existsSync(stateFile))throw Error('Review existing caption worker/output; never duplicate.');
const source=read(path.join(work,'final-source-cut-review.json')),ppt=read(path.join(work,'explanation-pixel-review-v1/direct-review.json'));
if(!source.approved||!ppt.sixExplanationsPassed||ppt.assSha256!==sha(ass))throw Error('Current source/PPT caption layout gate required');
const probe=JSON.parse(spawnSync('C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe',['-v','error','-show_streams','-show_format','-of','json',clean],{encoding:'utf8',windowsHide:true}).stdout);
const video=probe.streams.find(s=>s.codec_type==='video');
if(Number(video.nb_frames)!==plan.totalFrames||Math.abs(Number(probe.format.duration)-plan.seconds)>.01)throw Error('Exact assembled clean required');
const log=path.join(work,'caption-render.log'),fd=fs.openSync(log,'w'),assRelative=path.relative(root,ass).replaceAll('\\','/');
const args=['-v','error','-nostdin','-threads','4','-i',clean,'-vf',`ass=filename='${assRelative}'`,'-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',output];
const child=spawn('C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe',args,{cwd:root,windowsHide:true,stdio:['ignore',fd,fd]});
function save(status,exitCode=null){const state={pid:process.pid,childPid:child.pid,status,updatedAt:new Date().toISOString(),exitCode,cleanSha256:sha(clean),assSha256:sha(ass),captionCenter:[960,970],sourceAudioExcluded:true,finalVideoApproved:false,log:path.relative(root,log).replaceAll('\\','/')};write(stateFile,state);const q=read(queueFile),item=q.items.find(i=>i.slug==='hierarchical-game-outlines');item.execution.captionRender=state;item.execution.activeTasks=status==='running'?[{kind:'caption-render',pid:process.pid,childPid:child.pid,state:path.relative(root,stateFile).replaceAll('\\','/')}]:[];item.updatedAt=state.updatedAt;write(queueFile,q);}
save('running');const pulse=setInterval(()=>save('running'),30000);
child.on('error',e=>{clearInterval(pulse);console.error(e);save('failed',1);process.exitCode=1;});
child.on('exit',code=>{clearInterval(pulse);fs.closeSync(fd);save(code===0?'finished':'failed',code);if(code!==0){process.exitCode=code||1;return;}m.paths.captionsKo='projects/hierarchical-game-outlines/production/final-v1/captions.ko.srt';m.paths.captionsEn='projects/hierarchical-game-outlines/production/final-v1/captions.en.srt';write(manifestPath,m);console.log('Current reviewed fixed KO ASS burned; final decoded pixel/audio QA remains pending.');});
