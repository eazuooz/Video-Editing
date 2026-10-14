// Literal captions aligned to observed words. This draft grants no audio/pixel approval.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {alignOriginalCharacters}=require('./episode04-caption-alignment-v1.cjs');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const reviewPath=b+'part1-current-asr-direct-review-v223.json',review=read(reviewPath),state=read(b+'part1-current-asr-results-v223.json');
if(!review.all74FullTextsDirectlyCompared||!review.all74WordTimestampsDirectlyRead||state.completed.length!==74||state.exitCode!==0)throw Error('All actual74 texts/timestamps and closed execution required');
const captions=read(b+'part1-caption-phrases-v194.json'),selected=read(b+'part1-selected-current-tts-execution-v219.json');
const aliases=[['도시계','도식의'],['앞에','앞의'],['그때의','그때'],['여기에','여기의'],['그자리에','그자리의'],['그자리','그 자리'],['무늬','무늬'],['문의','무늬'],['자상','자산'],['자사','자산'],['변이','변위'],['얄은','얇은'],['가수','자수'],['붕기','분기'],['뒤에','뒤의'],['세이더','셰이더'],['쉐이더','셰이더'],['쉐이딩','셰이딩'],['안에','안의'],['네 종','4종'],['디엘에스에스','DLSS']];
const pending=new Set();
const wordsFor=id=>{
 const label=(id==='tsr-rotation-vectors'?'context-':'whole-')+id,d=state.completed.find(x=>x.label===label);if(!d)throw Error('Missing '+label);
 if(ref(d.result).sha256!==d.sha256)throw Error('Result changed '+label);
 const r=read(d.result),take=selected.results.find(x=>x.id===id);if(!take||ref(take.path).sha256!==take.sha256)throw Error('Take changed '+id);
 let words=r.chunks,offset=0;
 if(id==='tsr-rotation-vectors'){
  const sr=r.sourceRanges.find(x=>x.id===id);if(!sr||sr.source.sha256!==take.sha256||sr.source.sampleRange[0]!==0||sr.source.sampleRange[1]!==take.samples)throw Error('Current fan context binding required');
  offset=sr.windowSampleRange[0]/r.sampleRate;
  words=words.filter(w=>(w.timestamp[0]+w.timestamp[1])/2>=offset-.01&&(w.timestamp[0]+w.timestamp[1])/2<=offset+take.seconds+.01).map(w=>({text:w.text,timestamp:w.timestamp.map(t=>Math.max(0,Math.min(take.seconds,t-offset)))}));
 }
 if(words.some((w,i)=>!w.timestamp||w.timestamp[1]<w.timestamp[0]||(i&&w.timestamp[0]<words[i-1].timestamp[0]-.01)))throw Error('Backward word times '+id);
 return{words,take,result:ref(d.result),offset,sourceRanges:r.sourceRanges};
};
const rows=captions.rows.map(row=>{
 if(pending.has(row.id))return{id:row.id,ko:row.ko,status:'unchanged-onset-repair-pending',captionApproval:false};
 const {words,take,result,offset,sourceRanges}=wordsFor(row.id),a=alignOriginalCharacters(row.ko,words,aliases);
 const bounds=span=>{
  const matches=a.matching.filter((m,i)=>m!==null&&a.original.map[i]>=span[0]&&a.original.map[i]<span[1]);if(!matches.length)throw Error('No word anchor '+row.id);
  const lo=Math.min(...matches),hi=Math.max(...matches);return{from:words[lo].timestamp[0],to:words[hi].timestamp[1],recognizerWordIndices:[lo,hi]};
 };
 const cues=row.cues.map(c=>({...c,...bounds(c.sourceCharacters),timingDirectlyReviewed:false,pixelsReviewed:false}));
 const corrections=[];
 for(let i=1;i<cues.length;i++)if(cues[i].from<cues[i-1].to){const boundary=(cues[i].from+cues[i-1].to)/2;corrections.push({first:i,second:i+1,previousEnd:cues[i-1].to,nextStart:cues[i].from,boundary,method:'midpoint of overlapping recognizer word boundaries; no changed PCM'});cues[i-1].to=boundary;cues[i].from=boundary;}
 for(const c of cues){c.fromFrame=Math.round(c.from*60);c.toFrame=Math.round(c.to*60);if(c.toFrame<=c.fromFrame)throw Error('Empty cue '+row.id);}
 const sentences=[...row.ko.matchAll(/[^.!?]+(?:[.!?](?!\d)|$)/g)].map(m=>{const leading=m[0].length-m[0].trimStart().length,span=[m.index+leading,m.index+m[0].length];return{text:m[0].trim(),sourceCharacters:span,...bounds(span)};});
 return{id:row.id,status:'literal-word-anchor-draft',ko:row.ko,source:{path:take.path,sha256:take.sha256,samples:take.samples,sampleRate:take.sampleRate},result,recognizerWindowOffset:offset,contextPcmBinding:offset?sourceRanges.find(x=>x.id===row.id):null,alignment:a.alignment,cues,sentences,overlapCorrections:corrections,phoneticApproval:false,humanListening:'pending',captionApproval:false};
});
const out=b+'part1-word-anchor-draft-v224.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve draft');
fs.writeFileSync(path.join(root,out),JSON.stringify({preparedAt:new Date().toISOString(),review:ref(reviewPath),captions:ref(b+'part1-caption-phrases-v194.json'),selected:ref(b+'part1-selected-current-tts-execution-v219.json'),rows,retainedDrafts:35,currentRepairedDrafts:2,onsetRepairPending:[...pending],wholeFanExcluded:'Chunk-boundary repetition/backward timestamps; complete independent context words with identical current source PCM binding used instead',captionStyle:'boxed-white-forest-v1',center:[960,970],fontSize:48,captionTimingApproved:false,currentMixApproved:false,rendered:false,uploaded:false},null,2)+'\n');
console.log(JSON.stringify({drafts:37,repairPending:0,cues:rows.reduce((n,r)=>n+(r.cues?.length||0),0),approval:false}));
