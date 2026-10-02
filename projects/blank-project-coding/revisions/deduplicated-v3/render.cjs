// Rebuild only the three adjusted cuts; retain every other reviewed cut verbatim.
const fs=require('fs'),path=require('path'),{spawnSync}=require('child_process');
const W=__dirname,R=path.resolve(W,'../../../..'),B=path.join(W,'../original-restored-v2');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8')),p=read(path.join(W,'plan.json')),m=read(path.join(W,'final.manifest.json'));
const write=(f,v)=>fs.writeFileSync(path.join(W,f),JSON.stringify(v,null,2)+'\n');
function run(cmd,args,log){const o=spawnSync(cmd,args,{cwd:R,encoding:'utf8',windowsHide:true,maxBuffer:12e6});if(log)fs.writeFileSync(path.join(W,log),o.stdout+'\n'+o.stderr);if(o.status!==0)throw Error(o.stderr||String(o.error));return o.stdout;}
const ff=a=>run('ffmpeg',['-v','error','-y','-threads','2',...a]);
const enc=['-an','-c:v','libx264','-threads','3','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000'];
fs.mkdirSync(path.join(W,'cuts'),{recursive:true});
fs.writeFileSync(path.join(W,'header.txt'),'AI 시대의 개발자 · 17장','utf8');
for(const c of p.cuts.filter(c=>c.baselineSource)){
 const args=['-ss',String(c.sourceTrimStartFrame/60),'-i',path.join(R,c.baselineSource)];
 if(c.headerChapterOverride){
  const header=path.relative(R,path.join(W,'header.txt')).replaceAll('\\','/');
  const filter=`drawbox=x=90:y=38:w=1450:h=49:color=white:t=fill,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='${header}':x=110:y=48:fontsize=23:fontcolor=0x737373`;
  const file=path.join(W,`filter-${c.id}.txt`);fs.writeFileSync(file,filter);args.push('-filter_script:v',file);
 }
 ff([...args,'-frames:v',String(c.frames),...enc,path.join(R,c.source)]);
 console.log('Adjusted cut',c.id,c.frames);
}
run(process.execPath,[path.join(W,'mix-audio.cjs')],'mix-audio.log');console.log('Continuous music remixed from original scene WAVs.');
const files=[path.join(B,'cuts/intro.mp4'),...p.cuts.map(c=>path.join(R,c.source)),path.join(B,'cuts/outro.mp4')];
for(let i=0;i<files.length;i++){
 const v=JSON.parse(run('ffprobe',['-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,width,height,r_frame_rate','-of','json',files[i]])).streams[0];
 const expected=i===0?120:i===files.length-1?600:p.cuts[i-1].frames;
 if(+v.nb_frames!==expected||v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1')throw Error('Cut metadata mismatch '+files[i]);
}
const concat=path.join(W,'final-concat.txt');fs.writeFileSync(concat,files.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
ff(['-f','concat','-safe','0','-i',concat,'-i',path.join(R,m.paths.audioMix),'-map','0:v:0','-map','1:a:0','-c','copy','-t',String(p.seconds),'-movflags','+faststart',path.join(R,m.paths.videoClean)]);
write('assembly.json',{frames:p.totalFrames,seconds:p.seconds,allCutFramesVerified:true,sourceSequence:files.map(f=>path.relative(R,f).replaceAll('\\','/')),originalIntroAndMemberIdentitiesRetained:true});
console.log('Clean master assembled.');
run(process.execPath,[path.join(W,'caption-video.cjs')],'caption-video.log');console.log('Fixed bottom-center Korean captions rendered.');
run(process.execPath,[path.join(W,'build-editor.cjs')],'build-editor.log');
write('render-result.json',{stage:'rendered',seconds:p.seconds,retainedScenes:49,completedAt:new Date().toISOString(),qa:'pending'});
