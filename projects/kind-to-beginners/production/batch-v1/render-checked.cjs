// Fail before launching a media job when the editable chapter snapshot is stale.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const ROOT=path.resolve(__dirname,'../../../..'),slug=path.basename(path.resolve(__dirname,'../..'));
const local=path.join(ROOT,'projects',slug,'production/local/batch-v1');
const mc=path.join(ROOT,'motion-canvas/src/projects',slug,'batch-v1');
const packedFile=path.join(local,'diagram-assets/packed-cues.json');
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const packed=JSON.parse(fs.readFileSync(packedFile,'utf8'));
const binding=JSON.parse(fs.readFileSync(path.join(local,'diagram-assets/module-clock-binding.json'),'utf8'));
if(binding.packedCuesSha256!==hash(packedFile)||binding.packedFrames!==packed.totalFrames)throw Error('Packed cue hash changed. Run build-edit.py before rendering.');
let count=0;
for(const sid of [...new Set(packed.cues.map(c=>c.scene))]){
 const file=path.join(mc,`scene-${sid}.tsx`);const source=fs.readFileSync(file,'utf8');
 const match=/const cues:\s*Cue\[\]\s*=\s*(\[[\s\S]*\]);\s*export function/.exec(source);
 if(!match)throw Error('Missing explicitly authored cue array: '+file);
 const actual=JSON.parse(match[1]),expected=packed.cues.filter(c=>c.scene===sid);
 if(JSON.stringify(actual)!==JSON.stringify(expected))throw Error('Scene snapshot does not match current packed clock: '+sid);
 const row=binding.modules.find(r=>path.resolve(ROOT,r.path)===file);
 if(!row||row.sha256!==hash(file))throw Error('Editable chapter bytes changed after clock binding: '+sid);
 count+=actual.reduce((n,c)=>n+c.frames,0);
}
if(count!==packed.totalFrames)throw Error('Chapter frame sum changed.');
const [name,frameText,firstText='0']=process.argv.slice(2);const frames=Number(frameText),first=Number(firstText);
if(name==='--check-only'){console.log(JSON.stringify({slug,checked:true,frames:count,packedCuesSha256:hash(packedFile)}));process.exit(0);}
if(!(first===0&&frames===count)&&!packed.cues.some(c=>c.startFrame===first&&c.frames===frames))throw Error('Render an exact full packed timeline or exact whole cue.');
const inputs={slug,name,frames,firstFrame:first,packedCuesSha256:hash(packedFile),chapterClockBindingSha256:hash(path.join(local,'diagram-assets/module-clock-binding.json')),
 rendererInputs:['visuals.tsx','scene.tsx','project.ts'].map(file=>({path:path.relative(ROOT,path.join(mc,file)).replaceAll('\\','/'),sha256:hash(path.join(mc,file))})),
 images:[...new Set(packed.cues.map(c=>c.sourceImage.replace('/@fs/','')))].map(file=>({path:file,sha256:hash(file)})),checkedAt:new Date().toISOString()};
const receipt=path.join(local,'rendered',name+'.inputs.json');fs.mkdirSync(path.dirname(receipt),{recursive:true});
if(fs.existsSync(receipt))throw Error('Preserve existing render input receipt; select a fresh export name.');
fs.writeFileSync(receipt,JSON.stringify(inputs,null,2)+'\n');
const result=cp.spawnSync(process.execPath,[path.join(ROOT,'production/batches/design-finish-six-20261026/render-motion.cjs'),slug,name,frameText,firstText],{cwd:ROOT,stdio:'inherit',windowsHide:true});
process.exit(result.status??1);
