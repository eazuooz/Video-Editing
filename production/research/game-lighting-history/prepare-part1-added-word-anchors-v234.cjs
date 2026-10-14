const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {alignNarratedEntry,alignOriginalCharacters}=require('./episode04-caption-alignment-v1.cjs');
const root=path.resolve(__dirname,'../../..'),b='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const ref=p=>({path:p,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex')});
const approval=read(b+'part1-added-observations-direct-review-v234.json');if(!approval.allFourFullTextsDirectlyCompared||!approval.wholeAndIndependentContextApproval)throw Error('Direct comparison missing');
const script=read('projects/game-lighting-history-04/script/physical-part1-added-observations.koen.v232.json'),tts=read(b+'part1-added-observations-tts-execution-v232.json');
const aliases=[['바닥에','바닥의'],['표면에','표면의'],['켜진과','켜짐과'],['꺼진','꺼짐']];
const rows=script.scenes.map(s=>{
 const result=ref(b+'local/part1-added-observations-asr-v233/whole-'+s.id+'.json'),r=read(result.path),take=tts.results.find(t=>t.id===s.id);if(ref(take.path).sha256!==take.sha256)throw Error('PCM changed');
 const a=alignNarratedEntry(s.ko,r.chunks,aliases),chars=alignOriginalCharacters(s.ko,r.chunks,aliases);
 const cues=a.cues.map(c=>({...c,fromFrame:Math.round(c.from*60),toFrame:Math.round(c.to*60)}));
 for(let i=1;i<cues.length;i++)if(cues[i].fromFrame<cues[i-1].toFrame){const n=Math.round((cues[i].fromFrame+cues[i-1].toFrame)/2);cues[i-1].toFrame=n;cues[i].fromFrame=n;}
 const sentences=[...s.ko.matchAll(/[^.!?]+(?:[.!?](?!\d)|$)/g)].map(m=>{const span=[m.index+m[0].length-m[0].trimStart().length,m.index+m[0].length],idx=chars.matching.filter((w,i)=>w!==null&&chars.original.map[i]>=span[0]&&chars.original.map[i]<span[1]);return {text:m[0].trim(),sourceCharacters:span,from:r.chunks[Math.min(...idx)].timestamp[0],to:r.chunks[Math.max(...idx)].timestamp[1]};});
 return {...s,sourceKey:s.id.startsWith('cyber')?'cyber':'rivalry',originalNumericSourceMetadataRetained:s.source,source:{path:take.path,sha256:take.sha256,samples:take.samples,sampleRate:24000},result,alignment:a.alignment,cues,sentences,phoneticApproval:false,humanListening:'pending',captionApproval:false};
});
const out=b+'part1-added-word-anchors-v234.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve');fs.writeFileSync(path.join(root,out),JSON.stringify({preparedAt:new Date().toISOString(),review:ref(b+'part1-added-observations-direct-review-v234.json'),rows,metadataResolution:'Numeric source fields in protected v232 are preserved; selected source keys explicitly resolved as cyber/rivalry.',captionStyle:'boxed-white-forest-v1',center:[960,970],fontSize:48,captionTimingApproved:false,currentMixApproved:false,uploaded:false},null,2)+'\n');console.log(JSON.stringify({rows:rows.length,cues:rows.flatMap(x=>x.cues).length,finalApproved:false}));
