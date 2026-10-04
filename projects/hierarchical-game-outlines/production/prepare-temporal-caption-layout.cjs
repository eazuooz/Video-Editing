// Pixel-measured layout draft, with no caption render or approval.
const fs=require('node:fs'),path=require('node:path');
const {createCanvas,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:[path.join(process.env.USERPROFILE,'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules')]}));
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun Gothic');
const work=path.join(__dirname,'final-v1'),plan=JSON.parse(fs.readFileSync(path.join(work,'plan.json'),'utf8'));
const crypto=require('node:crypto');
const temporal=JSON.parse(fs.readFileSync(path.join(work,'caption-temporal-v3.json'),'utf8'));
const baseline=path.join(work,'caption-temporal-baseline-v3/caption-layout-qa.json');
const selection=path.join(work,'cut-selection.json');
if(!temporal.allKoreanAndEnglishTextIdentical||!fs.readFileSync(baseline).equals(fs.readFileSync(path.join(work,'caption-layout-qa.json')))||temporal.sourceSelectionSha256!==crypto.createHash('sha256').update(fs.readFileSync(selection)).digest('hex'))throw Error('Current unchanged-text temporal baseline required');
const sec=t=>{const [h,m,s]=t.split(':');return +h*3600+ +m*60+ +s.replace(',','.');};
const tm=(t,ass=false)=>{const base=ass?100:1000,n=Math.round(t*base);return `${String(Math.floor(n/(base*3600))).padStart(ass?1:2,'0')}:${String(Math.floor(n/(base*60))%60).padStart(2,'0')}:${String(Math.floor(n/base)%60).padStart(2,'0')}${ass?'.':','}${String(n%base).padStart(ass?2:3,'0')}`;};
const file=path.join(work,'captions.ko.srt'),cues=fs.readFileSync(file,'utf8').trim().split(/\r?\n\s*\r?\n/).map(b=>{const [id,t,...lines]=b.split(/\r?\n/),[a,z]=t.split(' --> ');return {id:+id,start:sec(a),end:sec(z),lines};});
const ctx=createCanvas(1920,1080).getContext('2d');ctx.font='48px Malgun Gothic';
let ass='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n';
const evidence=[];
for(const c of cues){
 const text=c.lines.join(' '),words=text.split(/\s+/),hasGame=plan.cuts.some(k=>Math.min(c.end,k.timelineEnd)-Math.max(c.start,k.timelineStart)>.001),limit=hasGame?(process.argv.includes('--reviewed-v3')?650:1050):1570;
 const measure=s=>ctx.measureText(s).width;let lines=[text];
 if(measure(text)>limit){let best=Infinity;for(let j=1;j<words.length;j++){const pair=[words.slice(0,j).join(' '),words.slice(j).join(' ')],widths=pair.map(measure);if(Math.max(...widths)>limit)continue;const cost=Math.abs(widths[0]-widths[1])-(pair[0].endsWith(',')?65:0);if(cost<best){best=cost;lines=pair;}}}
 if(Math.max(...lines.map(measure))>limit)throw Error('Editorial cue split needed:'+c.id);
 c.lines=lines;const width=Math.ceil(Math.max(...lines.map(measure)))+44,height=lines.length*62+22,x=Math.round(960-width/2),y=Math.round(970-height/2);
 if(lines.length>2||(hasGame&&process.argv.includes('--reviewed-v3')&&lines.length!==1)||x<2||x+width+16>1920||y+height+16>1080)throw Error('Fixed center bounds failed');
 const bounds=[...new Set([c.start,...plan.cuts.flatMap(k=>[k.timelineStart,k.timelineEnd]).filter(t=>t>c.start+.001&&t<c.end-.001),c.end])].sort((a,b)=>a-b);
 for(let j=0;j<bounds.length-1;j++){
  const start=bounds[j],end=bounds[j+1],mid=(start+end)/2,cut=plan.cuts.find(k=>mid>=k.timelineStart&&mid<k.timelineEnd);
  const box=(xx,yy,color,border)=>`{\\an7\\pos(${xx},${yy})\\p1\\bord${border}\\shad0\\1c&H${color}&\\3c&H181B16&}m 0 0 l ${width} 0 ${width} ${height} 0 ${height}`;
  const evt=(layer,text)=>{ass+=`Dialogue: ${layer},${tm(start,true)},${tm(end,true)},Default,,0,0,0,,${text}\n`;};
  evt(0,box(x+14,y+14,'323C07',0));evt(1,box(x,y,'FFFFFF',3));lines.forEach((line,n)=>evt(2,`{\\an5\\pos(960,${y+42+n*62})\\bord0\\shad0}${line.replaceAll('{','').replaceAll('}','')}`));
  evidence.push({cue:c.id,start,end,cut:cut?.id??null,scene:cut?.scene??plan.scenes.find(s=>mid>=s.start&&mid<s.start+s.seconds)?.id,width,height,x,y,centerX:960,centerY:970,shadowBottom:y+height+14,lines,pixelActionOverlap:'pending-direct-inspection'});
 }
}
fs.writeFileSync(file,cues.map(c=>`${c.id}\n${tm(c.start)} --> ${tm(c.end)}\n${c.lines.join('\n')}`).join('\n\n')+'\n');
fs.writeFileSync(path.join(work,'captions.ko.ass'),ass);
fs.writeFileSync(path.join(work,'caption-layout-qa.json'),JSON.stringify({style:'boxed-white-forest-v1',font:'Malgun Gothic (approved fallback)',size:48,captionCenter:[960,970],cueCount:cues.length,segmentCount:evidence.length,allCuesMeasured:true,allActualPixelsReviewed:false,allPptPixelsReviewed:false,renderedVisualReview:'pending',cues:evidence},null,2)+'\n');
console.log(JSON.stringify({cueCount:cues.length,segments:evidence.length,actualSegments:evidence.filter(c=>c.cut).length,approval:false}));
