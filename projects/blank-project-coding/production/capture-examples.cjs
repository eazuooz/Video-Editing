// Record this project's owned, executing application. No remote/browser account automation.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer'),catalog=require('../examples/lessons.cjs');
const root=path.resolve(__dirname,'../../..'),revision=process.env.BLANK_CAPTURE_REVISION||'actual-v1',base=path.join(root,'shared/assets/blank-project-coding',revision),reportPath=path.join(__dirname,'capture-report.json');
fs.mkdirSync(base,{recursive:true});
const digest=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const inputs=['app.js','engine.js','style.css','index.html','lessons.cjs','server.cjs','trace.hpp'].map(p=>({path:'projects/blank-project-coding/examples/'+p,sha256:digest(path.join(__dirname,'../examples',p))}));
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const step=(action,arg,hold=3)=>({action,arg,hold});
const inp=(a,h=2.3)=>step('input',a,h),scenario=(n,h=3)=>step('scenario',n,h),source=(n,h=3)=>step('source',n,h);
const cpp=(id,name,steps,edit=true)=>({id,mode:'cpp',actions:[step('blank',null,2),...(edit?[step('type',catalog.cpp[name],2)]:[source(name,4)]),step('run',null,4),...Array.from({length:steps},()=>step('step',null,4)),step('scroll',0,4),source(name,4),step('run',null,3),...Array.from({length:steps},()=>step('step',null,2))]});
const testMoves=[inp('left'),inp('right'),inp('rotate'),inp('down'),inp('drop')];
const takes=[
 {id:'01',mode:'blocks',actions:[step('full'),scenario('two-rows'),inp('down'),inp('down'),inp('drop',4),...testMoves,step('full'),step('blank',null,4),step('type',catalog.js.data,2),step('run'),step('full'),...testMoves]},
 cpp('03','pair',5,false),{...cpp('05','node',2),actions:[...cpp('05','node',2).actions,source('pair',3),step('run',null,3),step('step',null,3),step('step',null,3),step('step',null,3)]},cpp('07','pair',5),cpp('09','insert',4),cpp('10','remove',5),
 {id:'12',mode:'blocks',actions:[source('movement'),step('full'),...testMoves,step('full'),step('blank',null,4),step('type',catalog.js.data,3),step('run'),step('full'),...testMoves]},
 {id:'14',mode:'blocks',actions:[step('blank',null,3),step('type',catalog.js.data,3),step('run'),...testMoves,source('movement'),step('run'),scenario('empty'),...testMoves,...testMoves]},
 {id:'16',mode:'blocks',actions:[step('full'),scenario('right-wall'),inp('right',4),inp('left'),inp('right'),inp('right'),scenario('left-wall'),inp('left',4),inp('right'),scenario('occupied'),inp('down'),inp('down'),inp('down'),inp('down'),inp('rotate'),inp('left'),inp('down'),inp('drop'),scenario('empty'),...testMoves]},
 {id:'18',mode:'blocks',actions:[source('rotation'),step('run'),step('full'),scenario('empty'),inp('rotate',3),inp('rotate',3),inp('rotate',3),inp('rotate',3),scenario('right-wall'),inp('rotate'),inp('right'),inp('rotate'),scenario('occupied'),inp('down'),inp('rotate'),inp('down'),inp('rotate'),inp('drop'),...testMoves]},
 {id:'19',mode:'blocks',actions:[step('full'),scenario('one-row'),inp('down'),inp('down'),inp('drop',4),scenario('two-rows'),inp('down'),inp('down'),inp('drop',4),scenario('separate'),inp('down'),inp('drop',4),scenario('empty'),...testMoves,...testMoves]},
 cpp('21','tail',4),
 {id:'23',mode:'blocks',actions:[step('blank',null,3),step('type',catalog.js.clear,4),step('run'),step('full'),scenario('one-row'),inp('drop',4),scenario('two-rows'),inp('down'),inp('drop',4),scenario('separate'),inp('drop',4),scenario('empty'),...testMoves]},
 {id:'25',mode:'blocks',actions:[source('buggy',4),step('run'),scenario('right-wall'),inp('right',4),scenario('right-wall'),step('debug',null,3),inp('right'),step('step',null,4),step('step',null,4),step('step',null,4),scenario('left-wall'),inp('left'),step('step',null,3),step('step',null,3),step('step',null,4),step('debug'),source('movement',5)]},
 {id:'26',mode:'blocks',actions:[source('buggy'),step('blank',null,2),step('type',catalog.js.movement,3),step('run'),scenario('right-wall'),step('debug'),inp('right'),step('step',null,4),step('step',null,4),step('debug'),step('full'),scenario('right-wall'),inp('right'),inp('left'),scenario('empty'),inp('right'),inp('left'),scenario('left-wall'),inp('left'),inp('right'),inp('rotate'),inp('down'),inp('drop')]},
 {id:'28',mode:'blocks',actions:[source('clear',5),step('blank',null,3),step('type',catalog.js.clear,3),step('run'),step('full'),scenario('two-rows'),inp('down'),inp('drop',4),scenario('separate'),inp('down'),inp('drop',4),scenario('one-row'),inp('drop',4),scenario('empty'),...testMoves]},
 {id:'30',mode:'blocks',actions:[source('tests',5),step('run',null,5),source('movement',4),step('run'),step('full'),scenario('empty'),...testMoves,scenario('right-wall'),inp('right'),inp('rotate'),scenario('two-rows'),inp('drop',4),scenario('empty'),...testMoves]},
 {id:'32',mode:'breakout',actions:[step('blank',null,2),step('type',catalog.js.breakout,3),step('run'),step('full'),scenario('paddle-center',6),inp('left'),inp('right'),scenario('paddle-edge',6),inp('left'),inp('right'),inp('right'),inp('left'),scenario('paddle-center',6),inp('left'),inp('left'),scenario('paddle-edge',6)]},
 {id:'34',mode:'cpp',actions:[step('blank',null,3),step('type',catalog.cpp.node,3),step('run'),step('step',null,4),step('step',null,4),step('blank',null,3),step('type',catalog.cpp.pair,2),step('run'),step('step',null,3),step('step',null,3),step('step',null,3),step('step',null,3),step('step',null,3)]}
];
const existing=fs.existsSync(reportPath)?JSON.parse(fs.readFileSync(reportPath,'utf8')):null;
if(existing?.status==='running')try{process.kill(existing.pid,0);throw Error('Existing capture process is alive');}catch(e){if(e.code!=='ESRCH')throw e;}
const report={...existing,pid:process.pid,status:'running',updatedAt:new Date().toISOString(),inputs,method:'Actual UI edits/clicks, MSVC process and local JS game execution; wall-clock screencast timestamps; no loops/speed changes; owned educational reconstruction disclosed.',takes:existing?.takes||[]};
const save=()=>{report.updatedAt=new Date().toISOString();fs.writeFileSync(reportPath,JSON.stringify(report,null,2)+'\n');};
async function capture(take){const old=report.takes.find(t=>t.id===take.id&&t.status==='finished'&&(t.revision||'actual-v1')===revision);if(old){assert.deepEqual(old.inputs,inputs);assert.equal(digest(path.join(root,old.path)),old.sha256);console.log('Verified existing '+take.id);return;}
 const out=path.join(base,'scene-'+take.id+'.mp4'),framesDir=path.join(base,'frames-'+take.id+'-attempt'+(1+report.takes.filter(t=>t.id===take.id).length));assert(!fs.existsSync(out),'Preserve prior partial file');fs.mkdirSync(framesDir,{recursive:true});fs.writeFileSync(path.join(framesDir,'.gitignore'),'*\n');
 const browser=await puppeteer.launch({headless:true,args:['--disable-gpu','--disable-accelerated-2d-canvas'],protocolTimeout:120000});
 const record={id:take.id,revision,status:'recording',inputs,path:path.relative(root,out).replaceAll('\\','/'),actions:[],errors:[]};report.takes.push(record);save();
 try{const page=await browser.newPage();await page.setViewport({width:1920,height:1080});page.on('pageerror',e=>record.errors.push(String(e)));await page.goto('http://127.0.0.1:9341');await page.waitForFunction(()=>window.workbench);if(take.mode!=='cpp')await page.click(`[data-mode="${take.mode}"]`);await page.evaluate(()=>document.fonts.ready);
 const cdp=await page.createCDPSession(),frames=[];cdp.on('Page.screencastFrame',e=>{const name=String(frames.length).padStart(6,'0')+'.jpg';fs.writeFileSync(path.join(framesDir,name),Buffer.from(e.data,'base64'));frames.push({file:name,timestamp:e.metadata.timestamp});cdp.send('Page.screencastFrameAck',{sessionId:e.sessionId}).catch(()=>{});});
 await cdp.send('Page.startScreencast',{format:'jpeg',quality:93,maxWidth:1920,maxHeight:1080,everyNthFrame:2});const began=Date.now();
 for(const [i,s]of take.actions.entries()){const at=(Date.now()-began)/1000;
  if(s.action==='source')await page.select('#lesson',s.arg);
  else if(s.action==='type'){await page.click('#editor');await page.keyboard.down('Control');await page.keyboard.press('A');await page.keyboard.up('Control');await page.type('#editor',s.arg,{delay:18});await page.evaluate(()=>document.querySelector('#editor').scrollTop=0);}
  else if(s.action==='scroll')await page.$eval('#editor',(e,y)=>e.scrollTop=y,s.arg);
  else if(s.action==='input')await page.click(`[data-input="${s.arg}"]`);
  else if(s.action==='scenario')await page.click(`[data-scenario="${s.arg}"]`);
  else if(s.action==='full')await page.click(await page.evaluate(()=>document.body.classList.contains('full'))?'#return-editor':'#view-toggle');
  else await page.click('#'+s.action);
  await delay(s.hold*1000);record.actions.push({index:i,...s,at,after:(Date.now()-began)/1000,state:await page.evaluate(()=>({status:document.querySelector('#status').textContent,mode:workbench.getMode(),game:workbench.getGame(),latest:window.audit.slice(-4)}))});save();
 }
 await cdp.send('Page.stopScreencast');const captureWallSeconds=(Date.now()-began)/1000;await page.screenshot({path:path.join(__dirname,'capture-'+take.id+'-last.png')});record.executionAudit=await page.evaluate(()=>window.audit);record.captureWallSeconds=captureWallSeconds;assert.deepEqual(record.errors,[]);
 const valid=[...new Map(frames.filter(f=>Number.isFinite(f.timestamp)&&f.timestamp>0).map(f=>[f.timestamp,f])).values()].sort((a,b)=>a.timestamp-b.timestamp);assert(valid.length>=(take.mode==='cpp'?8:15));const elapsed=valid.at(-1).timestamp-valid[0].timestamp;
 fs.writeFileSync(path.join(framesDir,'timestamps.json'),JSON.stringify(valid));const concat=['ffconcat version 1.0'];for(let i=0;i<valid.length-1;i++)concat.push(`file '${valid[i].file}'`,`duration ${(valid[i+1].timestamp-valid[i].timestamp).toFixed(9)}`);concat.push(`file '${valid.at(-1).file}'`);fs.writeFileSync(path.join(framesDir,'capture.ffconcat'),concat.join('\n'));
 record.status='encoding';save();record.encoding=require('./encode-capture.cjs')(valid,framesDir,out);
 const p=spawnSync('ffprobe',['-v','error','-show_entries','format=duration','-of','json',out],{encoding:'utf8',windowsHide:true});const seconds=+JSON.parse(p.stdout).format.duration;assert(Math.abs(seconds-elapsed)<.1);Object.assign(record,{status:'finished',seconds,sourceInterval:[0,seconds],sha256:digest(out),frameCount:valid.length,wallClockSeconds:elapsed,finishedAt:new Date().toISOString(),cutReview:'pending'});save();console.log(`scene ${take.id}: ${seconds.toFixed(2)}s actual capture, ${valid.length} frames`);
 }catch(e){record.status='failed';record.error=String(e);save();throw e;}finally{await browser.close();}}
(async()=>{save();const ids=process.argv.slice(2);for(const t of takes.filter(t=>!ids.length||ids.includes(t.id)))await capture(t);report.status='finished';save();console.log('Selected recordings finished. Exact final intervals still require narration timing and QA.');})().catch(e=>{report.status='failed';report.error=String(e);save();console.error(e);process.exitCode=1;});
