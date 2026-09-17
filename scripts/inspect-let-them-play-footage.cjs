// Render a local video contact sheet for editorial QA, never modify the source.
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const puppeteer=require('../motion-canvas/node_modules/puppeteer');
const [input,startText,endText,stepText,label]=process.argv.slice(2);
const start=Number(startText),end=Number(endText),step=Number(stepText);
if(!input||!fs.existsSync(input)||!Number.isFinite(start)||!Number.isFinite(end)||!(step>0)||end<start||!/^[a-z0-9-]+$/i.test(label))throw Error('Usage: node scripts/inspect-let-them-play-footage.cjs input start end step label');
const out=path.resolve('shared/output/let-them-play/footage-qa',label);fs.mkdirSync(out,{recursive:true});
async function main(){
 const images=[];
 for(let t=start;t<=end;t+=step){
  const file=path.join(out,String(t).padStart(6,'0')+'.jpg');
  const result=spawnSync('ffmpeg',['-y','-v','error','-ss',String(t),'-i',input,'-frames:v','1','-vf','scale=480:-2',file],{windowsHide:true,encoding:'utf8'});
  if(result.status!==0||!fs.existsSync(file))throw Error('Snapshot '+t+': '+result.stderr);
  const time=new Date(t*1000).toISOString().slice(11,19);
  images.push({seconds:t,time,data:fs.readFileSync(file).toString('base64')});
 }
 const browser=await puppeteer.launch({headless:true});
 try{
  const page=await browser.newPage();await page.setViewport({width:1440,height:1000,deviceScaleFactor:1});
  await page.setContent('<body style="margin:0;background:#eee;font:20px sans-serif"><div style="display:grid;grid-template-columns:repeat(3,480px)">'+images.map(x=>'<div>'+x.seconds+' sec · '+x.time+'<img width="480" src="data:image/jpeg;base64,'+x.data+'"></div>').join('')+'</div></body>');
  await page.screenshot({path:path.join(out,'contact.png'),fullPage:true});
 }finally{await browser.close()}
 fs.writeFileSync(path.join(out,'index.json'),JSON.stringify({input:path.resolve(input),images:images.map(({seconds,time})=>({seconds,time})),reviewStatus:'requires-visual-inspection'},null,2));
 console.log(out);
}
main().catch(e=>{console.error(e);process.exitCode=1});
