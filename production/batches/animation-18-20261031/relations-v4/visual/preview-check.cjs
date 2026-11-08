/* Lightweight, no-video layout review; timings here are explicitly provisional. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const {createCanvas,loadImage}=require('C:/Users/1/Videos/YamyamCoding/ai-2d-tools/render-node/node_modules/@napi-rs/canvas');
const r=require('./renderer.cjs'),base=path.join(__dirname,'..'),planPath=path.join(base,'planning/relations-plan.json');
const p=JSON.parse(fs.readFileSync(planPath,'utf8')),out=path.join(base,'local/visual-previews');r.setup(p);
async function main(){
 fs.mkdirSync(out,{recursive:true});
 const ranges=[.18,.55,.9],safe=[];
 for(const f of ranges){
  const sheet=createCanvas(1125,1410),g=sheet.getContext('2d');g.fillStyle='#151515';g.fillRect(0,0,sheet.width,sheet.height);
  for(let i=0;i<p.episodes.length;i++){
   const ep=p.episodes[i],cv=r.frame(ep.id,35*f,{duration:35}),png=cv.toBuffer('image/png');
   fs.writeFileSync(path.join(out,`${ep.id}-${f}.png`),png);
   const mini=createCanvas(375,211);mini.getContext('2d').drawImage(cv,0,0,375,211);fs.writeFileSync(path.join(out,`${ep.id}-${f}-mobile.png`),mini.toBuffer('image/png'));
   const rgba=cv.getContext('2d').getImageData(0,920,1920,160).data;
   for(let q=0;q<rgba.length;q+=4)assert.equal(rgba[q]===9&&rgba[q+1]===13&&rgba[q+2]===11,true,ep.id+' intrudes caption safe area');
   safe.push({id:ep.id,fraction:f,captionSafeY:920,result:'clear'});
   const x=(i%3)*375,y=Math.floor(i/3)*235;g.drawImage(cv,x,y,375,211);g.fillStyle='#eeeeee';g.font='15px sans-serif';g.fillText(ep.id+' · provisional '+f,x+8,y+228);
  }
  fs.writeFileSync(path.join(out,`mobile-all-${f}.png`),sheet.toBuffer('image/png'));
 }
 const body=JSON.parse(fs.readFileSync(path.join(__dirname,'body-timing.json'),'utf8'));
 for(const ep of body.episodes){for(const sec of[.5,ep.duration*.55,ep.duration-.5]){r.frame(ep.id,sec,ep);fs.writeFileSync(path.join(out,`${ep.id}-body-${sec.toFixed(2)}.png`),r.canvas.toBuffer('image/png'));}}
 const subset=r.timingState(p.episodes.find(x=>x.id==='A03'),.5,{beats:[{id:'A03-B04',start:0,end:2}]});assert.equal(subset.level,3,'Subset uses plan beat index');
 assert.throws(()=>r.timingState(p.episodes[0],0,{sentences:[{id:'missing',start:0,end:2}]}),/does not match/);
 fs.writeFileSync(path.join(out,'layout-check.json'),JSON.stringify({kind:'layout-only-not-audio-or-final-encode-review',planSha256:crypto.createHash('sha256').update(fs.readFileSync(planPath)).digest('hex'),provisionalPreviewDuration:35,episodes:p.episodes.length,previewFrames:safe.length,captionSafeChecks:safe,selectedBeatRangeTest:'passed',invalidTimingRejected:'passed'},null,2));
 console.log(JSON.stringify({episodes:p.episodes.length,previewFrames:safe.length,captionSafe:'passed',out}));
}
main().catch(e=>{console.error(e);process.exitCode=1});
