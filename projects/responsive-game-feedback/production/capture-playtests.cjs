const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawn}=require('node:child_process');
const puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),slug='responsive-game-feedback',version=process.argv.includes('--v4')?'v4':process.argv.includes('--v3')?'v3':process.argv.includes('--v2')?'v2':'v1',dest=path.join(root,`shared/assets/${slug}/playtests-${version}`);
const schedules={
 receipt:[['Space',3,3.2],['Space',7,7.2],['ArrowRight',12,15],['KeyE',16,16.2],['ArrowLeft',17,19],['Space',21,21.2],['Space',27,27.2]],
 blocked:[['Space',3,3.2],['Space',7,7.2],['ArrowRight',10,10.2],['Space',12,12.2],['KeyE',16,16.2],['Space',19,19.2],['ArrowRight',23,23.2],['Space',25,25.2]],
 menu:[['Space',3,3.2],['Escape',7,7.2],['ArrowDown',10,10.2],['Space',12,12.2],['Escape',16,16.2],['Enter',19,19.2],['Escape',23,23.2],['ArrowUp',25,25.2],['Enter',27,27.2]],
 cutscene:[['Space',3,3.15],['Space',8,8.5],['Space',15,16.7],['KeyR',20,20.2],['Space',25,26.4]],
 pending:[['Space',3,3.2],['Space',4,4.2],['Space',6,6.2],['Space',11,11.2],['Space',12,12.2],['Space',20,20.2],['Space',21,21.2]],
 context:[['KeyQ',3,3.2],['KeyZ',5,5.2],['Space',8,8.2],['Escape',12,12.2],['KeyQ',14,14.2],['Space',17,17.2],['KeyZ',21,21.2],['Space',24,24.2],['Escape',28,28.2]]
};
if(version==='v2')schedules.pending=[['Space',4,4.2],['Space',5,5.2],['Space',9,9.2],['Space',12,12.2],['Space',16,16.2]];
const buttons={Space:' ',ArrowRight:'ArrowRight',ArrowLeft:'ArrowLeft',ArrowUp:'ArrowUp',ArrowDown:'ArrowDown',KeyE:'e',KeyR:'r',KeyQ:'q',KeyZ:'z',Enter:'Enter',Escape:'Escape'};
function verify(mode,evidence){const events=evidence.outcomes,by=(p,k)=>events.filter(e=>e.panel===p&&e.kind===k),a=evidence.finalState[0],b=evidence.finalState[1];assert(evidence.input.some(e=>e.down));
 if(mode==='receipt'){assert.equal(by(0,'blocked').length,2);assert.equal(by(1,'blocked').length,2);assert(a.open&&b.open&&a.hasKey&&b.hasKey);assert(by(1,'feedback').some(e=>e.reason==='blocked'));assert(!by(0,'feedback').some(e=>e.reason==='blocked'));}
 if(mode==='blocked'){for(const p of [0,1]){assert(by(p,'blocked').some(e=>e.reason==='occupied'));assert(by(p,'blocked').some(e=>e.reason==='materials'));assert.equal(by(p,'built').length,1);}assert.equal(a.wood,b.wood);assert.deepEqual(a.buildings,b.buildings);if(version==='v4')assert.equal(by(0,'color-only-refusal').length,by(0,'blocked').length);}
 if(mode==='menu'){assert(by(1,'confirmed').some(e=>e.code==='Space'));assert(!by(0,'confirmed').some(e=>e.code==='Space'));assert(by(0,'confirmed').some(e=>e.code==='Enter'));assert(by(1,'confirmed').some(e=>e.code==='Enter'));}
 if(mode==='cutscene'){for(const p of [0,1]){assert.equal(by(p,'skipped').length,2);assert(by(p,'skipped').every(e=>e.heldSeconds>=1.2));assert.equal(by(p,'cancel-confirmation').length,2);}assert(by(1,'feedback').some(e=>e.text.includes('길게')));}
 if(mode==='pending'){const delay=version==='v2'?13:4,count=version==='v2'?1:3;for(const p of [0,1]){assert.equal(by(p,'save-request').length,count);assert.equal(by(p,'save-complete').length,count);assert.equal(by(p,'ignored-duplicate').length,4);for(const e of by(p,'save-complete'))assert(e.t>=by(p,'save-request').find(r=>Math.abs(e.t-r.t-delay)<.03).t+delay);}assert.equal(a.saves,b.saves);}
 if(mode==='context'){assert(by(0,'unassigned').length===4);assert(by(1,'unassigned').length===4);assert(by(0,'feedback').some(e=>e.text.includes('이 키')));assert(!by(1,'feedback').some(e=>e.text.includes('이 키')));assert(by(1,'feedback').some(e=>e.text==='계속하기'));assert(by(1,'blocked').some(e=>e.reason==='out-of-range'));}
}
async function capture(mode){const output=path.join(dest,mode+'.mp4');if(fs.existsSync(output))throw Error('Preserve existing recording; choose a new version: '+output);const browser=await puppeteer.launch({headless:true});
try{const page=await browser.newPage();await page.setViewport({width:1920,height:1080});await page.goto('file:///'+path.join(__dirname,'prototype/index.html').replaceAll('\\','/')+'?mode='+mode+(mode==='pending'&&version==='v2'?'&pendingSeconds=13':''));await page.evaluate(()=>document.fonts.ready);
const ff=spawn('ffmpeg',['-v','error','-n','-f','image2pipe','-framerate','60','-vcodec','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','90000',output],{windowsHide:true,stdio:['pipe','ignore','pipe']});let err='';ff.stderr.on('data',s=>err+=s);const done=new Promise((r,j)=>ff.on('exit',v=>v===0?r():j(Error(err))));const down=new Set(),schedule=schedules[mode],frames=1920;
for(let frame=0;frame<frames;frame++){const t=frame/60;await page.evaluate(t=>window.captureStep(t),t);for(const code of Object.keys(buttons)){const active=schedule.some(([k,a,b])=>k===code&&t>=a&&t<b);if(down.has(code)!==active){await page.keyboard[active?'down':'up'](buttons[code]);active?down.add(code):down.delete(code);}}
 const jpg=await page.evaluate(t=>{window.captureStep(t);return document.querySelector('canvas').toDataURL('image/jpeg',.93).split(',')[1];},t);if(!ff.stdin.write(Buffer.from(jpg,'base64')))await new Promise(r=>ff.stdin.once('drain',r));
 if([250,650,950,1700].includes(frame))fs.writeFileSync(path.join(__dirname,`prototype-${mode}-${frame}.jpg`),Buffer.from(jpg,'base64'));if(frame%600===0)console.log(mode,frame+'/'+frames);
}
const evidence=await page.evaluate(()=>({input:window.inputLog,sounds:window.soundLog,outcomes:window.outcomeLog,finalState:window.testState()}));ff.stdin.end();await done;verify(mode,evidence);
fs.writeFileSync(path.join(__dirname,mode+'-'+version+'-input-log.json'),JSON.stringify({kind:'original-browser-keyboard-state-transition-test',fps:60,seconds:32,mode,assertions:'passed actual input and mode-specific state transitions',humanUsability:'not-tested',...evidence},null,2)+'\n');console.log(mode+' assertions passed');
}finally{await browser.close();}}
(async()=>{fs.mkdirSync(dest,{recursive:true});const selected=process.argv[2];for(const mode of selected?[selected]:Object.keys(schedules))await capture(mode);})().catch(e=>{console.error(e);process.exitCode=1;});
