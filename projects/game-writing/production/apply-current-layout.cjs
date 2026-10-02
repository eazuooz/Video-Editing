const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1'),read=p=>JSON.parse(fs.readFileSync(p,'utf8')),save=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n'),abs=p=>path.join(root,p),rel=p=>path.relative(root,p).replaceAll('\\','/');
const m=read(abs('projects/game-writing/project.json')),p=read(path.join(work,'plan.json')),dest=path.join(work,'current-layout');fs.mkdirSync(dest,{recursive:true});
const enc=['-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','90000'];
function run(args){const r=spawnSync('ffmpeg',['-v','error','-y','-threads','2','-filter_complex_threads','2',...args],{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||String(r.error));}
const proof={startedAt:new Date().toISOString(),captionCenter:[960,970],sourceComposition:{background:'same-shot full-screen blur; no white slide frame',sharpActionBounds:[187,5,1733,875],sourceSize:[1546,870],sourceIntervalAndNormalSpeedPreserved:true},scenes:[]};
for(const s of p.scenes.filter(s=>s.classification==='actual')){
 const c=p.cuts.filter(c=>c.scene===s.id&&['gm','overview'].includes(c.key));if(!c.length)continue;
 const input=s.originalActualVideo||s.actualVideo,file=path.join(dest,`scene${s.id}.mp4`),enable=c.map(c=>`between(t,${c.timelineStart-s.start},${c.timelineEnd-s.start})`).join('+');
 const filter=`[0:v]split=3[orig][bg][fg];[bg]boxblur=18:2[blur];[fg]scale=1546:870[small];[blur][small]overlay=187:5[framed];[orig][framed]overlay=0:0:enable='${enable}'[v]`;
 run(['-i',abs(input),'-filter_complex',filter,'-map','[v]','-frames:v',String(s.frames),...enc,file]);s.originalActualVideo=input;s.actualVideo=rel(file);s.currentCaptionComposition=true;proof.scenes.push({scene:s.id,input,output:s.actualVideo,frames:s.frames,cuts:c.map(c=>c.id)});save(path.join(work,'current-layout-progress.json'),proof);console.log('Composed official source scene',s.id);
}
// Original member screenshot/title/logo stay intact; coaching text occupies
// unused upper-left space, independently of clickable platform elements.
const outro=path.join(dest,'outro.mp4'),text=path.join(dest,'coaching.txt');fs.writeFileSync(text,'프로그래밍 과외\nhttps://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328');
const filter=`drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='${rel(text)}':fontsize=30:fontcolor=0x202020:x=96:y=180:line_spacing=18`;
run(['-i',path.join(work,'outro.mp4'),'-vf',filter,'-frames:v','600',...enc,outro]);
const list=[path.join(work,'intro.mp4'),...p.scenes.map(s=>s.classification==='actual'?abs(s.actualVideo):path.join(work,`explanation-${s.id}.mp4`)),outro],concat=path.join(dest,'concat.txt');fs.writeFileSync(concat,list.map(f=>`file '${f.replaceAll('\\','/')}'`).join('\n'));
const pre=path.join(dest,'before-current-layout-clean.mp4');if(!fs.existsSync(pre))fs.copyFileSync(abs(m.paths.videoClean),pre);
run(['-f','concat','-safe','0','-i',concat,'-i',abs(m.paths.audioMix),'-map','0:v','-map','1:a','-c','copy','-t',String(p.seconds),'-movflags','+faststart',abs(m.paths.videoClean)]);
save(path.join(work,'plan.json'),p);save(abs('motion-canvas/src/projects/game-writing/production-plan.json'),p);
proof.finishedAt=new Date().toISOString();proof.outro={originalImageTitleLogoPreserved:true,seconds:10,coachingText:text,clickablePlatformLink:'pending-private-upload'};proof.clean=m.paths.videoClean;save(path.join(work,'current-layout-progress.json'),proof);
const r=spawnSync(process.execPath,[path.join(__dirname,'caption-video.cjs')],{stdio:'inherit',windowsHide:true});if(r.status!==0)throw Error('Caption render failed');console.log('Current bottom-center layout and coaching ending rendered; full QA required.');
