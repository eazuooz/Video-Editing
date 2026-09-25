// Exact channel-caption artwork from LectureCaption's canvas draw routine.
// Reuse the clean Motion Canvas master: do not render the same 88 slide images twice.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..');
const base=path.join(root,'projects/renderformer-explained/production/body-review');
const timing=JSON.parse(fs.readFileSync(path.join(base,'timing.json'),'utf8'));
const dir=path.join(base,'caption-overlays');fs.mkdirSync(dir,{recursive:true});
const source=fs.readFileSync(path.join(root,'motion-canvas/src/projects/renderformer-explained/preview/caption.ts'),'utf8');
const routine=source.slice(source.indexOf('    c.save();'),source.indexOf('this.drawChildren(c);'))
 .replace('const lines:string[]=[]','const lines=[]');
if(!routine.includes('c.restore();')||!routine.includes('1540'))throw Error('Caption drawing routine changed: inspect before proceeding.');
const run=(cmd,args)=>{const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||r.error);return r.stdout;};
const probe=f=>JSON.parse(run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',f]));
const outputName=process.argv.find(a=>a.startsWith('--output-name='))?.slice('--output-name='.length)??'renderformer-captioned-review.mp4';
if(path.basename(outputName)!==outputName||!outputName.endsWith('.mp4'))throw Error('Output must be an MP4 filename in body-review.');
const clean=path.join(base,'renderformer-clean-review.mp4'),output=path.join(base,outputName);
const preparing=process.argv.includes('--prepare-only');
(async()=>{
 if(!preparing&&fs.existsSync(output))throw Error('Existing captioned master preserved.');
 const browser=await puppeteer.launch({headless:true});
 const segments=[],layout=[];let cursor=0,index=0;
 try{
  const page=await browser.newPage();await page.goto('http://127.0.0.1:9210/render-worker.html');
  await page.evaluate(()=>document.fonts.ready);
  async function png(name,text){
   const result=await page.evaluate(({routine,text})=>{
    const canvas=document.createElement('canvas');canvas.width=1920;canvas.height=240;
    const c=canvas.getContext('2d');c.translate(960,100);
    if(text)new Function('c','text',routine)(c,text);
    c.font="500 44px 'Noto Sans KR', 'Malgun Gothic', sans-serif";
    let lines=[],line='';for(const word of text.split(/\s+/)){const n=line?line+' '+word:word;
      if(line&&c.measureText(n).width>1540){lines.push(line);line=word;}else line=n;}
    if(line)lines.push(line);
    return {data:canvas.toDataURL('image/png').split(',')[1],lines,width:Math.ceil(Math.max(0,...lines.map(l=>c.measureText(l).width)))+44};
   },{routine,text});
   if(result.lines.length>2||result.width>1700)throw Error('Caption overflow: '+text);
   fs.writeFileSync(path.join(dir,name),Buffer.from(result.data,'base64'));return result;
  }
  await png('blank.png','');
  for(const scene of timing.scenes){
   for(const cue of scene.cues){
    // slide.tsx maps local tween time through (frames-.5)/60 to data.duration.
    const factor=(scene.frames-.5)/scene.duration;
    const start=scene.firstFrame+Math.ceil(cue.start*factor-1e-8);
    const end=scene.firstFrame+Math.ceil(cue.end*factor-1e-8);
    if(start<cursor||end<=start)throw Error('Overlapping/empty caption interval');
    if(start>cursor)segments.push({file:'blank.png',frames:start-cursor});
    const name=`cue-${String(++index).padStart(4,'0')}.png`;
    const details=await png(name,cue.ko);
    segments.push({file:name,frames:end-start});cursor=end;
    layout.push({page:scene.sourcePage,index,startFrame:start,endFrame:end,lines:details.lines,width:details.width});
   }
  }
 }finally{await browser.close();}
 if(cursor<timing.totalFrames)segments.push({file:'blank.png',frames:timing.totalFrames-cursor});
 if(segments.reduce((n,s)=>n+s.frames,0)!==timing.totalFrames)throw Error('Overlay duration mismatch');
 const list=path.join(dir,'captions.ffconcat');
 fs.writeFileSync(list,'ffconcat version 1.0\n'+segments.map(s=>`file '${s.file}'\noption framerate 60\nduration ${(s.frames/60).toFixed(9)}`).join('\n')+"\nfile 'blank.png'\noption framerate 60\n");
 fs.writeFileSync(path.join(dir,'layout.json'),JSON.stringify({sourceSHA256:crypto.createHash('sha256').update(source).digest('hex'),fps:60,totalFrames:timing.totalFrames,stripY:840,centerY:940,layout},null,2));
 console.log('Prepared identical canvas captions:',layout.length);
 if(preparing)return;
 const p=probe(clean),v=p.streams.find(s=>s.codec_type==='video');
 if(+v.nb_frames!==timing.totalFrames)throw Error('Clean master is not ready');
 run('ffmpeg',['-v','error','-n','-i',clean,'-f','concat','-safe','0','-i',list,
  '-filter_complex','[0:v][1:v]overlay=x=0:y=840:format=auto:shortest=1,format=yuv420p[v]',
  '-map','[v]','-map','0:a:0','-c:v','h264_nvenc','-preset','p5','-cq','18','-b:v','0',
  '-r','60','-frames:v',String(timing.totalFrames),'-c:a','copy','-movflags','+faststart',output]);
 const q=probe(output),ov=q.streams.find(s=>s.codec_type==='video');
 if(+ov.nb_frames!==timing.totalFrames||Math.abs(+q.format.duration-timing.duration)>.08)throw Error('Captioned master duration mismatch');
 run('ffmpeg',['-v','error','-i',output,'-f','null','-']);
 fs.writeFileSync(path.join(base,'caption-composition.json'),JSON.stringify({method:'original-canvas-routine-transparent-overlays',output:outputName,timingSHA256:crypto.createHash('sha256').update(JSON.stringify(timing)).digest('hex'),captionNotationRevision:timing.captionNotationRevision??null,cues:layout.length,totalFrames:timing.totalFrames,fullDecodePassed:true,audio:'copied-from-clean-master',publishReady:false},null,2));
 console.log(output);
})().catch(e=>{console.error(e);process.exitCode=1;});
