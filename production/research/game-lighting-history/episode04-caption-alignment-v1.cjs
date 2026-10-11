// Scoped to episode04. Normalization only aligns original wording to ASR
// timestamps; it never rewrites narration or grants an audio/pixel approval.
const {width,wrap}=require('./caption-phrases-v2.cjs');
function canonical(text,indices,aliases){
 let chars=Array.from(text.toLowerCase()),map=indices??chars.map((_,i)=>i);
 for(const [from,to] of aliases){
  const find=Array.from(from.toLowerCase()),replace=Array.from(to.toLowerCase());
  for(let at=0;at<=chars.length-find.length;at++){
   if(!find.every((c,i)=>chars[at+i]===c))continue;
   const old=map.slice(at,at+find.length);
   const replacementMap=replace.map((_,i)=>old[Math.min(old.length-1,Math.floor(i*old.length/replace.length))]);
   chars.splice(at,find.length,...replace);map.splice(at,find.length,...replacementMap);at+=replace.length-1;
  }
 }
 const out=[],positions=[];
 chars.forEach((c,i)=>{if(/[\p{L}\p{N}]/u.test(c)){out.push(c);positions.push(map[i]);}});
 return {chars:out,map:positions};
}
function partition(words){
 const n=words.length,cost=Array(n+1).fill(Infinity),next=Array(n).fill(-1);cost[n]=0;
 for(let i=n-1;i>=0;i--)for(let j=i+1;j<=n;j++){
  const part=words.slice(i,j),w=width(part.join(' '));if(w>52)break;
  try{wrap(part);}catch{continue;}
  const orphan=j===n&&i>0&&(part.length<3||w<12)?2000:0;
  const candidate=100+(w-42)**2+orphan+(j<n&&part.length<3?700:0)+cost[j];
  if(candidate<cost[i]){cost[i]=candidate;next[i]=j;}
 }
 if(next[0]<0)throw Error('Original sentence cannot wrap');
 const result=[];for(let i=0;i<n;){const j=next[i];result.push(words.slice(i,j));i=j;}return result;
}
function alignOriginalCharacters(text,words,aliases=[]){
 if(!words.length||words.some(w=>!Array.isArray(w.timestamp)||w.timestamp.some(t=>!Number.isFinite(t))))throw Error('Actual word times required');
 const original=canonical(text,undefined,aliases);let recognizedText='',indices=[];
 words.forEach((w,index)=>{recognizedText+=w.text;indices.push(...Array.from(w.text).map(()=>index));});
 const recognized=canonical(recognizedText,indices,aliases),a=original.chars,b=recognized.chars;
 const dp=Array.from({length:a.length+1},()=>new Uint16Array(b.length+1));
 for(let i=0;i<=a.length;i++)dp[i][0]=i;for(let j=0;j<=b.length;j++)dp[0][j]=j;
 for(let i=1;i<=a.length;i++)for(let j=1;j<=b.length;j++)dp[i][j]=Math.min(dp[i-1][j]+1,dp[i][j-1]+1,dp[i-1][j-1]+(a[i-1]===b[j-1]?0:1));
 const matching=Array(a.length).fill(null);let i=a.length,j=b.length;
 while(i||j){if(i&&j&&dp[i][j]===dp[i-1][j-1]+(a[i-1]===b[j-1]?0:1)){matching[i-1]=recognized.map[j-1];i--;j--;}else if(i&&dp[i][j]===dp[i-1][j]+1)i--;else j--;}
 return {original,matching,alignment:{editDistance:dp[a.length][b.length],originalCharacters:a.length,recognizedCharacters:b.length,method:'scoped-alias-character-alignment-with-original-character-spans',aliases}};
}
function alignNarratedEntry(text,words,aliases=[]){
 const {original,matching,alignment}=alignOriginalCharacters(text,words,aliases);
 const cues=[];let sourcePosition=0;
 const sentences=text.match(/[^.!?]+(?:[.!?](?!\d)|$)/g)||[text];
 for(const sentence of sentences){
  for(const part of partition(sentence.trim().split(/\s+/))){
   const literal=part.join(' '),fromChar=text.indexOf(literal,sourcePosition);if(fromChar<0)throw Error('Original words changed');
   const toChar=fromChar+Array.from(literal).length;
   const matches=matching.filter((m,index)=>m!==null&&original.map[index]>=fromChar&&original.map[index]<toChar);
   if(!matches.length)throw Error('Caption has no observed word anchor');
   const lo=Math.min(...matches),hi=Math.max(...matches);
   cues.push({id:cues.length+1,text:wrap(part),from:words[lo].timestamp[0],to:words[hi].timestamp[1],recognizerWordIndices:[lo,hi],sourceCharacters:[fromChar,toChar],timingDirectlyReviewed:false,pixelsReviewed:false});
   sourcePosition=toChar;
  }
 }
 if(cues.map(c=>c.text.replace(/\n/g,' ')).join(' ')!==text.replace(/\s+/g,' ').trim())throw Error('Complete original wording not retained');
 const overlaps=cues.slice(1).flatMap((c,index)=>c.from<cues[index].to?[{first:index+1,second:index+2,seconds:cues[index].to-c.from}]:[]);
 return {cues,alignment,overlaps,captionWordTimesDirectlyReviewed:false,allFinalCaptionPixelsReviewed:false};
}
module.exports={alignNarratedEntry,alignOriginalCharacters};
