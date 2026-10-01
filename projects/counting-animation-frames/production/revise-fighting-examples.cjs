// final-v2: content-aligned, normal-speed fighting examples between numeric tests.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),slug='counting-animation-frames',base=path.dirname(__dirname),work=path.join(__dirname,'final-v2'),mc=path.join(root,'motion-canvas/src/projects',slug);
const read=f=>JSON.parse(fs.readFileSync(f,'utf8')),write=(f,v)=>{fs.mkdirSync(path.dirname(f),{recursive:true});fs.writeFileSync(f,typeof v==='string'?v:JSON.stringify(v,null,2)+'\n');},rel=f=>path.relative(root,f).replaceAll('\\','/'),abs=f=>path.join(root,f),hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:24e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const ff=a=>run('ffmpeg',['-v','error','-y',...a]),enc=['-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
const old=read(path.join(__dirname,'final-v1/plan.json')),mf=path.join(base,'project.json'),m=read(mf),step=process.argv[2];fs.mkdirSync(work,{recursive:true});
const sources={
 ryu:{file:'shared/assets/counting-animation-frames/raw/sf6-ryu-guide.mp4',game:'Street Fighter 6',title:'스트리트 파이터 6 · 류의 준비와 회복',url:'https://www.youtube.com/watch?v=iAs1p3LVdAs',id:'iAs1p3LVdAs',owner:'Street Fighter',policy:'https://www.capcomusa.com/video-policy/Capcom_Video_Policy.pdf',build:'Official character guide, 2023; no current move-number claim'},
 chunli:{file:'shared/assets/counting-animation-frames/raw/sf6-chunli-guide.mp4',game:'Street Fighter 6',title:'스트리트 파이터 6 · 춘리의 공격 동작',url:'https://www.youtube.com/watch?v=seX6oUfwjII',id:'seX6oUfwjII',owner:'Street Fighter',policy:'https://www.capcomusa.com/video-policy/Capcom_Video_Policy.pdf',build:'Official character guide, 2023; no current move-number claim'},
 sol:{file:'shared/assets/counting-animation-frames/raw/ggst-sol-guide.mp4',game:'Guilty Gear -Strive-',title:'길티기어 스트라이브 · 자세와 타격',url:'https://www.youtube.com/watch?v=Nvtkod61MH8',id:'Nvtkod61MH8',owner:'arcsystemworks',policy:'https://www.arcsystemworks.jp/portal/videopolicy/',build:'Official closed-beta guide, 2020; observation only, not current release frame data'}
};
// Absolute movie boundaries are aligned to the existing narration, never to an
// arbitrary example-slot duration. Numerals remain on original tests/diagrams.
const layout=[
 [['megaman',10,12],['rise',19.2,9],['diagram',old.scenes[1].start,0]],
 [['chunli',34.6666666667,8],['diagram',44,0],['rate',54.35,0],['diagram',58.35,0],['chunli',old.scenes[2].start,27]],
 [['ryu',65.8,8],['interval',80.8,0],['diagram',90.88,0],['ryu',old.scenes[3].start,16.25]],
 [['sol',97.96,22.5],['diagram',113.56,0],['sol',120.96,40],['poses',old.scenes[4].start,0]],
 [['sol',129.68,33],['pause',136.82,0],['diagram',142.66,0],['sol',150.92,82],['diagram',old.scenes[5].start,0]],
 [['chunli',161.2166666667,17],['sol',164.7166666667,28],['render',171.44,0],['ryu',178.66,24],['diagram',old.bodyEnd,0]]
];
if(step==='prepare'){
 // Preserve the already uploaded v1 and its audio locally, without Git media.
 const archive=path.join(__dirname,'final-v1/archived-media');fs.mkdirSync(archive,{recursive:true});
 for(const [key,name] of [['videoClean','clean.mp4'],['videoBurnedCaptions','captioned.mp4'],['audioMix','final-mix.m4a'],['editorAudioMix','final-mix.wav']]){const target=path.join(archive,name);if(!fs.existsSync(target))fs.copyFileSync(abs(m.paths[key]),target);}
 write(path.join(work,'preserved-v1.json'),{uploadedVideoId:'piZTx_239R8',uploadedRevision:'final-v1',files:['clean.mp4','captioned.mp4','final-mix.m4a','final-mix.wav'].map(n=>({file:rel(path.join(archive,n)),sha256:hash(path.join(archive,n))})),previousQa:'projects/counting-animation-frames/production/final-v1/qa.json'});
 const catalogs=Object.fromEntries(old.scenes.flatMap(s=>s.cuts).map(c=>[c.key,c]));
 const p={...old,revision:'final-v2',sceneLayout:'actual game -> original measurement/explanation -> fresh actual game; captions remain tied to unchanged speech',scenes:[],diagramFrames:0,gameplaySeconds:0};
 const ranges={};let reelFrame=old.introFrames;
 for(const [index,s] of old.scenes.entries()){
  const scene={...s,segments:[],cuts:[],gameFrames:0,diagramFrames:0};let cursor=Math.round(s.start*60),diagrams=0;
  for(const [j,[key,end,sourceIn]] of layout[index].entries()){
   const endFrame=Math.round(end*60),frames=endFrame-cursor;if(frames<=0)throw Error('Non-positive edit');const seconds=frames/60,timelineStart=cursor/60,stem=`segment-${s.id}-${j+1}`,video=path.join(work,stem+'.mp4');
   const segment={key,frames,seconds,timelineStart,sceneOffset:(cursor-Math.round(s.start*60))/60,video:rel(video),kind:key==='diagram'?'original-2.5d-explanation':sources[key]?'actual-commercial-gameplay':'original-executable-playtest'};
   if(key==='diagram'){segment.diagramOffset=diagrams/60;diagrams+=frames;scene.diagramFrames+=frames;}
   else{
    const catalog=sources[key]||catalogs[key],file=catalog.file,source=abs(file),meta=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',source]));
    if(+meta.format.duration<sourceIn+seconds-.02)throw Error('Short source '+key);
    const identity=catalog.url||file,previous=ranges[identity]??=[];if(previous.some(([a,b])=>sourceIn<b-.001&&sourceIn+seconds>a+.001))throw Error('Repeated source range '+key);previous.push([sourceIn,sourceIn+seconds]);ranges[identity]=previous;
    const cut={...catalog,key,sourceIn,originalIn:sourceIn,originalOffset:0,frames,seconds,timelineStart,file,video:rel(video),audio:rel(path.join(work,stem+'.wav')),presentation:'full-screen',muteSourceAudio:!!sources[key]||!!catalog.muteSourceAudio,hasSourceAudio:!sources[key]&&!catalog.muteSourceAudio&&meta.streams.some(x=>x.codec_type==='audio'),normalSpeed:true,loop:false,artificialSlowdown:false};
    const label=sources[key]?catalog.title+' · 동작 관찰 (기술 수치 측정 아님)':'';
    const credit=path.join(work,stem+'-label.txt');write(credit,label);
    const overlay=label?`,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='${rel(credit)}':x=24:y=${key==='sol'?130:25}:fontsize=27:fontcolor=white:box=1:boxcolor=black@0.62:boxborderw=9`:'';
    console.log(`Cut ${s.id}.${j+1} ${key} ${sourceIn.toFixed(3)}–${(sourceIn+seconds).toFixed(3)} -> ${timelineStart.toFixed(3)}`);
    ff(['-ss',String(sourceIn),'-i',source,'-frames:v',String(frames),'-vf',`fps=60,scale=1920:1080,setsar=1${overlay}`,...enc,video]);
    if(cut.hasSourceAudio)ff(['-ss',String(sourceIn),'-i',source,'-vn','-af',`atrim=duration=${seconds},asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-3:LRA=11,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.12,afade=t=out:st=${Math.max(0,seconds-.3)}:d=0.3,apad,atrim=duration=${seconds}`,'-c:a','pcm_s16le',abs(cut.audio)]);
    else ff(['-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',String(seconds),'-c:a','pcm_s16le',abs(cut.audio)]);
    scene.cuts.push(cut);scene.gameFrames+=frames;segment.source=cut;
   }
   scene.segments.push(segment);cursor=endFrame;
  }
  if(cursor!==Math.round((s.start+s.seconds)*60))throw Error('Scene boundary changed');
  scene.diagramStart=reelFrame/60;reelFrame+=scene.diagramFrames;scene.gameSeconds=scene.gameFrames/60;scene.diagramSeconds=scene.diagramFrames/60;p.diagramFrames+=scene.diagramFrames;p.gameplaySeconds+=scene.gameSeconds;p.scenes.push(scene);
 }
 p.explanationSeconds=p.diagramFrames/60;p.gameplayShare=p.gameplaySeconds/p.bodySeconds;
 p.commercialGameplaySeconds=p.scenes.flatMap(s=>s.segments).filter(s=>s.kind==='actual-commercial-gameplay'||['megaman','rise'].includes(s.key)).reduce((n,s)=>n+s.seconds,0);
 p.originalPlaytestSeconds=p.gameplaySeconds-p.commercialGameplaySeconds;
 if(p.gameplayShare<.6||p.gameplayShare>.62)throw Error('Body ratio outside approved range');
 write(path.join(work,'plan.json'),p);write(path.join(mc,'production-plan.json'),p);
 for(const lang of ['ko','en']){const file=path.join(work,`captions.${lang}.srt`);fs.copyFileSync(path.join(__dirname,`final-v1/captions.${lang}.srt`),file);m.paths[lang==='ko'?'captionsKo':'captionsEn']=rel(file);}
 m.paths.timeline=rel(path.join(work,'plan.json'));m.paths.captionEditable=rel(path.join(work,'captions.ko.ass'));m.localRevision={revision:'final-v2',status:'preparing',uploadedRevision:'final-v1',uploadedVideoId:'piZTx_239R8',userRequest:'실제 격투게임 예시를 중간에 삽입하고 PPT처럼 보이는 자체 테스트를 줄이기',narrationAndCaptionTimingChanged:false};write(mf,m);
 const records=Object.values(sources).map(c=>{const info=read(abs(c.file.replace('.mp4','.info.json')));if(info.id!==c.id||info.uploader!==c.owner)throw Error('Unexpected recording owner');return {...c,recordingOwner:info.uploader,metadataChannelId:info.channel_id,metadataTitle:info.title,durationSeconds:info.duration,width:info.width,height:info.height,sourceFps:info.fps,sha256:hash(abs(c.file)),sourceAudio:'official voice/music omitted; approved continuous Nimbus retained',rights:{policy:c.policy,checkedAt:new Date().toISOString(),use:'short dynamic move examples with original timing commentary, not a repost of the guide',monetization:'publisher guideline permits platform advertising, subject to conditions; no paid-exclusive game video',publicRightsReview:'pending',policyRevision:c.owner==='arcsystemworks'?'2026-08-24 JP / 2021-06 US':'2021-03-15'}};});
 write(path.join(work,'fresh-source-review.json'),{reviewedAt:new Date().toISOString(),userSteering:'격투게임 예시가 적절',priorUseCheck:'Repository source/candidate search: SF6 previously F2347gyZp0U 40–46.5s; these two official guide IDs and all selected intervals unused. Guilty Gear Strive title/source not found previously.',selected:records,rejected:[{game:'Street Fighter 6 previous trailer F2347gyZp0U',reason:'Previously used; no interval reused'},{game:'Street Fighter II',reason:'Previously used; prioritize new GGST and fresh SF6 moves'},{game:'SF6 TGS2022 stream wZ7dEfccTZo',reason:'Capcom policy excludes reposting official event/competition footage without authorization; do not infer permission from general gameplay policy'},{game:'Tekken 8 / third-party frame guides',reason:'Adequate rights-holder recordings selected; unverified third-party recording permission not used'}],normalSpeed:true,loop:false,artificialSlowdown:false,accuracyBoundary:'No commercial move frame count or undocumented internal-clock implementation is asserted; 12/3/15 and pause=4 remain exclusively original-test data.'});
 console.log(JSON.stringify({seconds:p.seconds,commercial:p.commercialGameplaySeconds,originalTests:p.originalPlaytestSeconds,white2_5d:p.explanationSeconds,footageShare:p.gameplayShare}));
}else if(step==='assemble'){
 const p=read(path.join(work,'plan.json')),reel=abs('shared/output/motion-canvas/counting-animation-frames-explanation-reel.mp4'),all=[];
 const intro=path.join(work,'intro.mp4');ff(['-i',reel,'-frames:v','120',...enc,intro]);all.push(intro);
 for(const s of p.scenes){const sceneFiles=[];for(const seg of s.segments){const f=abs(seg.video);if(seg.key==='diagram')ff(['-ss',String(s.diagramStart+seg.diagramOffset),'-i',reel,'-frames:v',String(seg.frames),...enc,f]);sceneFiles.push(f);all.push(f);}
  const list=path.join(work,`scene-${s.id}-concat.txt`);write(list,sceneFiles.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));ff(['-f','concat','-safe','0','-i',list,'-c','copy',path.join(mc,`assets/body-${s.id}.mp4`)]);
 }
 const outro=path.join(work,'outro.mp4');ff(['-ss',String(p.introSeconds+p.explanationSeconds),'-i',reel,'-frames:v','600',...enc,outro]);all.push(outro);
 const list=path.join(work,'final-concat.txt');write(list,all.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
 ff(['-f','concat','-safe','0','-i',list,'-i',abs(m.paths.audioMix),'-map','0:v','-map','1:a','-c','copy','-t',String(p.seconds),'-movflags','+faststart',abs(m.paths.videoClean)]);console.log('Assembled final-v2, unchanged narration/caption times.');
}else throw Error('Use prepare | assemble');
