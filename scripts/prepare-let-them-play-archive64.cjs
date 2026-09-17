const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),plan=require('../projects/let-them-play/sources/archive64-cuts.json'),time=require('../motion-canvas/src/projects/let-them-play/timeline.generated.json');
if(!time.voiceAligned)throw Error('Assemble measured narration first');
const out=path.join(root,'motion-canvas/src/projects/let-them-play/assets/broll-archive64');fs.mkdirSync(out,{recursive:true});
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:8*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stdout;}
const reports=[];
for(const [index,c] of plan.clips.entries()){
 const seconds=time.scenes[index].segmentFrames/time.fps,args=['-y','-v','error'],filters=[],cuts=[];let used=0;
 c.segments.forEach((cut,i)=>{
  const len=cut.seconds==='remaining'?seconds-used:cut.seconds;if(len<=0)throw Error('Invalid segment length');used+=len;
  const raw=path.join(root,`shared/output/let-them-play/media-cache/archive64-${cut.part}-${cut.rawStart}.mp4`);
  const p=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',raw]));
  if(!p.streams.some(s=>s.codec_type==='audio')||!p.streams.some(s=>s.codec_type==='video'&&s.width>=1920)||cut.offset+len>Number(p.format.duration)+.01)throw Error('Invalid HQ source / length '+raw);
  args.push('-ss',String(cut.offset),'-t',String(len),'-i',raw);
  filters.push(`[${i}:v]setpts=PTS-STARTPTS,fps=${time.fps},scale=1920:1080,setsar=1,format=yuv420p[v${i}]`);
  filters.push(`[${i}:a]asetpts=PTS-STARTPTS,aresample=48000,apad,atrim=duration=${len}[a${i}]`);
  cuts.push({source:plan.sources[cut.part].url,start:cut.rawStart+cut.offset,end:cut.rawStart+cut.offset+len});
 });
 filters.push(c.segments.map((_,i)=>`[v${i}][a${i}]`).join('')+`concat=n=${c.segments.length}:v=1:a=1[v][a]`);
 const target=path.join(out,`scene${c.scene}.mp4`);
 run('ffmpeg',[...args,'-filter_complex',filters.join(';'),'-map','[v]','-map','[a]','-t',String(seconds),'-c:v','libx264','-preset','fast','-crf','19','-c:a','aac','-b:a','192k','-movflags','+faststart',target]);
 const p=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',target]));
 if(Number(p.streams.find(s=>s.codec_type==='video').nb_frames)!==time.scenes[index].segmentFrames)throw Error('Wrong frame count');
 run('ffmpeg',['-v','error','-i',target,'-f','null','-']);
 reports.push({scene:c.scene,file:path.relative(root,target),seconds,cuts,audioPreserved:true,fullDecodePassed:true});console.log('Prepared Archive64 '+c.scene);
}
fs.writeFileSync(path.join(out,'media-report.json'),JSON.stringify({reports,permission:plan.permission,creditPlacement:plan.creditPlacement},null,2));
