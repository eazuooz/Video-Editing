const fs=require('fs'),path=require('path');
const root=path.resolve(__dirname,'../../..'),dir=path.join(root,'production/batches/sakurai-planning-game-design/proof-game-reward-planning/source-research'),target=path.join(dir,'action-bank-v13.json');
if(fs.existsSync(target))throw Error('Preserve existing source-fit inspection');
const old=JSON.parse(fs.readFileSync(path.join(dir,'action-bank-v12.json'),'utf8')),full=JSON.parse(fs.readFileSync(path.join(dir,'action-bank-v1.json'),'utf8'));
const sources=full.sources.filter(x=>x.videoId==='ZTV0rPQ0_ik');if(sources.length!==1||old.cuts.some(c=>!sources.some(s=>s.videoId===c.sourceId)))throw Error('Source metadata unresolved');
fs.writeFileSync(target,JSON.stringify({...old,sources,createdAt:new Date().toISOString(),recovery:'v12 contained four requests but supplementary-bank metadata omitted the cooperative source, so its zero extracted frames are not inspection evidence. v13 restores the original verified source metadata; the inspector now rejects unresolved source IDs before running.'},null,2)+'\n');
console.log('v13 includes the full verified cooperative source metadata; v12 zero-frame record retained as invalid.');
