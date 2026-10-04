const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1'),mc=path.join(root,'motion-canvas/src/projects/hierarchical-game-outlines'),mf=path.join(root,'projects/hierarchical-game-outlines/project.json');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');},abs=p=>path.join(root,p),rel=p=>path.relative(root,p).replaceAll('\\','/');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const FF='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe',PROBE='C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe';
const plan=read(path.join(work,'plan.json')),m=read(mf),stage=process.argv[2];
const executionFile=path.join(work,`build-${stage}-execution.json`),qpath=abs('production/batches/sakurai-planning-game-design/queue.json'),history=[];
if(!['setup','mix','assemble'].includes(stage))throw Error('Use setup, mix or assemble');
if(fs.existsSync(executionFile))throw Error('Inspect existing stage execution rather than duplicate it.');
function saveExecution(status,command=null,exitCode=null){const e={pid:process.pid,stage,status,updatedAt:new Date().toISOString(),currentCommand:command,commands:history,exitCode,finalVideoApproved:false};write(executionFile,e);const q=read(qpath),item=q.items.find(x=>x.slug==='hierarchical-game-outlines');item.execution.finalBuild=e;item.execution.activeTasks=status==='running'?[{kind:'final-build-'+stage,pid:process.pid,state:rel(executionFile)}]:[];item.updatedAt=e.updatedAt;write(qpath,q);}
saveExecution('running');process.on('exit',code=>saveExecution(code===0?'finished':'failed',null,code));
function run(cmd,args){saveExecution('running',[cmd,...args]);const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});const logfile=path.join(work,`build-${stage}-${String(history.length+1).padStart(2,'0')}.log`);write(logfile,(r.stdout??'')+(r.stderr??''));history.push({pid:r.pid,command:[cmd,...args],exitCode:r.status,log:rel(logfile)});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const ff=a=>run(FF,['-v','error','-y','-threads','2',...a]);
const enc=['-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
function sourceGate(){const g=read(path.join(work,'final-source-cut-review.json'));if(!g.allEncodedNativeBoundaryPixelsReviewed||!g.approved||g.selectionSha256!==sha(path.join(work,'cut-selection.json'))||g.layoutSha256!==sha(path.join(work,'caption-layout-qa.json')))throw Error('Current inspected source/caption layout required');const v=read(path.join(__dirname,'voice-approval-v2.json'));if(!v.allCurrentScenesTechnicallyReviewed)throw Error('Current whole voice review required');}
if(stage==='setup'){
 sourceGate();if(!plan.finalSourceTimingApproved||!plan.actualFootageMeasuredAndApproved||Math.abs(plan.ratioErrorFrames)>1)throw Error('Measured compiled actual footage required');
 for(const s of plan.scenes){if(sha(abs(s.voice))!==s.audioSha256)throw Error('Voice changed');if(s.classification==='actual'){
  const probe=JSON.parse(run(PROBE,['-v','error','-show_streams','-of','json',abs(s.actualVideo)]));const video=probe.streams.find(v=>v.codec_type==='video');
  if(probe.streams.some(v=>v.codec_type==='audio')||Number(video.nb_frames)!==s.frames||sha(abs(s.actualVideo))!==s.actualMediaVerified.sha256)throw Error('Actual media changed');
 }}
 const mcPlan={status:'measured-source-compiled-final-pixel-QA-pending',currentFinalTimingApproved:true,bodyRatioApproved:true,captionReviewComplete:false,
  scenes:plan.scenes.map(s=>({id:s.id,title:s.title,kind:s.classification==='actual'?'actual-existing-game-action':'explanation',seconds:s.seconds,
   paragraphEnds:s.paragraphs.map((p,i)=>i===s.paragraphs.length-1?s.seconds:p.end),actualVideo:s.actualVideo??'',actualMediaVerified:s.classification==='actual',actualAudioStreams:s.classification==='actual'?0:-1}))};
 write(path.join(mc,'production-plan.json'),mcPlan);
 write(path.join(mc,'timing.ts'),`export const NARRATION_FPS=60;\nexport const TOTAL_DURATION=${plan.seconds};\nexport const TOTAL_FRAMES=${plan.totalFrames};\nexport const SCENE_STARTS=${JSON.stringify(plan.scenes.map(s=>s.start))} as const;\nexport const SCENE_DURATIONS=${JSON.stringify(plan.scenes.map(s=>s.seconds))} as const;\nexport const SCENE_TITLES=${JSON.stringify(plan.scenes.map(s=>s.title))} as const;\n`);
 // Preserve all outlineConcept scene implementations and their four narrative
 // phases. Only install their current measured paragraph boundaries.
 const intro="import intro from '../small-window-game-design/intro-cats-v2/scene?scene';\n",outro="import outro from './scenes/membership-outro?scene';\n";
 write(path.join(mc,'project.ts'),`import {makeProject} from '@motion-canvas/core';\nimport audio from './assets/final-mix.m4a';\n${intro}${plan.scenes.map(s=>`import s${s.id} from './scenes/scene${s.id}?scene';`).join('\n')}\n${outro}export default makeProject({name:'hierarchical-game-outlines',audio,scenes:[intro,${plan.scenes.map(s=>'s'+s.id).join(',')},outro]});\n`);
 const explanations=plan.scenes.filter(s=>s.classification==='explanation');let start=2;for(const s of explanations){s.reelStart=start;start+=s.seconds;}
 write(path.join(mc,'explanation-project.ts'),`import {makeProject} from '@motion-canvas/core';\n${intro}${explanations.map(s=>`import s${s.id} from './scenes/scene${s.id}?scene';`).join('\n')}\n${outro}export default makeProject({name:'hierarchical-game-outlines-explanation-reel',scenes:[intro,${explanations.map(s=>'s'+s.id).join(',')},outro]});\n`);
 const config=path.join(root,'motion-canvas/vite.hierarchical-game-outlines.config.ts');let configText=fs.readFileSync(config,'utf8');const route="    './src/projects/hierarchical-game-outlines/explanation-project.ts',";
 if(!configText.includes(route))write(config,configText.replace("    './src/projects/hierarchical-game-outlines/project.ts',", "    './src/projects/hierarchical-game-outlines/project.ts',\n"+route));
 plan.explanationReelFrames=120+plan.explanationFrames+600;write(path.join(work,'plan.json'),plan);
 m.paths.editorAudioMix='motion-canvas/src/projects/hierarchical-game-outlines/assets/final-mix.wav';m.paths.timelineNarration=plan.timedBodyNarration;
 m.status='compiled-source-timing-installed-final-render-pending';m.editing.actualGameplaySeconds=plan.gameplaySeconds;m.editing.actualExplanationSeconds=plan.explanationSeconds;m.editing.actualGameplayShare=plan.gameplayShare;
 m.editing.actualCommercialGameplaySeconds=plan.gameplaySeconds;m.editing.actualDevelopmentFootageSeconds=0;m.editing.actualPrototypeExplanationSeconds=0;
 m.editing.timingStatus='compiled-existing-game-action-and-retained-explanation-measured; final-pixel-QA-pending';m.editing.exampleInterleaving.reviewStatus='exact source-action/caption segments directly reviewed; encoded final QA pending';write(mf,m);
 console.log('Current six outline explanations retained; six audio-free actual chapters installed. Final pixel QA pending.');
}else if(stage==='mix'){
 sourceGate();if(m.audio.backgroundMusic.approvalStatus!=='approved')throw Error('Existing music approval required');
 if(fs.existsSync(path.join(work,'mix-settings.json')))throw Error('Review existing mix; do not duplicate it');
 m.audio.musicFallbackScenes=plan.scenes.filter(s=>s.classification==='actual').map(s=>s.id);write(mf,m);
 if(!plan.timedBodyNarration||sha(abs(plan.timedBodyNarration))!==plan.timedBodyNarrationSha256)throw Error('Exact preserved-PCM timed body required');
 const D=plan.seconds,voice=abs(plan.timedBodyNarration),normal=path.join(work,'voice-normalized.wav');
 function scan(file,I=-16,TP=-2){const r=spawnSync(FF,['-hide_banner','-threads','2','-i',file,'-af',`loudnorm=I=${I}:TP=${TP}:LRA=11:print_format=json`,'-f','null','-'],{encoding:'utf8',windowsHide:true,maxBuffer:3e6});if(r.status!==0)throw Error(r.stderr);return JSON.parse(r.stderr.match(/\{\s*"input_i"[\s\S]*?\}/)[0]);}
 // Materialize the body before editorial delay: combining buffered loudnorm
 // with adelay previously dropped the intro in this FFmpeg build.
 const measured=scan(voice),bodyNormal=path.join(work,'voice-normalized-body.wav');
 ff(['-i',voice,'-af',`loudnorm=I=-16:TP=-2:LRA=11:measured_I=${measured.input_i}:measured_TP=${measured.input_tp}:measured_LRA=${measured.input_lra}:measured_thresh=${measured.input_thresh}:offset=${measured.target_offset}:linear=true,aresample=48000,aformat=channel_layouts=stereo`,'-c:a','pcm_s16le',bodyNormal]);
 const bodyDuration=Number(JSON.parse(run(PROBE,['-v','error','-show_format','-of','json',bodyNormal])).format.duration);if(Math.abs(bodyDuration-plan.bodySeconds)>1/48000)throw Error('Normalization changed body duration');
 ff(['-i',bodyNormal,'-af',`adelay=2000:all=1,apad,atrim=duration=${D}`,'-c:a','pcm_s16le',normal]);
 const duration=Number(JSON.parse(run(PROBE,['-v','error','-show_format','-of','json',normal])).format.duration);if(Math.abs(duration-D)>1/48000)throw Error('Padding duration mismatch');
 const silence=spawnSync(FF,['-hide_banner','-i',normal,'-af','atrim=end_sample=96000,volumedetect','-f','null','-'],{encoding:'utf8',windowsHide:true});const peak=Number(silence.stderr.match(/max_volume: ([-\d.]+) dB/)[1]);if(peak>-90)throw Error('Early intro narration');
 const vscan=scan(normal),gain=Math.min(-16-Number(vscan.input_i),-2-Number(vscan.input_tp)),first=path.join(work,'voice-loudnorm-pass.wav');fs.copyFileSync(normal,first);ff(['-i',first,'-af',`volume=${gain}dB`,'-c:a','pcm_s16le',normal]);
 let music=abs(m.audio.backgroundMusic.file);const md=Number(JSON.parse(run(PROBE,['-v','error','-show_format','-of','json',music])).format.duration);
 if(md<D){const n=Math.ceil((D-1)/(md-1)),inputs=Array.from({length:n},()=>['-i',music]).flat();let chain='';for(let i=1;i<n;i++)chain+=`${i===1?'[0:a]':'[b'+(i-1)+']'}[${i}:a]acrossfade=d=1:c1=tri:c2=tri[b${i}];`;const f=path.join(work,'nimbus-continuous.wav');ff([...inputs,'-filter_complex',chain.slice(0,-1),'-map',`[b${n-1}]`,'-c:a','pcm_s16le',f]);music=f;}
 const filter=`[0:a]asplit[n][d];[1:a]atrim=duration=${D},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.45,afade=t=out:st=${D-.45}:d=0.45[b];[b][d]sidechaincompress=threshold=.08:ratio=2.2:attack=15:release=280[bg];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=.80:level=false:latency=true[mix]`;
 write(path.join(work,'mix-filter.txt'),filter);ff(['-i',normal,'-i',music,'-filter_complex_script',path.join(work,'mix-filter.txt'),'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',abs(m.paths.editorAudioMix)]);ff(['-i',abs(m.paths.editorAudioMix),'-c:a','aac','-b:a','192k',abs(m.paths.audioMix)]);
 const final=scan(abs(m.paths.editorAudioMix),-16,-1.5);if(Math.abs(Number(final.input_i)+16)>.6||Number(final.input_tp)>-1.45)throw Error('Measured mix requires review '+JSON.stringify(final));
 write(path.join(work,'mix-settings.json'),{seconds:D,narration:measured,voicePass:vscan,constantVoiceGainDb:gain,finalMeasurement:final,continuousApprovedNimbus:true,sourceAudioMuted:true,reason:'Official presenter voice/music excluded. Approved narration and continuous Nimbus cover intro/body/outro; no invented game sounds.',humanListening:'pending',finalMixedWindowAsr:'pending'});console.log('Measured continuous voice/Nimbus mix created.');
}else if(stage==='assemble'){
 sourceGate();const render=read(path.join(work,'explanation-render-result.json'));if(!render.done||render.result!==0||render.errors.length)throw Error('Successful current reel required');
 const reel=abs('shared/output/motion-canvas/hierarchical-game-outlines-explanation-reel.mp4'),files=[],intro=path.join(work,'intro.mp4');
 const explanationReview=read(path.join(work,'explanation-pixel-review-v1/direct-review.json'));
 if(!explanationReview.sixExplanationsPassed||explanationReview.reelSha256!==sha(reel))throw Error('Current six explanations require direct pixel review');
 const replacement=abs('shared/output/motion-canvas/hierarchical-game-outlines-membership-outro.mp4');
 const outroReview=read(path.join(work,'outro-pixel-review-v2/direct-review.json'));
 if(!outroReview.approved||outroReview.sha256!==sha(replacement)||outroReview.frames!==600||outroReview.audioStreams!==0)throw Error('Original profile/name/badge/logo/coaching outro requires current direct review');
 if(fs.existsSync(abs(m.paths.videoClean)))throw Error('Review existing final rather than duplicate render');
 ff(['-i',reel,'-frames:v','120',...enc,intro]);files.push(intro);
 for(const s of plan.scenes){if(s.classification==='actual')files.push(abs(s.actualVideo));else{const f=path.join(work,`explanation-${s.id}.mp4`);ff(['-ss',String(s.reelStart),'-i',reel,'-frames:v',String(s.frames),...enc,f]);files.push(f);}}
 // The historical reel's generic text-only ending was rejected. Retain its
 // six explanations, then encode the reviewed original-identity replacement
 // to the same time base as all compiled clips before concatenation.
 const outro=path.join(work,'outro.mp4');ff(['-i',replacement,'-frames:v','600',...enc,outro]);files.push(outro);
 const concat=path.join(work,'final-concat.txt');write(concat,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));ff(['-f','concat','-safe','0','-i',concat,'-i',abs(m.paths.audioMix),'-map','0:v','-map','1:a','-c','copy','-t',String(plan.seconds),'-movflags','+faststart',abs(m.paths.videoClean)]);console.log('Narrated clean final assembled; captioning/full final QA pending.');
}else throw Error('Use setup, mix or assemble');
