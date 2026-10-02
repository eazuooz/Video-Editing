// Offline source-composition proof; not a final-caption or full-video QA substitute.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const {createCanvas,loadImage,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:[path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]}));
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun Gothic');
const root=path.resolve(__dirname,'../../..'),dest=path.join(__dirname,'crop-review-v3');fs.mkdirSync(dest,{recursive:true});
const recipes=[
 ['space-d','Z5jytMiH4rI',362,373.1,[310,170,1280,720]],
 ['space-f','Z5jytMiH4rI',393,403.15,[280,180,1360,765]],
 ['identity-extension','Z5jytMiH4rI',67,70,[120,0,1680,945]],
 ['flight-extension','Z5jytMiH4rI',358,362,[360,80,1216,684]],
];
function run(args){const r=spawnSync('ffmpeg',args,{encoding:'utf8',windowsHide:true,maxBuffer:1e6});if(r.status!==0)throw Error(r.stderr);}
(async()=>{const all=[];
for(const [id,source,start,end,crop]of recipes){
 const images=[];for(const t of [start+.15,(start+end)/2,end-.15]){
  const file=path.join(dest,`${id}-${t.toFixed(2)}.png`),[x,y,w,h]=crop;
  run(['-v','error','-y','-threads','2','-ss',String(t),'-i',path.join(root,'shared/output/picking-sides/media-cache',source+'.mp4'),'-frames:v','1','-vf',`crop=${w}:${h}:${x}:${y},scale=960:540`,file]);
  images.push({time:t,path:file});
 }
 const c=createCanvas(1920,614),ctx=c.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,1920,614);
 for(let i=0;i<3;i++){const left=i*640;ctx.drawImage(await loadImage(images[i].path),left,46,640,360);ctx.font='18px Malgun Gothic';ctx.fillStyle='#222';ctx.fillText(`${id} | ${source} | ${images[i].time.toFixed(2)}s`,left+8,28);
  // Same permanent center (960,970), scaled to640x360; maximum two-line sample.
  ctx.fillStyle='#0c4037';ctx.fillRect(left+114,354,421,52);ctx.fillStyle='white';ctx.fillRect(left+109,350,421,52);ctx.strokeStyle='#111';ctx.strokeRect(left+109,350,421,52);ctx.fillStyle='#111';ctx.font='17px Malgun Gothic';ctx.textAlign='center';ctx.fillText('같은 대상을 따라가며',left+320,371);ctx.fillText('다음 행동을 함께 살펴보세요.',left+320,393);ctx.textAlign='left';
 }
 ctx.fillStyle='#111';ctx.font='23px Malgun Gothic';ctx.fillText('사전 화면 구성 검토 · 실제 최종 자막 큐/시간 검수는 별도',24,454);ctx.fillText(`Original crop x,y,w,h: ${crop.join(', ')} / normal speed / no loop`,24,496);
 const contact=path.join(dest,id+'.png');fs.writeFileSync(contact,c.toBuffer('image/png'));all.push({id,source,start,end,crop,stills:images.map(x=>({time:x.time,path:path.relative(root,x.path).replaceAll('\\','/')})),contact:path.relative(root,contact).replaceAll('\\','/'),review:'pending-direct-review'});
}
fs.writeFileSync(path.join(dest,'recipes.json'),JSON.stringify({createdAt:new Date().toISOString(),kind:'preliminary-source-crop-proof',fixedCaptionCenter:[960,970],finalCueReview:false,recipes:all},null,2)+'\n');console.log('Created15source-composition contact sheets.');
})().catch(e=>{console.error(e);process.exitCode=1;});
