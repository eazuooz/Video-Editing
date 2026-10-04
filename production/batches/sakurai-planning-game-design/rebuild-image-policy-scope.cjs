// Metadata only: preserve the shared project index and all render/audio outputs.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const {build}=require(path.join(root,'scripts/build-rebuild-manifests.cjs'));
const audit=JSON.parse(fs.readFileSync(path.join(__dirname,'image-git-cleanup-20261005.json'),'utf8'));
const targets=[...new Set(audit.candidates.map(r=>r.path.split('/')[1]))].sort();
if(targets.length!==10)throw Error('Expected exactly the ten completed batch projects.');
const exists=f=>fs.existsSync(path.join(root,f));
function walk(dir){if(!exists(dir))return [];return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name)).flatMap(e=>{if(e.isSymbolicLink()||/^(node_modules|\.git|\.venv|delivery-history|delivery-stage-.*|media.*|chunks)$/.test(e.name))return [];const f=dir+'/'+e.name;return e.isDirectory()?walk(f):[f];});}
const slugs=fs.readdirSync(path.join(root,'projects')).filter(s=>exists('projects/'+s+'/project.json')).sort();
const listed=cp.execFileSync('git',['ls-files','--cached','--others','--exclude-standard','-z'],{cwd:root,encoding:'utf8',maxBuffer:128e6}).split('\0').filter(Boolean);
const files=[...new Set([...listed,...slugs.flatMap(s=>walk('projects/'+s)),...slugs.flatMap(s=>walk('motion-canvas/src/projects/'+s))])].filter(exists).sort();
const index=fs.readFileSync(path.join(root,'projects/rebuild-index.json'));
for(const slug of targets){const data=build(slug,files);fs.writeFileSync(path.join(root,'projects/'+slug+'/rebuild.json'),JSON.stringify(data,null,2)+'\n');console.log(slug+': '+JSON.stringify(data.counts));}
if(!index.equals(fs.readFileSync(path.join(root,'projects/rebuild-index.json'))))throw Error('Shared project index changed.');
console.log('Scoped metadata rebuilt; shared index SHA256 '+crypto.createHash('sha256').update(index).digest('hex')+' preserved. No synthesis/render/collection.');
