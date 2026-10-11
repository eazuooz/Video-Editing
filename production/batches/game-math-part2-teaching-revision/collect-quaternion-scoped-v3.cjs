// Use the normal collector while regenerating only this owned project's manifest.
// The shared rebuild index may be held by another active production task.
const fs=require('node:fs'),path=require('node:path');
const {execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..');
const slug=process.argv[2];
if(!['game-math-quaternion-foundations-v3','game-math-quaternion-calculations-v3'].includes(slug))throw Error('Not an owned quaternion delivery');
const rebuild=require(path.join(root,'scripts/build-rebuild-manifests.cjs'));
function walk(relative){const p=path.join(root,relative);if(!fs.existsSync(p))return[];return fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(relative+'/'+e.name):[relative+'/'+e.name]);}
rebuild.generate=(target)=>{
  if(target!==slug)throw Error('Unexpected project');
  const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>fs.existsSync(path.join(root,'projects',s,'project.json'))).sort();
  const tracked=execFileSync('git',['ls-files','--cached','--others','--exclude-standard','-z'],{cwd:root,windowsHide:true,maxBuffer:128e6}).toString('utf8').split('\0').filter(Boolean);
  const files=[...new Set([...tracked,...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>walk('motion-canvas/src/projects/'+s))])].filter(f=>fs.existsSync(path.join(root,f))).sort();
  fs.writeFileSync(path.join(root,'projects',slug,'rebuild.json'),JSON.stringify(rebuild.build(slug,files),null,2)+'\n');
  console.log('Updated only owned rebuild manifest; shared rebuild index preserved.');
};
require(path.join(root,'scripts/collect-video-output.cjs'));
