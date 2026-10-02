const fs=require('fs'),path=require('path');const W=__dirname,R=path.resolve(W,'../../../..');
const old=fs.readFileSync(path.join(R,'projects/blank-project-coding/production/build-final.cjs'),'utf8');
const mix=old.slice(old.indexOf("}else if(stage==='mix'){")+"}else if(stage==='mix'){".length,old.indexOf("}else if(stage==='assemble'){"))
 .replace("reason:'All examples are owned silent executing-code/playtest screencasts. Narration/Nimbus still cover every frame including membership outro.'","reason:'External source audio removed to avoid third-party music; approved continuous narration and Nimbus cover the final membership ending.'");
if(!mix.includes('continuous-Nimbus')&&!mix.includes('Continuous')&&!mix.includes('Measured continuous'))throw Error('Mix extraction failed');
const pre=`const fs=require('fs'),path=require('path'),{spawnSync}=require('child_process');
const root=path.resolve(__dirname,'../../../..'),work=__dirname,read=p=>JSON.parse(fs.readFileSync(p,'utf8')),write=(p,v)=>fs.writeFileSync(p,typeof v==='string'?v:JSON.stringify(v,null,2)+'\\n'),abs=p=>path.join(root,p),m=read(path.join(work,'final.manifest.json')),plan=read(path.join(work,'plan.json'));
function run(cmd,args){const r=spawnSync(cmd,args,{encoding:'utf8',windowsHide:true,maxBuffer:8e6});if(r.status!==0)throw Error(r.stderr||String(r.error));return r.stdout;}
const ff=a=>run('ffmpeg',['-v','error','-y','-threads','2',...a]);
`;
fs.writeFileSync(path.join(W,'mix-audio.cjs'),pre+mix);
const cap=fs.readFileSync(path.join(R,'projects/blank-project-coding/production/caption-video.cjs'),'utf8')
 .replace("require('../../../motion-canvas/node_modules/puppeteer')","require('../../../../motion-canvas/node_modules/puppeteer')")
 .replace("path.resolve(__dirname,'../../..'),work=path.join(__dirname,'final-v1')","path.resolve(__dirname,'../../../..'),work=__dirname")
 .replace("m=read(path.join(root,'projects/blank-project-coding/project.json'))","m=read(path.join(work,'final.manifest.json'))")
 .replace("const protectedRegions=cut?[[0,0,1920,920]]:[[100,240,1820,883]];","const protectedRegions=cut?.classification==='actual'?[[0,0,1920,920],[0,1033,1920,1080]]:[[100,240,1820,889]];")
 .replace("c.lines.length>2","c.lines.length>1")
 .replace("owned workbench controls composed above920px","actual footage composed above920px; source credits below1033px; every Korean cue one line");
fs.writeFileSync(path.join(W,'caption-video.cjs'),cap);
console.log('Revision-isolated measured mix and fixed-caption builders created.');
