// Refresh only this project's metadata using the normal checker input inventory; preserve shared index/other projects.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..');
const {build}=require(path.join(root,'scripts/build-rebuild-manifests.cjs'));
function walk(dir){
 const full=path.join(root,dir);if(!fs.existsSync(full))return [];
 return fs.readdirSync(full,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{
  if(e.isSymbolicLink()||/^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks)$/.test(e.name))return [];
  const f=dir+'/'+e.name;return e.isDirectory()?walk(f):[f];
 });
}
const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>fs.existsSync(path.join(root,'projects',s,'project.json'))).sort();
const tracked=cp.execFileSync('git',['ls-files','--cached','--others','--exclude-standard','-z'],{cwd:root,encoding:'utf8',maxBuffer:32e6}).split('\0').filter(Boolean);
const files=[...new Set([...tracked,...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>walk('motion-canvas/src/projects/'+s))])].filter(f=>fs.existsSync(path.join(root,f))).sort();
const data=build('making-game-sequels',files);
fs.writeFileSync(path.join(root,'projects/making-game-sequels/rebuild.json'),JSON.stringify(data,null,2)+'\n');
console.log(JSON.stringify({slug:data.slug,counts:data.counts,sharedRebuildIndexChanged:false}));
