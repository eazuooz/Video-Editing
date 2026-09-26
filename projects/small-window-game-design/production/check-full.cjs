const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),project=path.join(root,'projects/small-window-game-design'),work=path.join(__dirname,'full-v2'),m=JSON.parse(fs.readFileSync(path.join(project,'project.json'),'utf8')),plan=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8'));
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:24e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r;}
const probe=f=>JSON.parse(run('ffprobe',['-v','error','-show_format','-show_streams','-of','json',f]).stdout);
const ff=args=>run('ffmpeg',['-v','error','-y',...args]);
const videos={};
for(const key of ['videoClean','videoBurnedCaptions']){
  const file=path.join(root,m.paths[key]),info=probe(file),v=info.streams.find(s=>s.codec_type==='video'),a=info.streams.find(s=>s.codec_type==='audio');
  if(v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1'||+v.nb_frames!==plan.totalFrames||!a)throw Error('Output format/frame mismatch '+key);
  ff(['-i',file,'-f','null','-']);videos[key]={seconds:+info.format.duration,frames:+v.nb_frames,width:v.width,height:v.height,fps:v.r_frame_rate,audio:a.codec_name};
}
const audioHash=file=>run('ffmpeg',['-v','error','-i',file,'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-']).stdout.trim();
const cleanHash=audioHash(path.join(root,m.paths.videoClean));
if(cleanHash!==audioHash(path.join(root,m.paths.videoBurnedCaptions))||cleanHash!==audioHash(path.join(root,m.paths.audioMix)))throw Error('AAC streams differ');
function loudness(file){const result=run('ffmpeg',['-hide_banner','-i',file,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr;const start=result.lastIndexOf('{');return JSON.parse(result.slice(start,result.indexOf('}',start)+1));}
const fullLoudness=loudness(path.join(root,m.paths.videoClean)),backgroundLoudness=loudness(path.join(work,'background-only.wav'));
if(+fullLoudness.input_tp> -1.5)throw Error('True peak too high');
const volume=gain=>{const result=run('ffmpeg',['-hide_banner','-i',path.join(work,'game-01.wav'),'-t','10','-af',`volume=${gain},volumedetect`,'-f','null','-']).stderr;return +/mean_volume: ([-\d.]+) dB/.exec(result)[1];};
const before=volume(1),after=volume(m.audio.gameAudioGain);if(Math.abs(after-before+6.0206)>.15)throw Error('Source gain audit failed');
const points=[];
for(const s of plan.scenes){for(const [kind,time] of [['game',s.start+6],['diagram',s.start+s.gameSeconds+s.diagramSeconds*.5]]){
  const f=path.join(work,`${kind}-${s.id}.jpg`);ff(['-ss',String(time),'-i',path.join(root,m.paths.videoBurnedCaptions),'-frames:v','1',f]);points.push({scene:s.id,kind,time,file:path.relative(root,f).replaceAll('\\','/')});
}}
for(const kind of ['game','diagram']){
  const inputs=plan.scenes.flatMap(s=>['-i',path.join(work,`${kind}-${s.id}.jpg`)]),filters=plan.scenes.map((s,i)=>`[${i}:v]scale=640:360[v${i}]`).join(';')+';[v0][v1][v2][v3][v4][v5]xstack=inputs=6:layout=0_0|640_0|0_360|640_360|0_720|640_720[out]';
  ff([...inputs,'-filter_complex',filters,'-map','[out]','-frames:v','1',path.join(work,`${kind}-contact.jpg`)]);
}
const report={videos,aacPacketHash:cleanHash,fullLoudness,backgroundLoudness,sourceGainAudit:{gain:m.audio.gameAudioGain,expectedDb:20*Math.log10(m.audio.gameAudioGain),testBeforeDb:before,testAfterDb:after,measuredDeltaDb:after-before,postGainNormalization:false},gameplayShare:plan.gameplayShare,points,humanListeningApproved:false,membershipOutroApplied:false};
fs.writeFileSync(path.join(work,'qa.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
