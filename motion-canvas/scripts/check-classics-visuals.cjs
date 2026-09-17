// Read-only browser QA of our local Motion Canvas application, not an external website.
const puppeteer=require('puppeteer'),fs=require('node:fs'),path=require('node:path');
const out=path.resolve(__dirname,'../../shared/output/choice-driven-classics/visual-qa');
const board=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../projects/choice-driven-classics/script/storyboard.json'),'utf8'));
async function main(){
 fs.mkdirSync(out,{recursive:true});
 const browser=await puppeteer.launch({headless:true,args:['--autoplay-policy=no-user-gesture-required']});
 const errors=[];
 try{
  const page=await browser.newPage();await page.setViewport({width:1480,height:1180});page.on('pageerror',e=>errors.push(e.message));
  page.on('console',msg=>{if(msg.type()==='error')errors.push(msg.text());});
  await page.goto('http://localhost:9100/classics-review.html',{waitUntil:'networkidle0',timeout:60000});
  await page.waitForFunction(()=>window.classicsReview?.ready,{timeout:60000});
  const times=[3,9,12,17,23,29,35,40,47,50,55,58.8];
  for(const t of times){
   await page.evaluate(t=>classicsReview.jump(t),t);
   await page.waitForFunction(f=>classicsReview.rendered===f,{timeout:30000},Math.round(t*60));
   const b64=await page.evaluate(()=>classicsReview.stage.finalBuffer.toDataURL('image/png').split(',')[1]);
   fs.writeFileSync(path.join(out,`t-${String(t).replace('.','-')}.png`),Buffer.from(b64,'base64'));console.log(`Captured ${t}s`);
  }
  const actual=await page.evaluate(()=>classicsReview.player.playback.duration);
  const sceneFrames=await page.evaluate(()=>classicsReview.player.playback.onScenesRecalculated.current.map(s=>({name:s.name,first:s.firstFrame,last:s.lastFrame})));
  const total=board.scenes.reduce((sum,s)=>sum+s.end-s.start,0);
  if(total!==60||board.scenes.length!==6||board.scenes.some((s,i)=>s.start!==(i?board.scenes[i-1].end:0)))throw Error('Invalid six-scene timeline');
  if(actual!==3600||sceneFrames.some((s,i)=>s.first!==board.scenes[i].start*60||s.last!==board.scenes[i].end*60))throw Error('Scene boundaries differ from fixed storyboard');
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({frames:times,errors,sceneFrames,requestedSeconds:total,playbackDurationFrames:actual,publishReady:false},null,2));
  if(errors.length)throw Error(errors.join('\n'));
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e);process.exitCode=1;});
