// Repeatable, measured three-layer mix. Never use the already-mixed review MP4 as input.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),m=require('../projects/let-them-play/project.json'),t=require('../motion-canvas/src/projects/let-them-play/timeline.generated.json');
if(!t.voiceAligned||!m.approvals.voice.startsWith('approved')||m.audio.backgroundMusic.approvalStatus!=='approved')throw Error('Measured voice and music approvals required');
const dir=path.join(root,'shared/output/let-them-play/final-audio-v4');fs.mkdirSync(dir,{recursive:true});
const duration=t.totalFrames/t.fps,A=m.audio;
function run(args){const r=spawnSync('ffmpeg',args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stderr;}
function meter(file,target=-16){const r=run(['-hide_banner','-i',file,'-vn','-af',`aformat=channel_layouts=stereo,loudnorm=I=${target}:TP=-2:LRA=11:print_format=json`,'-f','null','-']);return JSON.parse(r.slice(r.lastIndexOf('{'),r.lastIndexOf('}')+1));}
function normalize(file,out,target){
 const x=meter(file,target);if(!Number.isFinite(Number(x.input_i)))throw Error('Silent input '+file);
 // The second pass must use this layer's first-pass target_offset, not zero.
 run(['-y','-v','error','-i',file,'-vn','-af',`aformat=channel_layouts=stereo,loudnorm=I=${target}:TP=-2:LRA=11:measured_I=${x.input_i}:measured_TP=${x.input_tp}:measured_LRA=${x.input_lra}:measured_thresh=${x.input_thresh}:offset=${x.target_offset}:linear=true`,'-ar','48000','-ac','2','-c:a','pcm_s16le',out]);
 let measured=meter(out,target);const corrections=[];
 for(let pass=0;pass<2&&Math.abs(Number(measured.input_i)-target)>.2;pass++){
  const gain=target-Number(measured.input_i),corrected=out.replace(/\.wav$/,'.level-pass.wav');
  run(['-y','-v','error','-i',out,'-af',`volume=${gain}dB,alimiter=limit=0.794:level=false:latency=true`,'-ar','48000','-ac','2',corrected]);
  fs.renameSync(corrected,out);corrections.push(gain);measured=meter(out,target);
 }
 if(Math.abs(Number(measured.input_i)-target)>.75)throw Error(`Layer misses loudness target: ${out} ${measured.input_i} vs ${target}`);
 console.log(`Normalized ${path.basename(out)}: ${measured.input_i} LUFS`);
 return {input:x,normalized:measured,correctionGainsDb:corrections};
}
const voice=path.join(dir,'narration-normalized.wav'),music=path.join(dir,'music-normalized.wav'),game=path.join(dir,'game-only.wav');
const meters={voice:normalize(path.join(root,m.paths.narration),voice,A.narrationTargetLufs),music:normalize(path.join(root,A.backgroundMusic.file),music,A.bgmTargetLufs),game:[]};
const inputs=[],filters=[],labels=[];
for(const [i,s] of t.scenes.entries()){
 const p=path.join(dir,`game-${s.id}.wav`),source=path.join(root,`motion-canvas/src/projects/let-them-play/assets/broll-archive64/scene${s.id}.mp4`);
 meters.game.push({scene:s.id,...normalize(source,p,A.gameAudioTargetLufs)});inputs.push('-i',p);
 const len=s.segmentFrames/t.fps,delay=Math.round(s.startFrame/t.fps*48000);
 filters.push(`[${i}:a]afade=t=in:d=0.12,afade=t=out:st=${len-.3}:d=0.3,adelay=${delay}S:all=1[g${i}]`);labels.push(`[g${i}]`);
}
filters.push(labels.join('')+`amix=inputs=${labels.length}:normalize=0,apad,atrim=duration=${duration}[game]`);
run(['-y','-v','error',...inputs,'-filter_complex',filters.join(';'),'-map','[game]','-ar','48000','-ac','2',game]);
const info=spawnSync('ffprobe',['-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',music],{encoding:'utf8',windowsHide:true});if(info.status!==0)throw Error(info.stderr);
const musicDuration=Number(info.stdout),cross=A.bgmLoopCrossfadeSeconds,n=Math.max(1,Math.ceil((duration-cross)/(musicDuration-cross)));
const musInputs=Array.from({length:n},()=>['-i',music]).flat(),musFilters=[];
let prev='0:a';for(let i=1;i<n;i++){musFilters.push(`[${prev}][${i}:a]acrossfade=d=${cross}:c1=tri:c2=tri[b${i}]`);prev=`b${i}`;}
const envelopes=t.scenes.map(s=>{const start=s.startFrame/t.fps,end=(s.startFrame+s.segmentFrames)/t.fps;return `max(0,min(1,min((t-${start})/0.45,(${end}-t)/0.45)))`;});
const envelope=envelopes.reduce((a,b)=>`max(${a},${b})`),bgm=path.join(dir,'bgm-only-before-narration-ducking.wav');
musFilters.push(`[${prev}]atrim=duration=${duration},volume='pow(10,${A.bgmDuringGameplayDb}/20*(${envelope}))':eval=frame,afade=t=in:d=0.45,afade=t=out:st=${duration-.45}:d=0.45[bgm]`);
run(['-y','-v','error',...musInputs,'-filter_complex',musFilters.join(';'),'-map','[bgm]','-ar','48000','-ac','2',bgm]);
const mix=path.join(dir,'final-mix.wav'),background=path.join(dir,'background-only.wav');
const duck=`sidechaincompress=threshold=${A.duckingThreshold}:ratio=${A.duckingRatio}:attack=15:release=280:makeup=1`;
// Keep the approved ducking reference unchanged; boost only the audible voice.
run(['-y','-v','error','-i',voice,'-i',game,'-i',bgm,'-filter_complex',`[0:a]asplit=3[n0][ng][nb];[n0]volume=${A.narrationGain??1}[n];[1:a][ng]${duck}[g];[2:a][nb]${duck}[b];[g][b]amix=inputs=2:normalize=0,asplit=2[bg][bgout];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=${A.finalLimiterCeiling}:level=false:latency=true,atrim=duration=${duration}[out]`,'-map','[out]','-ar','48000','-ac','2',mix,'-map','[bgout]','-ar','48000','-ac','2',background]);
const aac=path.join(root,m.paths.audioMix),editor=path.join(root,'motion-canvas/src/projects/let-them-play/assets/final-mix.wav');
run(['-y','-v','error','-i',mix,'-c:a','aac','-b:a','192k','-ar','48000','-ac','2',aac]);
// Decode the same AAC for editor environments without AAC support.
run(['-y','-v','error','-i',aac,'-t',String(duration),'-c:a','pcm_s16le',editor]);
const final=meter(aac);if(Number(final.input_tp)>A.truePeakDbtp)throw Error('AAC true peak exceeds target');
const samples=[];
for(const s of t.scenes)for(const kind of ['gameplay','explanation']){
 const sec=(s.startFrame+s.segmentFrames*(kind==='gameplay'?.5:1.5))/t.fps;
 const levels={};for(const [layer,file] of Object.entries({voice,game,bgm,background})){
  const log=run(['-hide_banner','-ss',String(sec),'-t','2','-i',file,'-af','volumedetect','-f','null','-']);const match=log.match(/mean_volume:\s*([-\d.]+) dB/);levels[layer]=match?Number(match[1]):null;
 }
 if(levels.bgm===null||levels.bgm< -65||levels.voice===null||levels.voice< -60||(kind==='gameplay'&&(levels.game===null||levels.game< -65)))throw Error('Missing layer '+s.id+' '+JSON.stringify(levels));
 samples.push({scene:s.id,kind,seconds:sec,meanDbfs:levels});
}
const report={duration,meters,final,samples,narrationGain:A.narrationGain??1,music:A.backgroundMusic.title,continuousBgm:true,loopCrossfadeSeconds:cross,editor,aac,background,source:'Archive64 with description-only credits permitted',humanListeningApproval:'pending'};
fs.writeFileSync(path.join(dir,'mix-report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify({duration,final,aac,editor}));
