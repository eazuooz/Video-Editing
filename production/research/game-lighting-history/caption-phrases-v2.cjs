// Preserve original script words; independent ASR word times provide anchors.
// This does not approve pronunciation, listening or rendered caption pixels.
const width=s=>Array.from(s).reduce((n,c)=>n+(/[\x00-\x7f]/.test(c)?.5:1),0);
const aliases=[['비브이에이치','bvh'],['디디지아이','ddgi'],['지아이','gi'],['이천십팔','2018'],['이천이십','2020']];
function norm(s){for(const[a,b]of aliases)s=s.replaceAll(a,b);return s.toLowerCase().replace(/[^\p{L}\p{N}]/gu,'');}
function wrap(words){
 const full=words.join(' ');if(width(full)<=28)return full;
 let best=null,cost=Infinity;
 for(let i=1;i<words.length;i++){const a=words.slice(0,i).join(' '),b=words.slice(i).join(' '),wa=width(a),wb=width(b);if(wa>28||wb>28)continue;const c=(wa-wb)**2+((words.length-i<2||wb<8)?500:0)+(/[,，]$/.test(words[i-1])?-20:0);if(c<cost){cost=c;best=a+'\n'+b;}}
 if(best===null)throw Error('Caption exceeds two lines');return best;
}
function align(original,recognized){const a=Array.from(norm(original)),b=[];recognized.forEach((w,i)=>Array.from(norm(w.text)).forEach(c=>b.push({c,i})));const rows=Array.from({length:a.length+1},()=>new Uint16Array(b.length+1));for(let i=0;i<=a.length;i++)rows[i][0]=i;for(let j=0;j<=b.length;j++)rows[0][j]=j;for(let i=1;i<=a.length;i++)for(let j=1;j<=b.length;j++)rows[i][j]=Math.min(rows[i-1][j]+1,rows[i][j-1]+1,rows[i-1][j-1]+(a[i-1]===b[j-1].c?0:1));let i=a.length,j=b.length;const mapping=Array(a.length).fill(null);while(i||j){if(i&&j&&rows[i][j]===rows[i-1][j-1]+(a[i-1]===b[j-1].c?0:1)){mapping[i-1]=b[j-1].i;i--;j--;}else if(i&&rows[i][j]===rows[i-1][j]+1)i--;else j--;}return{mapping,editDistance:rows[a.length][b.length],originalCharacters:a.length,recognizedCharacters:b.length};}
function phrases(words){
 const n=words.length,dp=Array(n+1).fill(Infinity),next=Array(n).fill(-1);dp[n]=0;
 const target=Math.min(45,width(words.join(' '))/Math.ceil(width(words.join(' '))/48));
 for(let i=n-1;i>=0;i--)for(let j=i+1;j<=n;j++){
  const part=words.slice(i,j),w=width(part.join(' '));if(w>52)break;try{wrap(part);}catch{continue;}
  // Penalize dangling terminal cues and phrase cuts immediately before particles.
  const orphan=(i>0&&j===n&&(part.length<3||w<12))?2000:0;
  const small=(j<n&&part.length<3)?700:0;
  const comma=/[,，]$/.test(words[j-1])?-30:0;
  const cost=100+(w-target)**2+orphan+small+comma+dp[j];
  if(cost<dp[i]){dp[i]=cost;next[i]=j;}
 }
 if(next[0]<0)throw Error('Original sentence cannot fit caption rules');
 const out=[];for(let i=0;i<n;){const j=next[i];out.push(words.slice(i,j));i=j;}
 if(out.flat().join(' ')!==words.join(' '))throw Error('Original words changed');return out;
}
function makeCues(r){
 const sentences=r.expectedKo.flatMap((p,paragraph)=>(p.match(/[^.!?]+[.!?]/g)||[]).map(text=>({paragraph,text:text.trim()})));
 const groups=[];let group=[];for(const word of r.chunks){group.push(word);if(/[.!?]$/.test(word.text.trim())){groups.push(group);group=[];}}
 if(group.length||groups.length!==sentences.length)throw Error('Sentence boundaries require direct repair');
 const cues=[];
 for(let s=0;s<sentences.length;s++){
  const sentence=sentences[s],words=groups[s],a=align(sentence.text,words);let at=0;
  for(const part of phrases(sentence.text.split(/\s+/))){const end=at+norm(part.join(' ')).length,matched=a.mapping.slice(at,end).filter(x=>x!==null);at=end;if(!matched.length)throw Error('No ASR anchor');const lo=Math.min(...matched),hi=Math.max(...matched),from=words[lo].timestamp[0],to=words[hi].timestamp[1];if(!(to>from))throw Error('Degenerate caption');cues.push({id:cues.length+1,paragraph:sentence.paragraph,text:wrap(part),from,to,recognizerWordIndices:[lo,hi],sentence:s,alignment:{editDistance:a.editDistance,originalCharacters:a.originalCharacters,recognizedCharacters:a.recognizedCharacters},timingDirectlyReviewed:false,pixelsReviewed:false});}
 }
 return cues;
}
// Some independent recognitions omit sentence punctuation. Align the complete
// original chapter to all observed words rather than inventing punctuation.
function makeCuesGlobal(r){
 const original=r.expectedKo.join(' '),a=align(original,r.chunks),cues=[];let at=0,sentence=0;
 for(let paragraph=0;paragraph<r.expectedKo.length;paragraph++)for(const text of(r.expectedKo[paragraph].match(/[^.!?]+[.!?]/g)||[])){
  for(const part of phrases(text.trim().split(/\s+/))){const end=at+norm(part.join(' ')).length,matched=a.mapping.slice(at,end).filter(x=>x!==null);at=end;if(!matched.length)throw Error('No whole-chapter ASR anchor');const lo=Math.min(...matched),hi=Math.max(...matched),from=r.chunks[lo].timestamp[0],to=r.chunks[hi].timestamp[1];if(!(to>from))throw Error('Degenerate caption');cues.push({id:cues.length+1,paragraph,text:wrap(part),from,to,recognizerWordIndices:[lo,hi],sentence,alignment:{method:'whole-original-chapter-character-alignment',editDistance:a.editDistance,originalCharacters:a.originalCharacters,recognizedCharacters:a.recognizedCharacters},timingDirectlyReviewed:false,pixelsReviewed:false});}
  sentence++;
 }
 if(at!==norm(original).length||norm(cues.map(c=>c.text).join(' '))!==norm(original))throw Error('Original words not preserved');
 return cues;
}
module.exports={makeCues,makeCuesGlobal,norm,width,wrap};
