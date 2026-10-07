// CPU-only adapter for the exact authored Motion Canvas vector scene trees.
// No browser, local web access, GPU, screenshots, TTS or existing image editing.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto'),{spawn}=require('node:child_process'),{once}=require('node:events');
const ROOT=path.resolve(__dirname,'../../..'),MC=path.join(ROOT,'motion-canvas');
const ts=require(path.join(MC,'node_modules/typescript'));
const {createCanvas,GlobalFonts}=require(require.resolve('@napi-rs/canvas',{paths:['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules']}));
GlobalFonts.registerFromPath('C:/Windows/Fonts/malgun.ttf','Malgun Gothic');GlobalFonts.registerFromPath('C:/Windows/Fonts/malgunbd.ttf','Malgun Gothic Bold');
const slug=process.argv[2]||'picking-sides',DIR=path.join(ROOT,'projects',slug,'production/visual-depth-v1');
const revision=process.argv[3]||'v1';if(!/^v[1-9][0-9]*$/.test(revision))throw Error('Explicit revision required');
const plan=JSON.parse(fs.readFileSync(path.join(MC,'src/projects',slug,'depth-reel-plan-v1.json'),'utf8'));
const lookdev=process.argv.includes('--lookdev-only');const only=process.argv[4]&&!process.argv[4].startsWith('--')?process.argv[4].split(','):undefined;const renderRows=only?plan.rows.filter(r=>only.includes(r.id)):plan.rows;
if(!renderRows.length||only&&renderRows.length!==only.length)throw Error('Requested scene must exist');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const out=p=>path.relative(ROOT,p).replaceAll('\\','/');
const write=(p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
if(!lookdev && slug!=='picking-sides'){
 const review=JSON.parse(fs.readFileSync(path.join(DIR,'white-preflight-direct-review.json'),'utf8'));
 if(!review.preflightPixelsApproved||review.sourceSha256!==sha(path.join(MC,'src/projects',slug,'depth-explanations-v1.tsx'))||review.sharedGeometrySha256!==sha(path.join(MC,'src/shared/depth-diagrams.tsx')))throw Error('Current directly read authored preflight required before rendering');
}
const exportState=path.join(DIR,lookdev?`white-lookdev-execution-${revision}.json`:revision==='v1'?'white-cpu-execution.json':`white-cpu-execution-${revision}.json`);
if(fs.existsSync(exportState)){
 const previous=JSON.parse(fs.readFileSync(exportState,'utf8'));
 if(previous.status!=='failed'||previous.completed.length!==0)throw Error('Existing execution must be inspected; do not blindly repeat');
 const history=path.join(DIR,'white-cpu-failure-jsx-name.json');if(fs.existsSync(history))throw Error('Preserve earlier failure history');fs.renameSync(exportState,history);
}
let time=0;class Node{constructor(props={}){this.props=props;this.children=[];}add(v){this.children.push(...(Array.isArray(v)?v:[v]).flat(Infinity).filter(Boolean));}removeChildren(){this.children=[];}}
class Txt extends Node{}class Line extends Node{}class Rect extends Node{}class Circle extends Node{}class View2D extends Node{fill(c){this.color=c;}}
const Fragment='fragment';
function h(type,props,...children){if(type===Fragment)return children.flat(Infinity);const n=new type(props||{});n.add(children);return n;}
const cache=new Map();
function load(p){
 p=path.resolve(p);if(!p.startsWith(MC+path.sep))throw Error('Only authored workspace Motion Canvas source is loaded');
 if(!path.extname(p))p=fs.existsSync(p+'.tsx')?p+'.tsx':p+'.ts';
 if(cache.has(p))return cache.get(p);if(p.endsWith('.json'))return JSON.parse(fs.readFileSync(p,'utf8'));
 const compiled=ts.transpileModule(fs.readFileSync(p,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020,jsx:ts.JsxEmit.React,jsxFactory:'__depthJSX',jsxFragmentFactory:'Fragment',esModuleInterop:true}}).outputText;
 const module={exports:{}};cache.set(p,module.exports);
 const requireLocal=spec=>{
  if(spec==='@motion-canvas/2d')return {Node,Txt,Line,Rect,Circle,View2D};
  if(spec==='@motion-canvas/core')return {linear:x=>x,createSignal:()=>function(value,duration){if(arguments.length===0)return time;return(function*(){yield {duration};})();}};
  if(spec.startsWith('.'))return load(path.join(path.dirname(p),spec));
  throw Error('Unsupported import: '+spec);
 };
 vm.runInNewContext(compiled,{require:requireLocal,exports:module.exports,module,__depthJSX:h,Fragment,Math,Error,console},{filename:p});return module.exports;
}
const val=v=>typeof v==='function'?v():v;
const color=v=>val(v)||'#202020';
function shortened(points,f){if(f>=1)return points;if(f<=0)return[];let total=0;const lengths=[];for(let i=1;i<points.length;i++){const d=Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]);lengths.push(d);total+=d;}const result=[points[0]];let left=total*f;for(let i=0;i<lengths.length;i++){if(left>=lengths[i]){result.push(points[i+1]);left-=lengths[i];}else{const a=points[i],b=points[i+1],u=left/lengths[i];result.push([a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u]);break;}}return result;}
function draw(c,n){
 if(Array.isArray(n)){n.forEach(x=>draw(c,x));return;}if(!n)return;
 const p=n.props;c.save();const pos=val(p.position)||[val(p.x)||0,val(p.y)||0];c.translate(pos[0],pos[1]);c.globalAlpha*=p.opacity===undefined?1:val(p.opacity);if(c.globalAlpha===0){c.restore();return;}
 if(p.rotation)c.rotate(val(p.rotation)*Math.PI/180);
 if(n instanceof Txt){
  const size=val(p.fontSize)||29;c.font=`${Number(val(p.fontWeight)||500)>=600?'bold ':''}${size}px "Malgun Gothic"`;c.textBaseline='middle';c.textAlign=p.offset?.[0]===-1?'left':'center';c.fillStyle=color(p.fill);
  String(val(p.text)||'').split('\n').forEach((s,i,lines)=>c.fillText(s,0,(i-(lines.length-1)/2)*size*1.3));
 }else if(n instanceof Line){
  let pts=val(p.points)||[];if(p.end!==undefined)pts=shortened(pts,val(p.end));
  if(pts.length>1){c.beginPath();c.moveTo(...pts[0]);pts.slice(1).forEach(pt=>c.lineTo(...pt));if(p.closed)c.closePath();
   if(p.fill){c.fillStyle=color(p.fill);c.fill();}if(p.stroke){c.strokeStyle=color(p.stroke);c.lineWidth=val(p.lineWidth)||1.7;c.lineJoin=p.lineJoin||'round';c.lineCap='round';c.setLineDash(p.lineDash||[]);c.stroke();}
   if(p.endArrow&&!p.closed){const a=pts[pts.length-2],b=pts[pts.length-1],ang=Math.atan2(b[1]-a[1],b[0]-a[0]),s=p.arrowSize||15;c.setLineDash([]);c.beginPath();c.moveTo(...b);c.lineTo(b[0]-s*Math.cos(ang-.43),b[1]-s*Math.sin(ang-.43));c.lineTo(b[0]-s*Math.cos(ang+.43),b[1]-s*Math.sin(ang+.43));c.closePath();c.fillStyle=color(p.stroke);c.fill();}
  }
 }else if(n instanceof Rect){const w=val(p.width)||val(p.size)||100,hh=val(p.height)||val(p.size)||100;c.beginPath();c.roundRect(-w/2,-hh/2,w,hh,p.radius||0);if(p.fill){c.fillStyle=color(p.fill);c.fill();}if(p.stroke){c.strokeStyle=color(p.stroke);c.lineWidth=val(p.lineWidth)||2;c.stroke();}}
 else if(n instanceof Circle){const w=val(p.width)||val(p.size)||100,hh=val(p.height)||val(p.size)||100;c.beginPath();c.ellipse(0,0,w/2,hh/2,0,0,Math.PI*2);if(p.fill){c.fillStyle=color(p.fill);c.fill();}if(p.stroke){c.strokeStyle=color(p.stroke);c.lineWidth=val(p.lineWidth)||2;c.stroke();}}
 n.children.forEach(x=>draw(c,x));c.restore();
}
const state={status:'running',slug,revision,startedAt:new Date().toISOString(),pid:process.pid,commandLine:process.argv,renderer:'CPU Canvas adapter executing the exact Motion Canvas JSX scene tree',gpuTts:0,browserAccess:false,threads:2,totalFrames:renderRows.reduce((a,r)=>a+r.frames,0),completed:[],allPixelsReviewed:false};write(exportState,state);
const ff='C:/ProgramData/HP/LCDDisplayHelper/bin/ffmpeg.exe';
const canvas=createCanvas(1920,1080),c=canvas.getContext('2d');
const scene=load(path.join(MC,'src/projects',slug,'depth-explanations-v1.tsx'));
const sampleDir=path.join(DIR,lookdev?`white-preflight-${revision}-local`:revision==='v1'?'white-lookdev-local':`white-lookdev-${revision}-local`);fs.mkdirSync(sampleDir,{recursive:true});
(async()=>{
 for(const row of renderRows){
  if(lookdev){time=0;const view=new View2D();scene.depthExplanation(view,row.id,row.frames).next();const samples=[...new Set([0,row.frames-1,...row.paragraphStarts.flatMap(f=>[Math.min(row.frames-1,f+60),Math.min(row.frames-1,f+150)])])].sort((a,b)=>a-b);for(const f of samples){time=f/60;c.fillStyle=view.color||'#fff';c.fillRect(0,0,1920,1080);c.save();c.translate(960,540);view.children.forEach(n=>draw(c,n));c.restore();fs.writeFileSync(path.join(sampleDir,`${row.id}-${String(f).padStart(5,'0')}.png`),canvas.toBuffer('image/png'));}state.completed.push({id:row.id,frames:row.frames,samples,sourceSha256:sha(path.join(MC,'src/projects',slug,'depth-explanations-v1.tsx'))});write(exportState,state);continue;}
  const dest=path.join(DIR,revision==='v1'?`white-${row.id}.mp4`:`white-${row.id}-${revision}.mp4`);if(fs.existsSync(dest))throw Error('Preserve existing white render');
  time=0;const view=new View2D();const g=scene.depthExplanation(view,row.id,row.frames);g.next();
  const proc=spawn(ff,['-hide_banner','-loglevel','warning','-y','-f','rawvideo','-pix_fmt','rgba','-s','1920x1080','-r','60','-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','90000','-movflags','+faststart',dest],{windowsHide:true});
  let stderr='';proc.stderr.on('data',b=>stderr+=b);proc.stdin.on('error',()=>{});const finished=once(proc,'close');
  state.activeScene=row.id;state.ffmpegPid=proc.pid;write(exportState,state);
  const samples=new Set([0,row.frames-1,...row.paragraphStarts.flatMap(f=>[Math.min(row.frames-1,f+60),Math.min(row.frames-1,f+150)])]);
  for(let f=0;f<row.frames;f++){
   time=f/60;c.fillStyle=view.color||'#fff';c.fillRect(0,0,1920,1080);c.save();c.translate(960,540);view.children.forEach(n=>draw(c,n));c.restore();
   if(samples.has(f))fs.writeFileSync(path.join(sampleDir,`${row.id}-${String(f).padStart(5,'0')}.png`),canvas.toBuffer('image/png'));
   if(!proc.stdin.write(canvas.data()))await once(proc.stdin,'drain');
   if(f%600===0){state.frame=f;state.updatedAt=new Date().toISOString();write(exportState,state);}
  }
  proc.stdin.end();const [code]=await finished;if(code!==0)throw Error('FFmpeg failed '+stderr);
  state.completed.push({id:row.id,frames:row.frames,file:out(dest),sha256:sha(dest),stderr});write(exportState,state);console.log('Completed white scene '+row.id+' '+row.frames+' frames');
 }
 state.status=lookdev?'preflight-samples-awaiting-direct-reading':'rendered-pending-direct-pixels-and-full-decode';state.endedAt=new Date().toISOString();write(exportState,state);console.log('White inputs finished; approval gates remain false');
})().catch(e=>{state.status='failed';state.error=String(e);write(exportState,state);console.error(e);process.exitCode=1;});
