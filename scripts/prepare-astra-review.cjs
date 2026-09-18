// Builds a rights-pending LOCAL picture edit. No TTS, BGM or publication.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),base=path.join(root,'projects/gpt-astra-showcase');
const plan=require('../projects/gpt-astra-showcase/planning/edit-plan.json');
const posts=require('../projects/gpt-astra-showcase/sources/posts.generated.json').posts;
const motion=path.join(root,'motion-canvas/src/projects/gpt-astra-showcase');
const assets=path.join(motion,'assets/examples'),cache=path.join(base,'review/assembly');
fs.mkdirSync(assets,{recursive:true});fs.mkdirSync(cache,{recursive:true});
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;}
const probe=f=>JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',f]));
const duration=s=>s.cuts.reduce((n,c)=>n+c.out-c.in,0);
const audioParts=[],starts=[],durations=[],evidence=[];let current=0;
for(const scene of plan.scenes){
  starts.push(current);durations.push(scene.duration);current+=scene.duration;
  const clips=[],source=posts.find(p=>p.index===scene.post);
  for(const [index,cut] of scene.cuts.entries()){
    const media=source?.videos[cut.video-1];if(!media)throw Error('Missing source for '+scene.id);
    if(cut.in<0||cut.out>media.duration||cut.out<=cut.in)throw Error('Invalid source range');
    const seconds=cut.out-cut.in,frames=Math.round(seconds*plan.fps),id=`scene${scene.id}-cut${index+1}`;
    const input=path.join(root,media.file),file=path.join(cache,id+'.mp4'),wav=path.join(cache,id+'.wav');
    if(!fs.existsSync(file))run('ffmpeg',['-v','error','-n','-ss',String(cut.in),'-i',input,'-an','-vf','scale=1920:1080:force_original_aspect_ratio=decrease:force_divisible_by=2,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1,fps=60,format=yuv420p','-frames:v',String(frames),'-c:v','libx264','-preset','veryfast','-crf','23','-movflags','+faststart',file]);
    if(Number(probe(file).streams.find(s=>s.codec_type==='video').nb_frames)!==frames)throw Error('Incorrect cached cut '+id);
    const hasAudio=media.streams.some(s=>s.codec_type==='audio');
    if(!fs.existsSync(wav)){
      const args=hasAudio?['-ss',String(cut.in),'-i',input,'-vn','-af',`volume=0.15,afade=t=in:d=0.12,afade=t=out:st=${Math.max(0,seconds-.3)}:d=0.3,apad,atrim=duration=${seconds}`]:['-f','lavfi','-i','anullsrc=r=48000:cl=stereo'];
      run('ffmpeg',['-v','error','-n',...args,'-t',String(seconds),'-ar','48000','-ac','2','-c:a','pcm_s16le',wav]);
    }
    clips.push(file);audioParts.push(wav);evidence.push({scene:scene.id,sourcePost:source.url,sourceVideo:cut.video,in:cut.in,out:cut.out,frames,sourceHasAudio:hasAudio,reviewGain:0.15});
  }
  if(clips.length){
    const list=path.join(cache,`scene${scene.id}.ffconcat`),output=path.join(assets,`scene${scene.id}.mp4`);
    fs.writeFileSync(list,'ffconcat version 1.0\n'+clips.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n')+'\n');
    if(!fs.existsSync(output))run('ffmpeg',['-v','error','-n','-f','concat','-safe','0','-i',list,'-c:v','copy','-an','-movflags','+faststart',output]);
    if(Number(probe(output).streams[0].nb_frames)!==Math.round(duration(scene)*plan.fps))throw Error('Example frame mismatch '+scene.id);
  }
  const gap=scene.duration-duration(scene);if(gap<0)throw Error('Scene shorter than example');
  if(gap){const silence=path.join(cache,`scene${scene.id}-explanation-${gap}s.wav`);if(!fs.existsSync(silence))run('ffmpeg',['-v','error','-n','-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-t',String(gap),'-c:a','pcm_s16le',silence]);audioParts.push(silence);}
  console.log(`scene${scene.id}: ${duration(scene)}s example + ${gap}s original explanation`);
}
if(current!==plan.durationSeconds)throw Error('Duration mismatch');
const audioList=path.join(cache,'source-audio.ffconcat');fs.writeFileSync(audioList,'ffconcat version 1.0\n'+audioParts.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n')+'\n');
const reviewAudio=path.join(motion,`assets/review-source-only-v${plan.version}.wav`);
if(!fs.existsSync(reviewAudio))run('ffmpeg',['-v','error','-n','-f','concat','-safe','0','-i',audioList,'-c:a','pcm_s16le',reviewAudio]);
if(Math.abs(+probe(reviewAudio).format.duration-current)>.001)throw Error('Audio duration mismatch');
fs.writeFileSync(path.join(base,'planning/cuts.generated.json'),JSON.stringify({status:'internal-review-only',duration:current,sourceSeconds:evidence.reduce((n,c)=>n+c.out-c.in,0),narration:false,bgm:false,originalAudioRightsStatus:'unverified',cuts:evidence},null,2)+'\n');
fs.writeFileSync(path.join(motion,'timing.ts'),`// Provisional picture edit. Replace together with audio and KO/EN SRT after TTS approval.\nexport const NARRATION_FPS = 60;\nexport const TOTAL_DURATION = ${current};\nexport const TOTAL_FRAMES = ${current*60};\nexport const SCENE_STARTS = ${JSON.stringify(starts)} as const;\nexport const SCENE_DURATIONS = ${JSON.stringify(durations)} as const;\nexport const SCENE_TITLES = ${JSON.stringify(plan.scenes.map(s=>s.title))} as const;\n`);
console.log(`Ready: ${current}s picture edit; source-only review sound, no TTS or BGM.`);
const csv=v=>'"'+String(v).replaceAll('"','""')+'"';
const clock=n=>`${String(Math.floor(n/60)).padStart(2,'0')}:${(n%60).toFixed(3).padStart(6,'0')}`;
const rows=[['scene','start','end','segment_type','visual','source','source_audio','bgm','status']];
plan.scenes.forEach((s,i)=>{const ex=duration(s),st=starts[i];if(ex)rows.push([s.id,clock(st),clock(st+ex),'real-example',s.title,s.post,'review-only-0.15-gain','absent-pending-approval','rights-pending']);rows.push([s.id,clock(st+ex),clock(st+s.duration),'channel-explanation',s.takeaway,'original','silent-tts-pending','absent-pending-approval','picture-review-not-final']);});
fs.writeFileSync(path.join(base,'planning/edit-cues.csv'),rows.map(row=>row.map(csv).join(',')).join('\n')+'\n');
