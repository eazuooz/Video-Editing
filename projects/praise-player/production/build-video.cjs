// Measured narration -> distinct gameplay cuts -> editable explanations -> final mix.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),slug='praise-player',mc=path.join(root,'motion-canvas/src/projects',slug),work=path.join(__dirname,'final-v1');
const mf=path.join(root,'projects',slug,'project.json'),read=f=>JSON.parse(fs.readFileSync(f,'utf8')),m=read(mf);
const write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
const rel=f=>path.relative(root,f).replaceAll('\\','/'),abs=f=>path.join(root,f);
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:24e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const ff=a=>run('ffmpeg',['-v','error','-y',...a]);
const probe=f=>JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',f]));
const enc=['-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
const raw=n=>`shared/assets/${slug}/raw/${n}.mp4`,own=n=>`shared/assets/${slug}/playtests-v1/${n}.mp4`;
const font='C\\:/Windows/Fonts/malgun.ttf';
const esc=f=>rel(f).replaceAll(':','\\:');
const catalog={
 sports:{file:raw('switch-sports-official'),originalOffset:0,title:'닌텐도 스위치 스포츠 · 성공 직후의 인정',credit:'Nintendo of America | tiwjvBSS_Wk | source audio omitted',url:'https://www.youtube.com/watch?v=tiwjvBSS_Wk',muteSourceAudio:true},
 ringfit:{file:raw('ringfit-official'),originalOffset:0,title:'링 피트 어드벤처 · 동작 평가',credit:'Nintendo of America | skBNiJd61Qw | source audio omitted',url:'https://www.youtube.com/watch?v=skBNiJd61Qw',muteSourceAudio:true},
 timing:{file:'shared/assets/praise-player/playtests-v2/timing-sound.mp4',originalOffset:0,title:'직접 만든 방어 테스트 · 반응 시점',credit:'Original equal-state keyboard and collision test'},
 specificity:{file:own('specificity-sound'),originalOffset:0,title:'직접 만든 방어 테스트 · 행동 문구',credit:'Original actual block/dodge outcomes'},
 strength:{file:'shared/assets/praise-player/playtests-v2/strength-sound.mp4',originalOffset:0,title:'직접 만든 방어 테스트 · 성과와 강도',credit:'Original streak collision counter; equal fixed-center labels, full text visible'},
 honesty:{file:own('honesty-sound'),originalOffset:0,title:'직접 만든 방어 테스트 · 실패와 실제 성공',credit:'Original equal missed attack and health deduction'},
 placement:{file:own('placement-sound'),originalOffset:0,title:'직접 만든 방어 테스트 · 다음 행동 공간',credit:'Original same input and message, changed visual placement'}
};
const slots=[
 [['sports',237,5],['ringfit',442,10.5],['specificity',26.5,5.5]],
 [['timing',0,32]],
 [['specificity',0,32]],
 [['sports',244,3.5],['strength',0,32]],
 [['honesty',0,32]],
 [['placement',0,32]]
];
fs.mkdirSync(work,{recursive:true});
const stage=process.argv[2];
if(stage==='prepare'){
 const script=read(abs(m.paths.script)),timing=read(abs(`${m.tts.outputDir}/${m.tts.filenameStem}.timing.json`));
 const starts=script.scenes.map(s=>Math.round(timing.entries.find(e=>e.scene_id===s.id).start*30)*2),bodyFrames=Math.round(timing.duration_seconds*30)*2;
 const weights=[.58,.62,.62,.60,.60,.58];
 const introFrames=120,introSeconds=introFrames/60;
 const scenes=script.scenes.map((s,i)=>({id:s.id,index:i,title:s.title,bodyStart:starts[i]/60,start:starts[i]/60+introSeconds,frames:(starts[i+1]??bodyFrames)-starts[i]}));
 // Respect each new capture's real duration. Balance the body rather than
 // extending a short source or forcing every scene to the same percentage.
 const caps=scenes.map((s,i)=>Math.min(Math.floor(slots[i].reduce((n,c)=>n+c[2],0)*60),s.frames-480));
 scenes.forEach((s,i)=>s.gameFrames=Math.min(caps[i],Math.round(s.frames*weights[i])));
 const target=Math.ceil(bodyFrames*.6);let delta=target-scenes.reduce((n,s)=>n+s.gameFrames,0);
 for(const i of [5,3,0,4,2,1]){
  if(!delta)break;
  const change=delta>0?Math.min(delta,caps[i]-scenes[i].gameFrames):-Math.min(-delta,scenes[i].gameFrames-180);
  scenes[i].gameFrames+=change;delta-=change;
 }
 if(delta)throw Error('Need fresh related capture; never loop/slow down footage to fill '+delta+' frames');
 let diagramStart=introSeconds;
 for(const s of scenes){
   s.seconds=s.frames/60;s.gameSeconds=s.gameFrames/60;s.diagramFrames=s.frames-s.gameFrames;s.diagramSeconds=s.diagramFrames/60;s.diagramStart=diagramStart;diagramStart+=s.diagramSeconds;

   let left=s.gameFrames;s.cuts=[];
   for(const [key,sourceIn,available] of slots[s.index]){
     if(!left)break;
     const frames=Math.min(left,Math.round(available*60));if(frames<180)throw Error(`Scene ${s.id}: avoid a sub-3-second flash cut (${key}, ${frames} frames)`);left-=frames;
     s.cuts.push({key,sourceIn,frames,seconds:frames/60,...catalog[key],originalIn:catalog[key].originalOffset+sourceIn});
   }
   if(left||s.gameFrames<=0||s.diagramFrames<=0)throw Error(`Scene ${s.id}: insufficient distinct cuts (${left} frames)`);
 }
 const plan={revision:'final-v1',fps:60,introFrames,introSeconds,bodyFrames,bodySeconds:bodyFrames/60,bodyEnd:introSeconds+bodyFrames/60,outroFrames:600,totalFrames:introFrames+bodyFrames+600,seconds:introSeconds+bodyFrames/60+10,gameplaySeconds:target/60,explanationSeconds:(bodyFrames-target)/60,gameplayShare:target/bodyFrames,diagramFrames:bodyFrames-target,screenLayout:'docs/VIDEO_SCREEN_LAYOUT.md',scenes};
 write(path.join(work,'plan.json'),plan);write(path.join(mc,'production-plan.json'),plan);
 const sourceRanges={};
 for(const s of scenes){
   const clips=[];
   for(const [i,c] of s.cuts.entries()){
     const source=abs(c.file),meta=probe(source);if(!meta.streams.some(v=>v.codec_type==='video'))throw Error('Source has no video: '+c.file);const sourceDuration=+meta.streams.find(v=>v.codec_type==='video').duration;if(sourceDuration<c.sourceIn+c.seconds-.02)throw Error('Source video stream too short: '+c.key);
     if(+meta.format.duration<c.sourceIn+c.seconds-.02)throw Error(`Source too short: ${c.key}`);
     // Detect accidental re-use of exactly the same source interval, even across raw files.
     const identity=c.url||c.file,ranges=sourceRanges[identity]??=[];
     if(ranges.some(([a,b])=>c.originalIn<b-.001&&c.originalIn+c.seconds>a+.001))throw Error(`Overlapping source range: ${c.key}`);
     ranges.push([c.originalIn,c.originalIn+c.seconds]);sourceRanges[identity]=ranges;
     const stem=`cut-${s.id}-${i+1}`,clip=path.join(work,stem+'.mp4'),audio=path.join(work,stem+'.wav');
     c.video=rel(clip);c.audio=rel(audio);c.timelineStart=s.start+s.cuts.slice(0,i).reduce((a,v)=>a+v.seconds,0);
     const title=path.join(work,stem+'-title.txt'),credit=path.join(work,stem+'-credit.txt');write(title,c.title);write(credit,c.credit);
     const v=meta.streams.find(v=>v.codec_type==='video'),ratio=v.width/v.height;
     const creditFilter='null';
     // 16:9 games fill the screen. Retro games keep their complete native image,
     // full-height, over a blurred extension of the SAME moving source frame.
     const filters=c.key==='meat'
       ? ['-filter_complex',`[0:v]fps=60,crop=1920:808:0:136,setsar=1,split[bg][fg];[bg]scale=480:270:force_original_aspect_ratio=increase,crop=480:270,boxblur=10:2,scale=1920:1080[back];[fg]scale=1920:808[front];[back][front]overlay=0:(H-h)/2,${creditFilter}[v]`,'-map','[v]']
       : ratio>1.72&&ratio<1.84
       ? ['-vf',`fps=60,scale=1920:1080,setsar=1,${creditFilter}`]
       : ['-filter_complex',`[0:v]fps=60,setsar=1,split[bg][fg];[bg]scale=480:270:force_original_aspect_ratio=increase,crop=480:270,boxblur=10:2,scale=1920:1080[back];[fg]scale=-2:1080:flags=neighbor[front];[back][front]overlay=(W-w)/2:0,${creditFilter}[v]`,'-map','[v]'];
     c.presentation=c.key==='meat'?'native-ultrawide-with-black-bars-removed-and-moving-source-extension':ratio>1.72&&ratio<1.84?'full-screen':'full-height-native-aspect-with-same-source-background-extension';
     console.log(`Cut ${s.id}-${i+1}: ${c.key} original ${c.originalIn} + ${c.seconds.toFixed(3)}s`);
     ff(['-ss',String(c.sourceIn),'-i',source,'-frames:v',String(c.frames),...filters,...enc,clip]);
     c.hasSourceAudio=!c.muteSourceAudio&&meta.streams.some(v=>v.codec_type==='audio');
     if(c.muteSourceAudio)c.audioNote='Separately licensed in-game music muted; approved continuous Nimbus used. Footage rights and educational commentary documented in SOURCES.md.';
     if(c.hasSourceAudio){
       ff(['-ss',String(c.sourceIn),'-i',source,'-vn','-af',`atrim=duration=${c.seconds},asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.12,afade=t=out:st=${Math.max(0,c.seconds-.3)}:d=0.3,apad,atrim=duration=${c.seconds}`,'-c:a','pcm_s16le',audio]);
     }else ff(['-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',String(c.seconds),'-c:a','pcm_s16le',audio]);
     clips.push(clip);
   }
   const list=path.join(work,`game-${s.id}-concat.txt`);write(list,clips.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
   ff(['-f','concat','-safe','0','-i',list,'-c','copy',path.join(mc,`assets/game-${s.id}.mp4`)]);
   write(path.join(mc,`scenes/diagram${s.id}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {diagramScene} from '../diagram';\nimport plan from '../production-plan.json';\nexport default makeScene2D(function*(view){yield* diagramScene(view,${s.index},plan.scenes[${s.index}].diagramSeconds);});\n`);
 }
 write(path.join(work,'plan.json'),plan);write(path.join(mc,'production-plan.json'),plan);
 const introImport="import intro from '../small-window-game-design/intro-cats-v2/scene?scene';\n";
 write(path.join(mc,'explanation-project.ts'),`import {makeProject} from '@motion-canvas/core';\n${introImport}${scenes.map(s=>`import s${s.id} from './scenes/diagram${s.id}?scene';`).join('\n')}\nimport outro from './scenes/membership-outro?scene';\nexport default makeProject({name:'praise-player-explanation-reel',scenes:[intro,${scenes.map(s=>'s'+s.id).join(',')},outro]});\n`);
 write(path.join(mc,'project.ts'),`import {makeProject} from '@motion-canvas/core';\nimport audio from './assets/final-mix.m4a';\n${introImport}${scenes.map(s=>`import s${s.id} from './scenes/scene${s.id}?scene';`).join('\n')}\nimport outro from './scenes/membership-outro?scene';\nexport default makeProject({name:'게임은 왜 플레이어를 칭찬할까 — 검토본',audio,scenes:[intro,${scenes.map(s=>'s'+s.id).join(',')},outro]});\n`);
 for(const [lang,suffix] of [['ko','.srt'],['en','.en.srt']]){
   const source=abs(`${m.tts.outputDir}/${m.tts.filenameStem}${suffix}`),target=path.join(work,`captions.${lang}.srt`);
   const shift=t=>{const [h,min,sec]=t.replace(',','.').split(':'),ms=Math.round((+h*3600+ +min*60+ +sec+introSeconds)*1000);return `${String(Math.floor(ms/3600000)).padStart(2,'0')}:${String(Math.floor(ms/60000)%60).padStart(2,'0')}:${String(Math.floor(ms/1000)%60).padStart(2,'0')},${String(ms%1000).padStart(3,'0')}`;};
   write(target,fs.readFileSync(source,'utf8').replace(/(\d\d:\d\d:\d\d,\d{3}) --> (\d\d:\d\d:\d\d,\d{3})/g,(_,a,b)=>`${shift(a)} --> ${shift(b)}`));
   m.paths[lang==='ko'?'captionsKo':'captionsEn']=rel(target);
 }
 write(mf,m);
 const registry=path.join(root,'motion-canvas/projects.json'),list=read(registry),route='./src/projects/praise-player/explanation-project.ts';if(!list.includes(route)){list.push(route);write(registry,list);}
 console.log(JSON.stringify({body:plan.bodySeconds,gameplay:plan.gameplaySeconds,explanation:plan.explanationSeconds,total:plan.seconds}));
}else if(stage==='mix'){
 const p=read(path.join(work,'plan.json')),D=p.seconds,cuts=p.scenes.flatMap(s=>s.cuts);
 if(m.audio.backgroundMusic.approvalStatus!=='approved')throw Error('Music approval missing');
 const narration=abs(m.paths.narration),norm=path.join(work,'narration-normalized.wav');
 const scan=spawnSync('ffmpeg',['-hide_banner','-i',narration,'-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-'],{encoding:'utf8',windowsHide:true,maxBuffer:4e6});
 if(scan.status!==0)throw Error(scan.stderr);const measured=JSON.parse(scan.stderr.match(/\{\s*"input_i"[\s\S]*?\}/)[0]);
 ff(['-i',narration,'-af',`loudnorm=I=-16:TP=-2:LRA=11:measured_I=${measured.input_i}:measured_TP=${measured.input_tp}:measured_LRA=${measured.input_lra}:measured_thresh=${measured.input_thresh}:offset=${measured.target_offset}:linear=true,aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,adelay=${p.introFrames/60*48000}S:all=1,asetpts=N/SR/TB,apad,atrim=duration=${D}`,'-c:a','pcm_s16le',norm]);
 // Dynamic loudnorm can undershoot on sparse speech. Use measured remaining
 // headroom for a constant final gain, without raising the -2 dBTP voice ceiling.
 const voiceScan=spawnSync('ffmpeg',['-hide_banner','-i',norm,'-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-'],{encoding:'utf8',windowsHide:true,maxBuffer:4e6});
 if(voiceScan.status!==0)throw Error(voiceScan.stderr);
 const voiceMeasured=JSON.parse(voiceScan.stderr.match(/\{\s*"input_i"[\s\S]*?\}/)[0]),voiceGain=Math.min(-16- +voiceMeasured.input_i,-2- +voiceMeasured.input_tp);
 const voicePass=path.join(work,'narration-loudnorm-pass.wav');fs.copyFileSync(norm,voicePass);
 ff(['-i',voicePass,'-af',`volume=${voiceGain}dB`,'-c:a','pcm_s16le',norm]);
 if(Math.abs(+probe(norm).format.duration-D)>.02)throw Error('Normalized narration must cover the complete intro/body/outro timeline');
 let music=abs(m.audio.backgroundMusic.file),musicSeconds=+probe(music).format.duration;
 if(D>musicSeconds){const n=Math.ceil((D-1)/(musicSeconds-1)),args=[];for(let i=0;i<n;i++)args.push('-i',music);let chain='';for(let i=1;i<n;i++)chain+=`${i===1?'[0:a]':'[b'+(i-1)+']'}[${i}:a]acrossfade=d=1:c1=tri:c2=tri[b${i}];`;music=path.join(work,'music-loop.wav');ff([...args,'-filter_complex',chain.slice(0,-1),'-map',`[b${n-1}]`,'-c:a','pcm_s16le',music]);}
 const args=['-i',norm,...cuts.flatMap(c=>['-i',abs(c.audio)]),'-i',music];
 const filters=['[0:a]asplit=3[n][d1][d2]'];
 cuts.forEach((c,i)=>filters.push(`[${i+1}:a]adelay=${Math.round(c.timelineStart*48000)}S:all=1,apad,atrim=duration=${D}[g${i}]`));
 filters.push(cuts.map((c,i)=>`[g${i}]`).join('')+`amix=inputs=${cuts.length}:normalize=0[g]`);
 const overlap=cuts.filter(c=>c.hasSourceAudio).map(c=>`if(between(t,${c.timelineStart},${c.timelineStart+c.seconds}),min(1,min((t-${c.timelineStart})/0.45,(${c.timelineStart+c.seconds}-t)/0.45)),0)`).join('+');
 filters.push(`[${cuts.length+1}:a]atrim=duration=${D},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,volume='1-0.292054*(${overlap})':eval=frame,afade=t=in:d=0.45,afade=t=out:st=${D-.45}:d=0.45[b]`);
 filters.push('[g][d1]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[gd]','[b][d2]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[bd]','[gd][bd]amix=inputs=2:normalize=0,asplit=2[bg][bgo]','[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true[mix]');
 write(path.join(work,'mix-filter.txt'),filters.join(';\n'));
 ff([...args,'-filter_complex_script',path.join(work,'mix-filter.txt'),'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',abs(m.paths.editorAudioMix),'-map','[bgo]','-ar','48000','-ac','2','-c:a','pcm_s16le',path.join(work,'background-only.wav')]);
 ff(['-i',abs(m.paths.editorAudioMix),'-c:a','aac','-b:a','192k',abs(m.paths.audioMix)]);
 if(Math.abs(+probe(abs(m.paths.audioMix)).format.duration-D)>.03)throw Error('Final mix duration does not cover intro/body/outro');
 write(path.join(work,'mix-settings.json'),{...m.audio,seconds:D,narrationMeasurement:measured,voicePostPassMeasurement:voiceMeasured,voiceFinalGainDb:voiceGain,sourceGainAfterDuckingDb:0,sourceTimeline:'per-cut absolute sample delays; silence preserved in explanations',outroCovered:true});
 console.log('Continuous narration, source sound and Nimbus mix created.');
}else if(stage==='assemble'){
 const p=read(path.join(work,'plan.json')),reel=abs('shared/output/motion-canvas/praise-player-explanation-reel.mp4'),files=[];
 const intro=path.join(work,'intro.mp4');ff(['-i',reel,'-frames:v',String(p.introFrames),...enc,intro]);files.push(intro);
 for(const s of p.scenes){const f=path.join(work,`diagram-${s.id}.mp4`);ff(['-ss',String(s.diagramStart),'-i',reel,'-frames:v',String(s.diagramFrames),...enc,f]);files.push(path.join(mc,`assets/game-${s.id}.mp4`),f);}
 const outro=path.join(work,'outro.mp4');ff(['-ss',String(p.introSeconds+p.explanationSeconds),'-i',reel,'-frames:v','600',...enc,outro]);files.push(outro);
 const list=path.join(work,'final-concat.txt');write(list,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
 ff(['-f','concat','-safe','0','-i',list,'-i',abs(m.paths.audioMix),'-map','0:v','-map','1:a','-c','copy','-t',String(p.seconds),'-movflags','+faststart',abs(m.paths.videoClean)]);
 console.log(abs(m.paths.videoClean));
}else if(stage==='remux'){
 const p=read(path.join(work,'plan.json'));
 for(const key of ['videoClean','videoBurnedCaptions']){
  const original=abs(m.paths[key]),target=path.join(work,key+'-remix.mp4'),backup=path.join(work,key+'-previous-mix.mp4');
  ff(['-i',original,'-i',abs(m.paths.audioMix),'-map','0:v','-map','1:a','-c','copy','-t',String(p.seconds),'-movflags','+faststart',target]);
  fs.copyFileSync(original,backup);fs.copyFileSync(target,original);
 }
 console.log('Both video pictures and captions preserved; approved full mix replaced together.');
}else throw Error('Use prepare | mix | assemble | remux');
