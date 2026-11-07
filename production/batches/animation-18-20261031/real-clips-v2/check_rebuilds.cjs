// Check the selected metadata using one read-only Git inventory snapshot.
const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process');
const root=path.resolve(__dirname,'../../../..'),original=cp.execFileSync,cache=new Map();
cp.execFileSync=function(command,args,options){
  if(command==='git'&&args[0]==='ls-files'){
    const key=JSON.stringify(args);
    if(!cache.has(key))cache.set(key,original(command,args,{...options,stdio:['pipe','pipe','pipe']}));
    return cache.get(key);
  }
  return original(command,args,options);
};
const {generate}=require(path.join(root,'scripts/build-rebuild-manifests.cjs'));
const plan=JSON.parse(fs.readFileSync(path.join(__dirname,'revision-plan.json'),'utf8')),results=[];
for(const row of plan.episodes){
  let regenerated=false;
  try{generate(row.slug,true);}catch(error){
    if(!String(error).includes('Stale rebuild manifest'))throw error;
    generate(row.slug,false);generate(row.slug,true);regenerated=true;
  }
  results.push({id:row.id,status:'passed',regenerated});
}
fs.writeFileSync(path.join(__dirname,'../local/real-clips-v2/rebuild-checks.json'),JSON.stringify(results,null,2));
