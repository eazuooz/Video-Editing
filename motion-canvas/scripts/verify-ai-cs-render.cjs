// Verify a completed full-length review render, then package sidecar captions.
// node scripts/verify-ai-cs-render.cjs <absolute-or-repo-relative-mp4>
const fs=require('node:fs'), path=require('node:path'), crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../..');
const manifest=JSON.parse(fs.readFileSync(path.join(root,'projects/ai-era-cs-fundamentals/project.json'),'utf8'));
const video=path.resolve(root,process.argv[2]??'');
const outputRoot=path.join(root,'shared/output/motion-canvas')+path.sep;
if(!video.startsWith(outputRoot)||!video.endsWith('.mp4')||!fs.existsSync(video))throw Error('Expected a completed review MP4');
const stem=video.slice(0,-4), base=path.basename(stem);
const qa=path.join(root,'shared/output/ai-cs-media-cache',`${base}-qa`);
fs.mkdirSync(qa,{recursive:true});
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,windowsHide:true,encoding:'utf8',maxBuffer:8*1024*1024});if(r.status!==0)throw Error(r.stderr);return r;}
const probe=JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',video]).stdout);
const v=probe.streams.find(s=>s.codec_type==='video'),a=probe.streams.find(s=>s.codec_type==='audio');
if(+v.nb_frames!==Math.round(manifest.video.durationSeconds*manifest.video.fps)||v.avg_frame_rate!==`${manifest.video.fps}/1`||!a||Math.abs(+probe.format.duration-manifest.video.durationSeconds)>.05)throw Error('Not the expected full render');
const packetHash=file=>run('ffmpeg',['-hide_banner','-v','error','-i',file,'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-']).stdout.trim();
const sourceAudioHash=packetHash(path.join(root,manifest.paths.audioMix)), renderedAudioHash=packetHash(video);
if(sourceAudioHash!==renderedAudioHash)throw Error('Rendered audio packets differ from the approved input mix');
const timing=JSON.parse(fs.readFileSync(path.join(root,manifest.tts.outputDir,`${manifest.tts.filenameStem}.timing.json`),'utf8'));
const first=new Map();for(const e of timing.entries)if(!first.has(e.scene_id))first.set(e.scene_id,e.start);
const lead=manifest.editing.narrationPlacement==='continuous-across-example-and-explanation'?0:manifest.editing.exampleSeconds;
const scenes=[...first].map(([scene,narrationStart])=>({scene,narrationStart,start:Math.round((narrationStart-lead)*30)/30}));
const measurements=[];
for(let i=0;i<scenes.length;i++){
  const s=scenes[i], entries=timing.entries.filter(e=>e.scene_id===s.scene), narrationEnd=entries.at(-1).end;
  for(const [kind,start,seconds,frameTime] of [
    ['example',s.start+.2,manifest.editing.exampleSeconds-.5,s.start+8],
    ['narration',s.narrationStart,narrationEnd-s.narrationStart,s.narrationStart+(narrationEnd-s.narrationStart)*.7],
  ]){
    const r=run('ffmpeg',['-hide_banner','-ss',String(start),'-t',String(seconds),'-i',video,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']);
    const levels=JSON.parse(r.stderr.match(/\{\s*"input_i"[\s\S]*?\}/)[0]);
    if(!Number.isFinite(+levels.input_i)||+levels.input_i<-40)throw Error(`Silent ${s.scene} ${kind}`);
    measurements.push({scene:s.scene,kind,start,seconds,lufs:+levels.input_i,truePeak:+levels.input_tp});
    run('ffmpeg',['-hide_banner','-v','error','-n','-ss',String(frameTime),'-i',video,'-frames:v','1','-update','1',path.join(qa,`${s.scene}-${kind}.png`)]);
  }
  console.log(`Verified scene ${s.scene}: original footage + narration`);
}
for(const kind of ['example','narration']){
  const inputs=scenes.flatMap(s=>['-i',path.join(qa,`${s.scene}-${kind}.png`)]);
  const scales=scenes.map((_,i)=>`[${i}:v]scale=480:270[s${i}]`);
  const stack=scenes.map((_,i)=>`[s${i}]`).join('')+`xstack=inputs=12:layout=${scenes.map((_,i)=>`${i%4*480}_${Math.floor(i/4)*270}`).join('|')}[sheet]`;
  run('ffmpeg',['-hide_banner','-v','error','-n',...inputs,'-filter_complex',[...scales,stack].join(';'),'-map','[sheet]','-frames:v','1','-update','1',path.join(qa,`${kind}-overview.jpg`)]);
}
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const captions=[];
for(const [language,key]of[['ko','captionsKo'],['en','captionsEn']]){
  const src=path.join(root,manifest.paths[key]),dest=`${stem}.${language}.srt`;
  fs.copyFileSync(src,dest,fs.constants.COPYFILE_EXCL);
  if(sha(src)!==sha(dest))throw Error('Caption copy mismatch');
  captions.push({language,path:path.relative(root,dest).replaceAll('\\','/'),sha256:sha(dest)});
}
const compatible=`${stem}-vscode.mp4`;
run('ffmpeg',['-hide_banner','-v','error','-n','-i',video,'-map','0:v:0','-map','0:a:0','-c:v','copy','-c:a','libmp3lame','-b:a','192k','-ar','48000','-movflags','+faststart',compatible]);
run('ffmpeg',['-hide_banner','-v','error','-i',compatible,'-f','null','-']);
const report={checkedAt:new Date().toISOString(),scriptRevision:manifest.scriptRevision,video:path.relative(root,video).replaceAll('\\','/'),bgmIncluded:['full-mix-awaiting-listening-review','full-mix-license-pending','final'].includes(manifest.audio.mixStatus),musicRightsVerified:manifest.audio.backgroundMusic.licenseStatus?.startsWith('verified')??false,publishReady:false,sourceAudioHash,renderedAudioHash,measurements,captions,compatible:path.relative(root,compatible).replaceAll('\\','/'),qa:path.relative(root,qa).replaceAll('\\','/'),subjectiveListeningApproval:false};
fs.writeFileSync(`${stem}-qa.json`,JSON.stringify(report,null,2)+'\n');
console.log(`QA complete: ${qa}`);
