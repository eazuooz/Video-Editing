// Preserve exact captured accessibility text locally before whitespace cleanup.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../..');
const base='production/batches/sakurai-planning-game-design/proof-avoid-game-comparisons';
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const files=['existing-planning-evaluation-observed.ax.txt','source-original-observed.ax.txt','studio-comparison-search.ax.txt','studio-planning-search.ax.txt'];
const evidence=[];
for(const name of files){
  const file=path.join(root,base,name),raw=path.join(root,base,'research-local',name+'.raw-original');
  const captured=fs.readFileSync(file);
  if(!fs.existsSync(raw))fs.writeFileSync(raw,captured);
  const normalized=captured.toString('utf8').replace(/[\t ]+$/gm,'');
  fs.writeFileSync(file,normalized);
  evidence.push({path:base+'/'+name,rawLocalOnly:base+'/research-local/'+name+'.raw-original',rawSha256:hash(fs.readFileSync(raw)),normalizedSha256:hash(Buffer.from(normalized)),transformation:'Remove only trailing horizontal whitespace; preserve content, indentation and screenshots.',representation:name.startsWith('existing-')?'AX diff after pausing; full title/channel context in observed screenshot and earlier actual state':'Full AX snapshot'});
}
fs.writeFileSync(path.join(root,base,'ax-normalization.json'),JSON.stringify({recordedAt:new Date().toISOString(),rawCopiesExcludedFromGit:true,evidence},null,2)+'\n');
console.log('Four AX records normalized; exact original bytes preserved locally.');
