// Approved cat intro + preserved body. Rebuild from original stems, never mixed audio.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'intro-v3');
const abs=p=>path.join(root,p),rel=p=>path.relative(root,p).replaceAll('\\','/');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const write=(p,v)=>{fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');};
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:32e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const ff=args=>run('ffmpeg',['-hide_banner','-v','error','-y',...args]);
const probe=p=>JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',p]));
const mp=abs('projects/small-window-game-design/project.json');
fs.mkdirSync(work,{recursive:true});
const snapshot=path.join(work,'body-manifest.json');
if(!fs.existsSync(snapshot)){const m=read(mp);if(m.editing.intro?.applied)throw Error('Need original body manifest, not intro version');write(snapshot,m);}
const m=read(snapshot),plan=read(path.join(__dirname,'full-v2/plan.json')),offset=2,D=plan.seconds+offset,frames=plan.totalFrames+120;
const intro=abs('shared/output/motion-canvas/yamyam-intro-sample-v2-visual.mp4');
const assets='motion-canvas/src/projects/small-window-game-design/assets/';
const outputs={audioMix:assets+'final-mix-intro-v3.m4a',editorAudioMix:assets+'final-mix-intro-v3.wav',videoClean:'shared/output/motion-canvas/small-window-game-design-intro-v3.mp4',videoBurnedCaptions:'shared/output/motion-canvas/small-window-game-design-intro-v3-subtitled.mp4',captionsKo:rel(path.join(work,'captions.ko.srt')),captionsEn:rel(path.join(work,'captions.en.srt')),captionEditable:rel(path.join(work,'captions.ko.ass'))};
const stage=process.argv[2];
if(stage==='build'){
  if(+probe(intro).streams.find(s=>s.codec_type==='video').nb_frames!==120)throw Error('Intro must be 120 frames');
  if(+probe(abs(m.paths.videoClean)).streams.find(s=>s.codec_type==='video').nb_frames!==plan.totalFrames)throw Error('Unexpected body');
  if(m.audio.backgroundMusic.approvalStatus!=='approved')throw Error('Music approval missing');
  if(+probe(abs(m.audio.backgroundMusic.file)).format.duration<D)throw Error('Need music crossfade, not a hard loop');
  const args=['-i',abs(m.paths.narration)];plan.scenes.forEach(s=>args.push('-i',path.join(__dirname,`full-v2/game-${s.id}.wav`)));args.push('-i',abs(m.audio.backgroundMusic.file));
  const overlap=plan.scenes.map(s=>{const a=s.start+offset,b=a+s.gameSeconds;return `if(between(t,${a},${b}),min(1,min((t-${a})/0.45,(${b}-t)/0.45)),0)`;}).join('+');
  const filter=`[0:a]loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,adelay=2000:all=1,asetpts=N/SR/TB,apad,atrim=duration=${D},asplit=3[n][d1][d2];`+
    `[1:a][2:a][3:a][4:a][5:a][6:a]concat=n=6:v=0:a=1,adelay=2000:all=1,asetpts=N/SR/TB,apad,atrim=duration=${D}[g];`+
    `[7:a]atrim=duration=${D},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,asetpts=N/SR/TB,volume='1-0.292054*(${overlap})':eval=frame,afade=t=in:d=0.45,afade=t=out:st=${D-.45}:d=0.45[b];`+
    `[g][d1]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280,volume=${m.audio.gameAudioGain}[gd];`+
    `[b][d2]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[bd];`+
    `[gd][bd]amix=inputs=2:normalize=0,asplit=2[bg][bgo];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true,asetpts=N/SR/TB,apad,atrim=end_sample=${Math.round(D*48000)}[mix]`;
  write(path.join(work,'mix-filter.txt'),filter);
  console.log('Mix: continuous Discovery, delayed narration/source, source gain 0.5');
  ff([...args,'-filter_complex',filter,'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',abs(outputs.editorAudioMix),'-map','[bgo]','-ar','48000','-ac','2','-c:a','pcm_s16le',path.join(work,'background-only.wav')]);
  ff(['-i',abs(outputs.editorAudioMix),'-c:a','aac','-b:a','192k',abs(outputs.audioMix)]);
  for(const lang of ['Ko','En']){
    const original=fs.readFileSync(abs(m.paths['captions'+lang]),'utf8');
    const shifted=original.replace(/(\d{2}):(\d{2}):(\d{2}),(\d{3})/g,(_,h,m,s,ms)=>{let t=(((+h*60)+ +m)*60+ +s)*1000+ +ms+2000;return `${String(Math.floor(t/3600000)).padStart(2,'0')}:${String(Math.floor(t/60000)%60).padStart(2,'0')}:${String(Math.floor(t/1000)%60).padStart(2,'0')},${String(t%1000).padStart(3,'0')}`;});
    write(abs(outputs['captions'+lang]),shifted);
  }
  const shiftAss=t=>{const [h,m,s]=t.split(':');const c=Math.round((+h*3600+ +m*60+ +s+2)*100);return `${Math.floor(c/360000)}:${String(Math.floor(c/6000)%60).padStart(2,'0')}:${String(Math.floor(c/100)%60).padStart(2,'0')}.${String(c%100).padStart(2,'0')}`;};
  write(abs(outputs.captionEditable),fs.readFileSync(abs(m.paths.captionEditable),'utf8').replace(/^(Dialogue: \d+,)([^,]+),([^,]+)/gm,(_,a,b,c)=>a+shiftAss(b)+','+shiftAss(c)));
  console.log('Assemble: 120 intro frames + unchanged body video stream');
  const normalized=path.join(work,'intro-normalized.mp4');
  ff(['-i',intro,'-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-frames:v','120','-video_track_timescale','90000',normalized]);
  const list=path.join(work,'concat.txt');write(list,[normalized,abs(m.paths.videoClean)].map(p=>`file '${p.replaceAll('\\','/')}'`).join('\n'));
  ff(['-f','concat','-safe','0','-i',list,'-i',abs(outputs.audioMix),'-map','0:v','-map','1:a','-c','copy','-t',String(D),'-movflags','+faststart',abs(outputs.videoClean)]);
  console.log('Burn captions: original layout, all cues shifted +2s');
  ff(['-i',abs(outputs.videoClean),'-vf',`ass='${outputs.captionEditable}'`,'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',abs(outputs.videoBurnedCaptions)]);
  write(path.join(work,'timeline.json'),{introSeconds:2,seconds:D,frames,bodyOffsetSeconds:2,bodySeconds:plan.seconds,scenes:[{id:'intro-cats-v2',start:0,seconds:2},...plan.scenes.map(s=>({...s,start:s.start+2}))]});
  console.log('Build complete');
}else if(stage==='verify'){
  const qa={seconds:D,frames,introSeconds:2,bodyPreserved:true,gameAudioGain:m.audio.gameAudioGain,bgmContinuous:true,files:{}};
  qa.editorAudioSeconds=+probe(abs(outputs.editorAudioMix)).format.duration;
  if(Math.abs(qa.editorAudioSeconds-D)>.001)throw Error('Editor mix duration mismatch');
  const audioHashes=p=>run('ffmpeg',['-v','error','-i',p,'-map','0:a:0','-c','copy','-f','framehash','-']).split('\n').filter(l=>l&&!l.startsWith('#')).map(l=>l.split(',').at(-1).trim());
  const masterAudioHashes=audioHashes(abs(outputs.audioMix));
  for(const key of ['videoClean','videoBurnedCaptions']){
    const p=probe(abs(outputs[key])),v=p.streams.find(s=>s.codec_type==='video'),a=p.streams.find(s=>s.codec_type==='audio');
    if(+v.nb_frames!==frames||Math.abs(+v.duration-D)>.04||!a)throw Error('Bad output '+key);
    ff(['-i',abs(outputs[key]),'-f','null','-']);qa.files[key]={frames:+v.nb_frames,seconds:+v.duration,width:v.width,height:v.height,fps:v.avg_frame_rate};
    if(Math.abs(+a.duration-D)>.05)throw Error('Muxed audio duration mismatch');
    if(JSON.stringify(masterAudioHashes)!==JSON.stringify(audioHashes(abs(outputs[key]))))throw Error('Audio packets differ');
  }
  const videoHashes=p=>run('ffmpeg',['-v','error','-i',p,'-map','0:v:0','-c','copy','-f','framehash','-']).split('\n').filter(l=>l&&!l.startsWith('#')).map(l=>l.split(',').at(-1).trim());
  const oldHashes=videoHashes(abs(m.paths.videoClean)),newHashes=videoHashes(abs(outputs.videoClean)).slice(120);
  if(JSON.stringify(oldHashes)!==JSON.stringify(newHashes))throw Error('Body packet content changed');qa.unchangedBodyPackets=oldHashes.length;
  const times=p=>fs.readFileSync(abs(p),'utf8').match(/\d\d:\d\d:\d\d,\d{3} --> \d\d:\d\d:\d\d,\d{3}/g);
  if(JSON.stringify(times(outputs.captionsKo))!==JSON.stringify(times(outputs.captionsEn)))throw Error('KO/EN mismatch');qa.cueCount=times(outputs.captionsKo).length;
  for(const [label,t] of [['intro',1.2],['body-start',2.5],['diagram',30],['end',D-1]])ff(['-ss',String(t),'-i',abs(outputs.videoBurnedCaptions),'-frames:v','1','-update','1',path.join(work,`${label}.jpg`)]);
  write(path.join(work,'qa.json'),qa);console.log(qa);
}else if(stage==='activate'){
  const qa=read(path.join(work,'qa.json')),current=read(mp);
  Object.assign(current.paths,outputs);current.approvals.intro='approved-user-selected-second-cat-intro';
  current.editing.intro={applied:true,seconds:2,frames:120,position:'prepend',scene:'intro-cats-v2',asset:'shared/assets/branding/yamyamcoding-cats-original.png',scope:'this-project'};
  current.production.bodyOnly=false;current.production.sceneCount=7;current.production.introSeconds=2;
  current.video.durationSeconds=D;current.finalRender={...current.finalRender,kind:'intro-and-full-body',qa:rel(path.join(work,'qa.json')),frames,seconds:D};
  current.audio.mixStatus='intro-and-body-mixed-verified-awaiting-human-listening';
  write(mp,current);console.log('Manifest activated',qa.frames);
}else throw Error('Use build | verify | activate');
