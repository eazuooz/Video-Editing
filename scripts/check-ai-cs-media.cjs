// Verify all edited clips, source-audio slots, and create review contact sheets.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),cache=path.join(root,'shared/output/ai-cs-media-cache');
const media=JSON.parse(fs.readFileSync(path.join(root,'projects/ai-era-cs-fundamentals/sources/selected-footage.json'),'utf8'));
const audio=JSON.parse(fs.readFileSync(path.join(root,'projects/ai-era-cs-fundamentals/audio/preview-report.json'),'utf8'));
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:10*1024*1024});if(r.status)throw Error(r.stderr);return {out:r.stdout,err:r.stderr};}
const report=[];
for(const c of media.clips){
 const trimmed=JSON.parse(fs.readFileSync(path.join(cache,`${c.scene}-trim-report.json`),'utf8'));
 if(JSON.stringify(trimmed.segments)!==JSON.stringify(c.segments))throw Error(`Stale edit recipe ${c.scene}: trim again before mixing`);
 const file=`motion-canvas/src/projects/ai-era-cs-fundamentals/assets/broll/scene${c.scene}.mp4`;
 const p=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',file]).out);
 const v=p.streams.find(s=>s.codec_type==='video'),hasAudio=p.streams.some(s=>s.codec_type==='audio');
 if(v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1'||Number(v.nb_frames)!==Math.round(media.clipDuration*60))throw Error(`Invalid video ${c.scene}`);
 const slot=audio.scenes.find(s=>s.scene===c.scene);
 if(!slot || slot.clipDuration!==media.clipDuration || slot.hasSourceAudio!==hasAudio)throw Error(`Stale audio report ${c.scene}`);
 const volume=run('ffmpeg',['-hide_banner','-ss',String(slot.start),'-i','motion-canvas/src/projects/ai-era-cs-fundamentals/assets/preview-source-mix.m4a','-t',String(media.clipDuration),'-af','volumedetect','-f','null','-']).err;
 const peak=volume.match(/max_volume:\s*([^\r\n]+)/)?.[1];
 if(hasAudio&&(!peak||parseFloat(peak)<-55))throw Error(`Missing audible source mix ${c.scene}`);
 run('ffmpeg',['-y','-v','error','-i',file,'-vf',`fps=1,scale=480:-2,drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='SCENE ${c.scene}':fontsize=22:fontcolor=white:box=1:boxcolor=black@0.8:x=8:y=8,tile=5x4`,'-frames:v','1',path.join(cache,`${c.scene}-cut-contact.jpg`)]);
 report.push({scene:c.scene,sourceStart:c.start,duration:Number(v.duration),frames:Number(v.nb_frames),hasAudio,mixPeak:peak});
}
for(const kind of ['example','meme','concept']){
 const args=[];for(const c of media.clips)args.push('-i',path.join(cache,'visual-qa',`${c.scene}-${kind}.png`));
 const filters=media.clips.map((_,i)=>`[${i}:v]scale=480:270[v${i}]`);
 filters.push(media.clips.map((_,i)=>`[v${i}]`).join('')+'xstack=inputs=12:layout=0_0|480_0|960_0|0_270|480_270|960_270|0_540|480_540|960_540|0_810|480_810|960_810[out]');
 run('ffmpeg',['-y','-v','error',...args,'-filter_complex',filters.join(';'),'-map','[out]','-frames:v','1',path.join(cache,`${kind}-overview.jpg`)]);
}
fs.writeFileSync(path.join(root,'projects/ai-era-cs-fundamentals/sources/media-check.json'),JSON.stringify({checkedAt:new Date().toISOString(),video:'1920x1080 60fps',clips:report},null,2)+'\n');
console.log(JSON.stringify(report,null,2));
