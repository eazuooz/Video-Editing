const fs=require('node:fs'),path=require('node:path'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),manifest=require(path.join(root,'projects/game-dev-career/project.json')),suffix=manifest.production.revision>1?'-v'+manifest.production.revision:'';
const out=path.join(root,`projects/game-dev-career/production/qa-final${suffix}/cues`);fs.mkdirSync(out,{recursive:true});
(async()=>{const browser=await puppeteer.launch({headless:true,protocolTimeout:180000});try{
 const page=await browser.newPage();await page.setViewport({width:1440,height:1100});await page.goto('http://127.0.0.1:9191/career-final.html');await page.waitForFunction(()=>window.careerReview?.ready,{timeout:60000});const cues=await page.evaluate(()=>careerReview.timing.captions),images=[];
 for(let i=0;i<cues.length;i++){
  const cue=cues[i],frame=Math.round((cue.start+cue.end)/2*60);await page.evaluate(t=>careerReview.jump(t),frame/60);await page.waitForFunction(f=>careerReview.rendered===f,{timeout:30000},frame);
  const data=await page.evaluate(()=>{const c=document.createElement('canvas');c.width=640;c.height=360;c.getContext('2d').drawImage(careerReview.stage.finalBuffer,0,0,640,360);return c.toDataURL('image/png');});images.push({i:i+1,data});
 }
 for(let k=0;k<Math.ceil(images.length/24);k++){
  await page.setContent('<body style="margin:0;font:18px sans-serif"><div style="display:grid;grid-template-columns:repeat(3,640px)">'+images.slice(k*24,k*24+24).map(s=>`<div>cue ${s.i}<img width="640" src="${s.data}"></div>`).join('')+'</div>');
  await page.setViewport({width:1920,height:1080});await page.screenshot({path:path.join(out,`page-${k+1}.png`),fullPage:true});
 }
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({count:cues.length,allRendered:true,frames:cues.map(c=>Math.round((c.start+c.end)/2*60))},null,2));console.log('All '+cues.length+' narration cues captured.');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
