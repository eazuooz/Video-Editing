const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1'),read=p=>JSON.parse(fs.readFileSync(p,'utf8')),m=read(path.join(root,'projects/picking-sides/project.json')),plan=read(path.join(work,'plan.json')),cuts=plan.cuts;
const sec=t=>{const [h,min,s]=t.split(':');return +h*3600+ +min*60+ +s.replace(',','.');};
const time=(t,ass=false)=>{const base=ass?100:1000,n=Math.round(t*base);return `${String(Math.floor(n/(base*3600))).padStart(ass?1:2,'0')}:${String(Math.floor(n/(base*60))%60).padStart(2,'0')}:${String(Math.floor(n/base)%60).padStart(2,'0')}${ass?'.':','}${String(n%base).padStart(ass?2:3,'0')}`;};
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
(async()=>{
 const file=path.join(root,m.paths.captionsKo),cues=fs.readFileSync(file,'utf8').trim().split(/\r?\n\s*\r?\n/).map(b=>{const [id,t,...lines]=b.split(/\r?\n/),[a,z]=t.split(' --> ');return {id:+id,start:sec(a),end:sec(z),lines};});
 const browser=await puppeteer.launch({headless:true,args:['--disable-gpu']});let layouts;
 const cueLimits=cues.map(c=>({ ...c,maxTextWidth:1570 }));
 try{const p=await browser.newPage();layouts=await p.evaluate(cues=>{
  const ctx=document.createElement('canvas').getContext('2d');ctx.font="48px 'Malgun Gothic'";
  return cues.map(c=>{const text=c.lines.join(' '),words=text.split(/\s+/),measure=s=>ctx.measureText(s).width;let lines=[text];
   if(measure(text)>1050){let score=Infinity;for(let i=1;i<words.length;i++){const pair=[words.slice(0,i).join(' '),words.slice(i).join(' ')],widths=pair.map(measure);if(Math.max(...widths)>c.maxTextWidth)continue;const cost=Math.abs(widths[0]-widths[1])-(pair[0].endsWith(',')?65:0);if(cost<score){score=cost;lines=pair;}}}
   if(Math.max(...lines.map(measure))>c.maxTextWidth)throw Error('Cue needs an editorial split: '+c.id);
   return {lines,widths:lines.map(measure)};
  });
 },cueLimits);}finally{await browser.close();}
 let ass='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n';
 const evidence=[];
 for(const [i,c] of cues.entries()){
  c.lines=layouts[i].lines;const width=Math.ceil(Math.max(...layouts[i].widths))+44,height=c.lines.length*62+22;
  const bounds=[...new Set([c.start,...cuts.flatMap(k=>[k.timelineStart,k.timelineEnd]).filter(t=>t>c.start+.001&&t<c.end-.001),c.end].map(t=>Math.round(t*100)/100))].sort((a,b)=>a-b);
  for(let j=0;j<bounds.length-1;j++){
   const start=bounds[j],end=bounds[j+1],mid=(start+end)/2,cut=cuts.find(k=>mid>=k.timelineStart&&mid<k.timelineEnd),key=cut?'existing-game:'+cut.sourceId:'2.5D-explanation';
   const centerX=960,centerY=970,x=Math.round(centerX-width/2),y=Math.round(centerY-height/2);
   // The current channel rule fixes every caption at bottom-center. Official
   // Small flight/grip shots use an upper870px sharp foreground over the
   // source-filled blurred background; other shots fill the entire screen.
   const protectedRegions=cut?[]:[[100,240,1820,883]]; // Actual-game actions require direct every-cue pixel review, not an assumed rectangular safe area.
   const overlap=protectedRegions.some(r=>x<r[2]&&x+width+14>r[0]&&y<r[3]&&y+height+14>r[1]);
   if(c.lines.length>2||width>1614||x<2||x+width+16>1920||y<2||y+height+16>1080||overlap)throw Error(`Cue ${c.id} overlaps protected ${key} UI or image bounds`);
   const event=(layer,text)=>{ass+=`Dialogue: ${layer},${time(start,true)},${time(end,true)},Default,,0,0,0,,${text}\n`;};
   const box=(xx,yy,color,border)=>`{\\an7\\pos(${xx},${yy})\\p1\\bord${border}\\shad0\\1c&H${color}&\\3c&H181B16&}m 0 0 l ${width} 0 ${width} ${height} 0 ${height}`;
   event(0,box(x+14,y+14,'323C07',0));event(1,box(x,y,'FFFFFF',3));c.lines.forEach((line,n)=>event(2,`{\\an5\\pos(${centerX},${y+42+n*62})\\bord0\\shad0}${line.replaceAll('{','').replaceAll('}','')}`));
   evidence.push({cue:c.id,start,end,picture:key,cut:cut?.id??null,width,height,x,y,centerX,centerY,shadowBottom:y+height+14,lines:c.lines,protectedRegions,overlap});
  }
 }
 fs.writeFileSync(file,cues.map(c=>`${c.id}\n${time(c.start)} --> ${time(c.end)}\n${c.lines.join('\n')}`).join('\n\n')+'\n');
 fs.writeFileSync(path.join(work,'captions.ko.ass'),ass);fs.writeFileSync(path.join(work,'caption-layout-qa.json'),JSON.stringify({style:'boxed-white-forest-v1',font:'Malgun Gothic (approved fallback)',size:48,placement:'All narration bottom-center960,970; actual existing-game shots retain fixed bottom-center captions; direct action/caption review remains mandatory',allCuesMeasured:true,cueCount:cues.length,segmentCount:evidence.length,renderedVisualReview:'pending',cues:evidence},null,2)+'\n');
 console.log(`${cues.length} captions / ${evidence.length} cut-aware placements measured without protected UI overlap.`);
 if(process.argv.includes('--layout-only'))return;
 run('ffmpeg',['-v','error','-y','-threads','2','-i',path.join(root,m.paths.videoClean),'-vf',`ass=${path.relative(root,path.join(work,'captions.ko.ass')).replaceAll('\\','/')}`,'-c:v','libx264','-threads','4','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',path.join(root,m.paths.videoBurnedCaptions)]);
})().catch(e=>{console.error(e);process.exitCode=1;});
