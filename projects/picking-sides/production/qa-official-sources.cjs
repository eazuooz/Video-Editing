const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),file=path.join(__dirname,'official-source-qa.json');
const state={startedAt:new Date().toISOString(),pid:process.pid,status:'running',scope:'three-new-official-sources-only-not-final-video',records:[]};
const save=()=>fs.writeFileSync(file,JSON.stringify(state,null,2)+'\n');
const run=(bin,args)=>{const r=spawnSync(bin,args,{encoding:'utf8',windowsHide:true,maxBuffer:3e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;};
try{save();for(const id of ['VOZRzwlzQeA','BZRZmJnPmmA','Z5jytMiH4rI']){
 const p=path.join(root,'shared/output/picking-sides/media-cache',id+'.mp4');state.active=id;save();
 const meta=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',p]));
 run('ffmpeg',['-v','error','-threads','2','-i',p,'-f','null','-']);
 const video=meta.streams.find(x=>x.codec_type==='video');state.records.push({id,source:path.relative(root,p).replaceAll('\\','/'),sha256:crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),seconds:+meta.format.duration,width:video.width,height:video.height,fps:video.r_frame_rate,fullDecode:'passed',finalEditedCueReview:'pending'});save();console.log('Full source decoded '+id);
}state.active=null;state.status='completed';state.finishedAt=new Date().toISOString();save();}catch(e){state.status='failed';state.error=String(e);save();console.error(e);process.exitCode=1;}
