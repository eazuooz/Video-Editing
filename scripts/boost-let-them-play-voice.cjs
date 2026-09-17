// Audio-only revision from unmixed, normalized stems. Idempotent: never boost a mixed master.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),m=require('../projects/let-them-play/project.json');
const dir=path.join(root,'shared/output/let-them-play/voice-gain-1p1'),base=path.join(root,'shared/output/let-them-play/final-audio-v4');
fs.mkdirSync(dir,{recursive:true});
const voice=path.join(base,'narration-normalized.wav'),bg=path.join(base,'background-only.wav'),seconds=m.video.durationSeconds;
const video=path.join(root,m.paths.videoClean),aac=path.join(root,m.paths.audioMix),editor=path.join(root,m.paths.editorAudioMix);
const gain=m.audio.narrationGain;if(gain!==1.1)throw Error('This revision requires manifest narrationGain=1.1');
function run(tool,args){const r=spawnSync(tool,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:24*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stdout||r.stderr;}
function hash(file){return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');}
function mediaHash(file,kind){return run('ffmpeg',['-v','error','-i',file,'-map',`0:${kind}:0`,'-c','copy','-f','hash','-hash','sha256','-']).trim();}
function meter(file){const log=run('ffmpeg',['-hide_banner','-i',file,'-vn','-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);return JSON.parse(log.slice(log.lastIndexOf('{'),log.lastIndexOf('}')+1));}
const fingerprints={voice:hash(voice),background:hash(bg),ko:hash(path.join(root,m.paths.captionsKo)),en:hash(path.join(root,m.paths.captionsEn))};
// Recoverable baseline copies, made only on the first run.
for(const [src,name] of [[video,'before-voice-gain.mp4'],[aac,'before-voice-gain.m4a'],[editor,'before-voice-gain.wav']]){
 const dest=path.join(dir,name);if(!fs.existsSync(dest))fs.copyFileSync(src,dest);
}
const wave=path.join(dir,'final-mix.wav'),encoded=path.join(dir,'final-mix.m4a'),picture=path.join(dir,'validated-main.mp4');
console.log('Applying voice x1.1; background stem and timing unchanged');
run('ffmpeg',['-y','-v','error','-i',voice,'-i',bg,'-filter_complex',`[0:a]volume=${gain}[n];[n][1:a]amix=inputs=2:normalize=0,alimiter=limit=${m.audio.finalLimiterCeiling}:level=false:latency=true,atrim=duration=${seconds}[mix]`,'-map','[mix]','-ar','48000','-ac','2',wave]);
run('ffmpeg',['-y','-v','error','-i',wave,'-c:a','aac','-b:a','192k','-ar','48000','-ac','2',encoded]);
const measured=meter(encoded);if(Number(measured.input_tp)>m.audio.truePeakDbtp)throw Error('True peak fails: '+JSON.stringify(measured));
console.log('New AAC: '+measured.input_i+' LUFS / '+measured.input_tp+' dBTP');
// Preserve the CURRENT picture, including later approved design revisions.
// The old backup is recovery history, never an input that reverts newer visuals.
run('ffmpeg',['-y','-v','error','-i',video,'-i',encoded,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',picture]);
const probe=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',picture]));
const v=probe.streams.find(s=>s.codec_type==='video');
if(Number(v.nb_frames)!==28908||Number(v.duration)!==seconds)throw Error('Picture timing changed');
const oldPictureHash=mediaHash(video,'v'),newPictureHash=mediaHash(picture,'v');
if(oldPictureHash!==newPictureHash)throw Error('Video packets changed');
if(mediaHash(encoded,'a')!==mediaHash(picture,'a'))throw Error('AAC packets mismatch');
run('ffmpeg',['-v','error','-i',picture,'-f','null','-']);
if(hash(bg)!==fingerprints.background||hash(voice)!==fingerprints.voice||hash(path.join(root,m.paths.captionsKo))!==fingerprints.ko||hash(path.join(root,m.paths.captionsEn))!==fingerprints.en)throw Error('Source or subtitle changed');
// Publish local outputs only after validation; prior versions remain in this directory.
fs.copyFileSync(encoded,aac);
run('ffmpeg',['-y','-v','error','-i',encoded,'-t',String(seconds),'-ar','48000','-ac','2','-c:a','pcm_s16le',editor]);
fs.copyFileSync(picture,video);
// Start on the breath just before scene03's explanation (word onset 140.60s).
// A 0.25s preroll avoids clipping the first syllable at the visual-third boundary.
const sampleDir=path.join(root,'motion-canvas/src/projects/let-them-play/editorial-sample/assets');fs.mkdirSync(sampleDir,{recursive:true});
run('ffmpeg',['-y','-v','error','-ss','140.4','-i',encoded,'-t','39.7','-af','afade=t=in:d=0.06,afade=t=out:st=39.1:d=0.6','-ar','48000','-ac','2','-c:a','pcm_s16le',path.join(sampleDir,'sample-mix.wav')]);
const report={gain,decibels:20*Math.log10(gain),speed:1,seconds,measured,video,editor,aac,sourceFingerprints:fingerprints,videoPacketHash:newPictureHash,videoPacketsUnchanged:true,subtitlesUnchanged:true,backgroundStemUnchanged:true,fullDecodePassed:true,sample:{start:140.4,duration:39.7},humanListening:'new gain pending user review'};
fs.writeFileSync(path.join(dir,'report.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
