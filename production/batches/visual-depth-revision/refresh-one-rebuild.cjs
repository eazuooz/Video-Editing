// Refresh one authorized project's rebuild record without changing the shared global index.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),slug=process.argv[2];
const queue=JSON.parse(fs.readFileSync(path.join(__dirname,'queue.json'),'utf8'));
if(!queue.scope.includes(slug))throw Error('Outside the authorized scope');
const index=path.join(root,'projects/rebuild-index.json'),before=fs.readFileSync(index),original=fs.writeFileSync;
fs.writeFileSync=function(file,...args){
 if(path.resolve(file)===index)return;
 if(path.resolve(file)===path.join(root,`projects/${slug}/rebuild.json`)){
  const temp=path.join(root,`projects/${slug}/rebuild-depth-${crypto.randomUUID()}.tmp`);
  original.call(fs,temp,...args); fs.renameSync(temp,file); return;
 }
 return original.call(fs,file,...args);
};
try{require(path.join(root,'scripts/build-rebuild-manifests.cjs')).generate(slug);}finally{fs.writeFileSync=original;}
if(!before.equals(fs.readFileSync(index)))throw Error('Shared global rebuild index changed');
console.log('Shared rebuild index preserved: '+crypto.createHash('sha256').update(before).digest('hex'));
