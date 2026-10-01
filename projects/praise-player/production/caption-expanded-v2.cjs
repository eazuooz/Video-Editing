const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v2'),m=JSON.parse(fs.readFileSync(path.join(work,'project-draft.json'),'utf8'));
function run(cmd,args){const r=spawnSync(cmd,args,{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const sec=t=>{const [h,min,s]=t.split(':');return +h*3600+ +min*60+ +s.replace(',','.');};
const time=(t,ass=false)=>{const n=Math.round(t*(ass?100:1000)),base=ass?100:1000;return `${String(Math.floor(n/(base*3600))).padStart(ass?1:2,'0')}:${String(Math.floor(n/(base*60))%60).padStart(2,'0')}:${String(Math.floor(n/base)%60).padStart(2,'0')}${ass?'.':','}${String(n%base).padStart(ass?2:3,'0')}`;};
(async()=>{
 const plan=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8')),cuts=plan.scenes.flatMap(s=>s.cuts),ko=path.join(root,m.paths.captionsKo);
 const cues=fs.readFileSync(ko,'utf8').trim().split(/\r?\n\s*\r?\n/).map(b=>{const [id,t,...lines]=b.split(/\r?\n/),[a,z]=t.split(' --> ');return {id:+id,start:sec(a),end:sec(z),lines};});
 const browser=await puppeteer.launch({headless:true});let layouts;
 try{const page=await browser.newPage();layouts=await page.evaluate(cues=>{
  const c=document.createElement('canvas').getContext('2d');
  return cues.map(cue=>{
   const text=cue.lines.join(' '),words=text.split(/\s+/),measure=s=>c.measureText(s).width,max=cue.maxWidth??1570;
   for(const size of [48,46,44,42]){
    c.font=`${size}px 'Malgun Gothic'`;let lines=[text];
    if(measure(text)>Math.min(1100,max)){let best=Infinity;for(let i=1;i<words.length;i++){const pair=[words.slice(0,i).join(' '),words.slice(i).join(' ')],w=pair.map(measure);if(Math.max(...w)>max)continue;const cost=Math.abs(w[0]-w[1])-(pair[0].endsWith(',')?80:0);if(cost<best){best=cost;lines=pair;}}}
    if(Math.max(...lines.map(measure))<=max)return {size,lines,widths:lines.map(measure)};
   }
   throw Error(`Cue ${cue.id} cannot fit two readable lines in source-specific width ${max}`);
  });
 },cues.map(c=>({...c,maxWidth:Math.min(1570,...cuts.filter(k=>k.timelineStart<c.end&&k.timelineStart+k.seconds>c.start).map(k=>k.captionMaxWidth??1570))})));}finally{await browser.close();}
 let ass='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n';
 const evidence=[];
 for(const [i,cue] of cues.entries()){
  const layout=layouts[i];cue.lines=layout.lines;
  const lineHeight=layout.size===42?54:62,padding=layout.size===42?18:22,width=Math.ceil(Math.max(...layout.widths))+44,height=cue.lines.length*lineHeight+padding;
  const boundaries=[...new Set([Math.round(cue.start*100)/100,...cuts.flatMap(c=>[c.timelineStart,c.timelineStart+c.seconds]).filter(t=>t>cue.start+.001&&t<cue.end-.001).map(t=>Math.floor(t*100+1e-7)/100),Math.round(cue.end*100)/100])].sort((a,b)=>a-b);
  for(let j=0;j<boundaries.length-1;j++){
   const start=boundaries[j],end=boundaries[j+1],mid=(start+end)/2,cut=cuts.find(c=>mid>=c.timelineStart&&mid<c.timelineStart+c.seconds),ftl=cut?.key==='ftl',centerX=cut?.captionCenterX??960,centerY=cut?.captionCenterY??970,x=Math.round(centerX-width/2),y=Math.round(centerY-height/2);
   if(cue.lines.length>2||width>1614||y+height+15.5>1080||x<1.5||x+width+15.5>1920)throw Error(`Caption ${cue.id} exceeds picture`);
   const regions=cut?.protectedRegions??(cut?[[0,200,1920,883]]:[[120,250,1800,883]]);
   const overlap=regions.some(r=>x<r[2]&&x+width+14>r[0]&&y<r[3]&&y+height+14>r[1]);
   if(overlap)throw Error(`Caption ${cue.id} overlaps inspected action/HUD region in ${cut?.key??'diagram'}; change placement and review`);
   const event=(layer,text)=>{ass+=`Dialogue: ${layer},${time(start,true)},${time(end,true)},Default,,0,0,0,,${text}\n`;};
   const box=(xx,yy,color,border)=>`{\\an7\\pos(${xx},${yy})\\p1\\bord${border}\\shad0\\1c&H${color}&\\3c&H181B16&}m 0 0 l ${width} 0 ${width} ${height} 0 ${height}`;
   event(0,box(x+14,y+14,'323C07',0));event(1,box(x,y,'FFFFFF',3));
   cue.lines.forEach((line,k)=>event(2,`{\\an5\\pos(${centerX},${y+padding/2+lineHeight/2+k*lineHeight})\\fs${layout.size}\\bord0\\shad0}${line.replaceAll('{','').replaceAll('}','')}`));
   evidence.push({cue:cue.id,start,end,width,height,x,y,fontSize:layout.size,centerX,centerY,shadowBottom:y+height+14,picture:cut?.key??'2.5d-explanation',protectedRegions:regions,overlap,lines:cue.lines});
  }
 }
 fs.writeFileSync(ko,cues.map(c=>`${c.id}\n${time(c.start)} --> ${time(c.end)}\n${c.lines.join('\n')}`).join('\n\n')+'\n');
 fs.writeFileSync(path.join(work,'captions.ko.ass'),ass);
 fs.writeFileSync(path.join(work,'caption-layout-qa.json'),JSON.stringify({style:'boxed-white-forest-v1',font:'Malgun Gothic',placement:'Approved bottom box, with source-specific protected action regions and native Ring Fit instructions, Hi-Fi beat rows and Sports physical-input inset excluded',allCuesMeasured:true,protectedRegionReview:'From directly inspected source action/HUD; every rendered region still requires direct visual review',cues:evidence},null,2)+'\n');
 console.log(`Burning ${cues.length} Korean captions`);
 run('ffmpeg',['-v','error','-y','-i',path.join(root,m.paths.videoClean),'-vf',`ass=${path.relative(root,path.join(work,'captions.ko.ass')).replaceAll('\\','/')}`,'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',path.join(root,m.paths.videoBurnedCaptions)]);
})().catch(e=>{console.error(e);process.exitCode=1;});
