// Inspect the assembled MP4 itself, not only the live canvas.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'..'),m=require('../projects/let-them-play/project.json'),t=require('../motion-canvas/src/projects/let-them-play/timeline.generated.json'),video=path.join(root,m.paths.videoClean),out=path.join(root,'shared/output/let-them-play/final-assembled-qa');
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16*1024*1024});if(r.status!==0)throw Error(r.stderr);return r.stdout;}
async function main(){
 fs.mkdirSync(out,{recursive:true});const captures=[],lateComparisons=[];
 for(const s of t.scenes)for(let k=0;k<3;k++){
  const frame=s.startFrame+Math.round(s.segmentFrames*(k+.5)),sec=frame/t.fps,label=`scene${s.id}-part${k+1}`,file=path.join(out,label+'.jpg');
  run('ffmpeg',['-y','-v','error','-ss',String(sec),'-i',video,'-frames:v','1','-vf','scale=640:360',file]);
  captures.push({label,frame,seconds:sec,data:fs.readFileSync(file).toString('base64')});
 }
 for(const s of t.scenes){
  const frame=s.startFrame+Math.round(s.segmentFrames*2.88),label=`scene${s.id}-compare-late`,file=path.join(out,label+'.jpg');
  run('ffmpeg',['-y','-v','error','-ss',String(frame/t.fps),'-i',video,'-frames:v','1','-vf','scale=1280:720',file]);
  lateComparisons.push({label,frame,data:fs.readFileSync(file).toString('base64')});
 }
 run('ffmpeg',['-y','-v','error','-ss',String((t.totalFrames-1)/t.fps),'-i',video,'-frames:v','1',path.join(out,'ending.jpg')]);
 const browser=await puppeteer.launch({headless:true});
 try{const page=await browser.newPage();await page.setViewport({width:1920,height:1080});await page.setContent('<body style="margin:0;background:#ddd;font:20px sans-serif"><div style="display:grid;grid-template-columns:repeat(3,640px)">'+captures.map(c=>`<div>${c.label} / ${c.seconds.toFixed(2)}s<img width="640" height="360" src="data:image/jpeg;base64,${c.data}"></div>`).join('')+'</div></body>');await page.screenshot({path:path.join(out,'contact.png'),fullPage:true});
  await page.setViewport({width:1280,height:1080});await page.setContent('<body style="margin:0;background:#ddd;font:18px sans-serif"><div style="display:grid;grid-template-columns:repeat(2,640px)">'+lateComparisons.map(c=>`<div>${c.label}<img style="display:block" width="640" src="data:image/jpeg;base64,${c.data}"></div>`).join('')+'</div></body>');await page.screenshot({path:path.join(out,'late-contact.png'),fullPage:true});
 }finally{await browser.close();}
 const load=p=>fs.readFileSync(path.join(root,p),'utf8').trim().split(/\r?\n\s*\r?\n/).map(b=>b.split(/\r?\n/));
 const ko=load(m.paths.captionsKo),en=load(m.paths.captionsEn);
 if(ko.length!==120||en.length!==ko.length||ko.some((c,i)=>c[0]!==en[i][0]||c[1]!==en[i][1]))throw Error('Bilingual cue mismatch');
 const streams=JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',video]));
 const v=streams.streams.find(s=>s.codec_type==='video'),a=streams.streams.find(s=>s.codec_type==='audio');
 if(Number(v.nb_frames)!==t.totalFrames||v.width!==1920||v.height!==1080||v.r_frame_rate!=='60/1'||a.codec_name!=='aac'||a.sample_rate!=='48000'||a.channels!==2)throw Error('Wrong final media specification');
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({video,visualRevision:m.visualRevision??4,frames:t.totalFrames,seconds:t.totalFrames/t.fps,captions:{ko:ko.length,en:en.length,identicalTimings:true,last:ko.at(-1)[1]},captures:captures.map(({data,...c})=>c),lateComparisons:lateComparisons.map(({data,...c})=>c),endingFrame:t.totalFrames-1,visualReview:'contact-sheets-await-agent-inspection',humanListeningApproval:'pending'},null,2));
 console.log('Final MP4 QA: '+out);
}
main().catch(e=>{console.error(e);process.exitCode=1});
