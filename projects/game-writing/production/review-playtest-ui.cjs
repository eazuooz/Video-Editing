// Own local code artifact only: real UI clicks and resulting visible story lines.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url'),puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const dest=path.join(__dirname,'playtest-ui-proof');fs.mkdirSync(dest,{recursive:true});
const cases=[
 {id:'knowledge',actions:['start-skip','close','talk-guard','close','read-note','close','talk-guard','share-rule','close','talk-guard'],last:'guard.rule-shared'},
 {id:'absent-owner',actions:['start-skip','close','take-seal','close','give-companion','close','rest-companion','close','talk-guard'],last:'guard.first'},
 {id:'recovery',actions:['start-skip','close','take-seal','close','give-companion','close','rest-companion','close','recover-seal','close','talk-guard','present-seal','enter-harbor'],last:'harbor.arrived'},
 {id:'feed-route',actions:['start-read','close','road','feed','close','take-seal','close','talk-guard','present-seal','enter-harbor'],last:'harbor.arrived'},
 {id:'detour-route',actions:['start-skip','close','road','detour','close','take-seal','close','talk-guard','present-seal','enter-harbor'],last:'harbor.arrived'},
 {id:'intro-known',actions:['start-read','close','talk-guard','confirm-known-rule','close','talk-guard'],last:'guard.rule-shared'}
];
(async()=>{
 const browser=await puppeteer.launch({headless:true,args:['--disable-gpu'],protocolTimeout:120000});
 try{
 const page=await browser.newPage();await page.setViewport({width:1920,height:1080,deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 const proof=[];
 for(const test of cases){
  await page.goto(pathToFileURL(path.resolve(__dirname,'../playtest/index.html')).href);
  for(let i=0;i<test.actions.length;i++){
   const action=test.actions[i],selector=action.startsWith('start-')?`#${action}`:`[data-action="${action}"]`;
   await page.waitForSelector(selector,{visible:true});
   const before=await page.evaluate(()=>harborState.events.length);await page.click(selector);
   await page.waitForFunction(n=>harborState.events.length>n,{},before);
   const state=await page.evaluate(()=>harborState);assert.equal(state.events.at(-1).accepted,true);
   const file=`${test.id}-${String(i+1).padStart(2,'0')}-${action}.png`;
   if(i===0||i===test.actions.length-1||['talk-guard','share-rule','give-companion','rest-companion','recover-seal','feed','detour','present-seal'].includes(action))await page.screenshot({path:path.join(dest,file)});
   proof.push({case:test.id,action,event:state.events.at(-1),visibleLine:state.dialogue?.text||null,choices:state.dialogue?.choices||[],screenshot:fs.existsSync(path.join(dest,file))?`projects/game-writing/production/playtest-ui-proof/${file}`:null});
  }
  const state=await page.evaluate(()=>harborState);assert.equal(state.lastLineId,test.last);
  if(test.id==='absent-owner')assert(!state.dialogue.choices.some(c=>c[0]==='present-seal'));
  if(test.id==='feed-route')assert.equal(state.rations,0);
  if(test.id==='detour-route')assert.equal(state.minutes,3);
 }
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(__dirname,'playtest-ui-proof.json'),JSON.stringify({generatedAt:new Date().toISOString(),passed:true,kind:'Own local UI input/state proof; human narrative quality review and final footage review pending',cases:cases.length,actions:proof.length,pageErrors:errors,proof},null,2)+'\n');
 console.log(JSON.stringify({passed:true,cases:cases.length,actions:proof.length,pageErrors:errors.length}));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
