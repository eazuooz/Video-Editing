// Recover the already-created commit after a transient GitHub 500. Never creates a commit.
const fs=require('node:fs'),cp=require('node:child_process'),path=require('node:path');
const root=path.resolve(__dirname,'../../..');
const git=(args,env=process.env)=>{const r=cp.spawnSync('git',args,{cwd:root,env,encoding:'utf8',windowsHide:true});if(r.status)throw Error(r.stderr);return r.stdout.trimEnd();};
const commit='b71cf90dbc098655e5a080a5687cd9c3055fc109';
const index=path.join(root,'.git/depth-delivery-6tBUFb/index');
const env={...process.env,GIT_INDEX_FILE:index};
const local=git(['rev-parse','HEAD']),remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];
if(local!==commit||remote!==commit)throw Error('Existing delivery commit must equal actual local and remote');
if(git(['write-tree'],env)!==git(['rev-parse',commit+'^{tree}']))throw Error('Original isolated index differs from committed tree');
const parent=git(['rev-parse',commit+'^']);
const paths=git(['diff-tree','--no-commit-id','--name-only','-r',commit]).split('\n').filter(Boolean);
for(const p of paths)if(git(['rev-parse',remote+':'+p])!==git(['rev-parse',':'+p],env))throw Error('Remote blob mismatch: '+p);
const proof={schemaVersion:1,slug:'picking-sides',commit,parent,localCommit:local,remoteCommit:remote,temporaryIndex:index,stagedPaths:paths,changedPathCount:paths.length,exactLocalRemoteMatch:true,remoteBlobsVerified:true,pushed:true,essentialRasterPaths:paths.filter(p=>/\.(png|jpe?g|webp|gif|bmp|tiff?)$/i.test(p)),mediaCheck:true,scopedRebuildCheck:true,externalIndexUnchangedBeforeCommit:true,unrelatedIndexEntriesPreserved:true,ownIndexPathsSynchronized:true,checksSource:'Actual deliver-reviewed-source.cjs execution before commit; push alone failed afterwards',pushFailureHistory:[{at:'2026-10-07T16:56:16Z',reason:'GitHub Internal Server Error',requestId:'DB25:94466:D004C:14B7CE:6AC679AD',commitPreserved:true}],recovery:'Normal push of the same existing commit succeeded; no duplicate commit',verifiedAt:new Date().toISOString()};
fs.writeFileSync(path.join(__dirname,'git-delivery-picking-sides.json'),JSON.stringify(proof,null,2)+'\n');
const qpath=path.join(__dirname,'queue.json'),q=JSON.parse(fs.readFileSync(qpath,'utf8'));Object.assign(q.items.find(i=>i.slug==='picking-sides'),{gitDelivered:true,gitCommit:commit,remoteCommit:remote,gitVerification:'production/batches/visual-depth-revision/git-delivery-picking-sides.json'});fs.writeFileSync(qpath,JSON.stringify(q,null,2)+'\n');
console.log(JSON.stringify({commit,remote,paths:paths.length,raster:proof.essentialRasterPaths,recovered:true}));
