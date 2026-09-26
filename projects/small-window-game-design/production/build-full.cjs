// Reproducible body build. No membership screenshot is fabricated.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),slug='small-window-game-design',project=path.join(root,'projects',slug),mc=path.join(root,'motion-canvas/src/projects',slug),work=path.join(__dirname,'full-v2');
const manifestPath=path.join(project,'project.json'),m=JSON.parse(fs.readFileSync(manifestPath,'utf8'));
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:24e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const probe=f=>JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',f]));
const ff=args=>run('ffmpeg',['-v','error','-y',...args]);
const encoding=['-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
const stage=process.argv[2];fs.mkdirSync(work,{recursive:true});
if(stage==='prepare'){
  const script=read(path.join(project,'script/narration.ko.json')),timing=read(path.join(root,m.tts.outputDir,m.tts.filenameStem+'.timing.json'));
  const starts=script.scenes.map(s=>Math.round(timing.entries.find(e=>e.scene_id===s.id).start*30)*2),totalFrames=Math.round(timing.duration_seconds*30)*2;
  const sources=[['forza',30],['forza',185],['doom',65],['doom',170],['doom',115],['forza',285]];
  let diagramStart=0;
  const scenes=script.scenes.map((s,i)=>{
    const frames=(starts[i+1]??totalFrames)-starts[i];let gameFrames=Math.round(frames*m.editing.targetGameplayShare);
    // The spoken "our comparison" must begin with the original aspect-ratio diagram.
    if(i===1){const entry=timing.entries.filter(e=>e.scene_id===s.id)[4];gameFrames=Math.round((entry.voice_start??entry.start)*60)-starts[i];}
    const [game,sourceIn]=sources[i],source=path.join(project,`sources/media/${game}-full-${game==='forza'?'ZnCxVxfv3MM':'YANZzc_bHSU'}.mp4`);
    const row={id:s.id,index:i,title:s.title,start:starts[i]/60,frames,seconds:frames/60,gameFrames,gameSeconds:gameFrames/60,diagramStart,diagramSeconds:(frames-gameFrames)/60,game,source:path.relative(root,source).replaceAll('\\','/'),sourceIn};
    diagramStart+=row.diagramSeconds;return row;
  });
  const target=Math.round(totalFrames*m.editing.targetGameplayShare),delta=target-scenes.reduce((a,s)=>a+s.gameFrames,0);
  scenes[5].gameFrames+=delta;scenes[5].gameSeconds=scenes[5].gameFrames/60;scenes[5].diagramSeconds=scenes[5].seconds-scenes[5].gameSeconds;
  diagramStart=0;scenes.forEach(s=>{s.diagramStart=diagramStart;diagramStart+=s.diagramSeconds;});
  const plan={revision:'v2-screen-framing',fps:60,totalFrames,seconds:totalFrames/60,gameplaySeconds:target/60,gameplayShare:target/totalFrames,diagramFrames:totalFrames-target,scenes};
  write(path.join(work,'plan.json'),plan);write(path.join(mc,'full/plan.json'),plan);
  for(const s of scenes){
    const source=path.join(root,s.source),clip=path.join(mc,`assets/game-${s.id}.mp4`);
    if(+probe(source).format.duration<s.sourceIn+s.gameSeconds)throw Error('Source too short');
    console.log(`Cut ${s.id}: ${s.game} ${s.sourceIn} + ${s.gameSeconds.toFixed(3)} seconds`);
    ff(['-ss',String(s.sourceIn),'-i',source,'-t',String(s.gameSeconds),'-vf','fps=60,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1',...encoding,clip]);
    ff(['-ss',String(s.sourceIn),'-i',source,'-t',String(s.gameSeconds),'-vn','-af',`loudnorm=I=${m.audio.gameAudioTargetLufs}:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.12,afade=t=out:st=${s.gameSeconds-.3}:d=0.3,apad,atrim=duration=${s.seconds}`,'-c:a','pcm_s16le',path.join(work,`game-${s.id}.wav`)]);
    write(path.join(mc,`full/diagram${s.id}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {diagramScene} from './diagram';\nimport plan from './plan.json';\nexport default makeScene2D(function*(view){yield* diagramScene(view,${s.index},plan.scenes[${s.index}].diagramSeconds);});\n`);
    write(path.join(mc,`full/scene${s.id}.tsx`),`import {makeScene2D} from '@motion-canvas/2d';\nimport {fullScene} from './runner';\nimport clip from '../assets/game-${s.id}.mp4';\nexport default makeScene2D(function*(view){yield* fullScene(view,${s.index},clip);});\n`);
  }
  write(path.join(mc,'full/diagram-project.ts'),`import {makeProject} from '@motion-canvas/core';\n${scenes.map(s=>`import s${s.id} from './diagram${s.id}?scene';`).join('\n')}\nexport default makeProject({name:'화면 비율 · FOV — 자체 2.5D 설명',scenes:[${scenes.map(s=>'s'+s.id).join(',')}]});\n`);
  write(path.join(mc,'project.ts'),`import {makeProject} from '@motion-canvas/core';\nimport audio from './assets/final-mix.wav';\n${scenes.map(s=>`import s${s.id} from './full/scene${s.id}?scene';`).join('\n')}\nexport default makeProject({name:'화면 비율과 시야각 — 전체 음성 본편',audio,scenes:[${scenes.map(s=>'s'+s.id).join(',')}]});\n`);
  const registry=path.join(root,'motion-canvas/projects.json'),list=read(registry),route='./src/projects/small-window-game-design/full/diagram-project.ts';if(!list.includes(route)){list.push(route);write(registry,list);}
  console.log(plan);
}else if(stage==='mix'){
  const plan=read(path.join(work,'plan.json')),D=plan.seconds,bgm=path.join(root,m.audio.backgroundMusic.file);
  if(m.audio.backgroundMusic.approvalStatus!=='approved')throw Error('BGM not approved');
  let music=bgm;const musicSeconds=+probe(bgm).format.duration;
  if(D>musicSeconds){music=path.join(work,'music-loop.wav');ff(['-i',bgm,'-i',bgm,'-filter_complex',`[0:a][1:a]acrossfade=d=1:c1=tri:c2=tri,atrim=duration=${D}[b]`,'-map','[b]','-c:a','pcm_s16le',music]);}
  const args=['-i',path.join(root,m.paths.narration)];plan.scenes.forEach(s=>args.push('-i',path.join(work,`game-${s.id}.wav`)));args.push('-i',music);
  const overlap=plan.scenes.map(s=>`if(between(t,${s.start},${s.start+s.gameSeconds}),min(1,min((t-${s.start})/0.45,(${s.start+s.gameSeconds}-t)/0.45)),0)`).join('+');
  const filter=`[0:a]loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration=${D},asplit=3[n][d1][d2];`+
    `[1:a][2:a][3:a][4:a][5:a][6:a]concat=n=6:v=0:a=1[g];`+
    `[7:a]atrim=duration=${D},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,volume='1-0.292054*(${overlap})':eval=frame,afade=t=in:d=0.45,afade=t=out:st=${D-.45}:d=0.45[b];`+
    `[g][d1]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280,volume=${m.audio.gameAudioGain}[gd];`+
    `[b][d2]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[bd];`+
    `[gd][bd]amix=inputs=2:normalize=0,asplit=2[bg][bgo];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true[mix]`;
  ff([...args,'-filter_complex',filter,'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',path.join(mc,'assets/final-mix.wav'),'-map','[bgo]','-ar','48000','-ac','2','-c:a','pcm_s16le',path.join(work,'background-only.wav')]);
  ff(['-i',path.join(mc,'assets/final-mix.wav'),'-c:a','aac','-b:a','192k',path.join(root,m.paths.audioMix)]);
  write(path.join(work,'mix-settings.json'),{...m.audio,seconds:D,sourceGainAppliedAfterDucking:m.audio.gameAudioGain,postGainNormalization:false});
}else if(stage==='assemble'){
  const plan=read(path.join(work,'plan.json')),reel=path.join(root,'shared/output/motion-canvas/small-window-diagram-reel-v2.mp4'),files=[];
  for(const s of plan.scenes){
    const diagram=path.join(work,`diagram-${s.id}.mp4`);
    ff(['-ss',String(s.diagramStart),'-i',reel,'-frames:v',String(s.frames-s.gameFrames),...encoding,diagram]);
    files.push(path.join(mc,`assets/game-${s.id}.mp4`),diagram);
  }
  const concat=path.join(work,'concat.txt');write(concat,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
  ff(['-f','concat','-safe','0','-i',concat,'-i',path.join(root,m.paths.audioMix),'-map','0:v','-map','1:a','-c','copy','-t',String(plan.seconds),'-movflags','+faststart',path.join(root,m.paths.videoClean)]);
  console.log('Clean body: '+m.paths.videoClean);
}else throw Error('Use prepare | mix | assemble');
