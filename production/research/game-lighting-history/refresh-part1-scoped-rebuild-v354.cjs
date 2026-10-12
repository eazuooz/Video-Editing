// Reuse the official builder but write only the owned manifest.
// The global rebuild-index.json is locked by unrelated activity; never replace it.
const fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const {build}=require(path.join(root,'scripts/build-rebuild-manifests.cjs'));
const {git}=require(path.join(root,'scripts/media-policy.cjs'));
const exists=f=>fs.existsSync(path.join(root,f));
function walk(dir){if(!exists(dir))return[];return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{if(e.isSymbolicLink()||/^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks)$/.test(e.name))return[];const f=dir+'/'+e.name;return e.isDirectory()?walk(f):[f];});}
const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>exists('projects/'+s+'/project.json')).sort();
const files=[...new Set([...git(['ls-files','--cached','--others','--exclude-standard','-z']).split('\0').filter(Boolean),...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>walk('motion-canvas/src/projects/'+s))])].filter(exists).sort();
const slug='game-lighting-history-04-1',data=build(slug,files);
fs.writeFileSync(path.join(root,'projects/'+slug+'/rebuild.json'),JSON.stringify(data,null,2)+'\n');
console.log(JSON.stringify({scope:slug,counts:data.counts,globalIndexWritten:false,foreignManifestsWritten:0},null,2));
