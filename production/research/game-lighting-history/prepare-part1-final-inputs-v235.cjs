// Preserve 36 original paragraphs, 37 selected guides, two new observations and two framing paragraphs.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),B='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const hashes=new Map(),sha=p=>{if(!hashes.has(p))hashes.set(p,crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex'));return hashes.get(p);};
const ref=p=>({path:p,sha256:sha(p)});
const out=B+'part1-final-input-plan-v235.json';if(fs.existsSync(path.join(root,out)))throw Error('Preserve final plan');
const current=read(B+'part1-current-asr-direct-review-v223.json'),fresh=read(B+'part1-added-observations-direct-review-v234.json'),pixels=read(B+'part1-label-repair-direct-review-v227.json');
if(!current.all74FullTextsDirectlyCompared||!fresh.wholeAndIndependentContextApproval||!pixels.sourcePixelSelectionApproved)throw Error('Direct source gates required');
const old=read('projects/game-lighting-history-04/script/physical-part1-guided-actions.koen.v175.json').scenes,extra=read('projects/game-lighting-history-04/script/physical-part1-added-observations.koen.v232.json').scenes;
const takes=read(B+'part1-selected-current-tts-execution-v219.json').results.concat(read(B+'part1-added-observations-tts-execution-v232.json').results);
const anchors=read(B+'part1-word-anchor-draft-v224.json').rows.concat(read(B+'part1-added-word-anchors-v234.json').rows);
const selected=read(B+'part1-measured-allocation-draft-v192.json'),sources=read(B+'part1-source-selection-direct-review-v167.json').sources;
const bank=read('production/research/game-lighting-history/local/part1-spatial-bank-v206/plan.json'),repair=read('production/research/game-lighting-history/local/part1-label-repair-v225/plan.json');
const bankVideo=ref(bank.jobs[0].output),repairVideo=ref(repair.jobs[0].output);
const bridge=read('production/research/game-lighting-history/local/part1-observation-bridge-v236/plan.json');
if(read(bridge.jobs[0].execution).exitCode!==0)throw Error('Complete bridge render required');
const observedBeats={
 'texture-streaming-input':'Read the selected asset and its material input together.',
 'texture-stack-uv':'Compare shared coordinates with the displayed stack count after reconnection.',
 'texture-project-tile-settings':'Read tile size separately from the filtering border.',
 'runtime-texture-consumer':'Read the content format beside tile settings.',
 'ordinary-streaming-budget':'Read the ordinary Streaming label and its pool control.',
 'geometry-programmable-material':'Distinguish the selected diagnostic from original surface colour.',
 'geometry-car-material':'Follow the unchanged car shape as its material display changes.',
 'fortnite-mobile-test':'Read quality labels separately from the diagnostic graph.'
};
const groups={
 'shadow-address-view':[[2,1],[2,1]],'shadow-wheel-surface':[[2,1],[1,1],[1,1],[1,1],[2,1],[1,1]],
 'shadow-wheel-change':[[1,1],[2,1],[1,1],[1,1],[2,1],[1,1]],'shadow-resource-cache':[[2,1],[1,1],[1,1],[1,1],[1,1],[1,1]],
 'texture-streaming-input':[[1,1],[2,1],[1,1],[1,1]],'texture-stack-uv':[[2,2],[2,1],[1,1]],
 'texture-dependent-conversion':[[2,1],[2,1]],'texture-project-tile-settings':[[2,1],[2,1],[1,1]],
 'runtime-texture-producer':[[2,1],[1,1],[1,1]],'runtime-texture-consumer':[[2,1],[2,1],[2,1]],
 'virtual-pool-policy':[[2,1],[2,1],[1,1]],'texture-scene-return':[[2,1],[1,1],[1,1]],
 'tsr-silhouette-history':[[1,1],[3,1],[1,1],[1,1],[1,1],[2,1]],'tsr-rotation-vectors':[[2,1],[1,1],[2,1],[1,1],[1,1]],
 'horizon-comparison-before':[[1,1],[2,1]],'horizon-detail-motion':[[2,1]],'cyber-light-reconstruction':[[3,2],[2,2]],
 'geometry-road-mask':[[2,1],[1,1],[1,1]],'geometry-barrier-views':[[1,1],[3,1],[1,1],[2,1],[1,1]],
 'geometry-courtyard-data':[[2,1],[1,1],[2,1],[1,1],[1,1],[1,1]],
 'geometry-programmable-material':[[2,1],[2,1],[1,1],[1,1],[1,1],[1,1],[1,1]],
 'mobile-texture-group':[[1,1],[1,1],[2,1]],'mobile-device-policy':[[2,1],[1,1],[3,1]],
 'mobile-lod-settings':[[2,1],[1,1],[2,1]],'mobile-console-policy':[[1,1],[1,1],[1,1],[2,1]],
 'mobile-compiler-availability':[[2,1],[2,1],[1,1]],'fortnite-mobile-test':[[2,1],[1,1],[2,1]],
 'rivalry-mobile-history':[[1,1],[1,1],[1,1],[2,1],[1,1],[1,1],[2,1],[1,1],[1,1]]
};
function sentences(t){let at=0;return (t.match(/[\s\S]+?(?:[.!?](?=\s|$)|$)/g)||[]).filter(x=>x.trim()).map(x=>{const from=t.indexOf(x,at),start=from+x.length-x.trimStart().length;at=from+x.length;return {text:x.trim(),span:[start,at]};});}
function enParts(t){const words=t.trim().split(/\s+/),parts=[];let current=[];for(const w of words){if([...current,w].join(' ').length>72&&current.length){parts.push(current);current=[];}current.push(w);}if(current.length)parts.push(current);if(parts.length>1&&parts.at(-1).join(' ').length<22){const previous=parts.at(-2);while(parts.at(-1).join(' ').length<22&&previous.length>3)parts.at(-1).unshift(previous.pop());}return parts.map(a=>{if(a.join(' ').length<=42)return a.join(' ');let best;for(let i=1;i<a.length;i++){const x=a.slice(0,i).join(' '),y=a.slice(i).join(' ');if(x.length<=42&&y.length<=42&&(!best||Math.abs(x.length-y.length)<best.d))best={text:x+'\n'+y,d:Math.abs(x.length-y.length)};}if(!best)throw Error('EN wrap');return best.text;});}
function enTrack(s,ko){const K=sentences(s.ko),E=sentences(s.en),g=groups[s.id]??K.map(()=>[1,1]);if(g.reduce((n,x)=>n+x[0],0)!==K.length||g.reduce((n,x)=>n+x[1],0)!==E.length)throw Error('Read semantic mapping '+s.id+' '+K.length+'/'+E.length);
 let ki=0,ei=0;const o=[];for(const [nk,ne]of g){const lower=K[ki].span[0],upper=K[ki+nk-1].span[1],match=ko.filter(c=>c.sourceCharacters[1]>lower&&c.sourceCharacters[0]<upper);if(!match.length)throw Error('No KO anchors');const from=match[0].fromFrame,to=match.at(-1).toFrame,parts=enParts(E.slice(ei,ei+ne).map(e=>e.text).join(' ')),weights=parts.map(t=>t.replace(/\n/g,' ').length),total=weights.reduce((a,b)=>a+b,0);let used=0;for(let j=0;j<parts.length;j++){const start=Math.round(from+(to-from)*used/total);used+=weights[j];o.push({entryId:s.id,text:parts[j],fromFrame:start,toFrame:Math.round(from+(to-from)*used/total),koSentenceIndices:Array.from({length:nk},(_,j)=>ki+j),enSentenceIndices:Array.from({length:ne},(_,j)=>ei+j),timingMethod:'Directly compared semantic units over actual KO word anchors; proportional translation reading splits',measuredEnglishWordTiming:false});}ki+=nk;ei+=ne;}
 if(o.map(c=>c.text.replace(/\n/g,' ')).join(' ')!==s.en.replace(/\s+/g,' ').trim())throw Error('EN loss '+s.id);return o;
}
function spans(t,cues){let at=0;return cues.map(c=>{const text=c.text.replace(/\n/g,' '),from=t.indexOf(text,at);if(from<0)throw Error('Literal words changed');at=from+text.length;return {...c,sourceCharacters:[from,at]};});}
const rows=new Map(),children=new Map();
for(const s of old.concat(extra)){
 const t=takes.find(t=>t.id===s.id),a=anchors.find(a=>a.id===s.id);if(!t||!a||sha(t.path)!==t.sha256)throw Error('Selected PCM missing');
 const frames=Math.ceil(t.samples/400),legacy=selected.rows.find(x=>x.id===s.id);let ranges=legacy?.normalSpeedNativeRanges;
 let sourceKey=s.source;if(s.id==='cyber-surface-observation'){sourceKey='cyber';ranges=[[15,29.4],[32,42.733333333333334]];}
 if(s.id==='rivalry-surface-observation'){sourceKey='rivalry';ranges=[[.5,17.266666666666666]];}
 const source=sources[sourceKey];let spatial=repair.scenes.find(x=>x.id===s.id),video=repairVideo;if(!spatial){spatial=bank.scenes.find(x=>x.id===s.id);video=bankVideo;}
 if(s.id==='rivalry-surface-observation'){spatial={frames:252,fromFrame:0,sourceSampleRange:[402400,t.samples]};video=ref(bridge.jobs[0].output);}
 const E=spatial?.frames??0,A=spatial?Math.ceil(spatial.sourceSampleRange[0]/400):frames;
 if(A+E!==frames)throw Error('Exact source clock '+s.id+' '+A+'/'+E+'/'+frames);
 const pcm={path:t.path,sha256:t.sha256,sampleRate:24000,samples:t.samples};
 const row={...s,frames,actualFrames:A,explanationFrames:E,sourceKey,source:source?{path:source.path,sha256:source.sha256}:null,cropRect:source?.crop??null,ranges,pcm,koCues:a.cues,enCues:enTrack(s,a.cues),spatial:spatial?{...spatial,video}:null,observationFrames:observedBeats[s.id]?45:0};
 rows.set(s.id,row);if(!children.has(s.insertAfter))children.set(s.insertAfter,[]);children.get(s.insertAfter).push(s.id);
}
// New observed movement comes before the four-game conclusion, never after its summary.
children.set('rivalry-mobile-history',['rivalry-surface-observation','four-game-transfer-conclusion']);
const cuts=[],paragraphs=[],used=new Set(),bindings=[B+'part1-current-asr-direct-review-v223.json',B+'part1-current-asr-pcm-corroboration-v224.json',B+'part1-label-repair-direct-review-v227.json',B+'part1-added-observations-direct-review-v234.json',B+'part1-added-word-anchors-v234.json',B+'part1-source-selection-direct-review-v167.json'].map(ref);let cursor=120;
function append(c){c.fromFrame=cursor;c.toFrame=cursor+c.frames;cuts.push(c);cursor=c.toFrame;}
function nativeCuts(r,n){const o=[];for(const [a,z]of r.ranges??[]){const lo=Math.round(a*60),hi=Math.round(z*60),count=Math.min(n,hi-lo);if(count>0)o.push({inFrame:lo,outFrame:lo+count});n-=count;if(!n)break;}if(n)throw Error('Insufficient normal-speed source '+r.id);return o;}
const names={horizon:'Horizon Forbidden West · 움직이는 자수 비교',outer:'The Outer Worlds 2 · 원본 DLSS 4.5 표시 프레임 비교',cyber:'Cyberpunk 2077 · 원본 DLSS 3.5 묶음 조건',rivalry:'Rivalry · 2014 모바일 엔진 기술 시연',mobile:'Fortnite · 모바일 편집기 / 테스트 맵',tsrMan:'Unreal Engine · TSR 마네킹 시연',tsrFan:'Unreal Engine · 회전 날개 / 속도 벡터',vt:'Unreal Engine · 가상 텍스처 편집기',nanite:'Unreal Engine · 선택된 지오메트리 진단',vsmInitial:'Unreal Engine · 그림자 영역 시각화',vsmPool:'Unreal Engine · 그림자 물리 페이지 풀'};
function appendAddition(id){if(used.has(id))throw Error('Repeated '+id);used.add(id);const r=rows.get(id),start=cursor;
 if(r.actualFrames){const obs=r.observationFrames,n=r.actualFrames+obs,sampleEnd=r.spatial?r.spatial.sourceSampleRange[0]:r.pcm.samples;append({id:id+':native',paragraphId:id,kind:'actual',frames:n,video:r.source,pcm:{...r.pcm,firstSample:0,exclusiveEndSample:sampleEnd,samples:sampleEnd},proposedCuts:nativeCuts(r,n),cropRect:r.cropRect,captionMatteHeight:['cyber','horizon','outer'].includes(r.sourceKey)?180:0,identityLabel:names[r.sourceKey],onScreenConditionLabel:r.id==='cyber-surface-observation'?'原본 RTX ON/OFF 및 DLSS Off / DLSS 3.5 비교 · 단일 기능 실험 아님':r.id==='horizon-detail-motion'?'원본 업스케일 방식 비교 · 같은 자수 경계':null,observationBeat:obs?{frames:obs,purpose:observedBeats[id],normalSpeed:true,sourceContinuous:true}:null,sourceAudio:0,loop:0,slowdown:0});}
 if(r.spatial){const lo=r.spatial.sourceSampleRange[0],hi=r.pcm.samples;append({id:id+':model',paragraphId:id,kind:'explanation',frames:r.spatial.frames,video:r.spatial.video,sourceStartFrame:r.spatial.fromFrame,pcm:{...r.pcm,firstSample:lo,exclusiveEndSample:hi,samples:hi-lo},preserveFullPcm:true});}
 // Observation beats follow complete speech, so shift only later model cues if a model exists.
 const shift=c=>({...c,entryId:id,fromFrame:start+c.fromFrame+(r.spatial&&c.fromFrame>=r.actualFrames?r.observationFrames:0),toFrame:start+c.toFrame+(r.spatial&&c.toFrame>r.actualFrames?r.observationFrames:0)});
 paragraphs.push({id,kind:'new-guided',ko:r.ko,en:r.en,startFrame:start,endFrame:cursor,pcm:r.pcm,koCues:r.koCues.map(shift),enCues:r.enCues.map(shift)});
 for(const child of children.get(id)||[])appendAddition(child);
}
const framing=read('production/research/game-lighting-history/local/episode04-physical-framing-v59/plan.json'),fvideo=ref('production/research/game-lighting-history/local/episode04-physical-framing-v60/physical-framing.clean.mp4');
function appendFraming(id){const s=framing.scenes.find(x=>x.id===id),from=cursor,pcm={...s.source,samples:s.sourceSamples,sampleRate:24000},ko=spans(s.textKo,s.cues);append({id,kind:'explanation',frames:s.frames,video:fvideo,sourceStartFrame:s.fromFrame,pcm,preserveFullPcm:true});const row={id,ko:s.textKo,en:s.textEn};paragraphs.push({...row,kind:'physical-framing',startFrame:from,endFrame:cursor,pcm,koCues:ko.map(c=>({...c,entryId:id,fromFrame:c.fromFrame+from,toFrame:c.toFrame+from})),enCues:enTrack(row,ko).map(c=>({...c,fromFrame:c.fromFrame+from,toFrame:c.toFrame+from}))});}
appendFraming('part1-overview');
const enDraft=read(B+'local/english-caption-draft-v2.json'),chapterRanges=[],originalBoundaryRepairs=[];
for(const [name,ver,videoPath]of [['first',10,'production/research/game-lighting-history/local/episode04-first-chapter-framing-v12/game-lighting-history-04-first-chapter.clean.mp4'],['upscaling',13,'production/research/game-lighting-history/local/episode04-upscaling-label-v15/game-lighting-history-04-upscaling-chapter.clean.mp4'],['mobile',16,'production/research/game-lighting-history/local/episode04-mobile-chapter-v16/game-lighting-history-04-mobile-chapter.clean.mp4']]){
 const pp=B+(name==='first'?'first':name)+'-chapter-review-plan-v'+ver+'.json',p=read(pp),audio={...p.audio,exclusiveEndSample:p.audio.exclusiveEndSample??p.audio.endSample};audio.samplesInChapter=audio.exclusiveEndSample-audio.firstSample;bindings.push(ref(pp));const video=ref(videoPath),map=[];
 for(let i=0;i<p.cuts.length-1;i++){const c=p.cuts[i],parent=c.entryId,last=parent&&!p.cuts.slice(i+1).some(x=>x.entryId===parent);if(!last||!children.has(parent))continue;const e=p.entries.find(x=>x.id===parent),end=Math.max(Math.ceil((e.endSample-audio.firstSample)/400),...p.cues.filter(x=>x.entryId===parent).map(x=>x.exclusiveEndFrame)),extra=end-c.toFrame;if(extra>0){if(extra>1)throw Error('Original boundary needs reviewed retiming');originalBoundaryRepairs.push({entryId:parent,oldFrame:c.toFrame,newFrame:end,keepLastOriginalSample:true});c.nativeExtension=c.kind.startsWith('actual')?extra:0;c.toFrame=end;c.frames=end-c.fromFrame;p.cuts[i+1].fromFrame=end;p.cuts[i+1].frames=p.cuts[i+1].toFrame-end;}}
 for(let i=0;i<p.cuts.length;i++){const c=p.cuts[i],from=cursor,lo=audio.firstSample+c.fromFrame*400,hi=Math.min(audio.exclusiveEndSample,audio.firstSample+c.toFrame*400),obj={id:name+':'+c.id,kind:c.kind.startsWith('actual')?'actual':'explanation',frames:c.frames,video,sourceStartFrame:c.fromFrame,pcm:{...audio,firstSample:lo,exclusiveEndSample:hi},originalChapter:name,originalChapterFrames:[c.fromFrame,c.toFrame],preserveFullPcm:true};if(c.nativeExtension)obj.nativeBoundaryExtension={source:ref(c.path),sourceStartSeconds:c.sourceStart,frames:c.frames,cropRect:c.crop,label:c.label};append(obj);map.push({local:[c.fromFrame,c.toFrame],final:[from,cursor]});if(c.entryId&&!p.cuts.slice(i+1).some(x=>x.entryId===c.entryId))for(const id of children.get(c.entryId)||[])appendAddition(id);}
 const retime=(f,end=false)=>{for(const m of map)if(end?f>m.local[0]&&f<=m.local[1]:f>=m.local[0]&&f<m.local[1])return m.final[0]+f-m.local[0];if(f===map.at(-1).local[1])return map.at(-1).final[1];throw Error('Original retime outside '+name+' '+f);};
 for(const e of p.entries){const en=enDraft.paragraphs.find(x=>x.id===e.id);if(!en)throw Error('Original EN absent');paragraphs.push({id:e.id,kind:'preserved-original',ko:e.text,en:e.en,startFrame:retime(Math.floor((e.startSample-audio.firstSample)/400)),endFrame:retime(Math.min(map.at(-1).local[1],Math.ceil((e.endSample-audio.firstSample)/400)),true),originalChapter:name,originalPcmRange:[e.startSample,e.endSample],koCues:p.cues.filter(x=>x.entryId===e.id).map(c=>({...c,fromFrame:retime(c.firstFrame),toFrame:retime(c.exclusiveEndFrame,true)})),enCues:en.cues.map(c=>({...c,fromFrame:retime(Math.ceil((c.from-audio.firstSample/24000)*60-1e-7)),toFrame:retime(Math.ceil((c.to-audio.firstSample/24000)*60-1e-7),true)}))});}
 chapterRanges.push({chapter:name,audio,segments:map});
}
if(used.size!==39)throw Error('Unused new paragraphs '+[...rows.keys()].filter(x=>!used.has(x)));
appendFraming('part1-conclusion');
// At most a few measured frames adjust the eighth purposeful normal-speed observation beat.
let E=cuts.filter(c=>c.kind==='explanation').reduce((n,c)=>n+c.frames,0),A=cuts.filter(c=>c.kind==='actual').reduce((n,c)=>n+c.frames,0),delta=Math.round(1.5*E-A);
if(Math.abs(delta)>8)throw Error('Allocation requires new teaching selection '+JSON.stringify({A,E,delta}));
if(delta){const c=cuts.find(x=>x.id==='fortnite-mobile-test:native'),at=c.toFrame;c.frames+=delta;c.toFrame+=delta;c.observationBeat.frames+=delta;const last=c.proposedCuts.at(-1);last.outFrame+=delta;for(const z of cuts)if(z!==c&&z.fromFrame>=at){z.fromFrame+=delta;z.toFrame+=delta;}for(const p of paragraphs){if(p.startFrame>=at){p.startFrame+=delta;p.endFrame+=delta;for(const q of [...p.koCues,...p.enCues]){q.fromFrame+=delta;q.toFrame+=delta;}}else if(p.endFrame===at)p.endFrame+=delta;}for(const c of chapterRanges)for(const m of c.segments)if(m.final[0]>=at)m.final=m.final.map(x=>x+delta);cursor+=delta;A+=delta;}
paragraphs.sort((a,b)=>a.startFrame-b.startFrame);
const koCues=paragraphs.flatMap(x=>x.koCues).sort((a,b)=>a.fromFrame-b.fromFrame),enCues=paragraphs.flatMap(x=>x.enCues).sort((a,b)=>a.fromFrame-b.fromFrame);
for(const [lang,cc]of [['KO',koCues],['EN',enCues]])for(let i=0;i<cc.length;i++){cc[i].id=i+1;if(cc[i].toFrame<=cc[i].fromFrame||i&&cc[i].fromFrame<cc[i-1].toFrame)throw Error('Actual cue overlap '+lang+' '+JSON.stringify([cc[i-1],cc[i]]));}
if(paragraphs.length!==77||cuts.some((c,i)=>i&&c.fromFrame!==cuts[i-1].toFrame)||Math.abs(A-.6*(A+E))>1)throw Error('Continuity/count/ratio');
const plan={schemaVersion:1,preparedAt:new Date().toISOString(),slug:'game-lighting-history-04-1',logicalEpisode:4,physicalPart:1,question:'부족한 계산과 메모리로 선명한 화면을 만들려면 어떤 정보를 저장하고 재사용해야 할까요?',bindings,cuts,paragraphs,koCues,enCues,chapterRanges,originalBoundaryRepairs,branding:ref('projects/game-reward-planning/production/final-v1/white-segments/branding.mp4'),membership:ref('projects/game-reward-planning/production/final-v1/white-segments/membership.mp4'),bodyFrames:A+E,actualFrames:A,explanationFrames:E,finalFrames:cursor+600,ratioErrorFrames:A-.6*(A+E),palette:'research-black-v1',captionStyle:'boxed-white-forest-v1',captionCenter:[960,970],fontSize:48,maxLines:2,allOriginal36ParagraphsRetained:true,allSelected39GuidesRetained:true,original111Regenerated:false,allSelectedPcmMustBePreserved:true,sourceAudio:0,loop:0,slowdown:0,cpuThreads:2,gpuJobs:0,finalMixedAsrApproved:false,allFinalPixelsReviewed:false,allMovingPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,humanWholeListening:'pending',newGitImages:0};
fs.writeFileSync(path.join(root,out),JSON.stringify(plan,null,2)+'\n');console.log(JSON.stringify({path:out,paragraphs:77,cuts:cuts.length,A,E,finalFrames:plan.finalFrames,seconds:plan.finalFrames/60,ratioErrorFrames:plan.ratioErrorFrames,koCues:koCues.length,enCues:enCues.length,finalApproved:false}));
