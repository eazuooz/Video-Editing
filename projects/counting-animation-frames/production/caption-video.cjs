const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('../../../motion-canvas/node_modules/puppeteer');
const root=path.resolve(__dirname,'../../..'),work=path.join(root,'projects/counting-animation-frames/production',process.env.COUNTING_REVISION||'final-v1'),m=JSON.parse(fs.readFileSync(path.resolve(root,process.env.COUNTING_MANIFEST||'projects/counting-animation-frames/project.json'),'utf8'));
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:16e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const sec=t=>{const [h,min,s]=t.split(':');return +h*3600+ +min*60+ +s.replace(',','.');};
const ggst=c=>c&&['sol','ky'].includes(c.key);
const time=(t,ass=false)=>{const n=Math.round(t*(ass?100:1000)),base=ass?100:1000;return `${String(Math.floor(n/(base*3600))).padStart(ass?1:2,'0')}:${String(Math.floor(n/(base*60))%60).padStart(2,'0')}:${String(Math.floor(n/base)%60).padStart(2,'0')}${ass?'.':','}${String(n%base).padStart(ass?2:3,'0')}`;};
(async()=>{
 const plan=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8')),cuts=plan.scenes.flatMap(s=>s.cuts);
 const ko=path.join(root,m.paths.captionsKo),cues=fs.readFileSync(ko,'utf8').trim().split(/\r?\n\s*\r?\n/).map(b=>{const [id,t,...lines]=b.split(/\r?\n/),[a,z]=t.split(' --> ');return {id:+id,start:sec(a),end:sec(z),lines};});
 const browser=await puppeteer.launch({headless:true});let layouts;
 try{const p=await browser.newPage();layouts=await p.evaluate(cues=>{
   const c=document.createElement('canvas').getContext('2d');c.font="48px 'Malgun Gothic'";
   return cues.map(cue=>{const text=cue.lines.join(' '),words=text.split(/\s+/),measure=s=>c.measureText(s).width;let lines=[text];
    if(measure(text)>(cue.narrow?950:1100)){let best=Infinity;for(let i=1;i<words.length;i++){const pair=[words.slice(0,i).join(' '),words.slice(i).join(' ')],w=pair.map(measure);if(Math.max(...w)>(cue.narrow?1070:1570))continue;const cost=Math.abs(w[0]-w[1])-(pair[0].endsWith(',')?80:0);if(cost<best){best=cost;lines=pair;}}}
    return {lines,widths:lines.map(measure)};
   });
 },cues.map(c=>({...c,narrow:cuts.some(k=>ggst(k)&&k.timelineStart<c.end&&k.timelineStart+k.seconds>c.start)})));}finally{await browser.close();}
 let ass='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n';
 const evidence=[];
 for(const [i,cue] of cues.entries()){
  cue.lines=layouts[i].lines;const width=Math.ceil(Math.max(...layouts[i].widths))+44,height=cue.lines.length*62+22,x=Math.round(960-width/2);
  // Full-screen playtests keep their input indicators above y=879.
  // Bottom captions remain below protected action regions at picture cuts.
  // Adjacent cuts share an endpoint. Deduplicate at ASS centisecond precision
  // so a shared endpoint cannot create an empty caption event.
  // ASS has centisecond precision. A cut occurs on an exact 60-fps PTS:
  // floor its event boundary so the new position applies to that first frame,
  // while the preceding video frame still keeps the previous position.
  // Rounding upward briefly placed the game's upper caption on a diagram title.
  const boundaries=[...new Set([Math.round(cue.start*100)/100,...cuts.flatMap(c=>[c.timelineStart,c.timelineStart+c.seconds]).filter(t=>t>cue.start+.001&&t<cue.end-.001).map(t=>Math.floor(t*100+1e-7)/100),Math.round(cue.end*100)/100])].sort((a,b)=>a-b);
  for(let segment=0;segment<boundaries.length-1;segment++){
  const start=boundaries[segment],end=boundaries[segment+1],mid=(start+end)/2,cut=cuts.find(c=>mid>=c.timelineStart&&mid<c.timelineStart+c.seconds),own=cut&&['rate','interval','poses','pause','render'].includes(cut.key),centerY=ggst(cut)?275:970,centerX=ggst(cut)?1280:960,y=Math.round(centerY-height/2),segmentX=Math.round(centerX-width/2);
  if(cue.lines.length>2||width>1614||y+height+14+1.5>1080||x<1.5||x+width+14+1.5>1920)throw Error(`Caption ${cue.id} exceeds bounds`);
  const event=(layer,text)=>{ass+=`Dialogue: ${layer},${time(start,true)},${time(end,true)},Default,,0,0,0,,${text}\n`;};
  const box=(xx,yy,color,border)=>`{\\an7\\pos(${xx},${yy})\\p1\\bord${border}\\shad0\\1c&H${color}&\\3c&H181B16&}m 0 0 l ${width} 0 ${width} ${height} 0 ${height}`;
  event(0,box(segmentX+14,y+14,'323C07',0));event(1,box(segmentX,y,'FFFFFF',3));
  cue.lines.forEach((line,j)=>event(2,`{\\an5\\pos(${centerX},${y+11+31+j*62})\\bord0\\shad0}${line.replaceAll('{','').replaceAll('}','')}`));
  const protectedRegion=ggst(cut)?[0,370,1920,1080]:own?[0,220,1920,890]:cut?[0,250,1920,820]:[120,250,1800,883];
  // Actual external-game action is checked in every rendered cue segment.
  const overlap=segmentX<protectedRegion[2]&&segmentX+width+14>protectedRegion[0]&&y<protectedRegion[3]&&y+height+14>protectedRegion[1];
  if(ggst(cut)&&(segmentX<690||y<195||segmentX+width+16>1920))throw Error(`GGST caption ${cue.id} overlaps health/left combo UI or exceeds frame`);
  if(overlap)throw Error(`Caption ${cue.id} overlaps protected action/input region in ${cut?.key??'diagram'}`);
  evidence.push({cue:cue.id,start,end,width,height,x:segmentX,y,centerX,centerY,shadowBottom:y+height+14,picture:cut?.key??'2.5d-explanation',protectedRegion,overlap,lines:cue.lines});
  }
 }
 fs.writeFileSync(ko,cues.map(c=>`${c.id}\n${time(c.start)} --> ${time(c.end)}\n${c.lines.join('\n')}`).join('\n\n')+'\n');
 fs.writeFileSync(path.join(work,'captions.ko.ass'),ass);fs.writeFileSync(path.join(work,'caption-layout-qa.json'),JSON.stringify({style:'boxed-white-forest-v1',font:'Malgun Gothic (approved fallback)',size:48,placement:'upper right on GGST, clear of health bars/left combo/move banner; bottom on other footage and explanations',cutBoundaryRule:'floor exact frame PTS to ASS centiseconds; new placement starts on the first frame of each cut',maxBoxWidth:Math.max(...evidence.map(e=>e.width)),allCuesMeasured:true,protectedRegionReview:'based on inspected source game action and HUD; rendered cue contact sheets require subsequent visual review',cues:evidence},null,2));
 console.log(`Burning ${cues.length} measured Korean captions`);
 run('ffmpeg',['-v','error','-y','-i',path.join(root,m.paths.videoClean),'-vf',`ass=${path.relative(root,path.join(work,'captions.ko.ass')).replaceAll('\\','/')}`,'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','90000','-c:a','copy','-movflags','+faststart',path.join(root,m.paths.videoBurnedCaptions)]);
})().catch(e=>{console.error(e);process.exitCode=1;});
