// Approved reusable footage. Preserve originals/audio; no looping, freezing or retiming.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),m=require('../projects/visible-rewards/project.json'),plan=require('../projects/visible-rewards/sources/gameplay-cuts.json');
const cache=path.join(root,'shared/output/visible-rewards/media-cache'),out=path.join(root,'motion-canvas/src/projects/visible-rewards/assets/gameplay');fs.mkdirSync(out,{recursive:true});
function run(args){const r=spawnSync('ffmpeg',['-v','error',...args],{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr);}
for(const clip of plan.clips){
 if(Math.abs(clip.cuts.reduce((n,c)=>n+c.duration,0)-m.editing.exampleSeconds)>.001)throw Error('Duration mismatch');
 const parts=[];
 for(const [i,c] of clip.cuts.entries()){
  const file=path.join(cache,`cut-${clip.scene}-${i}.mp4`);parts.push(file);
  if(!fs.existsSync(file)||process.argv.includes('--rebuild-parts'))run([process.argv.includes('--rebuild-parts')?'-y':'-n','-ss',String(c.in),'-i',path.join(cache,c.id+'.mp4'),'-t',String(c.duration),'-vf','scale=1920:1080:force_original_aspect_ratio=decrease:out_color_matrix=bt709,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1,fps=60','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-video_track_timescale','15360','-af',`loudnorm=I=${c.targetLufs}:TP=-3:LRA=11,aresample=48000,afade=t=in:d=0.08,afade=t=out:st=${c.duration-.12}:d=0.12`,'-c:a','aac','-b:a','192k','-ac','2',file]);
 }
 const list=path.join(cache,`scene${clip.scene}.ffconcat`);fs.writeFileSync(list,'ffconcat version 1.0\n'+parts.map((f,i)=>`file '${f.replaceAll('\\','/')}'\nduration ${clip.cuts[i].duration}`).join('\n')+'\n');
 const target=path.join(out,`scene${clip.scene}.mp4`);
 const notes={
  '01':'설명용 가정  1,700G → 2,000G  |  실제 녹화의 소지금과는 별개입니다.',
  '03':'설명용 가정  현재 1,700G · 목표 2,000G · 남은 300G  |  실제 HUD 값 아님',
  '07':'자료화면은 이동·수집 예시  |  확률 재료 이야기는 특정 게임과 무관한 가상 사례'
 };
 const visual=notes[clip.scene]?['-vf',`setpts=PTS-STARTPTS,fps=60:start_time=0,scale=1760:990,pad=1920:1080:80:0:color=white,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='${notes[clip.scene]}':fontsize=30:fontcolor=0x202020:x=(w-tw)/2:y=1020`,'-frames:v',String(Math.round(m.editing.exampleSeconds*60)),'-c:v','libx264','-preset','fast','-crf','19','-video_track_timescale','15360']:['-c:v','copy'];
 if(!fs.existsSync(target)||process.argv.includes('--rebuild'))run([process.argv.includes('--rebuild')?'-y':'-n','-f','concat','-safe','0','-i',list,'-map','0:v','-map','0:a',...visual,'-af',`atrim=duration=${m.editing.exampleSeconds},afade=t=in:d=0.12,afade=t=out:st=${m.editing.exampleSeconds-.3}:d=0.3`,'-c:a','aac','-b:a','192k','-t',String(m.editing.exampleSeconds),'-movflags','+faststart',target]);
 console.log('Prepared '+clip.scene);
}
