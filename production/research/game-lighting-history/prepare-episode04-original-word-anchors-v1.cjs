// Prepare anchors from existing full chapter recognition; no synthesis or ASR.
// Paragraph allocation in the legacy timing JSON is not a speech boundary.
const fs=require('fs'),crypto=require('crypto');
const {alignOriginalCharacters,alignNarratedEntry}=require('./episode04-caption-alignment-v1.cjs');
const base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const assembly=read(base+'current-unmixed-assembly-v4.json'),timing=read(assembly.timing.path);
if(sha(assembly.audio.path)!==assembly.audio.sha256||sha(assembly.timing.path)!==assembly.timing.sha256)throw Error('Current original87 input changed');
const aliases=[
 ['디엘에스에스 삼 점 오','dlss3.5'],['디엘에스에스 삼','dlss3'],['디엘에스에스 사','dlss4'],['디엘에스에스 오','dlss5'],['dlssO','dlss5'],['디엘에스에스','dlss'],['티에스알','tsr'],['에스엠알티','smrt'],
 ['언리얼','얼리얼'],['셰이더','쉐이더'],['렌더독','랜더독'],['디퍼드','디퍼트'],
 ['열여섯 칸','16칸'],['다섯 칸','5칸'],['다섯 개','5개'],['세 개','3개'],['세 배','3배'],['육 배','6배'],
 ['사분의 일','4분의1'],['이천이십이 년','2022년'],['이공칠칠','2077'],['일 점 육 이','1.62'],['사 점 오','4.5'],['구월','9월'],['엔비에이','nba'],['이케이 이칠','2k27'],['삼차원','3차원'],
 ['이와 팔','2와8'],['오입니다','5입니다'],['영 점 팔','0.8'],['일 나누기','1나누기'],['지 버퍼','g버퍼']
];
const chapters=[];
for(const scene of assembly.scenes){
 const id=scene.scene;
 const path=base+(id==='18t'||id==='22r'?'local/current-assembly-asr-v4/whole-current-':'local/voice-asr-v2/whole-')+id+'.json';
 const raw=read(path),excluded=[];
 let words=raw.chunks.map((w,i)=>({...w,rawWordIndex:i}));
 if(id==='18v'){
  // Raw indices60–84 contain the directly reviewed chunk-edge hallucination
  // and backward duplicate. Raw evidence stays intact. Complete independent
  // 18–40sec diagnosis corroborates the second correct paragraph3 sequence.
  excluded.push({rawIndices:[60,84],reason:'Historical chunk-edge extra phrase and backward repeat; independent18–40 diagnosis preserves the complete next paragraph.',corroboratingPath:base+'local/voice-diagnostics-v1/18v-18-40.json',corroboratingSha256:sha(base+'local/voice-diagnostics-v1/18v-18-40.json')});
  words=words.filter(w=>w.rawWordIndex<60||w.rawWordIndex>84);
 }
 if(words.some((w,i)=>w.timestamp.some(t=>!Number.isFinite(t))||w.timestamp[1]<w.timestamp[0]||i&&w.timestamp[0]<words[i-1].timestamp[0]))throw Error('Unresolved actual word-time regression: '+id);
 const entries=timing.entries.filter(e=>e.scene_id===id);let offset=0;
 const spans=entries.map(e=>{const from=offset;offset+=e.text.length+2;return [from,from+e.text.length];});
 const expected=entries.map(e=>e.text).join('\n\n');
 const alignment=alignOriginalCharacters(expected,words,aliases),paragraphs=[];
 for(let p=0;p<entries.length;p++){
  const entry=entries[p],[from,to]=spans[p];
  const matched=alignment.matching.filter((m,index)=>m!==null&&alignment.original.map[index]>=from&&alignment.original.map[index]<to);
  if(!matched.length)throw Error('No actual paragraph anchors');
  const lo=Math.min(...matched),hi=Math.max(...matched),start=words[lo].timestamp[0],end=words[hi].timestamp[1];
  const caption=alignNarratedEntry(entry.text,words.slice(lo,hi+1),aliases);
  paragraphs.push({id:'original-'+id+'-'+entry.paragraph,paragraph:entry.paragraph,text:entry.text,legacyAllocationSeconds:[entry.start,entry.end],sceneRelativeSpokenSeconds:[start,end],originalMasterSpokenSeconds:[scene.sampleRange[0]/24000+start,scene.sampleRange[0]/24000+end],wordIndices:[lo,hi],rawWordIndices:[words[lo].rawWordIndex,words[hi].rawWordIndex],firstWord:words[lo],lastWord:words[hi],captionDraft:caption,actualBoundaryDirectlyReviewed:false});
 }
 chapters.push({scene:id,currentOriginalSampleRange:scene.sampleRange,recognition:{path,sha256:sha(path)},excludedRawRecognitionIndices:excluded,alignment:alignment.alignment,words,paragraphs,actualBoundariesDirectlyReviewed:false});
}
const output={createdAt:new Date().toISOString(),originalAudio:assembly.audio,originalAssembly:{path:base+'current-unmixed-assembly-v4.json',sha256:sha(base+'current-unmixed-assembly-v4.json')},legacyTiming:assembly.timing,chapters,paragraphCount:chapters.reduce((n,c)=>n+c.paragraphs.length,0),scope:'Existing whole recognition with current scene sample offsets; draft only. Boundaries require actual word comparison and PCM-gap inspection.',allOriginalBoundariesDirectlyReviewed:false,allCaptionWordTimesDirectlyReviewed:false,finalTimingApproved:false,finalMixedAsrApproved:false};
if(output.paragraphCount!==87)throw Error('Complete87 original paragraphs required');
const p=base+'local/original-word-anchors-draft-v1.json';fs.writeFileSync(p,JSON.stringify(output,null,2)+'\n');
for(const c of chapters){console.log(JSON.stringify({scene:c.scene,alignment:c.alignment,paragraphs:c.paragraphs.map(p=>({id:p.id,spoken:p.sceneRelativeSpokenSeconds,legacy:p.legacyAllocationSeconds,first:p.firstWord,last:p.lastWord,captions:p.captionDraft.cues.length,captionEditDistance:p.captionDraft.alignment.editDistance,overlaps:p.captionDraft.overlaps}))}));}
