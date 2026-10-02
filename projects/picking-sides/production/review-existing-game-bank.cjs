// Offline preliminary composition checks; does not replace final cue/cut QA.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const {createCanvas,loadImage,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:[path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]}));
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun Gothic');
const root=path.resolve(__dirname,'../../..'),dest=path.join(__dirname,process.env.BANK_REVIEW_DIR||'existing-game-replan/composition');fs.mkdirSync(dest,{recursive:true});
const plan=JSON.parse(fs.readFileSync(path.join(__dirname,'existing-game-replan/action-map-v2.json'),'utf8'));
const rel=p=>path.relative(root,p).replaceAll('\\','/');
function run(args){const r=spawnSync('ffmpeg',args,{encoding:'utf8',windowsHide:true,maxBuffer:1e6});if(r.status!==0)throw Error(r.stderr);}
(async()=>{
 const frames=[];
 for(const chapter of plan.chapters)for(const [index,cut]of chapter.cuts.entries()){
  if(process.env.BANK_REVIEW_CHANGED_ONLY==='1'&&!cut.compositionNeedsReview)continue;
  for(const [position,time]of [['first',cut.start+.1],['middle',(cut.start+cut.end)/2],['last',cut.end-.1]]){
   const id=`${chapter.scene}-${index+1}-${position}`,file=path.join(dest,id+'.png');
   let filter='scale=960:540';if(cut.crop){const[x,y,w,h]=cut.crop;filter=`crop=${w}:${h}:${x}:${y},`+filter;}
   run(['-v','error','-y','-threads','2','-ss',String(time),'-i',path.join(root,'shared/output/picking-sides/media-cache',cut.sourceId+'.mp4'),'-frames:v','1','-vf',filter,file]);
   frames.push({id,scene:chapter.scene,cut:index+1,source:cut.sourceId,time,file:rel(file),crop:cut.crop});
  }
 }
 const pages=[];
 for(let page=0;page<Math.ceil(frames.length/9);page++){
  const canvas=createCanvas(1920,1240),ctx=canvas.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,1920,1240);
  for(let n=0;n<9;n++){
   const f=frames[page*9+n];if(!f)break;const left=(n%3)*640,top=Math.floor(n/3)*410;
   ctx.fillStyle='#111';ctx.font='18px Malgun Gothic';ctx.fillText(`${f.id} | ${f.source} | ${f.time.toFixed(2)}s`,left+6,top+24);
   ctx.drawImage(await loadImage(path.join(root,f.file)),left,top+38,640,360);
   ctx.fillStyle='#0c4037';ctx.fillRect(left+113,top+339,422,52);ctx.fillStyle='white';ctx.fillRect(left+109,top+335,422,52);ctx.strokeStyle='#111';ctx.strokeRect(left+109,top+335,422,52);
   ctx.fillStyle='#111';ctx.font='17px Malgun Gothic';ctx.textAlign='center';ctx.fillText('응원하는 대상을 따라가며',left+320,top+356);ctx.fillText('다음 행동을 함께 살펴보세요.',left+320,top+378);ctx.textAlign='left';
  }
  const file=path.join(dest,`contact-${page+1}.png`);fs.writeFileSync(file,canvas.toBuffer('image/png'));pages.push(rel(file));
 }
 fs.writeFileSync(path.join(dest,'review.json'),JSON.stringify({createdAt:new Date().toISOString(),kind:'first-middle-last-provisional-bank-composition',fixedCaptionCenter:[960,970],finalCueReview:false,review:'pending-direct-review',frames,pages},null,2)+'\n');
 console.log(JSON.stringify({frames:frames.length,pages}));
})().catch(e=>{console.error(e);process.exitCode=1;});
