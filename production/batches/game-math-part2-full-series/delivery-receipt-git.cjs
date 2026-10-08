// Deliver a completed private-upload receipt without staging the next lecture.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug=process.argv[2];
const read=f=>JSON.parse(fs.readFileSync(path.join(root,f),'utf8').replace(/^\uFEFF/,''));
const run=(cmd,args,env=process.env,input)=>{const r=cp.spawnSync(cmd,args,{cwd:root,env,input,encoding:'utf8',windowsHide:true,maxBuffer:64e6});if(r.status!==0)throw Error(r.stderr+'\n'+r.stdout);return r.stdout.trimEnd();};
const git=(args,env,input)=>run('git',args,env,input);
const queueFile='production/batches/game-math-part2-full-series/queue.json',queue=read(queueFile),item=queue.items.find(x=>x.slug===slug);
if(!item)throw Error('Unknown lecture');
const receipt=read(`projects/${slug}/publishing/youtube-upload.json`),manifest=read(`projects/${slug}/project.json`),qa=read(`projects/${slug}/production/qa.json`);
if(!receipt.privateVisibilitySaveVerified||!receipt.fullPublishingSettingsComplete||!manifest.publishing.privateUploadComplete||!qa.fullDecodePassed||qa.directVisualReview?.status!=='passed')throw Error('Finish the actual reviewed private delivery first');
if(receipt.metadata.privacyStatus!=='private'||manifest.publishReady)throw Error('Private review state required');
for(const f of read(`projects/${slug}/production/delivery-output.json`).files){const data=fs.readFileSync(path.join(root,'output',slug,f.name));if(crypto.createHash('sha256').update(data).digest('hex')!==f.sha256)throw Error('Collected file changed');}
if(fs.existsSync(path.join(root,'.git/index.lock')))throw Error('Concurrent Git transaction; retry later');
const proofDir=`projects/${slug}/publishing/qa`;
const files=[`projects/${slug}/project.json`,`projects/${slug}/rebuild.json`,`projects/${slug}/publishing/youtube-upload.json`,`projects/${slug}/publish/assets/thumbnail-generation.json`,
 `projects/${slug}/publishing/qa/evidence-normalization.json`,
 'production/batches/game-math-part2-full-series/record-private-review.py','production/batches/game-math-part2-full-series/delivery-receipt-git.cjs',
 'production/batches/game-math-part2-full-series/README.md',
 ...fs.readdirSync(path.join(root,proofDir)).filter(f=>f.endsWith('.ax.txt')).map(f=>proofDir+'/'+f)];
const parent=git(['rev-parse','HEAD']),temp=fs.mkdtempSync(path.join(root,'.git','math-private-receipt-')),env={...process.env,GIT_INDEX_FILE:path.join(temp,'index')};
const mergeItem=text=>{const q=JSON.parse(text);const index=q.items.findIndex(x=>x.slug===slug);if(index<0)throw Error('Missing existing completed queue entry');q.items[index]=item;return JSON.stringify(q,null,2)+'\n';};
git(['read-tree',parent],env);git(['add','--',...files],env);
const blob=git(['hash-object','-w','--stdin'],env,mergeItem(git(['show',parent+':'+queueFile])));git(['update-index','--cacheinfo','100644',blob,queueFile],env);
const changed=git(['diff','--cached','--name-only',parent],env).split(/\r?\n/).filter(Boolean),allowed=new Set([...files,queueFile]);if(changed.some(f=>!allowed.has(f)))throw Error('Unrelated staged path');
git(['diff','--cached','--check',parent],env);
console.log(run(process.execPath,['scripts/media-policy.cjs'],env));console.log(run(process.execPath,['scripts/build-rebuild-manifests.cjs',slug,'--check'],env));
if(git(['rev-parse','HEAD'])!==parent)throw Error('Concurrent HEAD advanced; retry from new HEAD');
const tree=git(['write-tree'],env),commit=git(['commit-tree',tree,'-p',parent],env,`Verify private upload and bilingual publishing settings for ${slug}\n`);
git(['update-ref','HEAD',commit,parent]);
const own=changed.filter(f=>f!==queueFile);if(own.length)git(['restore','--staged','--source='+commit,'--',...own]);
const staged=git(['hash-object','-w','--stdin'],process.env,mergeItem(git(['show',':'+queueFile])));git(['update-index','--cacheinfo','100644',staged,queueFile]);
git(['push','origin',commit+':refs/heads/main']);const remote=git(['ls-remote','origin','refs/heads/main']).split(/\s/)[0];git(['merge-base','--is-ancestor',commit,remote]);
for(const f of files)git(['cat-file','-e',remote+':'+f]);
const proof={slug,commit,remoteCommit:remote,pushed:true,privateSettingsVerified:true,sourceOnly:true,isolatedIndex:true,files:changed.length,preservedOtherWork:true,recordedAt:new Date().toISOString()};
fs.writeFileSync(path.join(root,'tmp',slug+'-private-receipt-git.json'),JSON.stringify(proof,null,2)+'\n');
const current=read(queueFile),target=current.items.find(x=>x.slug===slug);target.gitPrivateReceiptEvidence=proof;fs.writeFileSync(path.join(root,queueFile),JSON.stringify(current,null,2)+'\n');console.log(JSON.stringify(proof));
