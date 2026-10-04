const fs=require('node:fs'),path=require('node:path'),cp=require('node:child_process'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..');
const result=cp.spawnSync('git',['diff','--cached','--check'],{cwd:root,encoding:'utf8'});
const paths=[...new Set([...result.stdout.matchAll(/^(.+?):\d+: (?:trailing whitespace|new blank line at EOF)\./gm)].map(x=>x[1]))];
const changes=[];
for(const rel of paths){
  if(!rel.startsWith('projects/game-reward-planning/')&&!rel.startsWith('production/batches/sakurai-planning-game-design/proof-game-reward-planning/'))throw Error('Unrelated whitespace must be preserved');
  const f=path.join(root,rel),original=fs.readFileSync(f),text=original.toString('utf8');
  const normalized=text.replace(/[ \t]+(?=\r?$)/gm,'').replace(/(?:\r?\n)+$/,'\n');
  if(normalized.replace(/\s/g,'')!==text.replace(/\s/g,''))throw Error('Semantic content changed');
  const backup=f+'.raw-original';if(!fs.existsSync(backup))fs.writeFileSync(backup,original);
  fs.writeFileSync(f,normalized);
  changes.push({path:rel,rawOriginalLocalBackup:rel+'.raw-original',originalSha256:crypto.createHash('sha256').update(original).digest('hex'),normalizedSha256:crypto.createHash('sha256').update(normalized).digest('hex')});
}
const audit='production/batches/sakurai-planning-game-design/proof-game-reward-planning/whitespace-normalization.json';
fs.writeFileSync(path.join(root,audit),JSON.stringify({at:new Date().toISOString(),scope:'Selected own diagnostic AX/initial templates/producer EOF only; all non-whitespace characters identical and original bytes retained locally.',changes},null,2)+'\n');
console.log(JSON.stringify({normalizedFiles:changes.length,semanticsPreserved:true,originalsRetainedLocally:true}));
