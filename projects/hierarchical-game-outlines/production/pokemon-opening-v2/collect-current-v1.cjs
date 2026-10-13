// Invoke the repository collector once, guarding shared index bytes and foreign rebuilds.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../../..'),slug='hierarchical-game-outlines',P=path.relative(root,__dirname).replaceAll('\\','/');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const hash=f=>sha(fs.readFileSync(path.join(root,f)));
const proof=path.join(__dirname,'collection-verification-v1.json');if(fs.existsSync(proof))throw Error('Existing collection outcome; never repeat blindly.');
const foreign=fs.readdirSync(path.join(root,'projects')).filter(s=>s!==slug).map(s=>'projects/'+s+'/rebuild.json').filter(f=>fs.existsSync(path.join(root,f))).map(f=>({path:f,sha256:hash(f)}));
const shared=path.join(root,'projects/rebuild-index.json'),before=fs.readFileSync(shared);
const git=cp.spawnSync('git',['rev-parse','--git-path','index'],{cwd:root,encoding:'utf8',windowsHide:true});if(git.status)throw Error(git.stderr);
const ext=path.resolve(root,git.stdout.trim()),extBytes=fs.readFileSync(ext);
const real=fs.writeFileSync;let noOp=false;
fs.writeFileSync=function(p,data,...args){
 if(typeof p!=='number'&&path.resolve(String(p)).toLowerCase()===shared.toLowerCase()){
  const intended=Buffer.isBuffer(data)?data:Buffer.from(data,'utf8'),norm=b=>b.toString('utf8').replace(/^\uFEFF/,'').replace(/\r\n/g,'\n');
  if(!fs.readFileSync(shared).equals(before)||norm(before)!==norm(intended))throw Error('Shared rebuild index changed or would differ; preserve it.');
  noOp=true;return;
 }
 return real.call(fs,p,data,...args);
};
process.argv[2]=slug;
process.on('beforeExit',()=>{
 fs.writeFileSync=real;
 const unchanged=before.equals(fs.readFileSync(shared))&&extBytes.equals(fs.readFileSync(ext))&&foreign.every(f=>hash(f.path)===f.sha256);
 const outcome={at:new Date().toISOString(),collector:'scripts/collect-video-output.cjs',ownSlug:slug,sharedIndexWriteNoop:noOp,externalIndexUnchanged:extBytes.equals(fs.readFileSync(ext)),sharedIndexUnchanged:before.equals(fs.readFileSync(shared)),foreignRebuilds:foreign,foreignRebuildsUnchanged:foreign.every(f=>hash(f.path)===f.sha256),exitCode:process.exitCode||0,files:[]};
 if(!unchanged){outcome.exitCode=1;process.exitCode=1;outcome.error='Preservation check failed; inspect without restore.';}
 if(!process.exitCode){
  const delivery=JSON.parse(fs.readFileSync(path.join(root,'projects/'+slug+'/production/delivery-output.json'),'utf8'));
  for(const f of delivery.files){const target=delivery.directory+'/'+f.name;if(hash(target)!==f.sha256||hash(f.source)!==f.sha256)throw Error('Four-file SHA mismatch');outcome.files.push({path:target,sha256:f.sha256,bytes:f.bytes});}
 }
 fs.writeFileSync(proof,JSON.stringify(outcome,null,2)+'\n');
 console.log(JSON.stringify({preservation:unchanged,sharedWriteNoop:noOp,foreignRebuilds:foreign.length,files:outcome.files.length,exitCode:outcome.exitCode}));
});
require(path.join(root,'scripts/collect-video-output.cjs'));
