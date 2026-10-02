const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1'),mc=path.join(root,'motion-canvas/src/projects/blank-project-coding'),mf=path.join(root,'projects/blank-project-coding/project.json');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');},abs=p=>path.join(root,p),rel=p=>path.relative(root,p).replaceAll('\\','/');
const plan=read(path.join(work,'plan.json')),m=read(mf),stage=process.argv[2];
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const ff=a=>run('ffmpeg',['-v','error','-y','-threads','2',...a]);
const enc=['-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
if(stage==='setup'){
 const explanations=plan.scenes.filter(s=>s.classification==='explanation');let start=2;for(const s of explanations){s.reelStart=start;start+=s.seconds;}
 plan.explanationReelFrames=120+plan.explanationFrames+600;write(path.join(work,'plan.json'),plan);write(path.join(mc,'production-plan.json'),plan);
 console.log('34 independent scenes use the measured current narration; final actual captures remain gated separately.');
}else if(stage==='mix'){
 if(m.audio.backgroundMusic.approvalStatus!=='approved')throw Error('Existing music approval required');
 const D=plan.seconds,voice=abs(m.paths.narration),normal=path.join(work,'voice-normalized.wav');
 function scan(file,I=-16,TP=-2){const r=spawnSync('ffmpeg',['-hide_banner','-threads','2','-i',file,'-af',`loudnorm=I=${I}:TP=${TP}:LRA=11:print_format=json`,'-f','null','-'],{encoding:'utf8',windowsHide:true,maxBuffer:3e6});if(r.status!==0)throw Error(r.stderr);return JSON.parse(r.stderr.match(/\{\s*"input_i"[\s\S]*?\}/)[0]);}
 // Materialize loudnorm's body before adding editorial silence. Combining its
 // buffered frames with adelay/apad in this FFmpeg build dropped the intro.
 const measured=scan(voice),bodyNormal=path.join(work,'voice-normalized-body.wav');
 ff(['-i',voice,'-af',`loudnorm=I=-16:TP=-2:LRA=11:measured_I=${measured.input_i}:measured_TP=${measured.input_tp}:measured_LRA=${measured.input_lra}:measured_thresh=${measured.input_thresh}:offset=${measured.target_offset}:linear=true,aresample=48000,aformat=channel_layouts=stereo`,'-c:a','pcm_s16le',bodyNormal]);
 const bodyDuration=Number(JSON.parse(run('ffprobe',['-v','error','-show_format','-of','json',bodyNormal])).format.duration);if(Math.abs(bodyDuration-plan.bodySeconds)>1/48000)throw Error('Normalization changed body sample duration');
 ff(['-i',bodyNormal,'-af',`adelay=2000:all=1,apad,atrim=duration=${D}`,'-c:a','pcm_s16le',normal]);
 const duration=Number(JSON.parse(run('ffprobe',['-v','error','-show_format','-of','json',normal])).format.duration);if(Math.abs(duration-D)>1/48000)throw Error('Final narration padding duration mismatch');
 const silence=spawnSync('ffmpeg',['-hide_banner','-i',normal,'-af','atrim=end_sample=96000,volumedetect','-f','null','-'],{encoding:'utf8',windowsHide:true});const peak=Number(silence.stderr.match(/max_volume: ([-\d.]+) dB/)[1]);if(peak>-90)throw Error('Intro contains early narration');
 const vscan=scan(normal),gain=Math.min(-16-Number(vscan.input_i),-2-Number(vscan.input_tp)),first=path.join(work,'voice-loudnorm-pass.wav');fs.copyFileSync(normal,first);ff(['-i',first,'-af',`volume=${gain}dB`,'-c:a','pcm_s16le',normal]);
 let music=abs(m.audio.backgroundMusic.file);const md=Number(JSON.parse(run('ffprobe',['-v','error','-show_format','-of','json',music])).format.duration);
 if(md<D){const n=Math.ceil((D-1)/(md-1)),inputs=Array.from({length:n},()=>['-i',music]).flat();let chain='';for(let i=1;i<n;i++)chain+=`${i===1?'[0:a]':'[b'+(i-1)+']'}[${i}:a]acrossfade=d=1:c1=tri:c2=tri[b${i}];`;const f=path.join(work,'nimbus-continuous.wav');ff([...inputs,'-filter_complex',chain.slice(0,-1),'-map',`[b${n-1}]`,'-c:a','pcm_s16le',f]);music=f;}
 const filter=`[0:a]asplit[n][d];[1:a]atrim=duration=${D},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.45,afade=t=out:st=${D-.45}:d=0.45[b];[b][d]sidechaincompress=threshold=.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=.80:level=false:latency=true[mix]`;
 write(path.join(work,'mix-filter.txt'),filter);ff(['-i',normal,'-i',music,'-filter_complex_script',path.join(work,'mix-filter.txt'),'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',abs(m.paths.editorAudioMix)]);ff(['-i',abs(m.paths.editorAudioMix),'-c:a','aac','-b:a','192k',abs(m.paths.audioMix)]);
 const final=scan(abs(m.paths.editorAudioMix),-16,-1.5);if(Math.abs(Number(final.input_i)+16)>.6||Number(final.input_tp)>-1.45)throw Error('Measured final audio requires review '+JSON.stringify(final));
 write(path.join(work,'mix-settings.json'),{seconds:D,narration:measured,voicePass:vscan,constantVoiceGainDb:gain,finalMeasurement:final,continuousApprovedNimbus:true,sourceAudioMuted:true,reason:'All examples are owned silent executing-code/playtest screencasts. Narration/Nimbus still cover every frame including membership outro.',humanListening:'pending'});console.log('Measured continuous voice/Nimbus full mix created.');
}else if(stage==='assemble'){
 if(plan.scenes.some(s=>s.classification!=='explanation'&&!s.actualMediaVerified))throw Error('Final actual capture review required');
 const reel=abs('shared/output/motion-canvas/blank-project-coding-explanation-reel.mp4'),files=[];const intro=path.join(work,'intro.mp4');ff(['-i',reel,'-frames:v','120',...enc,intro]);files.push(intro);
 for(const s of plan.scenes){if(s.classification==='actual')files.push(abs(s.actualVideo));else{const file=path.join(work,`explanation-${s.id}.mp4`);ff(['-ss',String(s.reelStart),'-i',reel,'-frames:v',String(s.frames),...enc,file]);files.push(file);}}
 const outro=path.join(work,'outro.mp4');ff(['-ss',String(2+plan.explanationSeconds),'-i',reel,'-frames:v','600',...enc,outro]);files.push(outro);
 const concat=path.join(work,'final-concat.txt');write(concat,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));ff(['-f','concat','-safe','0','-i',concat,'-i',abs(m.paths.audioMix),'-map','0:v','-map','1:a','-c','copy','-t',String(plan.seconds),'-movflags','+faststart',abs(m.paths.videoClean)]);console.log('Actual clean narrated final assembled; full decode/caption/mix review pending.');
}else throw Error('Use setup, mix or assemble');
