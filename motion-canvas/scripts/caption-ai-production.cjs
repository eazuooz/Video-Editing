// Render the exact editable CaptionBox canvas routine at the fixed channel position.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),slug='ai-game-development-human-craft';
const base=path.join(root,'shared/output',slug),dir=path.join(base,'caption-overlays');fs.mkdirSync(dir,{recursive:true});
const m=JSON.parse(fs.readFileSync(path.join(root,'projects',slug,'project.json'),'utf8'));
const data=JSON.parse(fs.readFileSync(path.join(root,'motion-canvas/src/projects',slug,'scene-data.json'),'utf8'));
if(data.captionTimingStatus!=='asr-aligned')throw Error('Aligned captions required');
const totalFrames=120+data.scenes.reduce((n,s)=>n+Math.round(s.duration*60),0)+600;
const source=fs.readFileSync(path.join(root,'motion-canvas/src/projects/game-dev-career/preview/caption-box.ts'),'utf8');
const routine=source.slice(source.indexOf('    c.save();'),source.indexOf('this.drawChildren(c);')).replace('const lines:string[]=[]','const lines=[]');
if(!routine.includes('1570')||!routine.includes('48px')||!routine.includes('c.restore();'))throw Error('Inspect changed caption routine');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;};
const sec=s=>{const [h,m,v]=s.replace(',','.').split(':');return +h*3600+ +m*60+ +v;};
const srtTime=t=>{const n=Math.round(t*1000);return `${String(Math.floor(n/3600000)).padStart(2,'0')}:${String(Math.floor(n/60000)%60).padStart(2,'0')}:${String(Math.floor(n/1000)%60).padStart(2,'0')},${String(n%1000).padStart(3,'0')}`;};
async function main(){
 const captions={};for(const lang of ['ko','en']){
  const p=path.join(root,m.tts.outputDir,m.tts.filenameStem+(lang==='en'?'.en':'')+'.srt');
  captions[lang]=fs.readFileSync(p,'utf8').trim().split(/\r?\n\s*\r?\n/).map(block=>{const [id,time,...lines]=block.split(/\r?\n/);const [a,b]=time.split(' --> ');return {id:+id,start:sec(a)+2,end:sec(b)+2,text:lines.join('\n')};});
  fs.writeFileSync(path.join(base,`final.${lang}.srt`),captions[lang].map(c=>`${c.id}\n${srtTime(c.start)} --> ${srtTime(c.end)}\n${c.text}`).join('\n\n')+'\n');
 }
 if(JSON.stringify(captions.ko.map(c=>[c.start,c.end]))!==JSON.stringify(captions.en.map(c=>[c.start,c.end])))throw Error('Bilingual times differ');
 const existing=path.join(dir,'layout.json');
 if(fs.existsSync(existing)){
  const r=JSON.parse(fs.readFileSync(existing,'utf8'));
  if(r.routineSha256===sha(source)&&r.sceneDataSha256===sha(JSON.stringify(data))&&r.captionsSha256===sha(JSON.stringify(captions.ko))){
   console.log('Reusing identical measured caption overlays.');
   if(process.argv.includes('--burn'))burn(path.join(dir,'captions.ffconcat'));
   return;
  }
 }
 const browser=await puppeteer.launch({headless:true});let cursor=0;const segments=[],layout=[];
 try{
  const page=await browser.newPage();await page.goto('http://127.0.0.1:9199/ai-production.html?scene=01',{waitUntil:'domcontentloaded'});await page.waitForFunction(()=>window.sampleReview?.ready);
  await page.evaluate(()=>document.fonts.load("500 48px 'Noto Sans KR'"));
  async function png(name,text){
   const r=await page.evaluate(({routine,text})=>{const c=document.createElement('canvas');c.width=1920;c.height=240;const x=c.getContext('2d');x.translate(960,100);if(text)new Function('c','text',routine)(x,text);
    x.font="500 48px 'Noto Sans KR', 'Malgun Gothic', sans-serif";let lines=[],line='';for(const w of text.split(/\s+/)){const next=line?line+' '+w:w;if(line&&x.measureText(next).width>1570){lines.push(line);line=w;}else line=next;}if(line)lines.push(line);
    return {data:c.toDataURL('image/png').split(',')[1],lines,width:Math.ceil(Math.max(0,...lines.map(l=>x.measureText(l).width)))+44};},{routine,text});
   if(r.lines.length>2||r.width>1614)throw Error('Caption overflow '+name);
   fs.writeFileSync(path.join(dir,name),Buffer.from(r.data,'base64'));return r;
  }
  await png('blank.png','');
  for(const c of captions.ko){
   const a=Math.ceil(c.start*60-1e-7),b=Math.ceil(c.end*60-1e-7);if(a<cursor||b<=a)throw Error('Caption interval conflict '+c.id);
   if(a>cursor)segments.push({file:'blank.png',frames:a-cursor});
   const file=`cue-${String(c.id).padStart(4,'0')}.png`,r=await png(file,c.text);
   segments.push({file,frames:b-a});cursor=b;layout.push({cue:c.id,startFrame:a,endFrame:b,lines:r.lines,width:r.width,height:r.lines.length*62+22});
  }
 }finally{await browser.close();}
 if(cursor>totalFrames-600)throw Error('Captions overlap silent member ending');
 if(cursor<totalFrames)segments.push({file:'blank.png',frames:totalFrames-cursor});
 const list=path.join(dir,'captions.ffconcat');fs.writeFileSync(list,'ffconcat version 1.0\n'+segments.map(s=>`file '${s.file}'\noption framerate 60\nduration ${(s.frames/60).toFixed(9)}`).join('\n')+"\nfile 'blank.png'\noption framerate 60\n");
 fs.writeFileSync(path.join(dir,'layout.json'),JSON.stringify({routineSha256:sha(source),sceneDataSha256:sha(JSON.stringify(data)),captionsSha256:sha(JSON.stringify(captions.ko)),fps:60,totalFrames,stripY:870,centerY:970,font:'Noto Sans KR 500',fontSize:48,layout,pixelReview:'pending'},null,2)+'\n');
 console.log(`Prepared ${layout.length} exact caption overlays for ${totalFrames} frames.`);
 if(!process.argv.includes('--burn'))return;
 burn(list);
}
function burn(list){
 const control=JSON.parse(fs.readFileSync(path.join(root,'shared/publishing/video-production-control.json'),'utf8').replace(/^\uFEFF/,''));
 if(control.selectedVideo!==slug)throw Error('Selected production changed');
 const clean=path.join(root,m.paths.videoClean),target=path.join(root,m.paths.videoBurnedCaptions);
 if(fs.existsSync(target))throw Error('Preserve existing captioned master; explicitly version revisions');
 run('ffmpeg',['-v','error','-n','-i',clean,'-f','concat','-safe','0','-i',list,'-filter_complex','[0:v][1:v]overlay=x=0:y=870:format=auto:shortest=1,format=yuv420p[v]','-map','[v]','-map','0:a:0','-c:v','h264_nvenc','-preset','p5','-cq','18','-b:v','0','-r','60','-frames:v',String(totalFrames),'-c:a','copy','-movflags','+faststart',target]);
 console.log(target);
}
main().catch(e=>{console.error(e);process.exitCode=1;});
