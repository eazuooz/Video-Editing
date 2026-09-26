// Approval preview only: new source gameplay + continuous narration + approved Discovery.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),project=path.join(root,'projects/small-window-game-design');
const manifest=JSON.parse(fs.readFileSync(path.join(project,'project.json'),'utf8'));
const asset=path.join(root,'motion-canvas/src/projects/small-window-game-design/voice-preview/assets');
const out=path.join(project,'preview/narrated-v1');fs.mkdirSync(asset,{recursive:true});fs.mkdirSync(out,{recursive:true});
const narration=path.join(root,'shared/audio-samples/small-window-game-design-qwen3-1.7b-approval-sample.wav');
const source=path.join(project,'sources/media/forza-ZnCxVxfv3MM-30-75-avc.mp4');
const music=path.join(root,manifest.audio.backgroundMusic.file);
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:16e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
function probe(file){return JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',file]));}
if(manifest.audio.backgroundMusic.approvalStatus!=='approved')throw Error('Music approval required');
const frames=Math.ceil((+probe(narration).format.duration+.5)*60),seconds=frames/60;
const gameplayFrames=Math.round(frames*manifest.editing.targetGameplayShare),gameplaySeconds=gameplayFrames/60;
if(+probe(source).format.duration<gameplaySeconds)throw Error('Insufficient unique footage');
fs.copyFileSync(source,path.join(asset,'forza.mp4'));
const timing={frames,seconds,gameplayFrames,gameplaySeconds,gameplayShare:gameplayFrames/frames};
fs.writeFileSync(path.join(asset,'../timing.json'),JSON.stringify(timing,null,2));
run('ffmpeg',['-v','error','-n','-i',narration,'-i',source,'-i',music,'-filter_complex',
`[0:a]loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration=${seconds},asplit=3[n][d1][d2];`+
`[1:a]atrim=duration=${gameplaySeconds},asetpts=PTS-STARTPTS,loudnorm=I=-23:TP=-3:LRA=11,aresample=48000,afade=t=in:d=0.12,afade=t=out:st=${gameplaySeconds-.3}:d=0.3,apad,atrim=duration=${seconds}[g];`+
`[2:a]atrim=duration=${seconds},asetpts=PTS-STARTPTS,loudnorm=I=-28:TP=-3:LRA=11,aresample=48000,volume='if(lt(t,${gameplaySeconds-.45}),0.70795,if(lt(t,${gameplaySeconds}),0.70795+(t-${gameplaySeconds-.45})/.45*.29205,1))':eval=frame,afade=t=in:d=0.45,afade=t=out:st=${seconds-.45}:d=0.45[b];`+
`[g][d1]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[gd];[b][d2]sidechaincompress=threshold=0.08:ratio=2.2:attack=15:release=280[bd];`+
`[gd][bd]amix=inputs=2:normalize=0,asplit=2[bg][bgout];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true[mix]`,
'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',path.join(asset,'review-mix.wav'),
'-map','[bgout]','-ar','48000','-ac','2','-c:a','pcm_s16le',path.join(out,'background-only.wav')]);
fs.writeFileSync(path.join(out,'timing.json'),JSON.stringify({...timing,narrationSeconds:+probe(narration).format.duration,sourceUrl:'https://www.youtube.com/watch?v=ZnCxVxfv3MM',sourceIn:30,sourceOut:30+gameplaySeconds,loopedFootage:false,publishReady:false,voiceApproval:'pending',sourceAudioRights:'publication review pending'},null,2));
console.log(timing);
