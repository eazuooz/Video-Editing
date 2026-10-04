// Exercise the real Git-index gate without touching shared staging or working files.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const temporary=fs.mkdtempSync(path.join(root,'.git','essential-image-gate-test-'));
const env={...process.env,GIT_INDEX_FILE:path.join(temporary,'index')};
function git(args,input){const r=spawnSync('git',args,{cwd:root,env,input,encoding:'utf8',windowsHide:true});assert.equal(r.status,0,r.stderr);return r.stdout.trim();}
function stage(file,content){const blob=git(['hash-object','-w','--stdin'],content);git(['update-index','--add','--cacheinfo','100644,'+blob+','+file]);}
function check(){return spawnSync(process.execPath,['scripts/media-policy.cjs'],{cwd:root,env,encoding:'utf8',windowsHide:true});}
const cases=[];
try{
  git(['read-tree','HEAD']);
  const file='production/essential-image-gate-fixture.JPG';
  const pixels=fs.readFileSync(path.join(root,'projects/game-reward-planning/publishing/thumbnail.png'));
  const registry=JSON.parse(fs.readFileSync(path.join(root,'shared/git-essential-images.json'),'utf8'));
  stage(file,pixels);stage('shared/git-essential-images.json',JSON.stringify(registry));
  let r=check();assert.equal(r.status,1);assert.match(r.stderr,/Unapproved new raster/);cases.push('unregistered uppercase JPG rejected');
  registry.entries.push({path:file,purpose:'minimal-publishing-proof',reason:'Isolated gate fixture using existing pixels; this is never committed as a production image.',reviewedAt:new Date().toISOString(),sha256:crypto.createHash('sha256').update(pixels).digest('hex')});
  stage('shared/git-essential-images.json',JSON.stringify(registry));r=check();assert.equal(r.status,0,r.stderr);cases.push('exact reviewed staged blob accepted');
  stage(file,Buffer.concat([pixels,Buffer.from('changed')]));r=check();assert.equal(r.status,1);assert.match(r.stderr,/differs from reviewed SHA256/);cases.push('changed staged pixels rejected');
  registry.entries[0].sha256=crypto.createHash('sha256').update(Buffer.concat([pixels,Buffer.from('changed')])).digest('hex');registry.entries[0].purpose='bulk-qa-frames';
  stage('shared/git-essential-images.json',JSON.stringify(registry));r=check();assert.equal(r.status,1);assert.match(r.stderr,/purpose/);cases.push('bulk QA purpose rejected');
  console.log(JSON.stringify({status:'passed',cases,sharedIndexNotModified:true,workingFilesNotModified:true}));
}finally{
  // Remove only files in the freshly allocated .git test directory, no recursion.
  assert.ok(path.resolve(temporary).startsWith(path.join(root,'.git')+path.sep));
  for(const name of fs.readdirSync(temporary)){const file=path.join(temporary,name);assert.ok(fs.statSync(file).isFile());fs.unlinkSync(file);}
  fs.rmdirSync(temporary);
}
