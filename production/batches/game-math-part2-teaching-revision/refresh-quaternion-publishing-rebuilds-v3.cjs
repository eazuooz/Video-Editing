// Regenerate only the four owned quaternion metadata manifests.
const fs=require('node:fs'),path=require('node:path');
const {execFileSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..');
const rebuild=require(path.join(root,'scripts/build-rebuild-manifests.cjs'));
function walk(relative){const p=path.join(root,relative);if(!fs.existsSync(p))return[];return fs.readdirSync(p,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(relative+'/'+e.name):[relative+'/'+e.name]);}
const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>fs.existsSync(path.join(root,'projects',s,'project.json'))).sort();
const tracked=execFileSync('git',['ls-files','--cached','--others','--exclude-standard','-z'],{cwd:root,windowsHide:true,maxBuffer:128e6}).toString('utf8').split('\0').filter(Boolean);
const files=[...new Set([...tracked,...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>walk('motion-canvas/src/projects/'+s))])].filter(f=>fs.existsSync(path.join(root,f))).sort();
for(const episode of ['foundations','calculations'])for(const version of ['v2','v3']){
  const slug=`game-math-quaternion-${episode}-${version}`;
  fs.writeFileSync(path.join(root,'projects',slug,'rebuild.json'),JSON.stringify(rebuild.build(slug,files),null,2)+'\n');
  console.log('Updated owned metadata: '+slug);
}
