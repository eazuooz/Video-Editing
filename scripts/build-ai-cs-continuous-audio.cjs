// v6+ continuous narration, quiet source audio, optional approved continuous BGM.
// Missing music is an explicit review-only mode, never a completed final mix.
// node scripts/build-ai-cs-continuous-audio.cjs [--allow-missing-bgm]
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const repo=p=>{const v=path.resolve(root,p);if(!v.startsWith(root+path.sep))throw Error('Path outside repository');return v;};
const read=p=>JSON.parse(fs.readFileSync(repo(p),'utf8'));
const rel=p=>path.relative(root,p).replaceAll('\\','/');
const manifestIndex=process.argv.indexOf('--manifest');
const manifestPath=manifestIndex<0?'projects/ai-era-cs-fundamentals/project.json':process.argv[manifestIndex+1];
if(!manifestPath)throw Error('Missing --manifest path');
const m=read(manifestPath),cfg=m.audio;
const project=rel(path.dirname(repo(manifestPath)));
const assets=rel(path.join(path.dirname(repo(m.paths.motionCanvasProject)),'assets'));
const timing=read(`${m.tts.outputDir}/${m.tts.filenameStem}.timing.json`);
const script=read(m.paths.script),media=read(`${project}/sources/selected-footage.json`);
const placement='continuous-across-example-and-explanation';
if(m.scriptRevision<6||m.editing.narrationPlacement!==placement||timing.narration_placement!==placement)throw Error('Requires measured v6+ continuous narration');
const example=m.editing.exampleSeconds;
if(timing.example_seconds!==example||media.clipDuration!==example)throw Error('Example duration mismatch');
const music=cfg.backgroundMusic;
const hasMusic=Boolean(music.file);
if(!hasMusic&&!process.argv.includes('--allow-missing-bgm'))throw Error('Approved Blue Dream file missing; use explicit review-only flag or supply the licensed file');
const rightsVerified=Boolean(music.license&&music.licenseStatus?.startsWith('verified'));
const artistReview=process.argv.includes('--artist-review')&&music.acquisitionSource==='creator-public-upload'&&music.evidenceFile&&fs.existsSync(repo(music.evidenceFile));
if(hasMusic&&(music.approvalStatus!=='approved'||(!rightsVerified&&!artistReview)))throw Error('BGM approval / license verification missing; documented creator-source review requires explicit --artist-review and cannot be published');
const first=new Map();for(const e of timing.entries)if(!first.has(e.scene_id))first.set(e.scene_id,e.start);
const starts=script.scenes.map(s=>Math.round(first.get(s.id)*30)/30);
const duration=Math.round(timing.duration_seconds*30)/30;
if(starts[0]!==0||starts.some((s,i)=>!Number.isFinite(s)||(i&&s<=starts[i-1]))||Math.abs(duration-m.video.durationSeconds)>.002)throw Error('Run timing sync first');
if(starts.some((s,i)=>(starts[i+1]??duration)-s<=example))throw Error('Narration too short for example + explanation');
const cache=fs.mkdtempSync(repo('shared/output/ai-cs-media-cache/continuous-v6-'));
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:20*1024*1024});if(r.status!==0)throw Error(`${cmd}: ${r.stderr}`);return r;}
const probe=p=>JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',p]).stdout);
function loudness(file,start,seconds){const seek=start===undefined?[]:['-ss',String(start),'-t',String(seconds)];const r=run('ffmpeg',['-hide_banner',...seek,'-i',file,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-']);const found=r.stderr.match(/\{\s*"input_i"[\s\S]*?\}/);if(!found)throw Error('Loudness missing');return JSON.parse(found[0]);}
const wavOut=(args,filter,label,file)=>run('ffmpeg',['-hide_banner','-v','warning','-n',...args,'-filter_complex',filter,'-map',label,'-ar','48000','-ac','2','-c:a','pcm_s16le',file]);
const voiceFile=path.join(cache,'narration-normalized.wav');
if(Math.abs(+probe(m.paths.narration).format.duration-timing.duration_seconds)>.01)throw Error('Narration duration mismatch');
const measured=loudness(m.paths.narration);
if(!Number.isFinite(+measured.input_i))throw Error('Narration is silent');
const norm=`loudnorm=I=${cfg.narrationTargetLufs}:TP=${cfg.truePeakDbtp}:LRA=9:measured_I=${measured.input_i}:measured_TP=${measured.input_tp}:measured_LRA=${measured.input_lra}:measured_thresh=${measured.input_thresh}:offset=${measured.target_offset}:linear=true`;
wavOut(['-i',m.paths.narration],`[0:a]${norm},aresample=48000,aformat=channel_layouts=stereo,volume=${cfg.narrationPostNormalizationDb??0}dB,apad,atrim=0:${duration}[out]`,'[out]',voiceFile);
console.log('Normalized full narration');
const sourceFile=path.join(cache,'source-only-before-ducking.wav');
const inputs=[],filters=[],labels=[],sceneEvidence=[];
for(const [i,s]of script.scenes.entries()){
 const clip=media.clips.find(c=>c.scene===s.id);if(!clip)throw Error(`Missing footage ${s.id}`);
 const file=`${assets}/broll/scene${s.id}.mp4`,info=probe(file);
 if(!info.streams.some(t=>t.codec_type==='audio')||Math.abs(+info.format.duration-example)>.05)throw Error(`Invalid source ${s.id}`);
 inputs.push('-i',file);
 filters.push(`[${i}:a]atrim=0:${example},asetpts=PTS-STARTPTS,loudnorm=I=${cfg.gameAudioTargetLufs}:TP=${cfg.truePeakDbtp}:LRA=9,aresample=48000,aformat=channel_layouts=stereo,afade=t=in:d=0.12,afade=t=out:st=${example-.3}:d=0.3,adelay=${Math.round(starts[i]*48000)}S:all=1[s${i}]`);
 labels.push(`[s${i}]`);
 sceneEvidence.push({scene:s.id,start:starts[i],end:starts[i+1]??duration,exampleSeconds:example,narrationStart:first.get(s.id),source:file});
}
filters.push(`${labels.join('')}amix=inputs=${labels.length}:normalize=0:duration=longest,apad,atrim=0:${duration}[out]`);
wavOut(inputs,filters.join(';'),'[out]',sourceFile);
console.log(`Built ${script.scenes.length} low-level source slots`);
let bgmFile=null;
if(hasMusic){
 const file=repo(music.file),len=+probe(file).format.duration,fade=cfg.bgmLoopCrossfadeSeconds;
 if(!(len>2*fade&&fade>0)||cfg.bgmPlacement!=='continuous')throw Error('Invalid continuous BGM settings');
 const count=Math.max(1,Math.ceil((duration-fade)/(len-fade))),f=[];
 const names=Array.from({length:count},(_,i)=>`[b${i}]`);
 f.push(`[0:a]loudnorm=I=${cfg.bgmTargetLufs}:TP=${cfg.truePeakDbtp}:LRA=9,aresample=48000,aformat=channel_layouts=stereo,asplit=${count}${names.join('')}`);
 let current='[b0]';for(let i=1;i<count;i++){f.push(`${current}[b${i}]acrossfade=d=${fade}:c1=tri:c2=tri[j${i}]`);current=`[j${i}]`;}
 const overlap=starts.map(s=>`max(0,min(1,min((t-${s})/0.45,(${s+example}-t)/0.45)))`).join('+');
 f.push(`${current}apad,atrim=0:${duration},volume='pow(10,(${cfg.bgmDuringGameplayDb})*min(1,${overlap})/20)':eval=frame,afade=t=in:d=0.45,afade=t=out:st=${duration-.45}:d=0.45[out]`);
 bgmFile=path.join(cache,'bgm-only-before-ducking.wav');
 wavOut(['-i',file],f.join(';'),'[out]',bgmFile);
 console.log('Built continuous Blue Dream bed with crossfaded loops');
}
const bgFile=path.join(cache,'background-only.wav'),master=path.join(cache,'master.wav');
const mixInputs=['-i',voiceFile,'-i',sourceFile];if(bgmFile)mixInputs.push('-i',bgmFile);
const duck=`sidechaincompress=threshold=${cfg.duckingThreshold}:ratio=${cfg.duckingRatio}:attack=15:release=280:makeup=1`;
const f=[`[0:a]asplit=${hasMusic?3:2}[voice][key1]${hasMusic?'[key2]':''}`,`[1:a][key1]${duck}[source]`];
if(hasMusic)f.push(`[2:a][key2]${duck}[music]`,`[source][music]amix=inputs=2:normalize=0:duration=longest[background]`);
else f.push('[source]anull[background]');
f.push('[background]asplit=2[backgroundExport][backgroundMix]',`[voice][backgroundMix]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.7943:level=0:latency=1,apad,atrim=0:${duration}[mix]`);
run('ffmpeg',['-hide_banner','-v','warning','-n',...mixInputs,'-filter_complex',f.join(';'),'-map','[mix]','-ar','48000','-ac','2','-c:a','pcm_s16le',master,'-map','[backgroundExport]','-ar','48000','-ac','2','-c:a','pcm_s16le',bgFile]);
const aac=path.join(cache,'master.m4a');run('ffmpeg',['-v','error','-n','-i',master,'-c:a','aac','-b:a','192k',aac]);
const levels=loudness(aac);
if(+levels.input_tp>cfg.truePeakDbtp+.1||Math.abs(+probe(aac).format.duration-duration)>.05)throw Error('Mix peak/duration check failed');
for(const s of sceneEvidence){
 s.exampleVoiceLufs=+loudness(voiceFile,s.start+.2,example-.5).input_i;
 s.sourceLufs=+loudness(sourceFile,s.start+.2,example-.5).input_i;
 s.exampleBackgroundLufs=+loudness(bgFile,s.start+.2,example-.5).input_i;
 s.explanationVoiceLufs=+loudness(voiceFile,s.start+example+.2,Math.min(8,s.end-s.start-example-.4)).input_i;
 if(hasMusic){s.exampleBgmLufs=+loudness(bgmFile,s.start+.2,example-.5).input_i;s.explanationBgmLufs=+loudness(bgmFile,s.start+example+.2,8).input_i;}
 if(!Number.isFinite(s.exampleVoiceLufs)||s.exampleVoiceLufs< -28||!Number.isFinite(s.sourceLufs)||s.sourceLufs>s.exampleVoiceLufs-9||s.explanationVoiceLufs< -28)throw Error(`Voice/source balance failed: ${s.scene}`);
 if(hasMusic&&(!Number.isFinite(s.exampleBgmLufs)||!Number.isFinite(s.explanationBgmLufs)))throw Error(`BGM absent: ${s.scene}`);
 console.log(`Checked scene ${s.scene}: example voice ${s.exampleVoiceLufs}, source ${s.sourceLufs} LUFS`);
}
const suffix=`v${m.scriptRevision}-${hasMusic?(rightsVerified?'full':'artist-music-review'):'voice-source-review'}`;
const targetAac=`${assets}/mix-${suffix}.m4a`,targetWav=`${assets}/mix-${suffix}.wav`;
for(const [from,to]of [[aac,targetAac],[master,targetWav]]){
 const target=repo(to);if(fs.existsSync(target))fs.copyFileSync(target,path.join(cache,`previous-${path.basename(to)}`));
 fs.copyFileSync(from,target);
}
const report={createdAt:new Date().toISOString(),scriptRevision:m.scriptRevision,kind:hasMusic?(rightsVerified?'FULL MIX AWAITING LISTENING REVIEW':'PRIVATE ARTIST-MUSIC REVIEW; AUDIO LIBRARY LICENSE NOT VERIFIED'):'NARRATION + LOW SOURCE REVIEW; BGM MISSING',musicRightsVerified:hasMusic&&rightsVerified,publishReady:false,duration,narrationPlacement:placement,mix:targetAac,editorMix:targetWav,bgm:hasMusic?music:null,parameters:cfg,measurement:levels,layers:{voice:rel(voiceFile),source:rel(sourceFile),background:rel(bgFile),bgm:bgmFile?rel(bgmFile):null},scenes:sceneEvidence,subjectiveListeningApproved:false};
const reportPath=`${project}/audio/mix-v${m.scriptRevision}-report.json`;
fs.mkdirSync(path.dirname(repo(reportPath)),{recursive:true});
fs.writeFileSync(repo(reportPath),JSON.stringify(report,null,2)+'\n');
m.paths.audioMix=targetAac;m.paths.editorAudioMix=targetWav;m.paths.audioMixReport=reportPath;
m.audio.mixStatus=hasMusic?(rightsVerified?'full-mix-awaiting-listening-review':'full-mix-license-pending'):'narration-source-ready-bgm-pending';
fs.writeFileSync(repo(`${project}/project.json`),JSON.stringify(m,null,2)+'\n');
const audioModule=path.join(path.dirname(repo(m.paths.motionCanvasProject)),'editor-audio.generated.ts');
fs.writeFileSync(audioModule,`// GENERATED by scripts/build-ai-cs-continuous-audio.cjs.\n// Same full mix as the AAC master; PCM WAV supports VS Code playback.\nimport audio from './assets/${path.basename(targetWav)}';\nexport default audio;\n`);
console.log(`DONE ${targetWav}; ${duration.toFixed(3)}s; BGM ${hasMusic?'included':'MISSING (review only)'}`);
