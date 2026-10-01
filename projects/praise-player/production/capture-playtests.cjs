const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawn}=require('node:child_process');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),version=process.argv.includes('--v2')?'v2':'v1',dest=path.join(root,'shared/assets/praise-player/playtests-'+version);
const common=[['Space',3.78,4.05],['Space',9.78,10.05],['Space',15.78,16.05],['Space',21.78,22.05],['Space',27.78,28.05]];
const schedules={timing:common,specificity:[...common.filter(x=>x[1]!==9.78),['ArrowUp',8.95,9.65],['ArrowDown',10.45,11.15]],strength:common,honesty:common.filter(x=>x[1]!==15.78),placement:common};
async function capture(mode){const output=path.join(dest,mode+'.mp4');if(fs.existsSync(output))throw Error('Preserve existing capture '+output);const browser=await puppeteer.launch({headless:true});
try{const page=await browser.newPage();await page.setViewport({width:1920,height:1080});await page.goto('file:///'+path.join(__dirname,'prototype/index.html').replaceAll('\\','/')+'?mode='+mode);await page.evaluate(()=>document.fonts.ready);
const ff=spawn('ffmpeg',['-v','error','-n','-f','image2pipe','-framerate','60','-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','90000',output],{windowsHide:true,stdio:['pipe','ignore','pipe']});let err='';ff.stderr.on('data',s=>err+=s);const done=new Promise((r,j)=>ff.on('exit',v=>v===0?r():j(Error(err))));const down=new Set(),schedule=schedules[mode],frames=1920;
for(let frame=0;frame<frames;frame++){const t=frame/60;await page.evaluate(t=>window.captureStep(t),t);for(const code of ['Space','ArrowUp','ArrowDown']){const active=schedule.some(([k,a,b])=>k===code&&t>=a&&t<b);if(down.has(code)!==active){await page.keyboard[active?'down':'up'](code==='Space'?' ':code);active?down.add(code):down.delete(code);}}
 const jpg=await page.evaluate(t=>{window.captureStep(t);return document.querySelector('canvas').toDataURL('image/jpeg',.93).split(',')[1];},t);if(!ff.stdin.write(Buffer.from(jpg,'base64')))await new Promise(r=>ff.stdin.once('drain',r));
 if([250,650,950,1700].includes(frame))fs.writeFileSync(path.join(__dirname,`prototype-${mode}-${frame}.jpg`),Buffer.from(jpg,'base64'));if(frame%600===0)console.log(mode,frame+'/'+frames);
}
const evidence=await page.evaluate(()=>({input:window.inputLog,sounds:window.soundLog,outcomes:window.outcomeLog,finalState:window.testState()}));ff.stdin.end();await done;
const [a,b]=evidence.finalState;assert.deepEqual({...a,panel:0},{...b,panel:0,events:b.events.map(e=>({...e,panel:0}))},'Paired game state must remain identical');
assert.equal(a.events.length,5);assert(evidence.input.some(v=>v.code==='Space'&&v.down));
if(mode==='specificity'){assert(a.events.some(e=>e.kind==='dodge'));assert(a.events.some(e=>e.kind==='block'));assert(evidence.outcomes.some(e=>e.kind==='feedback'&&e.panel===1&&e.text==='회피 성공'));}
if(mode==='honesty'){assert.equal(a.hp,2);assert.equal(a.success,4);assert(evidence.outcomes.some(e=>e.kind==='feedback'&&e.panel===1&&e.text==='피격 · 다시 준비'));}
else assert.equal(a.hp,3);
if(mode==='timing'){for(const p of [0,1])assert(evidence.outcomes.filter(e=>e.kind==='feedback'&&e.panel===p).every(e=>Math.abs(e.delay-(p?2.4:.15))<.04));}
if(mode==='strength')assert(evidence.outcomes.some(e=>e.kind==='feedback'&&e.panel===1&&e.text==='연속 방어 3회!'));
fs.writeFileSync(path.join(__dirname,mode+'-'+version+'-input-log.json'),JSON.stringify({kind:'original-keyboard-projectile-collision-comparison',fps:60,seconds:32,mode,assertions:'passed equal paired state and mode-specific actual outcomes',humanEnjoyment:'not-tested',...evidence},null,2)+'\n');console.log(mode+' assertions passed');
}finally{await browser.close();}}
(async()=>{fs.mkdirSync(dest,{recursive:true});const selected=process.argv[2];for(const mode of selected?[selected]:Object.keys(schedules))await capture(mode);})().catch(e=>{console.error(e);process.exitCode=1;});
