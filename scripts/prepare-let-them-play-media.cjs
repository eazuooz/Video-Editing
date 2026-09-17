const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),manifest=require('../projects/let-them-play/project.json'),plan=require('../projects/let-them-play/sources/selected-footage.json');
const out=path.join(root,'motion-canvas/src/projects/let-them-play/assets/broll');
if(plan.clipDuration!==manifest.editing.exampleSeconds)throw Error('Retiming requires a new cut plan, never loop short footage.');
const selected=process.argv[2]?plan.clips.filter(c=>c.scene===process.argv[2]):plan.clips;
if(!selected.length)throw Error('Unknown scene');
fs.mkdirSync(out,{recursive:true});
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:8*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stdout}
const reports=[];
for(const c of selected){
 if(Math.abs(c.segments.reduce((a,b)=>a+b.seconds,0)-plan.clipDuration)>.00001)throw Error('Wrong duration '+c.scene);
 const target=path.join(out,'scene'+c.scene+'.mp4'),args=['-y','-v','error'],filters=[];
 c.segments.forEach((cut,i)=>{
  const raw=path.join(root,'shared/output/let-them-play/media-cache','longplays-hq-'+cut.rawStart+'.mp4');
  if(!fs.existsSync(raw))throw Error('Missing HQ input: '+raw);
  const p=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',raw]));
  if(!p.streams.some(s=>s.codec_type==='audio')||!p.streams.some(s=>s.codec_type==='video'&&s.width>=1920))throw Error('Missing full-resolution video/audio '+raw);
  if(cut.offset+cut.seconds>Number(p.format.duration)+.05)throw Error('Cut exceeds source');
  args.push('-ss',String(cut.offset),'-t',String(cut.seconds),'-i',raw);
  filters.push('['+i+':v]setpts=PTS-STARTPTS,fps=60,scale=1920:1080,setsar=1,format=yuv420p[v'+i+']');
  filters.push('['+i+':a]asetpts=PTS-STARTPTS,aresample=48000,apad,atrim=duration='+cut.seconds+'[a'+i+']');
 });
 filters.push(c.segments.map((_,i)=>'[v'+i+'][a'+i+']').join('')+'concat=n='+c.segments.length+':v=1:a=1[v][a]');
 run('ffmpeg',[...args,'-filter_complex',filters.join(';'),'-map','[v]','-map','[a]','-t',String(plan.clipDuration),'-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','192k','-movflags','+faststart',target]);
 const p=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',target]));
 const video=p.streams.find(s=>s.codec_type==='video');
 if(Number(video.nb_frames)!==1170||!p.streams.some(s=>s.codec_type==='audio'))throw Error('Bad final clip '+c.scene);
 run('ffmpeg',['-v','error','-i',target,'-f','null','-']);
 reports.push({scene:c.scene,file:path.relative(root,target),seconds:Number(p.format.duration),frames:Number(video.nb_frames),audioPreserved:true,fullDecodePassed:true,source:plan.source.url,cuts:c.segments.map(s=>({start:s.rawStart+s.offset,end:s.rawStart+s.offset+s.seconds})),reviewStatus:'requires-final-visual-and-listening-review'});
 console.log('Prepared '+c.scene);
}
fs.writeFileSync(path.join(out,'media-report'+(process.argv[2]?'-'+process.argv[2]:'')+'.json'),JSON.stringify({reports,source:plan.source,voiceAligned:false,publishReady:false},null,2));
