// Explicit isolated commit, followed by synchronization of only our shared-index
// paths. Never replace working registries or consume another task's staging.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug=process.argv[2];
const queue=JSON.parse(fs.readFileSync(path.join(__dirname,'queue.json'),'utf8').replace(/^\uFEFF/,''));
if(!queue.items.some(x=>x.slug===slug))throw Error('Unknown full-series lecture');
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const run=(command,args,env=process.env,input)=>{const r=cp.spawnSync(command,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:128e6});if(r.status!==0)throw Error(command+' failed: '+r.stderr+' '+r.stdout);return r.stdout.trimEnd();};
const git=(args,env,input)=>run('git',args,env,input);
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
if(fs.existsSync(path.join(root,'.git/index.lock')))throw Error('Another Git transaction is active; retry after it releases its lock. No working files changed.');
const qa=read(`projects/${slug}/production/qa.json`),delivery=read(`projects/${slug}/production/delivery-output.json`),manifest=read(`projects/${slug}/project.json`);
if(manifest.status!=='full-lecture-ready-for-private-review'||!qa.fullDecodePassed||qa.directVisualReview?.status!=='passed'||delivery.files.length!==4)throw Error('Finish the current full render, pixel review and four-file collection first');
for(const file of delivery.files){const actual=path.join(root,'output',slug,file.name);if(sha(fs.readFileSync(actual))!==file.sha256)throw Error('Collected delivery changed after QA: '+file.name);}
const parent=git(['rev-parse','HEAD']);
const bases=[`projects/${slug}`,`motion-canvas/src/projects/${slug}`,`manim/projects/${slug}`,'manim/projects/game-math-part2-full-series','production/batches/game-math-part2-full-series'];
const sourceExtensions=new Set(['.md','.json','.cjs','.py','.ps1','.ts','.tsx','.meta','.txt','.srt','.ass','.csv']);
function walk(dir){return fs.readdirSync(path.join(root,dir),{withFileTypes:true}).flatMap(e=>{
 if(e.isSymbolicLink()||/^(assets|__pycache__|delivery-history|delivery-stage-.*|media.*)$/.test(e.name))return dir===`projects/${slug}/publish`&&e.name==='assets'?walk(dir+'/assets'):[];
 const f=dir+'/'+e.name;return e.isDirectory()?walk(f):(sourceExtensions.has(path.extname(f))?[f]:[]);
});}
const files=[...bases.flatMap(walk),`production/preflight/${slug}.json`];
const thumb=`projects/${slug}/publish/assets/thumbnail.png`,entry=`./src/projects/${slug}/project.ts`,exception='!'+thumb;
const image=read('shared/git-essential-images.json').entries.find(x=>x.path===thumb);
if(!image||image.purpose!=='delivery-thumbnail'||image.sha256!==sha(fs.readFileSync(path.join(root,thumb))))throw Error('Review and register the exact essential thumbnail first');
files.push(thumb);
const special=['motion-canvas/projects.json','projects/rebuild-index.json','shared/git-essential-images.json','.gitignore'];
function mergeOwn(f,text){
 if(f==='.gitignore')return text.split(/\r?\n/).includes(exception)?text:text.trimEnd()+'\n'+exception+'\n';
 const value=JSON.parse(text);
 if(f===special[0]){if(!value.includes(entry))value.push(entry);}
 else if(f===special[1]){if(!value.projects.some(x=>x.slug===slug))value.projects.push({slug,manifest:`projects/${slug}/rebuild.json`});}
 else {const found=value.entries.find(x=>x.path===thumb);if(found&&found.sha256!==image.sha256)throw Error('Conflicting reviewed image hash');if(!found)value.entries.push(image);}
 return JSON.stringify(value,null,2)+'\n';
}
const temporary=fs.mkdtempSync(path.join(root,'.git','game-math-series-delivery-'));
const env={...process.env,GIT_INDEX_FILE:path.join(temporary,'index')};
git(['read-tree',parent],env);git(['add','--',...files],env);
for(const f of special){const value=mergeOwn(f,git(['show',parent+':'+f]));const blob=git(['hash-object','-w','--stdin'],env,value);git(['update-index','--add','--cacheinfo','100644',blob,f],env);}
const changes=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),rows=[];
for(let i=0;i<changes.length;i+=2)rows.push({status:changes[i],path:changes[i+1]});
const allowed=new Set([...files,...special]);if(rows.some(r=>!allowed.has(r.path)||r.status==='D'))throw Error('Unexpected path or deletion in isolated production delivery');
git(['diff','--cached','--check',parent],env);
console.log(run(process.execPath,['scripts/media-policy.cjs'],env));
console.log(run(process.execPath,['scripts/build-rebuild-manifests.cjs',slug,'--check'],env));
if(git(['rev-parse','HEAD'])!==parent)throw Error('Concurrent HEAD advanced; prepare a fresh isolated production tree. Working files preserved.');
const tree=git(['write-tree'],env);
const message=`Deliver ${read(`projects/${slug}/project.json`).titles.en} with verified captions and no music`;
const commit=git(['commit-tree',tree,'-p',parent],env,message+'\n');git(['update-ref','HEAD',commit,parent]);
const ownChanged=rows.filter(r=>!special.includes(r.path)).map(r=>r.path);
if(ownChanged.length)git(['restore','--staged','--source='+commit,'--',...ownChanged]);
// Preserve unrelated staged edits in shared files while adding only this
// completed lecture's entry. The working versions are never replaced.
for(const f of special){const current=git(['show',':'+f]);const value=mergeOwn(f,current);const blob=git(['hash-object','-w','--stdin'],process.env,value);git(['update-index','--add','--cacheinfo','100644',blob,f]);}
git(['push','origin',commit+':refs/heads/main']);
const remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
git(['merge-base','--is-ancestor',commit,remote]);for(const f of files)git(['cat-file','-e',remote+':'+f]);
const proof={slug,commit,remoteCommit:remote,pushed:true,sourceOnly:true,files:rows.length,preservedOtherWork:true,
 isolatedIndex:true,sharedIndexOwnPathsSynchronized:true,sharedRegistryOtherEditsPreserved:true,
 deliveredFilesVerifiedInRemoteTree:true,essentialRasterPaths:[thumb],recordedAt:new Date().toISOString()};
fs.writeFileSync(path.join(root,'tmp',slug+'-git-delivery.json'),JSON.stringify(proof,null,2)+'\n');
console.log(JSON.stringify(proof));
const currentQueue=read('production/batches/game-math-part2-full-series/queue.json'),item=currentQueue.items.find(x=>x.slug===slug);
item.gitDelivered=true;item.gitEvidence=proof;fs.writeFileSync(path.join(__dirname,'queue.json'),JSON.stringify(currentQueue,null,2)+'\n');
