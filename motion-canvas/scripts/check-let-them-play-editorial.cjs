// Temporal QA of both graphic thirds in every chapter. Separate from the 24-point gate.
const fs=require('node:fs'),path=require('node:path'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),t=require('../src/projects/let-them-play/timeline.generated.json');
const out=path.join(root,'shared/output/let-them-play/editorial-full-v5/qa');
async function main(){
 fs.mkdirSync(out,{recursive:true});const browser=await puppeteer.launch({headless:true,protocolTimeout:120000}),errors=[],captures=[];
 try{
  const page=await browser.newPage();page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://localhost:9100/let-them-play-review.html',{waitUntil:'domcontentloaded',timeout:60000});
  await page.waitForFunction(()=>window.thirdReview?.ready,{timeout:60000});await page.evaluate(()=>document.fonts.ready);
  const runtime=await page.evaluate(()=>thirdReview.player.playback.duration);if(runtime!==t.totalFrames)throw Error('Wrong runtime frames');
  for(const s of t.scenes)for(const part of [1,2])for(const phase of [.15,.55,.88]){
   const frame=s.startFrame+Math.round(s.segmentFrames*(part+phase)),label=`scene${s.id}-${part===1?'design':'compare'}-${phase}`;
   await page.evaluate(f=>thirdReview.jump(f/60),frame);await page.waitForFunction(f=>thirdReview.rendered===f,{timeout:60000},frame);
   const data=await page.evaluate(()=>thirdReview.stage.finalBuffer.toDataURL('image/png').split(',')[1]);
   fs.writeFileSync(path.join(out,label+'.png'),Buffer.from(data,'base64'));captures.push({label,frame,scene:s.id,part,phase,data});
  }
  // Exact final occupied frame must be a designed ending, not credits or a blank.
  await page.evaluate(f=>thirdReview.jump(f/60),t.totalFrames-1);await page.waitForFunction(f=>thirdReview.rendered===f,{timeout:60000},t.totalFrames-1);
  const ending=await page.evaluate(()=>thirdReview.stage.finalBuffer.toDataURL('image/png').split(',')[1]);fs.writeFileSync(path.join(out,'ending.png'),Buffer.from(ending,'base64'));
  for(const [batch,subset] of [captures.slice(0,24),captures.slice(24)].entries()){
   await page.setViewport({width:1440,height:1000});await page.setContent('<body style="margin:0;background:#e5e5e5;font:17px sans-serif"><div style="display:grid;grid-template-columns:repeat(3,480px)">'+subset.map(x=>`<div>${x.label}<img style="display:block" width="480" src="data:image/png;base64,${x.data}"></div>`).join('')+'</div></body>');
   await page.screenshot({path:path.join(out,`contact-${batch+1}.png`),fullPage:true});
  }
  if(errors.length)throw Error(errors.join('\n'));
  fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({frames:t.totalFrames,errors,screens:captures.map(({data,...c})=>c),endingFrame:t.totalFrames-1,agentVisualReview:'awaits-inspection'},null,2));console.log('48 temporal samples + final frame: '+out);
 }finally{await browser.close()}
}
main().catch(e=>{console.error(e);process.exitCode=1});
