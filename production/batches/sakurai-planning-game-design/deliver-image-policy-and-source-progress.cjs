// Explicit, isolated-index delivery. Never consume another task's shared staging.
// Usage: node <this-file> --prepare | --commit <prepared-record.json>
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='production/batches/sakurai-planning-game-design';
const own=[
  '.gitignore','AGENTS.md','docs/MEDIA_STORAGE.md','scripts/media-policy.cjs',
  'scripts/test-media-policy.cjs','scripts/test-essential-image-gate.cjs','scripts/audit-video-batch-images.cjs',
  'shared/git-essential-images.json',base+'/image-git-cleanup-20261005.json',
  base+'/deliver-image-policy-and-source-progress.cjs',base+'/rebuild-image-policy-scope.cjs',
  base+'/refresh-gate-after-receipt-change.cjs',base+'/record-followup-push-runtime.cjs',
  base+'/thumbnail-followup-git-verification-latest.json',base+'/image-policy-pre-delivery-checks.json',base+'/queue.json',
  base+'/preflight/avoid-game-comparisons.json',base+'/proof-avoid-game-comparisons/content-review.json',
  base+'/proof-avoid-game-comparisons/latest-checkpoint.json',
  base+'/proof-avoid-game-comparisons/source-candidates-and-usage-review.json',
  ...['acquisition.json','discovery.json','direct-discovery-review.json','extract-discovery.py','record-direct-discovery-review.cjs'].map(f=>base+'/proof-avoid-game-comparisons/source-research/'+f)
];
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function run(command,args,env=process.env,input){const r=cp.spawnSync(command,args,{cwd:root,env,input,encoding:'utf8',maxBuffer:128e6,windowsHide:true});if(r.status!==0)throw Error(command+' '+args.join(' ')+' failed:\n'+r.stdout+'\n'+r.stderr);return r.stdout.trimEnd();}
const git=(args,env,input)=>run('git',args,env,input);
function chunks(items,size=20){return Array.from({length:Math.ceil(items.length/size)},(_,i)=>items.slice(i*size,(i+1)*size));}
function verifyLocal(records){for(const r of records){const absolute=path.resolve(root,r.path);if(!absolute.startsWith(root+path.sep)||!fs.existsSync(absolute)||sha(fs.readFileSync(absolute))!==r.localSha256)throw Error('Local image missing/changed: '+r.path);}}
const argv=process.argv.slice(2);
if(argv[0]==='--prepare'){
  const parent=git(['rev-parse','HEAD']);
  const audit=JSON.parse(fs.readFileSync(path.join(root,base+'/image-git-cleanup-20261005.json'),'utf8'));
  if(audit.candidateCount!==350||audit.candidates.length!==350)throw Error('Unexpected audited scope.');
  verifyLocal(audit.candidates);
  const tree=new Map(git(['ls-tree','-r','-z',parent]).split('\0').filter(Boolean).map(row=>{const m=row.match(/^(\d+) blob ([a-f0-9]+)\t(.+)$/s);return m?[m[3],{mode:m[1],blob:m[2]}]:[row,null];}));
  for(const r of audit.candidates)if(tree.get(r.path)?.blob!==r.gitBlob||tree.get(r.path)?.mode!==r.mode)throw Error('Audited Git image changed: '+r.path);
  const targets=[...new Set(audit.candidates.map(r=>r.path.split('/')[1]))].sort();
  if(targets.length!==10)throw Error('Unexpected completed project scope.');
  const selected=[...own,...targets.map(s=>'projects/'+s+'/rebuild.json')];
  if(selected.some(f=>/\.(?:png|jpe?g|webp|gif|bmp|tiff?)$/i.test(f)))throw Error('No new raster belongs in this delivery.');
  const proofPath=base+'/image-policy-pre-delivery-checks.json';
  fs.writeFileSync(path.join(root,proofPath),JSON.stringify({status:'checks-running',parent},null,2)+'\n');
  const temporary=fs.mkdtempSync(path.join(root,'.git','batch-source-image-delivery-'));
  const env={...process.env,GIT_INDEX_FILE:path.join(temporary,'index')};
  git(['read-tree',parent],env);
  for(const paths of chunks(selected))git(['add','--',...paths],env);
  for(const paths of chunks(audit.candidates.map(r=>r.path)))git(['update-index','--force-remove','--',...paths],env);
  const changes=git(['diff','--cached','--name-status','-z',parent],env).split('\0').filter(Boolean),rows=[];
  for(let i=0;i<changes.length;i+=2)rows.push({status:changes[i],path:changes[i+1]});
  const removals=new Set(audit.candidates.map(r=>r.path)),allowed=new Set([...selected,...removals]);
  if(rows.some(r=>!allowed.has(r.path)||r.status==='D'&&!removals.has(r.path)||removals.has(r.path)&&r.status!=='D'))throw Error('Unapproved staged path or removal.');
  if(rows.filter(r=>r.status==='D').length!==350||rows.some(r=>r.status==='A'&&/\.(png|jpe?g|webp|gif|bmp|tiff?)$/i.test(r.path)))throw Error('Image change counts differ.');
  const checks=[];
  function node(args){const output=run(process.execPath,args,env);checks.push({command:'node '+args.join(' '),exitCode:0,output});console.log(output);}
  node(['scripts/media-policy.cjs']);node(['scripts/test-media-policy.cjs','--rules-only']);node(['scripts/test-essential-image-gate.cjs']);
  for(const slug of targets)node(['scripts/build-rebuild-manifests.cjs',slug,'--check']);
  node(['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check']);
  git(['diff','--cached','--check',parent],env);checks.push({command:'git diff --cached --check '+parent,exitCode:0});
  verifyLocal(audit.candidates);
  const record={schemaVersion:1,status:'passed',preparedAt:new Date().toISOString(),parent,temporaryIndex:env.GIT_INDEX_FILE,selected,changes:rows,removedRasterCount:350,newRasterCount:0,localImagesPreserved:true,sharedIndexConsumed:false,checks};
  const proof={...record,temporaryIndex:'machine-local isolated index; not a rebuild input'};
  fs.writeFileSync(path.join(root,proofPath),JSON.stringify(proof,null,2)+'\n');
  git(['add','--',proofPath],env);git(['diff','--cached','--check',parent],env);
  record.workingHashes=Object.fromEntries(selected.map(f=>[f,sha(fs.readFileSync(path.join(root,f)))]));record.tree=git(['write-tree'],env);
  const file=path.join(temporary,'prepared.json');fs.writeFileSync(file,JSON.stringify(record,null,2)+'\n');
  console.log(JSON.stringify({preparedRecord:file,parent,changes:rows.length,removedRaster:350,newRaster:0,checks:checks.length,tree:record.tree}));
}else if(argv[0]==='--commit'){
  const file=path.resolve(argv[1]||'');if(!file.startsWith(path.join(root,'.git','batch-source-image-delivery-')))throw Error('Invalid prepared record path.');
  const record=JSON.parse(fs.readFileSync(file,'utf8')),env={...process.env,GIT_INDEX_FILE:record.temporaryIndex};
  if(git(['rev-parse','HEAD'])!==record.parent)throw Error('Concurrent HEAD advanced; prepare a fresh explicit tree.');
  for(const f of record.selected)if(sha(fs.readFileSync(path.join(root,f)))!==record.workingHashes[f])throw Error('Selected file changed after checks: '+f);
  if(git(['write-tree'],env)!==record.tree)throw Error('Prepared index changed.');
  verifyLocal(JSON.parse(fs.readFileSync(path.join(root,base+'/image-git-cleanup-20261005.json'),'utf8')).candidates);
  const message='Keep essential images only and deliver reviewed video source progress\n\nRemove 350 reproducible QA images from the Git tree while preserving every local file. Default new raster images to local storage and check reviewed essential-image records. Preserve current private thumbnail completion, source-action discovery and duplicate review. Use an explicit isolated index without other tasks staging.\n';
  const commit=git(['commit-tree',record.tree,'-p',record.parent],env,message+'\n');
  git(['update-ref','HEAD',commit,record.parent]);
  // Synchronize only our paths to the new HEAD. This does not touch working files.
  for(const paths of chunks(record.changes.map(r=>r.path)))git(['restore','--staged','--source='+commit,'--',...paths]);
  verifyLocal(JSON.parse(fs.readFileSync(path.join(root,base+'/image-git-cleanup-20261005.json'),'utf8')).candidates);
  record.commit=commit;record.committedAt=new Date().toISOString();fs.writeFileSync(file,JSON.stringify(record,null,2)+'\n');
  console.log(JSON.stringify({commit,parent:record.parent,removedRaster:350,newRaster:0,localImagesPreserved:true,normalChildCommit:true,forcePush:false,sharedIndexOtherPathsPreserved:true,preparedRecord:file}));
}else throw Error('Use --prepare or --commit <prepared-record.json>.');
