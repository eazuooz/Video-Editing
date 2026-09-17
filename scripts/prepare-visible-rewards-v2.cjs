// v2 cuts are independent from v1. Refuse accidental overwrite of either source.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),plan=require('../projects/visible-rewards/sources/gameplay-cuts.v2.json');
const version=process.argv.includes('--v3')?3:2;
const out=path.join(root,`motion-canvas/src/projects/visible-rewards/assets/gameplay-v${version}`);
const cache=path.join(root,'shared/output/visible-rewards/media-cache-v2/cuts-exact');
const rebuild=process.argv.includes('--rebuild');
const sceneArg=process.argv.find(a=>a.startsWith('--scene='))?.split('=')[1];
fs.mkdirSync(out,{recursive:true});fs.mkdirSync(cache,{recursive:true});
function run(args){const r=spawnSync('ffmpeg',['-v','error',...args],{windowsHide:true,encoding:'utf8'});if(r.status!==0)throw Error(r.stderr);}
for(const clip of plan.clips){
 if(sceneArg && sceneArg!==clip.scene)continue;
 const target=path.join(out,`scene${clip.scene}.mp4`);
 const previous=path.join(root,`motion-canvas/src/projects/visible-rewards/assets/gameplay-v2/scene${clip.scene}.mp4`);
 if(version===3&&!clip.note){if(!fs.existsSync(target))fs.copyFileSync(previous,target,fs.constants.COPYFILE_EXCL);console.log('Preserved full-frame scene '+clip.scene);continue;}
 const total=clip.cuts.reduce((s,c)=>s+c.duration,0);if(Math.abs(total-plan.exampleSeconds)>.001)throw Error('Bad duration');
 const parts=[];
 for(const [i,c] of clip.cuts.entries()){
  const key=crypto.createHash('sha256').update(JSON.stringify({cut:c,file:plan.sources[c.id].file,revision:2})).digest('hex').slice(0,12);
  const file=path.join(cache,`${clip.scene}-${i}-${key}.mp4`);parts.push(file);
  if(!fs.existsSync(file))run(['-n','-ss',String(c.in),'-i',path.join(root,plan.sources[c.id].file),'-t',String(c.duration),'-vf','setpts=PTS-STARTPTS,scale=1920:1080:force_original_aspect_ratio=decrease:out_color_matrix=bt709,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=white,setsar=1,fps=60:start_time=0,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709','-frames:v',String(Math.round(c.duration*60)),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-color_range','tv','-video_track_timescale','15360','-af',`loudnorm=I=${c.targetLufs??-23}:TP=-3:LRA=11,aresample=48000,afade=t=in:d=0.08,afade=t=out:st=${c.duration-.12}:d=0.12`,'-c:a','aac','-b:a','192k','-ac','2',file]);
 }
 const list=path.join(cache,`${clip.scene}.ffconcat`);fs.writeFileSync(list,'ffconcat version 1.0\n'+parts.map((p,i)=>`file '${p.replaceAll('\\','/')}'\nduration ${clip.cuts[i].duration}`).join('\n'));
 const vf=version===2&&clip.note?`setpts=PTS-STARTPTS,fps=60:start_time=0,scale=1760:990,pad=1920:1080:80:0:white,drawtext=fontfile='C\\:/Windows/Fonts/malgun.ttf':text='${clip.note}':fontsize=29:fontcolor=0x202020:x=(w-tw)/2:y=1020`:'setpts=PTS-STARTPTS,fps=60:start_time=0';
 const audio=version===3?['-map','1:a','-c:a','copy']:['-af',`atrim=duration=${total},afade=t=in:d=0.12,afade=t=out:st=${total-.3}:d=0.3`,'-c:a','aac','-b:a','192k'];
 if(!fs.existsSync(target)||rebuild)run([rebuild?'-y':'-n','-f','concat','-safe','0','-i',list,...(version===3?['-i',previous,'-map','0:v']:[]),'-vf',vf,'-frames:v',String(Math.round(total*60)),'-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-video_track_timescale','15360',...audio,'-t',String(total),'-movflags','+faststart',target]);
 const p=spawnSync('ffprobe',['-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','csv=p=0',target],{encoding:'utf8',windowsHide:true});
 if(+p.stdout.trim()!==Math.round(total*60))throw Error('Wrong clip frames: '+clip.scene);
 console.log(`Verified v${version} scene `+clip.scene);
}
