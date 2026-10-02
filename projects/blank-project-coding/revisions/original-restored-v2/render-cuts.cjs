const fs=require('fs'),path=require('path'),{spawn}=require('child_process');
const stage=process.argv[2]||'media', onlyIds=process.argv[3]?new Set(process.argv[3].split(',')):null;
const R=path.resolve(__dirname,'../../../..'),W=__dirname,read=p=>JSON.parse(fs.readFileSync(p,'utf8')),planPath=path.join(W,stage==='preview'?'sample-cuts.json':'plan.json'),plan=read(planPath),sources=read(path.join(W,'sources.json')).candidates;
const O=path.join(W,stage==='preview'?'sample-cuts':'cuts');fs.mkdirSync(O,{recursive:true});const state={startedAt:new Date().toISOString(),cuts:[],status:'running'},save=()=>fs.writeFileSync(path.join(W,stage==='preview'?'sample-cut-render.json':'cut-render-'+stage+'.json'),JSON.stringify(state,null,2)+'\n');
function run(args,label){return new Promise((resolve,reject)=>{const log=fs.openSync(path.join(O,label+'.log'),'w'),p=spawn('ffmpeg',['-v','error','-y','-threads','2',...args],{cwd:R,windowsHide:true,stdio:['ignore',log,log]});p.on('error',reject);p.on('exit',code=>{fs.closeSync(log);code?reject(Error(label+' ffmpeg exit '+code)):resolve();});});}
const enc=['-an','-c:v','libx264','-threads','3','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-r','60','-video_track_timescale','90000','-movflags','+faststart'];
async function cut(c){const dest=path.join(O,c.id+'.mp4');let input,filter;
 if(c.sourceSegments){
  if(c.sourceSegments.reduce((n,s)=>n+s.frames,0)!==c.frames)throw Error('Segment frame mismatch '+c.id);
  const parts=[];for(let i=0;i<c.sourceSegments.length;i++){const s=c.sourceSegments[i],id=c.id+'-part'+i;await cut({...c,sourceSegments:undefined,id,localIn:s.sourceIn,sourceIn:s.sourceIn,sourceOut:s.sourceOut,frames:s.frames,seconds:s.frames/60});parts.push(path.join(O,id+'.mp4'));}
  const list=path.join(O,c.id+'-parts.txt');fs.writeFileSync(list,parts.map(p=>"file '"+p.replaceAll('\\','/')+"'").join('\n'));
  await run(['-f','concat','-safe','0','-i',list,'-c','copy','-movflags','+faststart',dest],c.id);
  c.source=path.relative(R,dest).replaceAll('\\','/');state.cuts.push({id:c.id,frames:c.frames,source:c.source,status:'rendered',sourceSegments:c.sourceSegments});save();return;
 }
 if(c.key==='motion-canvas'){input='shared/output/motion-canvas/blank-project-coding-original-restored-v2-reel.mp4';filter='setpts=PTS-STARTPTS,fps=60,setsar=1';}
 else if(c.key==='manim'){input=c.raw;filter='setpts=0.5*(PTS-STARTPTS),fps=60,setsar=1';}
 else{
  input=c.raw;const src=sources.find(s=>s.id===c.sourceId);if(!src)throw Error('Missing verified source '+c.sourceId);
  const ver=c.key==='tetris'?'3.0':'4.0';
  const credit=[`자료화면 | ${src.uploader} — ${src.title} | youtu.be/${src.id}`,`CC BY ${ver} · creativecommons.org/licenses/by/${ver}/ · 편집: 화면 재구성, 원음 제거, 한국어 자막`];
  const cf=credit.map((t,i)=>{const p=path.join(O,`credit-${c.id}-${i}.txt`);fs.writeFileSync(p,t);return path.relative(R,p).replaceAll('\\','/');});
  // Full-canvas source imagery with a blurred extension, no white PPT frame.
  // Preserve the complete board/editor above the fixed narration caption band.
  filter=`[0:v]setpts=PTS-STARTPTS,fps=60,split[back][front];[back]scale=1920:1080,boxblur=24:1,eq=brightness=-0.22[bg];[front]scale=-2:920[fg];[bg][fg]overlay=(W-w)/2:0,setsar=1,drawbox=x=0:y=1032:w=1920:h=48:color=black@0.80:t=fill,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='${cf[0]}':fontcolor=white:fontsize=17:x=(w-tw)/2:y=1036,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':textfile='${cf[1]}':fontcolor=white:fontsize=17:x=(w-tw)/2:y=1057[v]`;
 }
 const filterFile=path.join(O,c.id+'.filter.txt');fs.writeFileSync(filterFile,filter);
 const args=['-ss',String(c.localIn||0),'-i',path.join(R,input),...(c.classification==='actual'?['-filter_complex_script',filterFile,'-map','[v]']:['-vf',filter]),'-frames:v',String(c.frames),...enc,dest];
 await run(args,c.id);c.source=path.relative(R,dest).replaceAll('\\','/');state.cuts.push({id:c.id,frames:c.frames,source:c.source,status:'rendered',classification:c.classification,sourceIn:c.sourceIn,sourceOut:c.sourceOut});save();console.log('Rendered cut '+c.id+' '+c.key+' '+c.seconds.toFixed(2)+'s');
}
(async()=>{const todo=plan.cuts.filter(c=>(!onlyIds||onlyIds.has(c.id))&&(stage==='reel'?c.key==='motion-canvas':stage==='all'?true:c.key!=='motion-canvas'));let next=0;await Promise.all([0,1].map(async()=>{while(next<todo.length)await cut(todo[next++]);}));fs.writeFileSync(planPath,JSON.stringify(plan,null,2)+'\n');state.status='rendered-awaiting-visual-review';save();})().catch(e=>{state.status='failed';state.error=String(e);save();console.error(e);process.exitCode=1;});
