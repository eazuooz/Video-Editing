// Independent English wording, aligned to directly read Korean semantic sentences.
// English is a translation track over Korean speech, not measured English audio.
const fs=require('fs'),crypto=require('crypto');
const base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const source=base+'local/caption-word-draft-v2.json',d=read(source);
function sentences(t){
 const parts=(t.match(/[\s\S]+?(?:[.!?](?=\s|$)|$)/g)||[]).filter(x=>x.trim());let at=0;
 const result=parts.map(x=>{const start=t.indexOf(x,at);at=start+x.length;return {text:x.trim(),characters:[start,at]};});
 if(result.map(x=>x.text).join(' ')!==t.replace(/\s+/g,' ').trim())throw Error('Sentence splitter lost source text');return result;
}
// Each item names the consecutive KO sentence indices represented by one EN sentence.
const semanticGroups={
 'original-18t-3':[[0],[1,2]],'original-18t-6':[[0,1],[2]],
 'original-18a-1':[[0],[1,2]],'original-21a-3':[[0,1],[2],[3],[4]],
 'original-22-1':[[0],[1,2]],'original-22p-2':[[0,1],[2]],
 'original-22r-2':[[0,1],[2]],'original-22r-3':[[0,1],[2]],
 'original-conclusion-3':[[0,1],[2]]
};
function wrapEnglish(text){
 const words=text.split(/\s+/),n=words.length,cost=Array(n+1).fill(Infinity),next=Array(n).fill(null);cost[n]=0;
 function twoLines(ws){const s=ws.join(' ');if(s.length<=42)return s;let best=null;for(let at=1;at<ws.length;at++){const a=ws.slice(0,at).join(' '),b=ws.slice(at).join(' ');if(a.length<=42&&b.length<=42&&(!best||Math.abs(a.length-b.length)<best.cost))best={text:a+'\n'+b,cost:Math.abs(a.length-b.length)};}return best?.text;}
 for(let i=n-1;i>=0;i--)for(let j=i+1;j<=n;j++){
  const part=words.slice(i,j),s=part.join(' ');if(s.length>85)break;const wrapped=twoLines(part);if(!wrapped)continue;
  const orphan=(j===n&&i>0&&s.length<24)?2200:0,v=140+(s.length-64)**2+orphan+cost[j];
  if(v<cost[i]){cost[i]=v;next[i]={j,text:wrapped};}
 }
 if(!next[0])throw Error('Unwrappable English sentence');const cues=[];for(let i=0;i<n;){cues.push(next[i].text);i=next[i].j;}return cues;
}
const paragraphs=[],cues=[];
for(const p of d.paragraphs){
 const ko=sentences(p.text),en=sentences(p.en),groups=semanticGroups[p.id]??ko.map((_,i)=>[i]);
 if(groups.length!==en.length||groups.flat().join(',')!==ko.map((_,i)=>i).join(','))throw Error('Explicit semantic mapping required: '+p.id);
 const local=[];
 for(let i=0;i<en.length;i++){
  const indices=groups[i],first=ko[indices[0]].characters[0],last=ko[indices.at(-1)].characters[1];
  const related=p.cues.filter(c=>c.sourceCharacters[1]>first&&c.sourceCharacters[0]<last);
  if(!related.length)throw Error('No Korean word anchor for English sentence: '+p.id);
  const from=related[0].from,to=related.at(-1).to,parts=wrapEnglish(en[i].text),weight=parts.map(x=>x.replace(/\n/g,' ').length),total=weight.reduce((a,b)=>a+b,0);let passed=0;
  for(let j=0;j<parts.length;j++){
   const start=from+(to-from)*passed/total;passed+=weight[j];const end=from+(to-from)*passed/total;
   local.push({entryId:p.id,sentence:i+1,koSentenceIndices:indices,sourceKoCueIds:related.map(c=>c.id),text:parts[j],from:start,to:end,timingMethod:'reviewed-KO-semantic-sentence-bounds-with-English-reading-length-splits',measuredEnglishWordTiming:false,pixelsReviewed:false});
  }
 }
 if(local.map(c=>c.text.replace(/\n/g,' ')).join(' ')!==p.en.replace(/\s+/g,' ').trim())throw Error('Independent English wording lost');
 paragraphs.push({id:p.id,en:p.en,semanticSentenceGroups:groups,completeEnglishWordingPreserved:true,cues:local});cues.push(...local);
}
for(let i=0;i<cues.length;i++){cues[i].id=i+1;if(cues[i].to<=cues[i].from||i&&cues[i].from<cues[i-1].to-1e-8)throw Error('Translation cue timing overlap');}
const out={createdAt:new Date().toISOString(),source:{path:source,sha256:sha(source)},audio:d.audio,paragraphs,cues,complete111EnglishParagraphsPreserved:true,semanticMappingsDirectlyRead:true,allEnglishCuesDirectlyRead:false,integerFinalTimingProduced:false,finalMixedAsrApproved:false,allFinalCaptionPixelsReviewed:false,humanWholeListeningApproved:false,scope:'Prepared translation draft only; no final SRT, render or upload. Original87 and new24 independent English paragraphs preserved.'};
const target=base+'local/english-caption-draft-v2.json';fs.writeFileSync(target,JSON.stringify(out,null,2)+'\n');console.log(JSON.stringify({target,paragraphs:paragraphs.length,cues:cues.length,explicitSemanticGroups:Object.keys(semanticGroups).length}));
