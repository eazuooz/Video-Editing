// Validate every project in the Git index using the existing rebuild checker.
// Untracked concurrent projects remain the responsibility of their producer.
const fs=require('node:fs'),path=require('node:path');
const {git,root}=require('../../../scripts/media-policy.cjs');
const {build}=require('../../../scripts/build-rebuild-manifests.cjs');
const exists=f=>fs.existsSync(path.join(root,f));
const slugs=git(['ls-files','--cached','-z']).split('\0').filter(f=>/^projects\/[^/]+\/project\.json$/.test(f)).map(f=>f.split('/')[1]).sort();
if(!slugs.includes('game-reward-planning'))throw Error('Current delivery must be staged first');
function walk(dir){if(!exists(dir))return [];return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{
  if(e.isSymbolicLink()||/^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks)$/.test(e.name))return [];
  const f=dir+'/'+e.name;return e.isDirectory()?walk(f):[f];
});}
const files=[...new Set([...git(['ls-files','--cached','--others','--exclude-standard','-z']).split('\0').filter(Boolean),...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>walk('motion-canvas/src/projects/'+s))])].filter(exists).sort();
for(const slug of slugs){
  const rel='projects/'+slug+'/rebuild.json',actual=fs.readFileSync(path.join(root,rel),'utf8').replace(/^\uFEFF/,'').replace(/\r\n/g,'\n');
  if(actual!==JSON.stringify(build(slug,files),null,2)+'\n')throw Error('Stale delivery-scope rebuild: '+rel);
}
const excluded=fs.readdirSync(path.join(root,'projects')).filter(s=>exists('projects/'+s+'/project.json')&&!slugs.includes(s));
console.log(JSON.stringify({status:'passed',scope:'all-indexed-projects-plus-current-delivery',checkedProjects:slugs.length,untrackedConcurrentProjects:excluded,defaultCheckerUnchanged:true}));
