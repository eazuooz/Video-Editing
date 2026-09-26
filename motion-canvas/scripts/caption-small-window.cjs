const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process'),puppeteer=require('puppeteer');
const root=path.resolve(__dirname,'../..'),project=path.join(root,'projects/small-window-game-design'),work=path.join(project,'production/full-v2'),m=JSON.parse(fs.readFileSync(path.join(project,'project.json'),'utf8'));
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:16e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
function seconds(s){const [h,min,rest]=s.split(':');return +h*3600+ +min*60+ +rest.replace(',','.');}
const assTime=t=>{const n=Math.round(t*100);return `${Math.floor(n/360000)}:${String(Math.floor(n/6000)%60).padStart(2,'0')}:${String(Math.floor(n/100)%60).padStart(2,'0')}.${String(n%100).padStart(2,'0')}`;};
(async()=>{
  const koPath=path.join(root,m.paths.captionsKo);
  let srt=fs.readFileSync(koPath,'utf8').replaceAll('십육 대 구','16:9').replaceAll('이십일 대 구','21:9').replaceAll('필드 오브 뷰','Field of View').replaceAll('에프오브이','FOV');
  fs.writeFileSync(koPath,srt);
  const cues=srt.trim().split(/\r?\n\s*\r?\n/).map(block=>{const [id,time,...lines]=block.split(/\r?\n/);const [a,b]=time.split(' --> ');return {id:+id,start:seconds(a),end:seconds(b),lines};});
  const browser=await puppeteer.launch({headless:true});let measures;
  try{const p=await browser.newPage();const layouts=await p.evaluate(cues=>{
    const c=document.createElement('canvas').getContext('2d');c.font="48px 'Malgun Gothic'";
    return cues.map(cue=>{
      const text=cue.lines.join(' '),words=text.split(/\s+/),measure=s=>c.measureText(s).width;
      let lines=[text];
      if(measure(text)>1050){let best=Infinity;
        for(let j=1;j<words.length;j++){
          const pair=[words.slice(0,j).join(' '),words.slice(j).join(' ')],widths=pair.map(measure);
          if(Math.max(...widths)>1050)continue;
          const cost=Math.abs(widths[0]-widths[1])-(pair[0].endsWith(',')?80:0);
          if(cost<best){best=cost;lines=pair;}
        }
      }
      return {lines,widths:lines.map(measure)};
    });
  },cues);layouts.forEach((v,i)=>cues[i].lines=v.lines);measures=layouts.map(v=>v.widths);}finally{await browser.close();}
  const srtTime=t=>{const ms=Math.round(t*1000);return `${String(Math.floor(ms/3600000)).padStart(2,'0')}:${String(Math.floor(ms/60000)%60).padStart(2,'0')}:${String(Math.floor(ms/1000)%60).padStart(2,'0')},${String(ms%1000).padStart(3,'0')}`;};
  fs.writeFileSync(koPath,cues.map(c=>`${c.id}\n${srtTime(c.start)} --> ${srtTime(c.end)}\n${c.lines.join('\n')}`).join('\n\n')+'\n');
  let ass='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n';
  const evidence=[];
  for(let i=0;i<cues.length;i++){
    const cue=cues[i],width=Math.ceil(Math.max(...measures[i]))+52,height=cue.lines.length*62+22;
    if(cue.lines.length>2||width>1160)throw Error(`Caption ${cue.id} too wide (${width}) or too many lines`);
    const x=Math.round(960-width/2),y=Math.round(970-height/2),a=assTime(cue.start),b=assTime(cue.end);
    const event=(layer,text)=>{ass+=`Dialogue: ${layer},${a},${b},Default,,0,0,0,,${text}\n`;};
    const box=(xx,yy,color,border)=>`{\\an7\\pos(${xx},${yy})\\p1\\bord${border}\\shad0\\1c&H${color}&\\3c&H181B16&}m 0 0 l ${width} 0 ${width} ${height} 0 ${height}`;
    event(0,box(x+14,y+14,'323C07',0));event(1,box(x,y,'FFFFFF',3));
    cue.lines.forEach((line,j)=>event(2,`{\\an5\\pos(960,${y+11+31+j*62})\\bord0\\shad0}${line.replaceAll('{','').replaceAll('}','')}`));
    evidence.push({cue:cue.id,width,height,x,y,shadowBottom:y+height+14,lines:cue.lines});
  }
  fs.writeFileSync(path.join(work,'captions.ko.ass'),ass);fs.writeFileSync(path.join(work,'caption-layout-qa.json'),JSON.stringify({font:'Malgun Gothic',size:48,centerY:970,maxBoxWidth:Math.max(...evidence.map(e=>e.width)),cues:evidence},null,2));
  const relative=path.relative(root,path.join(work,'captions.ko.ass')).replaceAll('\\','/');
  console.log(`Burning ${cues.length} measured captions`);
  run('ffmpeg',['-v','error','-y','-i',path.join(root,m.paths.videoClean),'-vf',`ass=${relative}`,'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',path.join(root,m.paths.videoBurnedCaptions)]);
})().catch(e=>{console.error(e);process.exitCode=1;});
