// Draft only: source audio at reviewed slots + approved-script sample, no BGM.
// Never masquerades as the final narration/fullmix.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const media=read('projects/ai-era-cs-fundamentals/sources/selected-footage.json');
const manifest=read('projects/ai-era-cs-fundamentals/project.json');
if(media.clipDuration!==manifest.editing.exampleSeconds)throw Error('Example timing mismatch');
const storyboard=fs.readFileSync(path.join(root,'motion-canvas/src/projects/ai-era-cs-fundamentals/storyboard.ts'),'utf8');
const durations=JSON.parse(storyboard.match(/DRAFT_DURATIONS[^=]*=\s*(\[[^;]+\])/)[1]);
const starts=durations.map((_,i)=>durations.slice(0,i).reduce((a,b)=>a+b,0));
const duration=durations.reduce((a,b)=>a+b,0);
const asset='motion-canvas/src/projects/ai-era-cs-fundamentals/assets';
const sample='shared/audio-samples/ai-era-cs-fundamentals-v4-approval-sample-take3.wav';
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:10*1024*1024});if(r.status)throw Error(r.stderr);return r.stdout;}
let args=['-y','-v','warning','-f','lavfi','-i',`anullsrc=r=48000:cl=stereo:d=${duration}`,'-i',sample];
let filters=['[0:a]anull[base]',`[1:a]loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000,adelay=${Math.round(media.clipDuration*1000)}:all=1[sample]`];
let tracks=['[base]','[sample]'];let input=2;
let report=[];
for(const c of media.clips){
  const clip=`${asset}/broll/scene${c.scene}.mp4`;
  const info=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',clip]));
  const hasAudio=info.streams.some(s=>s.codec_type==='audio');
  report.push({scene:c.scene,start:starts[Number(c.scene)-1],clipDuration:media.clipDuration,hasSourceAudio:hasAudio});
  if(!hasAudio)continue;
  args.push('-i',clip);
  const tag=`c${c.scene}`;
  filters.push(`[${input++}:a]atrim=0:${media.clipDuration},asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-1.5:LRA=9,aresample=48000,afade=t=in:d=0.08,afade=t=out:st=${media.clipDuration-.25}:d=0.25,adelay=${Math.round(starts[Number(c.scene)-1]*1000)}:all=1[${tag}]`);
  tracks.push(`[${tag}]`);
}
filters.push(`${tracks.join('')}amix=inputs=${tracks.length}:normalize=0:duration=longest,alimiter=limit=0.8414:level=0:latency=1,atrim=0:${duration}[mix]`);
const part='shared/output/ai-cs-media-cache/preview-source-mix-render.m4a';
run('ffmpeg',[...args,'-filter_complex',filters.join(';'),'-map','[mix]','-c:a','aac','-b:a','192k','-ar','48000',part]);
const checked=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',part]));
if(Math.abs(Number(checked.format.duration)-duration)>.05 || !checked.streams.some(s=>s.codec_type==='audio')) throw Error('Invalid preview mix');
fs.copyFileSync(path.join(root,part),path.join(root,`${asset}/preview-source-mix.m4a`));
fs.writeFileSync(path.join(root,'projects/ai-era-cs-fundamentals/audio/preview-report.json'),JSON.stringify({kind:'DRAFT NOT FINAL',scriptRevision:manifest.scriptRevision,duration,narrationSample:sample,sampleStart:media.clipDuration,bgm:null,voiceSampleApproval:'pending',scenes:report},null,2)+'\n');
console.log(`Draft mix ${duration.toFixed(3)}s; ${report.filter(x=>x.hasSourceAudio).length} source-audio clips; NO full narration, NO BGM`);
