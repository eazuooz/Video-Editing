// Additive edit: every uploaded-v1 frame/line survives; actual footage is 60%.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v2'),baseline=path.join(__dirname,'private-expansion-baseline'),slug='deconstruct-analyze-rebuild';
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
const abs=f=>path.resolve(root,f),rel=f=>path.relative(root,f).replaceAll('\\','/'),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:24e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const ff=a=>run('ffmpeg',['-v','error','-y',...a]),probe=f=>JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',f]));
const enc=['-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
const old=read(path.join(baseline,'production/final-v1/plan.json')),preservation=read(path.join(baseline,'preservation.json')),tts=read(path.join(work,'tts-manifest.json')),addition=read(abs(tts.paths.script)),translation=read(abs(tts.paths.scriptEn));
const oldManifest=read(path.join(baseline,'project.json')),oldVoice=abs(oldManifest.paths.narration);
const step=process.argv[2];
const decodedHashes=f=>run('ffmpeg',['-v','error','-i',f,'-an','-vf','scale=192:108:flags=area','-f','framehash','-hash','sha256','-']).split(/\r?\n/).filter(l=>l&&!l.startsWith('#')).map(l=>l.split(',').at(-1).trim());
const time=t=>{const ms=Math.round(t*1000);return `${String(Math.floor(ms/3600000)).padStart(2,'0')}:${String(Math.floor(ms/60000)%60).padStart(2,'0')}:${String(Math.floor(ms/1000)%60).padStart(2,'0')},${String(ms%1000).padStart(3,'0')}`;};
const seconds=t=>{const [h,m,s]=t.replace(',','.').split(':');return +h*3600+ +m*60+ +s;};
const parseSrt=f=>fs.readFileSync(f,'utf8').trim().split(/\r?\n\s*\r?\n/).map(b=>{const [id,t,...text]=b.split(/\r?\n/),[a,z]=t.split(' --> ');return {start:seconds(a),end:seconds(z),text:text.join('\n')};});
const srt=(f,cues)=>write(f,cues.map((c,i)=>`${i+1}\n${time(c.start)} --> ${time(c.end)}\n${c.text}`).join('\n\n')+'\n');

if(step==='plan'){
 const approved=read(path.join(work,'addition-asr-direct-review.json'));
 const timing=read(abs(`${tts.tts.outputDir}/${tts.tts.filenameStem}.timing.json`));
 if(!approved.allCurrentChunksReviewed)throw Error('Direct current-hash addition ASR review required');
 const durations=addition.scenes.map(s=>{const wav=abs(`${tts.tts.outputDir}/chunks/${s.id}-scene.wav`),qa=approved.scenes.find(q=>q.scene===s.id);if(!qa||qa.status!=='accepted'||qa.audioSha256!==hash(wav))throw Error('Unapproved/stale addition '+s.id);return +probe(wav).format.duration;});
 const addFrames=durations.map((d,i)=>Math.ceil((d+(i<5?.72:0))*60-1e-7));
 let bodyFrames=old.bodyFrames+addFrames.reduce((n,v)=>n+v,0);
 // More speech may need a brief original recap; never remove original PPT.
 let actualFrames=Math.round(bodyFrames*.6),newExplanationFrames=bodyFrames-actualFrames-preservation.explanationFrames;
 if(newExplanationFrames<0){const extra=Math.ceil(-newExplanationFrames/.4);addFrames[5]+=extra;bodyFrames+=extra;actualFrames=Math.round(bodyFrames*.6);newExplanationFrames=bodyFrames-actualFrames-preservation.explanationFrames;}
 if(newExplanationFrames>addFrames[5]-600)throw Error('Recap exceeds last insertion; review additional script instead of shrinking original explanations');
 const map=read(path.join(work,'example-map.json')),sourceRanges={};
 const oldScripts={ko:read(path.join(baseline,'script/narration.ko.json')),en:read(path.join(baseline,'script/narration.en.json'))};
 const scripts={ko:{...oldScripts.ko,scenes:[]},en:{...oldScripts.en,scenes:[]}},p={revision:'final-v2',fps:60,introFrames:120,introSeconds:2,bodyFrames,bodySeconds:bodyFrames/60,bodyEnd:2+bodyFrames/60,outroFrames:600,totalFrames:bodyFrames+720,seconds:(bodyFrames+720)/60,gameplaySeconds:actualFrames/60,explanationSeconds:(bodyFrames-actualFrames)/60,gameplayShare:actualFrames/bodyFrames,diagramFrames:bodyFrames-actualFrames,originalBodyFrames:old.bodyFrames,originalExplanationFrames:preservation.explanationFrames,additionalExplanationFrames:newExplanationFrames,classification:'Diagram-dominated original landing/retry/rule tests count as explanation; only preserved commercial play and fresh observable game actions count as actual footage.',scenes:[],audioParts:[],preservation:rel(path.join(baseline,'preservation.json')),originalVoiceSha256:hash(oldVoice),additionAsrReview:rel(path.join(work,'addition-asr-direct-review.json'))};
 let cursor=120;
 function available(key,a,b){const blocks=sourceRanges[key]||[];let result=[[Math.round(a*60),Math.round(b*60)]];for(const [u,v] of blocks)result=result.flatMap(([x,y])=>v<=x||u>=y?[[x,y]]:[[x,Math.min(y,u)],[Math.max(x,v),y]].filter(([x,y])=>y-x>=180));return result.filter(([x,y])=>y-x>=180).map(([a,b])=>({key,a,b,capacity:b-a}));}
 function allocate(scene,windows,frames,label){
  let pool=windows.flatMap(([k,a,b])=>available(k,a,b));
  // Keep the longest available fresh shots when speech permits fewer cuts;
  // dropping the last candidate can discard the only sufficiently long shot.
  while(pool.length>1&&frames<pool.length*180){
   const smallest=pool.reduce((best,w,i)=>w.capacity<pool[best].capacity?i:best,0);
   pool.splice(smallest,1);
  }
  const cap=pool.reduce((n,w)=>n+w.capacity,0);if(cap<frames)throw Error(`Need fresh ${scene.id} footage for '${label}': ${(frames-cap)/60}s shortage`);
  let remainingExtra=frames-pool.length*180,capacityExtra=cap-pool.length*180;
  pool.forEach((w,i)=>{const extra=i===pool.length-1?remainingExtra:Math.min(w.capacity-180,Math.round(remainingExtra*(w.capacity-180)/Math.max(1,capacityExtra))),n=180+extra;remainingExtra-=extra;capacityExtra-=w.capacity-180;if(n<180||n>w.capacity)throw Error('Invalid addition shot duration');
   const source=map.sources[w.key],offset=scene.segments.reduce((n,s)=>n+s.frames,0),start=scene.start+offset/60,video=rel(path.join(work,`addition-${scene.originalId}-${scene.cuts.length+1}.mp4`));
   const c={...source,key:w.key,url:source.url,sourceIn:w.a/60,originalIn:w.a/60,frames:n,seconds:n/60,timelineStart:start,video,audio:video.replace('.mp4','.wav'),muteSourceAudio:true,hasSourceAudio:false,normalSpeed:true,loop:false,artificialSlowdown:false,presentation:'full-screen',title:source.label,claim:label};
   scene.cuts.push(c);scene.segments.push({key:w.key,kind:'actual-commercial-gameplay',frames:n,seconds:n/60,timelineStart:start,video,source:c});(sourceRanges[w.key]??=[]).push([w.a,w.a+n]);
  });
 }
 for(const [i,s] of old.scenes.entries()){
  const original={...s,id:'original-'+s.id,originalId:s.id,role:'preserved-original',start:cursor/60,bodyStart:(cursor-120)/60,cuts:s.cuts.map(c=>({...c,timelineStart:cursor/60+c.timelineStart-s.start})),segments:[],sceneVideo:rel(path.join(work,`original-${s.id}.mp4`))};
  for(const c of original.cuts)original.segments.push({key:c.key,kind:['meat','hollow','portal'].includes(c.key)?'actual-commercial-gameplay':'original-diagram-dominated-test',frames:c.frames,seconds:c.seconds,timelineStart:c.timelineStart,video:original.sceneVideo,source:c});
  original.segments.push({key:'diagram',kind:'original-2.5d-explanation',frames:s.diagramFrames,seconds:s.diagramSeconds,timelineStart:original.start+s.gameSeconds,video:original.sceneVideo});
  original.gameFrames=original.cuts.filter(c=>['meat','hollow','portal'].includes(c.key)).reduce((n,c)=>n+c.frames,0);original.diagramFrames=s.frames-original.gameFrames;original.gameSeconds=original.gameFrames/60;original.diagramSeconds=original.diagramFrames/60;p.scenes.push(original);
  p.audioParts.push({kind:'original-narration-unchanged',source:rel(oldVoice),sourceStart:s.bodyStart,frames:s.frames,bodyStart:(cursor-120)/60});
  for(const lang of ['ko','en'])scripts[lang].scenes.push({...oldScripts[lang].scenes[i],id:original.id,originalId:s.id});
  cursor+=s.frames;
  const a={id:'addition-'+s.id,originalId:s.id,role:'additional-commentary',title:addition.scenes[i].title,start:cursor/60,bodyStart:(cursor-120)/60,frames:addFrames[i],seconds:addFrames[i]/60,gameFrames:addFrames[i]-(i===5?newExplanationFrames:0),diagramFrames:i===5?newExplanationFrames:0,cuts:[],segments:[],sceneVideo:rel(path.join(work,`addition-${s.id}.mp4`))};a.gameSeconds=a.gameFrames/60;a.diagramSeconds=a.diagramFrames/60;
  const entries=timing.entries.filter(e=>e.scene_id===s.id),origin=entries[0].start,groups=map.chapters[i].groups;let previous=0;
  for(const group of groups){const end=group.endAtLine===9?a.gameFrames:Math.min(a.gameFrames,Math.floor((entries[group.endAtLine].voice_start-origin)*60));if(end<=previous)throw Error('Narration shot anchor invalid '+a.id);allocate(a,group.windows,end-previous,group.claim);previous=end;}
  if(previous!==a.gameFrames)throw Error('Insertion action gap '+a.id);
  if(a.diagramFrames)a.segments.push({key:'recap',kind:'original-2.5d-explanation',frames:a.diagramFrames,seconds:a.diagramSeconds,timelineStart:a.start+a.gameSeconds,video:rel(path.join(work,'recap.mp4'))});
  p.scenes.push(a);p.audioParts.push({kind:'new-commentary-same-approved-voice',source:`${tts.tts.outputDir}/chunks/${s.id}-scene.wav`,sourceStart:0,frames:a.frames,bodyStart:a.bodyStart});
  scripts.ko.scenes.push({...addition.scenes[i],id:a.id,originalId:s.id});scripts.en.scenes.push({...translation.scenes[i],id:a.id,originalId:s.id});cursor+=a.frames;
 }
 if(cursor!==Math.round(p.bodyEnd*60)||Math.abs(p.gameplayShare-.6)*p.bodyFrames>1.001)throw Error('Final frame/ratio arithmetic mismatch');
 for(const lang of ['ko','en']){
  write(path.join(work,`script.${lang}.json`),scripts[lang]);const oldCues=parseSrt(path.join(baseline,`production/final-v1/captions.${lang}.srt`)),newCues=parseSrt(path.join(work,`additions.${lang}.srt`)),all=[];
  for(const s of p.scenes){const i=+s.originalId-1,o=old.scenes[i],entries=timing.entries.filter(e=>e.scene_id===s.originalId),origin=entries[0].start;
   // Uploaded-v1 SRT rounded some 60-fps scene starts to centiseconds.
   // Include that sub-frame rounding and keep the cue inside its retained scene.
   const cues=s.role==='preserved-original'?oldCues.filter(c=>c.start>=o.start-.012&&c.end<=o.start+o.seconds+.012):newCues.filter(c=>c.start>=origin-.003&&c.end<=origin+durations[i]+.003);
   const shift=s.role==='preserved-original'?s.start-o.start:s.start-origin;for(const c of cues)all.push({...c,start:Math.max(s.start,c.start+shift),end:Math.min(s.start+s.seconds,c.end+shift)});
  }
  if(all.length!==oldCues.length+newCues.length)throw Error('Caption lost or duplicated');srt(path.join(work,`captions.${lang}.srt`),all);
 }
 const mc=path.join(root,'motion-canvas/src/projects',slug,'expanded-v2');
 const m={...oldManifest,status:'revision-in-progress',paths:{...oldManifest.paths,script:rel(path.join(work,'script.ko.json')),scriptEn:rel(path.join(work,'script.en.json')),narration:rel(path.join(work,'narration-composed.wav')),audioMix:rel(path.join(work,'final-mix.m4a')),editorAudioMix:rel(path.join(work,'final-mix.wav')),videoClean:rel(path.join(work,'clean.mp4')),videoBurnedCaptions:rel(path.join(work,'captioned.mp4')),captionsKo:rel(path.join(work,'captions.ko.srt')),captionsEn:rel(path.join(work,'captions.en.srt')),captionEditable:rel(path.join(work,'captions.ko.ass')),timeline:rel(path.join(work,'plan.json')),motionCanvasProject:rel(path.join(mc,'project.ts'))},additionTts:{manifest:rel(path.join(work,'tts-manifest.json')),outputDir:tts.tts.outputDir,originalVoicePreserved:true},editing:{...oldManifest.editing,targetGameplayShare:.6,targetExplanationShare:.4,gameplayShareRange:[.6,.6],ratioPolicy:'60:40 actual game actions / all preserved explanations and diagram-like tests; 1-frame rounding',actualGameplaySeconds:p.gameplaySeconds,actualExplanationSeconds:p.explanationSeconds,bodyDurationSeconds:p.bodySeconds,actualGameplayShare:p.gameplayShare,preservePptDuration:true,preserveOriginalNarration:true,classification:p.classification},finalRender:null,approvals:{...oldManifest.approvals,final:'pending expanded render and full QA'},publishReady:false};
 write(path.join(work,'project-draft.json'),m);write(path.join(work,'plan.json'),p);
 write(path.join(mc,'production-plan.json'),p);
 write(path.join(mc,'recap-scene.tsx'),`import {makeScene2D} from '@motion-canvas/2d';\nimport {diagramScene} from '../diagram';\nimport plan from './production-plan.json';\nexport default makeScene2D(function*(view){yield* diagramScene(view,5,plan.additionalExplanationFrames/60);});\n`);
 write(path.join(mc,'recap-project.ts'),`import {makeProject} from '@motion-canvas/core';\nimport recap from './recap-scene?scene';\nexport default makeProject({name:'deconstruct-analyze-rebuild-expanded-recap',scenes:[recap]});\n`);
 for(const [i,s] of p.scenes.entries())write(path.join(mc,'scenes',s.id+'.tsx'),`import {makeScene2D, Video} from '@motion-canvas/2d';\nimport {createRef, waitFor} from '@motion-canvas/core';\nimport clip from '../assets/${s.id}.mp4';\nclass MutedVideo extends Video {protected override video(){const element=super.video();element.muted=true;return element;}}\nexport default makeScene2D(function*(view){const video=createRef<Video>();view.add(<MutedVideo ref={video} src={clip} width={1920} height={1080}/>);yield video();video().play();yield* waitFor(${s.seconds});video().pause();});\n`);
 write(path.join(mc,'project.ts'),`import {makeProject} from '@motion-canvas/core';\nimport audio from './assets/final-mix.m4a';\nimport intro from '../../small-window-game-design/intro-cats-v2/scene?scene';\n${p.scenes.map((s,i)=>`import s${i} from './scenes/${s.id}?scene';`).join('\n')}\nimport outro from '../scenes/membership-outro?scene';\nexport default makeProject({name:'게임 분석·재조립 — 원본 설명 보존·실제 선택 관찰 확장본',audio,scenes:[intro,${p.scenes.map((s,i)=>'s'+i).join(',')},outro]});\n`);
 write(path.join(work,'source-ranges.json'),{ranges:sourceRanges,units:'60-fps normalized source frames',noOverlap:true,noLoops:true,normalSpeed:true});
 console.log(JSON.stringify({seconds:p.seconds,body:p.bodySeconds,gameplay:p.gameplaySeconds,explanation:p.explanationSeconds,preservedExplanation:preservation.explanationFrames/60,newRecap:p.additionalExplanationFrames/60}));
}else if(step==='prepare'){
 const p=read(path.join(work,'plan.json'));
 const only=process.argv.find(a=>a.startsWith('--only-addition='))?.split('=')[1]?.split(',');
 const record=preservation.files.find(f=>f.kind==='clean');if(hash(abs(record.copy))!==record.sha256||hash(oldVoice)!==p.originalVoiceSha256)throw Error('Preserved picture/voice changed');
 const originalFrameHashes=decodedHashes(path.join(baseline,'clean.mp4')),retention=[];
 function copyOriginal(name,startFrame,frames,target){
  ff(['-ss',String(startFrame/60),'-i',path.join(baseline,'clean.mp4'),'-frames:v',String(frames),'-an','-c:v','copy','-video_track_timescale','90000','-movflags','+faststart',target]);
  const got=decodedHashes(target),expected=originalFrameHashes.slice(startFrame,startFrame+frames);
  if(got.length!==frames||got.some((h,i)=>h!==expected[i]))throw Error('Original-frame copy mismatch '+name+'; inspect frame boundaries before proceeding');
  retention.push({name,originalStartFrame:startFrame,frames,untouchedCompressedPicture:true,everyDecodedFrameCompared:true,comparison:'SHA256 of identical 192x108 area-sampled decoded picture per frame'});
 }
 for(const s of p.scenes){
  if(only && (s.role!=='additional-commentary'||!only.includes(s.originalId)))continue;
  if(s.role==='preserved-original'){
   const o=old.scenes.find(o=>o.id===s.originalId);copyOriginal(s.id,Math.round(o.start*60),o.frames,abs(s.sceneVideo));
  }else for(const c of s.cuts){
   if(+probe(abs(c.file)).format.duration<c.sourceIn+c.seconds-.01)throw Error('Short original');
   const label=abs(c.video.replace('.mp4','-label.txt'));write(label,c.label);const ggst=false;
   ff(['-ss',String(c.sourceIn),'-i',abs(c.file),'-frames:v',String(c.frames),'-vf',`fps=60,scale=1920:1080,setsar=1,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='${rel(label)}':x=${c.labelX??500}:y=${c.labelY??25}:fontsize=23:fontcolor=white:box=1:boxcolor=black@0.62:boxborderw=9`,...enc,abs(c.video)]);
   ff(['-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',String(c.seconds),'-c:a','pcm_s16le',abs(c.audio)]);console.log(`${s.id} ${c.key} ${c.sourceIn}–${c.sourceIn+c.seconds}`);
  }
 }
 if(only){write(path.join(work,'picture-refresh.json'),{updatedAt:new Date().toISOString(),onlyAdditionalScenes:only,reason:'Exclude directly observed title/transition frames from actual-action intervals; narration, baseline explanations and overall timeline unchanged',bodyFrames:p.bodyFrames,aacSha256:hash(path.join(work,'final-mix.m4a')),narrationSha256:hash(path.join(work,'narration-composed.wav'))});console.log('Fresh picture cuts regenerated; all speech and original frames retained.');return;}
 const parts=[];
 for(const [i,a] of p.audioParts.entries()){
  const f=path.join(work,`voice-part-${String(i+1).padStart(2,'0')}.wav`);ff(['-i',abs(a.source),'-af',`atrim=start=${a.sourceStart}:end=${a.sourceStart+a.frames/60},asetpts=PTS-STARTPTS,apad,atrim=duration=${a.frames/60},aresample=24000`,'-ac','1','-c:a','pcm_s16le',f]);parts.push(f);
 }
 const list=path.join(work,'voice-concat.txt');write(list,parts.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));ff(['-f','concat','-safe','0','-i',list,'-c','copy',path.join(work,'narration-composed.wav')]);
 if(Math.abs(+probe(path.join(work,'narration-composed.wav')).format.duration-p.bodySeconds)>.001)throw Error('Narration/timeline mismatch');
 for(const [name,start,frames] of [['intro',0,120],['outro',Math.round(old.bodyEnd*60),600]])copyOriginal(name,start,frames,path.join(work,name+'.mp4'));
 write(path.join(work,'original-frame-retention.json'),{uploadedVideoId:preservation.videoId,uploadedRevision:'final-v1',baselineSha256:record.sha256,allOriginalBodyFrames:old.bodyFrames,originalExplanationFrames:preservation.explanationFrames,allOriginalFramesRetained:true,segments:retention});
 console.log('All uploaded-v1 frames and original narration retained in unchanged order.');
}else if(step==='assemble'){
 const p=read(path.join(work,'plan.json')),m=read(path.join(work,'project-draft.json')),all=[path.join(work,'intro.mp4')];
 for(const s of p.scenes){
  if(s.role==='additional-commentary'){
   const files=s.segments.map(v=>abs(v.video)),list=path.join(work,`scene-${s.id}-concat.txt`);for(const f of files)if(!fs.existsSync(f))throw Error('Missing segment '+f);write(list,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));ff(['-f','concat','-safe','0','-i',list,'-c','copy',abs(s.sceneVideo)]);
  }
  all.push(abs(s.sceneVideo));
 }
 all.push(path.join(work,'outro.mp4'));const list=path.join(work,'final-concat.txt');write(list,all.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
 ff(['-f','concat','-safe','0','-i',list,'-i',abs(m.paths.audioMix),'-map','0:v','-map','1:a','-c','copy','-t',String(p.seconds),'-movflags','+faststart',abs(m.paths.videoClean)]);
 const mc=path.join(root,'motion-canvas/src/projects',slug,'expanded-v2/assets');fs.mkdirSync(mc,{recursive:true});for(const s of p.scenes)fs.copyFileSync(abs(s.sceneVideo),path.join(mc,s.id+'.mp4'));fs.copyFileSync(abs(m.paths.audioMix),path.join(mc,'final-mix.m4a'));
 console.log('Expanded clean movie assembled; QA still pending.');
}else throw Error('Use plan | prepare | assemble');
