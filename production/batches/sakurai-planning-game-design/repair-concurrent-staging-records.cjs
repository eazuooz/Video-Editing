// Correct only accidental removals in our already-pushed commit.
// Uses a separate temporary Git index; never edits working files or shared staging.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),bad='18319f811eda4817c5859faea6ac3f8d95819bc1';
function git(args,opts={}){const r=cp.spawnSync('git',args,{cwd:root,encoding:'utf8',...opts});if(r.status!==0)throw Error(args.join(' ')+'\n'+r.stderr);return r.stdout.trimEnd();}
const head=git(['rev-parse','HEAD']);git(['merge-base','--is-ancestor',bad,head]);
const removed=git(['diff-tree','--no-commit-id','--diff-filter=D','--name-only','-r',bad]).split('\n').filter(Boolean);
const allowed=/^(?:manim\/projects\/game-math-polar-(?:2d|lecture)\/|motion-canvas\/src\/projects\/game-math-polar-2d\/|production\/batches\/game-math-polar-lecture\/|production\/preflight\/game-math-polar-2d\.json$|projects\/game-math-polar-2d\/)/;
if(removed.some(p=>!allowed.test(p)))throw Error('Unexpected removal outside the observed concurrent lecture');
const stillMissing=removed.filter(p=>cp.spawnSync('git',['cat-file','-e',head+':'+p],{cwd:root,stdio:'ignore'}).status!==0);
if(!stillMissing.length)throw Error('Already restored: no repair necessary');
const workingHashes=Object.fromEntries(stillMissing.map(p=>{const file=path.join(root,p);if(!fs.existsSync(file))throw Error('Working file absent: '+p);return [p,crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')];}));
const index=path.join(root,'.git','thumbnail-followup-repair-'+process.pid+'.index'),env={...process.env,GIT_INDEX_FILE:index};
git(['read-tree',head],{env});
const parent=git(['rev-parse',bad+'^']);
for(const p of stillMissing){const row=git(['ls-tree',parent,'--',p]);const m=row.match(/^(\d+) blob ([a-f0-9]+)\t/);if(!m)throw Error('No prior blob: '+p);git(['update-index','--add','--cacheinfo',m[1]+','+m[2]+','+p],{env});}
const recordPath='production/batches/sakurai-planning-game-design/concurrent-staging-repair-20261004.json';
const record={schemaVersion:1,recordedAt:new Date().toISOString(),accidentalCommit:bad,parentContainingConcurrentLecture:parent,remoteObservedAtDetection:bad,repairParent:head,restoreCount:stillMissing.length,restoredFromOriginalParent:stillMissing,workingFilesNotModified:true,sharedIndexNotModified:true,historyRewrite:false,forcePush:false,scope:'Restore only observed accidental deletions. Current shared registration files and all unrelated current changes are preserved.',remainingAction:'Normal push and actual local/remote SHA verification required.'};
const blob=git(['hash-object','-w','--stdin'],{input:JSON.stringify(record,null,2)+'\n'});
git(['update-index','--add','--cacheinfo','100644,'+blob+','+recordPath],{env});
const own='production/batches/sakurai-planning-game-design/repair-concurrent-staging-records.cjs';
git(['add','--',own],{env});
const media=cp.spawnSync(process.execPath,['scripts/media-policy.cjs'],{cwd:root,env,encoding:'utf8'});if(media.status!==0)throw Error(media.stdout+media.stderr);
git(['diff','--cached','--check'],{env});
const tree=git(['write-tree'],{env});
const changes=git(['diff','--name-only',head,tree]).split('\n').filter(Boolean);
const expected=new Set([...stillMissing,recordPath,own]);if(changes.length!==expected.size||changes.some(p=>!expected.has(p)))throw Error('Repair tree has unrelated paths');
for(const p of stillMissing){if(git(['rev-parse',tree+':'+p])!==git(['rev-parse',parent+':'+p]))throw Error('Restored blob differs: '+p);if(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')!==workingHashes[p])throw Error('Concurrent working file changed; re-audit '+p);}
const commit=git(['commit-tree',tree,'-p',head,'-m','Restore concurrent polar lecture records after shared-index collision']);
git(['update-ref','-m','restore only accidental concurrent removals','HEAD',commit,head]);
fs.writeFileSync(path.join(root,recordPath),JSON.stringify(record,null,2)+'\n');
console.log(JSON.stringify({status:'restored-with-normal-child-commit',parent:head,commit,restored:stillMissing.length,sharedIndexNotModified:true,mediaCheck:media.stdout.trim(),nextAction:'git push origin main; compare actual remote SHA'}));
