// Current physical part3: preserve all chapter PCM and reuse completed spatial sources.
// Preparation grants no mixed-audio, encoded-pixel or publishing approval.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {alignNarratedEntry}=require('./episode04-caption-alignment-v1.cjs');
const root=path.resolve(__dirname,'../../..'),base='projects/game-lighting-history-04/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const cache=new Map(),sha=p=>{if(!cache.has(p))cache.set(p,crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex'));return cache.get(p);};
const ref=p=>({path:p,sha256:sha(p)}),write=(p,j)=>{p=path.join(root,p);if(fs.existsSync(p))throw Error('Preserve '+p);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,JSON.stringify(j,null,2)+'\n');};
const selectedPath=base+'selected-part3-source-plan-v144.json',selected=read(selectedPath);
for(const r of selected.bindings)if(sha(r.path)!==r.sha256)throw Error('Changed selected review '+r.path);
const sourcePlan=read('production/research/game-lighting-history/local/guided-source-render-v132/plan.json');
const framing=read('production/research/game-lighting-history/local/episode04-physical-framing-v59/plan.json');
const overview=framing.scenes.find(s=>s.id==='part3-overview');if(!overview||overview.frames!==989)throw Error('Overview missing');
const enDraft=read(base+'local/english-caption-draft-v2.json');
const aliases=[...read(base+'local/original-word-anchors-draft-v1.json').chapters[0].alignment.aliases,
 ['이천이십육년','2026년'],['이천십칠년','2017년'],['이천이십이년','2022년'],['삼월','3월'],['구월','9월'],['이 번','2번'],['디엘에스에스 오','dlss5'],['레지던트 이블','레지던트이블'],['엘유티','lut']];
const semantic={
 'appearance-resident':[[0,1],[2],[3],[4]],'appearance-starfield':[[0],[1],[2,3]],
 'appearance-nba':[[0,1],[2,3],[4],[5]],'appearance-to-controls':[[0],[1,2],[3]],
 'exposure-context':[[0],[1],[2,3]],'histogram-control-result':[[0],[1,2],[3]],
 'bloom-surface':[[0,1],[2],[3]],'grade-to-lookup':[[0,1],[2]],'lookup-endpoint':[[0,1],[2],[3]],
 'focus-legend-context':[[0,1],[2],[3]],'focus-distance-transition':[[0],[1],[2,3]],
 'focus-normal-return':[[0],[1],[2,3]],'capture-context':[[0,1],[2],[3]],
 'hogwarts-stair-reference':[[0,1],[2],[3]],'hogwarts-brazier-view':[[0],[1],[2,3]]
};
function sentences(t){let at=0;return (t.match(/[\s\S]+?(?:[.!?](?=\s|$)|$)/g)||[]).filter(s=>s.trim()).map(s=>{const a=t.indexOf(s,at);at=a+s.length;return {text:s.trim(),characters:[a,at]};});}
function englishParts(t){const w=t.trim().split(/\s+/),cost=Array(w.length+1).fill(Infinity),next=[];cost[w.length]=0;
 function lines(a){const s=a.join(' ');if(s.length<=42)return s;let best;for(let i=1;i<a.length;i++){const x=a.slice(0,i).join(' '),y=a.slice(i).join(' '),d=Math.abs(x.length-y.length);if(x.length<=42&&y.length<=42&&(!best||d<best.d))best={s:x+'\n'+y,d};}return best?.s;}
 for(let i=w.length-1;i>=0;i--)for(let z=i+1;z<=w.length;z++){const s=w.slice(i,z).join(' ');if(s.length>85)break;const text=lines(w.slice(i,z));if(!text)continue;const q=140+(s.length-64)**2+(z===w.length&&i&&s.length<24?2200:0)+cost[z];if(q<cost[i]){cost[i]=q;next[i]={z,text};}}
 if(!next[0])throw Error('English wrapping '+t);let o=[];for(let i=0;i<w.length;){o.push(next[i].text);i=next[i].z;}return o;
}
function literalSpans(text,cues){const norm=t=>t.replace(/\s+/g,'');const all=norm(text);let cursor=0;return cues.map(c=>{const s=norm(c.text),a=all.indexOf(s,cursor);if(a!==cursor)throw Error('Literal cue wording gap '+text);cursor=a+s.length;const positions=[];for(let i=0;i<text.length;i++)if(!/\s/.test(text[i]))positions.push(i);return {...c,sourceCharacters:[positions[a],positions[cursor-1]+1]};});}
function englishTrack(p,ko){const a=sentences(p.ko),b=sentences(p.en),g=semantic[p.id]??a.map((_,i)=>[i]);if(g.length!==b.length||g.flat().join(',')!==a.map((_,i)=>i).join(','))throw Error('Semantic mapping '+p.id);
 const o=[];for(let i=0;i<b.length;i++){const first=a[g[i][0]].characters[0],last=a[g[i].at(-1)].characters[1],related=ko.filter(c=>c.sourceCharacters[1]>first&&c.sourceCharacters[0]<last);if(!related.length)throw Error('No word anchor '+p.id);const parts=englishParts(b[i].text),weights=parts.map(t=>t.replace(/\n/g,' ').length),total=weights.reduce((a,b)=>a+b,0),from=related[0].fromFrame,to=related.at(-1).toFrame;let used=0;for(let k=0;k<parts.length;k++){const start=Math.round(from+(to-from)*used/total);used+=weights[k];o.push({entryId:p.id,text:parts[k],fromFrame:start,toFrame:Math.round(from+(to-from)*used/total),koSentenceIndices:g[i],timingMethod:'KO-word-anchored-semantic-translation-reading-splits',measuredEnglishWordTiming:false});}}
 if(o.map(c=>c.text.replace(/\n/g,' ')).join(' ')!==p.en.replace(/\s+/g,' ').trim())throw Error('EN wording loss '+p.id);return o;
}
const eSources={
 'appearance-prerequisite':['production/research/game-lighting-history/local/episode04-guided-source-review-v135/guided-source.clean.mp4',0],
 'appearance-to-controls':['production/research/game-lighting-history/local/episode04-guided-source-review-v135/guided-source.clean.mp4',951],
 'focus-later-settings':['production/research/game-lighting-history/local/episode04-guided-source-review-v142/guided-source.clean.mp4',0],
 'focus-observation-protocol':['production/research/game-lighting-history/local/episode04-guided-source-review-v138/guided-source.clean.mp4',1100],
 'focus-to-frame-inspection':['production/research/game-lighting-history/local/episode04-guided-source-review-v138/guided-source.clean.mp4',2214]
};
const additions=new Map(),children=new Map();
for(const row of selected.rows){if(sha(row.pcm.path)!==row.pcm.sha256)throw Error('PCM changed '+row.id);if(row.source&&sha(row.source.path)!==row.source.sha256)throw Error('Native changed '+row.id);
 let koCues,asr=null;const s=sourcePlan.scenes.find(s=>s.id===row.id);
 if(s)koCues=literalSpans(row.ko,s.cues.map(c=>({...c,fromFrame:c.fromFrame,toFrame:c.toFrame})));
 else {const group=row.id==='capture-target-view'?'native-onset-asr-v131':['focus-scale-edit','focus-layers-entry','debugger-command-submit'].includes(row.id)?'native-followup-asr-v124':'guided-observation-asr-v107',p=base+'local/'+group+'/whole-'+row.id+'.json';const raw=read(p);asr=ref(p);const aligned=alignNarratedEntry(row.ko,raw.chunks,aliases);koCues=aligned.cues.map(c=>({...c,fromFrame:Math.max(0,Math.round(c.from*60)),toFrame:Math.min(row.capacityFrames,Math.round(c.to*60))}));for(let i=1;i<koCues.length;i++)if(koCues[i].fromFrame<koCues[i-1].toFrame){const boundary=Math.round((koCues[i].fromFrame+koCues[i-1].toFrame)/2);koCues[i-1].toFrame=boundary;koCues[i].fromFrame=boundary;}}
 const frames=row.effectiveRole==='explanation'?row.pcmFrames:row.capacityFrames;
 if(koCues.some(c=>c.toFrame<=c.fromFrame))throw Error('Empty KO cue '+row.id);
 const obj={...row,frames,kind:row.effectiveRole,koCues:koCues.map(c=>({...c,entryId:row.id})),enCues:englishTrack(row,koCues),asr,preserveFullPcm:true};
 if(row.effectiveRole==='explanation'){obj.video=ref(eSources[row.id][0]);obj.sourceStartFrame=eSources[row.id][1];}
 else{obj.video=row.source;obj.cropTopPixels=row.id.startsWith('appearance-')?160:120;obj.identityLabel=row.source.game?(row.source.game+' · '+(row.id==='appearance-nba'?'2026 출시 시연':'2026-03 미리보기')):row.id.startsWith('hogwarts-')?'Hogwarts Legacy · 2022 실제 시연':row.id.startsWith('capture-')?'DirectX 12 · 우리 채널 프레임 검사 시연':row.id==='debugger-command-submit'?'DirectX 12 · 명령 제출 관찰 · GPU 완료 측정 아님':row.id.startsWith('resource-')?'Unreal Engine · 가상 텍스처 편집기 시연':'Unreal Engine · 2017 후처리 편집기 시연';}
 additions.set(row.id,obj);if(!children.has(row.insertAfter))children.set(row.insertAfter,[]);children.get(row.insertAfter).push(row.id);
}
const paragraphs=[],cuts=[],used=new Set(),bindings=[ref(selectedPath),ref(base+'guided-selected-source-sample-review-v144.json')];let cursor=120;
function appendAddition(id){if(used.has(id))throw Error('Repeated addition');used.add(id);const row=additions.get(id),from=cursor;cuts.push({...row,fromFrame:from,toFrame:from+row.frames});paragraphs.push({id,kind:'new-guided',ko:row.ko,en:row.en,startFrame:from,endFrame:from+row.frames,pcm:row.pcm,koCues:row.koCues.map(c=>({...c,fromFrame:c.fromFrame+from,toFrame:c.toFrame+from})),enCues:row.enCues.map(c=>({...c,fromFrame:c.fromFrame+from,toFrame:c.toFrame+from}))});cursor+=row.frames;for(const child of children.get(id)||[])appendAddition(child);}
const overviewSource=ref('production/research/game-lighting-history/local/episode04-physical-framing-v60/physical-framing.clean.mp4');
const overviewRow={id:'part3-overview',ko:overview.textKo,en:overview.textEn};
// Source-plan cues are scene-local; remove an offset only when they are explicitly cumulative.
const overviewCues=literalSpans(overview.textKo,overview.cues.map(c=>({text:c.text,fromFrame:c.fromFrame>=overview.fromFrame?c.fromFrame-overview.fromFrame:c.fromFrame,toFrame:c.toFrame>=overview.fromFrame?c.toFrame-overview.fromFrame:c.toFrame})));
const opcm={path:overview.source.path,sha256:overview.source.sha256,samples:overview.sourceSamples,sampleRate:24000};
cuts.push({id:'part3-overview',kind:'explanation',frames:989,fromFrame:cursor,toFrame:cursor+989,video:overviewSource,sourceStartFrame:overview.fromFrame,pcm:opcm,preserveFullPcm:true});
paragraphs.push({...overviewRow,kind:'new-overview',startFrame:cursor,endFrame:cursor+989,pcm:opcm,koCues:overviewCues.map(c=>({...c,entryId:overviewRow.id,fromFrame:c.fromFrame+cursor,toFrame:c.toFrame+cursor})),enCues:englishTrack(overviewRow,overviewCues).map(c=>({...c,fromFrame:c.fromFrame+cursor,toFrame:c.toFrame+cursor}))});cursor+=989;
const chapterRanges=[],originalBoundaryRepairs=[];
for(const [name,ver] of [['dlss',33],['postprocess',37],['inspection',41]]){
 const pp=base+`${name}-chapter-review-plan-v${ver}.json`,ep=base+`${name}-chapter-review-execution-v${ver}.json`,plan=read(pp),execution=read(ep),map=[];bindings.push(ref(pp),ref(ep));
 for(const c of plan.cuts){c.encodedFromFrame=c.fromFrame;c.encodedFrames=c.frames;}
 for(let i=0;i<plan.cuts.length-1;i++){const c=plan.cuts[i],entry=plan.entries.find(e=>e.id===c.id)||plan.entries.filter(e=>c.id.startsWith(e.id+'-')).sort((a,b)=>b.id.length-a.id.length)[0];if(!entry||!children.has(entry.id)||plan.cuts.slice(i+1).some(z=>z.id===entry.id||z.id.startsWith(entry.id+'-')))continue;const end=Math.max(Math.ceil((entry.endSample-plan.audio.firstSample)/400),...plan.cues.filter(z=>z.entryId===entry.id).map(z=>z.exclusiveEndFrame));const extra=end-c.toFrame;if(extra>0){if(extra>1)throw Error('Boundary requires timing revision '+entry.id);originalBoundaryRepairs.push({entryId:entry.id,priorBoundary:c.toFrame,currentBoundary:end,roleBefore:c.kind,roleAfter:plan.cuts[i+1].kind,reason:'Keep complete original PCM and final word before inserting a new guide; opposite role shifts are measured in final totals',sourceModelsRerendered:0});c.toFrame=end;c.frames=c.toFrame-c.fromFrame;plan.cuts[i+1].fromFrame=end;plan.cuts[i+1].frames=plan.cuts[i+1].toFrame-end;}}
 for(let i=0;i<plan.cuts.length;i++){const cut=plan.cuts[i],result=execution.results.find(r=>r.id===cut.id);if(!result||sha(result.path)!==result.sha256)throw Error('Completed cut changed '+cut.id);const oldEnd=cut.toFrame,frames=cut.frames+(name==='inspection'&&i===plan.cuts.length-1?1:0),start=cursor,sourceStartFrame=cut.fromFrame-cut.encodedFromFrame,sourceFrames=cut.encodedFrames-sourceStartFrame;cuts.push({id:`${name}:${cut.id}`,kind:cut.kind,frames,fromFrame:start,toFrame:start+frames,video:{path:result.path,sha256:result.sha256},sourceStartFrame,sourceFrames,pcm:{...plan.audio,firstSample:plan.audio.firstSample+cut.fromFrame*400,exclusiveEndSample:Math.min(plan.audio.exclusiveEndSample,plan.audio.firstSample+oldEnd*400+(frames-cut.frames)*400)},preserveFullPcm:true,originalChapter:name,originalChapterFrames:[cut.fromFrame,cut.toFrame+(frames-cut.frames)],oneSilentVideoTailFrame:Math.max(0,frames-sourceFrames)});
 if(cut.kind==='actual'&&frames>sourceFrames)cuts.at(-1).nativeBoundaryExtension={source:ref(cut.path),sourceStartSeconds:cut.sourceStart+sourceStartFrame/60,frames,cropTopPixels:cut.cropTopPixels??0,shiftUpPixels:cut.shiftUpPixels??0,label:cut.label??null,secondaryLabel:cut.secondaryLabel??null,annotation:cut.annotation??null};
 map.push({local:[cut.fromFrame,cut.toFrame+(frames-cut.frames)],final:[start,start+frames]});cursor+=frames;
 const entry=plan.entries.find(e=>e.id===cut.id)||plan.entries.filter(e=>cut.id.startsWith(e.id+'-')).sort((a,b)=>b.id.length-a.id.length)[0];
 let parent=entry?.id??cut.id;const isLast=!plan.cuts.slice(i+1).some(c=>c.id===parent||c.id.startsWith(parent+'-'));
 if(isLast)for(const child of children.get(parent)||[])appendAddition(child);
 }
 function retime(frame,end=false){for(const m of map)if(end?frame>m.local[0]&&frame<=m.local[1]:frame>=m.local[0]&&frame<m.local[1])return m.final[0]+frame-m.local[0];const last=map.at(-1);if(frame===last.local[1])return last.final[1];throw Error('Outside original chapter '+name+' '+frame);}
 for(const entry of plan.entries){const ko=plan.cues.filter(c=>c.entryId===entry.id).map(c=>({...c,fromFrame:retime(c.firstFrame),toFrame:retime(c.exclusiveEndFrame,true)}));const e=enDraft.paragraphs.find(p=>p.id===entry.id);if(!e)throw Error('English draft '+entry.id);const en=e.cues.map(c=>({...c,fromFrame:retime(Math.ceil((c.from-plan.audio.firstSample/24000)*60-1e-7)),toFrame:retime(Math.ceil((c.to-plan.audio.firstSample/24000)*60-1e-7),true)}));paragraphs.push({id:entry.id,kind:'preserved-original',ko:entry.text,en:entry.en,startFrame:retime(Math.floor((entry.startSample-plan.audio.firstSample)/400)),endFrame:retime(Math.min(map.at(-1).local[1],Math.ceil((entry.endSample-plan.audio.firstSample)/400)),true),originalChapter:name,originalPcmRange:[entry.startSample,entry.endSample],koCues:ko,enCues:en});}
 chapterRanges.push({chapter:name,audio:plan.audio,segments:map});
}
if(used.size!==46)throw Error('Unused insertions '+[...additions.keys()].filter(k=>!used.has(k)));
paragraphs.sort((a,b)=>a.startFrame-b.startFrame);const koCues=paragraphs.flatMap(p=>p.koCues).sort((a,b)=>a.fromFrame-b.fromFrame),enCues=paragraphs.flatMap(p=>p.enCues).sort((a,b)=>a.fromFrame-b.fromFrame);
for(const [lang,cues]of [['ko',koCues],['en',enCues]]){for(let i=0;i<cues.length;i++){cues[i].id=i+1;if(cues[i].toFrame<=cues[i].fromFrame||i&&cues[i].fromFrame<cues[i-1].toFrame)throw Error('Cue overlap '+lang+' '+JSON.stringify([cues[i-1],cues[i]]));}}
const E=cuts.filter(c=>c.kind==='explanation').reduce((s,c)=>s+c.frames,0),A=cuts.filter(c=>c.kind==='actual').reduce((s,c)=>s+c.frames,0);if(E!==36527||A!==54791||cursor!==91438||Math.abs(A-.6*(A+E))>1)throw Error('Measured allocation changed '+JSON.stringify({E,A,cursor}));
const branding=ref('projects/game-reward-planning/production/final-v1/white-segments/branding.mp4'),membership=ref('projects/game-reward-planning/production/final-v1/white-segments/membership.mp4');
const plan={schemaVersion:1,preparedAt:new Date().toISOString(),slug:'game-lighting-history-04-3',logicalEpisode:4,physicalPart:3,question:'좋아 보이는 화면만으로 내부 계산까지 알 수 있을까요?',scope:'DLSS4/5 appearance, exposure/color/focus, frame commands and resources; full conceptual conclusion',bindings,cuts,paragraphs,koCues,enCues,chapterRanges,originalBoundaryRepairs,branding,membership,bodyFrames:E+A,actualFrames:A,explanationFrames:E,finalFrames:cursor+600,ratioErrorFrames:A-.6*(A+E),palette:'research-black-v1',captionStyle:'boxed-white-forest-v1',captionCenter:[960,970],fontSize:48,maxLines:2,original111Regenerated:false,allSelectedPcmMustBePreserved:true,sourceAudio:0,loop:0,slowdown:0,cpuThreads:2,gpuJobs:0,finalMixedAsrApproved:false,allFinalPixelsReviewed:false,allMovingPixelsReviewed:false,qaApproved:false,collected:false,uploaded:false,humanWholeListening:'pending',newGitImages:0};
write(base+'part3-final-input-plan-v145.json',plan);console.log(JSON.stringify({plan:base+'part3-final-input-plan-v145.json',cuts:cuts.length,paragraphs:paragraphs.length,koCues:koCues.length,enCues:enCues.length,E,A,bodyFrames:E+A,finalFrames:plan.finalFrames,finalApproved:false}));
