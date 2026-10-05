// Measure literal candidate captions and prepare fixed-pixel review samples.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const work=path.join(__dirname,'measured-edit-v2');
const read=n=>JSON.parse(fs.readFileSync(path.join(work,n),'utf8'));
const version=process.argv[2]||'v1';if(!['v1','v2'].includes(version))throw Error('Unknown caption version.');
const plan=read('plan.json'),tracks=read(`caption-tracks-${version}.json`);
if(fs.existsSync(path.join(work,`caption-layout-${version}.json`)))throw Error('Preserve existing candidate layout.');
const {createCanvas,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules']}));
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun Gothic');
const ctx=createCanvas(1920,1080).getContext('2d');ctx.font='48px Malgun Gothic';
const segments=plan.scenes.flatMap(s=>s.segments.map(c=>({...c,scene:s.id})));
const t=s=>{const n=Math.round(s*100);return `${Math.floor(n/360000)}:${String(Math.floor(n/6000)%60).padStart(2,'0')}:${String(Math.floor(n/100)%60).padStart(2,'0')}.${String(n%100).padStart(2,'0')}`;};
let ass='[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00323C07,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n';
const rows=[];
for(const c of tracks.koRows){
 const widths=c.lines.map(x=>ctx.measureText(x).width);
 const width=Math.ceil(Math.max(...widths))+44,height=c.lines.length*62+22;
 const x=Math.round(960-width/2),y=Math.round(970-height/2);
 if(Math.max(...widths)>651||c.lines.length>2||x<0||x+width+14>1920||y+height+14>1080)throw Error('Candidate cue needs editorial splitting:'+c.index);
 const event=(layer,text)=>{ass+=`Dialogue: ${layer},${t(c.startSeconds)},${t(c.endSeconds)},Default,,0,0,0,,${text}\n`;};
 const box=(xx,yy,color,border)=>`{\\an7\\pos(${xx},${yy})\\p1\\bord${border}\\shad0\\1c&H${color}&\\3c&H181B16&}m 0 0 l ${width} 0 ${width} ${height} 0 ${height}`;
 event(0,box(x+14,y+14,'323C07',0));event(1,box(x,y,'FFFFFF',3));
 c.lines.forEach((line,k)=>event(2,`{\\an5\\pos(960,${y+42+k*62})\\bord0\\shad0}${line}`));
 for(const s of segments){
  const a=Math.max(c.startSeconds,s.startFrame/60),z=Math.min(c.endSeconds,s.endFrameExclusive/60);
  if(z-a<=.001)continue;
  const sampleFrame=Math.min(s.endFrameExclusive-1,Math.max(s.startFrame,Math.round((a+z)*30)));
  rows.push({cue:c.index,scene:c.scene,paragraph:c.paragraph,segment:s.id,classification:s.classification,
   startSeconds:a,endSeconds:z,sampleFrame,localFrame:sampleFrame-s.startFrame,lines:c.lines,width,height,x,y,
   center:[960,970],timingApproved:false,actionUiOverlap:'pending-direct-pixel-review'});
 }
}
fs.writeFileSync(path.join(work,`captions.ko.candidate${version==='v1'?'':'.v2'}.ass`),ass);
fs.writeFileSync(path.join(work,`caption-layout-${version}.json`),JSON.stringify({schemaVersion:1,
 status:'measured-candidate-only-every-fixed-cue-pixel-and-source-framing-pending',style:'boxed-white-forest-v1',
 font:'Malgun Gothic (approved fallback)',size:48,captionCenter:[960,970],cueCount:tracks.koRows.length,
 enCueCount:tracks.enRows.length,segmentCount:rows.length,allCuesMeasured:true,rows,
 allActualPixelsReviewed:false,allPptPixelsReviewed:false,finalTimingApproved:false,
 minimumCueSeconds:Math.min(...tracks.koRows.map(c=>c.endSeconds-c.startSeconds)),
 inputHashes:{plan:crypto.createHash('sha256').update(fs.readFileSync(path.join(work,'plan.json'))).digest('hex'),
  tracks:crypto.createHash('sha256').update(fs.readFileSync(path.join(work,`caption-tracks-${version}.json`))).digest('hex')}
},null,2)+'\n');
console.log(JSON.stringify({koCues:tracks.koRows.length,enCues:tracks.enRows.length,intersections:rows.length,
 actualIntersections:rows.filter(r=>r.classification==='actual-existing-game').length,maxWidth:Math.max(...rows.map(r=>r.width)),finalPixelsApproved:false}));
