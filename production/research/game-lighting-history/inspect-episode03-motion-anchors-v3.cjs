const fs=require('node:fs'),path=require('node:path'),{makeCuesGlobal}=require('./caption-phrases-v2.cjs');
const root=path.resolve(__dirname,'../../..');
for(const scene of (process.argv.slice(2).length?process.argv.slice(2):['overview','12a','13b','14a','14b','16aa','16ab','conclusion'])){
 const r=JSON.parse(fs.readFileSync(path.join(root,`projects/game-lighting-history-03/production/local/voice-asr-v2/whole-${scene}.json`),'utf8')),cues=makeCuesGlobal(r);
 console.log(`SCENE ${scene} ${r.sourceFromSeconds}–${r.sourceToSeconds}`);
 for(let p=0;p<r.expectedKo.length;p++){
  const qs=cues.filter(c=>c.paragraph===p),lo=Math.min(...qs.map(c=>c.recognizerWordIndices[0])),hi=Math.max(...qs.map(c=>c.recognizerWordIndices[1]));
  console.log(`P${p+1} ${qs[0].from}–${qs.at(-1).to} EXPECT ${r.expectedKo[p]}`);
  console.log(r.chunks.slice(lo,hi+1).map(w=>`${w.timestamp.join('-')}:${w.text}`).join(' | '));
 }
}
