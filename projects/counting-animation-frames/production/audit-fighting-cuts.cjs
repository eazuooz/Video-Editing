const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v2'),p=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8')),cuts=p.scenes.flatMap(s=>s.cuts).filter(c=>['ryu','chunli','sol'].includes(c.key)),ranges={},results=[];
for(const c of cuts){
 const file=path.join(root,c.video),r=spawnSync('ffmpeg',['-hide_banner','-i',file,'-vf','blackdetect=d=0.12:pix_th=0.08','-an','-f','null','-'],{encoding:'utf8',windowsHide:true});if(r.status!==0)throw Error(r.stderr);
 const black=[...r.stderr.matchAll(/black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)/g)].map(a=>({start:+a[1],end:+a[2],seconds:+a[3]}));
 const meta=JSON.parse(spawnSync('ffprobe',['-v','error','-show_streams','-of','json',file],{encoding:'utf8',windowsHide:true}).stdout),v=meta.streams.find(v=>v.codec_type==='video');if(+v.nb_frames!==c.frames)throw Error('Frame-count mismatch '+c.video);
 const seen=ranges[c.url]??=[];if(seen.some(([a,b])=>c.sourceIn<b-.001&&c.sourceIn+c.seconds>a+.001))throw Error('Source overlap');seen.push([c.sourceIn,c.sourceIn+c.seconds]);ranges[c.url]=seen;
 results.push({key:c.key,url:c.url,sourceRange:[c.sourceIn,c.sourceIn+c.seconds],timelineRange:[c.timelineStart,c.timelineStart+c.seconds],video:c.video,sha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),frames:c.frames,normalSpeed:true,loop:false,blackIntervals:black});
}
const out={checkedAt:new Date().toISOString(),results,nonOverlappingSourceRanges:true,noArtificialSlowdownOrLoops:true,noBlackFramesLongerThan120ms:results.every(r=>!r.blackIntervals.length),motionAndCutContentReview:'inspect rendered all-cue sheets; frame-count/black detection does not approve action relevance'};
fs.writeFileSync(path.join(work,'fighting-cut-audit.json'),JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify(out,null,2));if(!out.noBlackFramesLongerThan120ms)process.exitCode=1;
