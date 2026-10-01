// Stage only this completed additive revision and its necessary evidence.
const fs=require('node:fs'),path=require('node:path'),{execFileSync}=require('node:child_process');
const slug=process.argv[2];
if(!['praise-player','responsive-game-feedback'].includes(slug))throw Error('Explicit revision slug required');
const root=path.resolve(__dirname,'../../..'),base=`projects/${slug}`,allowed=new Set(['.cjs','.py','.json','.md','.ts','.tsx','.meta','.srt','.ass','.png','.jpg','.txt']);
const files=new Set();
function add(f){if(!fs.existsSync(path.join(root,f)))return;const ext=path.extname(f);if(!allowed.has(ext)||/\.info\.json$|(?:concat|filter|label|credit|title)\.txt$|\.log$/.test(f))return;files.add(f);}
function walk(dir){if(!fs.existsSync(path.join(root,dir)))return;for(const e of fs.readdirSync(path.join(root,dir),{withFileTypes:true})){const f=dir+'/'+e.name;if(e.isDirectory())walk(f);else add(f);}}
for(const f of ['project.json','rebuild.json','sources/SOURCES.md','sources/game-candidates.json','production/build-video.cjs','production/delivery-output.json','production/revision-v2.json'])add(base+'/'+f);
for(const e of fs.readdirSync(path.join(root,base,'production'))){if(/v2\.(cjs|py|json)$/.test(e)||e==='review-expanded-sources.py')add(base+'/production/'+e);}
walk(base+'/production/final-v2');walk(base+'/production/private-expansion-baseline');walk(`motion-canvas/src/projects/${slug}/expanded-v2`);
for(const e of fs.readdirSync(path.join(root,base,'publishing'))){if(e.includes('v2')&&e!=='proof-v2')add(base+'/publishing/'+e);}walk(base+'/publishing/proof-v2');
add(base+'/planning/expansion-v2.md');
for(const f of ['production/batches/private-review-expansion/queue.json','production/batches/sakurai-planning-game-design/queue.json',`production/batches/private-review-expansion/complete-${slug==='praise-player'?'praise':'responsive'}-v2.cjs`,'production/batches/private-review-expansion/select-revision-files.cjs'])add(f);
const list=[...files].sort();
if(!list.length)throw Error('No revision files');
for(let n=0;n<list.length;n+=40)execFileSync('git',['add','--',...list.slice(n,n+40)],{cwd:root,stdio:'pipe',windowsHide:true});
const staged=execFileSync('git',['diff','--cached','--name-only'],{cwd:root,encoding:'utf8'}).trim().split(/\r?\n/);
if(staged.some(f=>/\.(mp4|mkv|mov|webm|wav|mp3|m4a|flac|ogg|zip|7z|rar|gif)$|\.info\.json$/i.test(f)))throw Error('Disallowed media staged');
console.log(`Selected ${list.length} revision files; ${staged.length} total staged. Inspect diff before commit.`);
