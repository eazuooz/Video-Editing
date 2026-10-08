// Usage: node projects/player-customization/production/refresh-scoped-rebuild-v1.cjs
// Refresh only this project's manifest; preserve the concurrent global rebuild index.
const fs=require('node:fs'),path=require('node:path');
const {build}=require('../../../scripts/build-rebuild-manifests.cjs');
const {git}=require('../../../scripts/media-policy.cjs');
const root=path.resolve(__dirname,'../../..');
const slug='player-customization';
function walk(dir){
 if(!fs.existsSync(path.join(root,dir)))return [];
 return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{
  if(e.isSymbolicLink()||/^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks)$/.test(e.name))return [];
  const f=dir+'/'+e.name;return e.isDirectory()?walk(f):[f];
 });
}
const indexPath=path.join(root,'projects/rebuild-index.json'),before=fs.readFileSync(indexPath);
const files=[...new Set([...git(['ls-files','--cached','--others','--exclude-standard','-z']).split('\0').filter(Boolean),...walk(`projects/${slug}`),...walk(`motion-canvas/src/projects/${slug}`)])].filter(f=>fs.existsSync(path.join(root,f))).sort();
const data=build(slug,files);fs.writeFileSync(path.join(root,`projects/${slug}/rebuild.json`),JSON.stringify(data,null,2)+'\n');
if(!fs.readFileSync(indexPath).equals(before))throw Error('The global rebuild index changed concurrently; it was not written by this script');
console.log(JSON.stringify({slug,counts:data.counts,globalRebuildIndexWritten:false}));
