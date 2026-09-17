// A voice/mix approval sample, NOT the full narrated video.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),m=require('../projects/let-them-play/project.json');
if(m.audio.backgroundMusic.approvalStatus!=='approved'||m.audio.backgroundMusic.title!=='Discovery')throw Error('Music not approved');
const dir=path.join(root,'shared/output/let-them-play/intro-review-20260914');fs.mkdirSync(dir,{recursive:true});
const sample=path.join(root,m.productionRequest.voiceSample),music=path.join(root,m.audio.backgroundMusic.file);
const raw=path.join(root,'shared/output/let-them-play/media-cache/longplays-hq-295.mp4'),duration=21.5;
for(const f of [sample,music,raw])if(!fs.existsSync(f))throw Error('Missing '+f);
function run(args){const r=spawnSync('ffmpeg',args,{encoding:'utf8',windowsHide:true,maxBuffer:16*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stderr}
function normalize(file,out,target){
 const log=run(['-hide_banner','-i',file,'-af','loudnorm=I='+target+':TP=-2:LRA=11:print_format=json','-f','null','-']);
 const meter=JSON.parse(log.slice(log.lastIndexOf('{'),log.lastIndexOf('}')+1));
 const filter='loudnorm=I='+target+':TP=-2:LRA=11:measured_I='+meter.input_i+':measured_TP='+meter.input_tp+':measured_LRA='+meter.input_lra+':measured_thresh='+meter.input_thresh+':offset='+meter.target_offset+':linear=true';
 run(['-y','-v','error','-i',file,'-af',filter,'-ar','48000','-ac','2',out]);return meter;
}
const game=path.join(dir,'game.wav'),voice=path.join(dir,'voice.wav'),bgm=path.join(dir,'bgm.wav'),video=path.join(dir,'game.mp4');
run(['-y','-v','error','-t','8','-i',raw,'-ss','20','-t','13.5','-i',raw,'-filter_complex','[0:v]setpts=PTS-STARTPTS,fps=60[v0];[1:v]setpts=PTS-STARTPTS,fps=60[v1];[0:a]asetpts=PTS-STARTPTS,aresample=48000[a0];[1:a]asetpts=PTS-STARTPTS,aresample=48000[a1];[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]','-map','[v]','-map','[a]','-t',String(duration),'-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','192k',video]);
const meters={voice:normalize(sample,voice,m.audio.narrationTargetLufs),game:normalize(video,game,m.audio.gameAudioTargetLufs)};
const bgmExcerpt=path.join(dir,'bgm-excerpt.wav');
run(['-y','-v','error','-i',music,'-t',String(duration),'-ar','48000','-ac','2',bgmExcerpt]);
meters.bgm=normalize(bgmExcerpt,bgm,m.audio.bgmTargetLufs);
const mix=path.join(dir,'mix.wav'),background=path.join(dir,'background.wav');
const duck='sidechaincompress=threshold='+m.audio.duckingThreshold+':ratio='+m.audio.duckingRatio+':attack=15:release=280:makeup=1';
run(['-y','-v','error','-i',voice,'-i',game,'-i',bgm,'-filter_complex',
 '[0:a]adelay=300|300,apad,atrim=duration=21.5,asplit=3[n][ng][nb];[1:a]afade=t=in:d=0.12,afade=t=out:st=21.2:d=0.3[g];[2:a]volume=-3dB,afade=t=in:d=0.45,afade=t=out:st=21.05:d=0.45[b];[g][ng]'+duck+'[gd];[b][nb]'+duck+'[bd];[gd][bd]amix=inputs=2:normalize=0,asplit=2[bg][bgout];[n][bg]amix=inputs=2:normalize=0,alimiter=limit=0.80:level=false:latency=true[out]',
 '-map','[out]','-ar','48000','-ac','2',mix,'-map','[bgout]','-ar','48000','-ac','2',background]);
const output=path.join(root,'shared/output/motion-canvas/let-them-play-INTRO-VOICE-GAME-DISCOVERY-REVIEW-20260914.mp4');
const visual="scale=1696:954,pad=1920:1080:112:63:white,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='도입부 음성·믹스 검토본 · 전체 본편 아님':x=112:y=20:fontsize=28:fontcolor=0x202020,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Gameplay Spazbo4 / World of Longplays / longplays.org   |   Music Discovery - Scott Buckley (CC BY 4.0)':x=112:y=1040:fontsize=22:fontcolor=0x737373";
run(['-y','-v','error','-i',video,'-i',mix,'-map','0:v','-map','1:a','-vf',visual,'-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','192k','-t',String(duration),'-movflags','+faststart',output]);
run(['-v','error','-i',output,'-f','null','-']);
const measure=run(['-hide_banner','-i',output,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']);
const final=JSON.parse(measure.slice(measure.lastIndexOf('{'),measure.lastIndexOf('}')+1));
if(Number(final.input_tp)>-1.5)throw Error('Final true peak too high');
fs.writeFileSync(path.join(dir,'report.json'),JSON.stringify({output,duration,meters,final,voiceApproval:'pending',music:'Discovery',audioLayers:['narration','gameplay-source','continuous-bgm'],publishReady:false,scope:'intro approval sample only'},null,2));
console.log(JSON.stringify({output,duration,truePeak:final.input_tp,voiceApproval:'pending'},null,2));
