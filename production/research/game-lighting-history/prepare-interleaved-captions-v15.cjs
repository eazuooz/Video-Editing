// Literal bilingual captions for a measured candidate; timing/pixels stay pending.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),prod='projects/game-lighting-history-03/production',dest=prod+'/local/captions-v15';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const helper=require('./caption-phrases-v2.cjs'),timelinePath=prod+'/measured-native-timeline-candidate-v15.json',dataPath='motion-canvas/src/projects/game-lighting-history-03/spatial/narrated-data-v3.json';
const enPath='projects/game-lighting-history-03/script/narration.en.json',approvalPath=prod+'/native-guide01-onset-asr-direct-review-v3.json';
if(fs.existsSync(path.join(root,dest,'caption-plan.json')))throw Error('Preserve existing caption candidate');
const timeline=read(timelinePath),data=read(dataPath),english=read(enPath),approval=read(approvalPath);
if(!approval.allCurrentGuideContentApproved)throw Error('Current20 guide content review required');
const inputs=[timelinePath,dataPath,enPath,approvalPath],ko=[],en=[],paragraphs=[],warnings=[];
const add=(arr,x)=>{if(!(x.to>x.from))throw Error('Degenerate cue');arr.push({...x,timingDirectlyReviewed:false,pixelsReviewed:false});};
const normWords=s=>s.replace(/\s+/g,' ').trim();
const originalSlots=(ch,p)=>timeline.slots.filter(s=>s.kind==='original-paragraph'&&s.scene===ch.scene&&s.paragraphIndex===p);
const mapTime=(slots,t)=>slots[0].fromFrame/60+t-slots[0].sourceSampleRange[0]/24000;
function englishParts(text){
 const words=text.trim().split(/\s+/),n=words.length,dp=Array(n+1).fill(Infinity),next=Array(n).fill(null);dp[n]=0;
 const wrap=ws=>{const all=ws.join(' ');if(all.length<=46)return all;let best=null,cost=Infinity;for(let i=1;i<ws.length;i++){const a=ws.slice(0,i).join(' '),b=ws.slice(i).join(' ');if(a.length>46||b.length>46)continue;const c=(a.length-b.length)**2;if(c<cost){cost=c;best=a+'\n'+b;}}return best;};
 for(let i=n-1;i>=0;i--)for(let j=i+1;j<=n;j++){const ws=words.slice(i,j),s=ws.join(' ');if(s.length>93)break;const wrapped=wrap(ws);if(!wrapped)continue;const cost=150+(s.length-76)**2+(/[.!?]$/.test(words[j-1])?-70:0)+(j===n&&s.length<20?600:0)+dp[j];if(cost<dp[i]){dp[i]=cost;next[i]={j,wrapped};}}
 if(!next[0])throw Error('English paragraph cannot fit');const parts=[];for(let i=0;i<n;){parts.push(next[i].wrapped);i=next[i].j;}return parts;
}
function addEnglish(text,from,to,meta){const parts=englishParts(text),weights=parts.map(s=>s.replace(/\s+/g,' ').length),total=weights.reduce((n,x)=>n+x,0);let cursor=from;parts.forEach((s,i)=>{const end=i===parts.length-1?to:cursor+(to-from)*weights[i]/total;add(en,{...meta,text:s,from:cursor,to:end,timingMethod:'Independent literal EN text apportioned within corresponding KO paragraph speech span; requires direct timing review.'});cursor=end;});if(normWords(parts.join(' '))!==normWords(text))throw Error('EN words changed');}
for(const ch of data.chapters){
 const enScene=english.scenes.find(s=>s.id===ch.scene);if(!enScene||enScene.lines.length!==ch.paragraphs.length)throw Error('Independent bilingual topology changed');
 for(const p of ch.paragraphs){const slots=originalSlots(ch,p.index),cues=ch.cues.filter(c=>c.paragraph===p.index);if(!slots.length||!cues.length)throw Error('Missing original paragraph/cues');
  if(normWords(cues.map(c=>c.text).join(' '))!==normWords(p.originalKo))throw Error('Original KO text changed');
  const meta={scene:ch.scene,paragraphId:slots[0].originalIndex,slotIds:slots.map(s=>s.id),sourceKind:'original-paragraph'};
  for(const c of cues){const a=ch.sourceFrom+c.from,b=ch.sourceFrom+c.to;add(ko,{...meta,text:c.text,from:mapTime(slots,a),to:mapTime(slots,b),sourceSeconds:[a,b],recognizerWordIndices:c.recognizerWordIndices,alignment:c.alignment,timingMethod:'Existing257 original ASR-anchored cues mapped by exact original PCM placement.'});}
  const from=mapTime(slots,ch.sourceFrom+cues[0].from),to=mapTime(slots,ch.sourceFrom+cues.at(-1).to);addEnglish(enScene.lines[p.index],from,to,meta);
  paragraphs.push({...meta,ko:p.originalKo,en:enScene.lines[p.index],from,to});
 }
}
for(const slot of timeline.slots.filter(s=>s.kind==='native-guide')){
 let p=prod+'/local/native-guides-asr-v1/whole-'+slot.id+'.json';
 if(slot.id.startsWith('01-'))p=prod+'/local/native-guide01-onset-asr-v3/whole-'+slot.id+'.json';
 if(slot.id.startsWith('20-'))p=prod+'/local/native-guide-repairs-asr-v2/whole-'+slot.id+'.json';
 const r=read(p);inputs.push(p);if(r.input.sha256!==slot.pcm.sha256)throw Error('ASR PCM changed '+slot.id);
 if(normWords([r.expectedKo].flat().join(' '))!==normWords(slot.text)||normWords([r.expectedEn].flat().join(' '))!==normWords(slot.en))throw Error('Current guide literal changed');
 const cues=helper.makeCuesGlobal({...r,expectedKo:[slot.text]}),meta={scene:slot.scene,paragraphId:slot.id,slotIds:[slot.id],sourceKind:'native-guide',asrPath:p};
 for(const c of cues)add(ko,{...meta,text:c.text,from:slot.fromFrame/60+c.from,to:slot.fromFrame/60+c.to,sourceSeconds:[c.from,c.to],recognizerWordIndices:c.recognizerWordIndices,alignment:c.alignment,timingMethod:'Current independent whole-guide ASR words, literal approved script preserved.'});
 if(normWords(cues.map(c=>c.text).join(' '))!==normWords(slot.text))throw Error('Guide KO words changed');
 const from=slot.fromFrame/60+cues[0].from,to=slot.fromFrame/60+cues.at(-1).to;addEnglish(slot.en,from,to,meta);paragraphs.push({...meta,ko:slot.text,en:slot.en,from,to});
}
const stamp=t=>{const ms=Math.round(t*1000),h=Math.floor(ms/3600000),m=Math.floor(ms/60000)%60,s=Math.floor(ms/1000)%60;return[h,m,s].map(x=>String(x).padStart(2,'0')).join(':')+','+String(ms%1000).padStart(3,'0');};
for(const [lang,arr]of[['ko',ko],['en',en]]){arr.sort((a,b)=>a.from-b.from);arr.forEach((c,i)=>{c.id=i+1;c.firstFrame=Math.ceil(c.from*60-1e-7);c.exclusiveEndFrame=Math.ceil(c.to*60-1e-7);if(c.text.split('\n').length>2)throw Error('Too many lines');if(c.to-c.from<.45)warnings.push({lang,id:c.id,type:'short-cue',seconds:c.to-c.from});if(i&&c.from<arr[i-1].to-1/60)warnings.push({lang,id:c.id,type:'overlap',seconds:arr[i-1].to-c.from,previousId:arr[i-1].id});});}
fs.mkdirSync(path.join(root,dest),{recursive:true});
for(const [lang,arr]of[['ko',ko],['en',en]])fs.writeFileSync(path.join(root,dest,'game-lighting-history-03.'+lang+'.srt'),arr.map(c=>c.id+'\n'+stamp(c.from)+' --> '+stamp(c.to)+'\n'+c.text+'\n').join('\n'));
const record={preparedAt:new Date().toISOString(),status:'candidate-not-adopted',inputs:[...new Set(inputs)].map(p=>({path:p,sha256:sha(p)})),totals:{originalParagraphs:84,guideParagraphs:20,koCues:ko.length,enCues:en.length,finalFrames:timeline.totals.finalFrames},captionStyle:'boxed-white-forest-v1',center:[960,970],fontSize:48,maximumLines:2,ko,en,paragraphs,warnings,allLiteralBilingualParagraphsPreserved:true,allCaptionTimingDirectlyReviewed:false,allFinalPixelsReviewed:false,finalMixedAsrApproved:false,collected:false,uploaded:false};
fs.writeFileSync(path.join(root,dest,'caption-plan.json'),JSON.stringify(record,null,2)+'\n');console.log(JSON.stringify({ko:ko.length,en:en.length,paragraphs:paragraphs.length,warnings,adopted:false}));
