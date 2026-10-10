const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),project='projects/game-lighting-history-03',prod=project+'/production';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8')),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const state=read(prod+'/native-guides-asr-execution-v1.json');
const notes=[
 ['01-mesh-distance-field','Both full transcripts begin 보는 instead of expected 지금 보는. Preserve suspected missing onset as unresolved; do not approve from agreement between recognizers. Whole recognizes 기하, independent context 기아; 앞의→앞에 and 자료이므로→자료임으로 are also preserved. Every other sentence and final 묶지 않겠습니다 appears once. Targeted onset with silence padding and actual PCM comparison required.'],
 ['02-global-distance-field','Full whole/context agree on all three sentences and final 구별해야 합니다. 앞의 메시별 is recognized 앞에 메시벨. Device/term pronunciation remains pending human review.'],
 ['03-ray-shadow','All four complete sentences including final 비용까지 측정했다고 말할 수는 없습니다 appear once in both decodes. 점광원 recognized 전광원; preserve pronunciation uncertainty. No greeting/extra conclusion observed.'],
 ['04-nvrtx-result','All four sentences and final 뜻이 아닙니다 appear once. 물체의 recognized 물체에; retain particle uncertainty. Distinct reflection/shadow/indirect-light controls and no identical-filter claim are preserved.'],
 ['05-dlss-helmet','Both complete transcripts preserve helmet/glove/wall, quality-mode conditions, small boundaries and enlarged-source caveat; final 일반화하지 않겠습니다 present once. No omitted sentence or repetition observed.'],
 ['06-dlss-thin-lines','Both complete transcripts preserve indoor thin lights/branches, moving boundaries, single-frame sharpness versus temporal stability and vendor-measurement caveat. 실내의 recognized 실내에; human particle pronunciation pending.'],
 ['07-dlss-engine-modes','All four complete sentences appear once with final 가정하지 않겠습니다. 디엘에스에스→DLSS, 디엘에이에이→DLA, 엔아이에스→NIS in both decodes; DLAA letter pronunciation remains unresolved for human review. Reconstruction/native antialiasing/spatial enlargement remain distinct.'],
 ['08-ddgi-light-change','Both complete transcripts preserve sunlight/shadows, None→Plugin operation, recovered wall color and no latency measurement. 시연 recognized 시험, retained as recognition/pronunciation uncertainty. Final 재지는 않겠습니다 present once.'],
 ['09-ddgi-volume','Both full four-sentence transcripts preserve volume size, spatial points, wall occlusion and the final 해결되지는 않습니다 once. 볼륨의→볼륨에 and 벽뒤의→벽뒤에 remain pronunciation/recognition uncertainties.'],
 ['10-ddgi-spacing','All four sentences and final 연결하겠습니다 appear once in both full texts. 앞의 보간 is recognized 앞에 보관; preserve the term uncertainty for human review. Debug spheres are not physical inserted lights.'],
 ['11-ddgi-city','Both complete two-sentence texts preserve the specific city grid settings and the warning against generalizing to every game. No omission, repeat or greeting observed.'],
 ['12-rtxdi-boulevard','Both complete four-sentence texts preserve moving car/signs/surfaces, 2021 capture date and the separation of visible results from reservoir internals. Spoken date and 일삼 normalize to numerals. No omission or repeat observed.'],
 ['13-nanite-occlusion','Both complete four-sentence texts preserve facade occlusion, changing screen size and the independent depth-pyramid explanation. 도식의 is recognized 도시계; preserve uncertainty. No isolated culling-cost measurement claim or repeated sentence observed.'],
 ['14-nanite-cave-visibility','Both complete six-sentence texts preserve rocks, cave exit, facade visibility and the final 있습니다 once, ending at27.68 within27.92 seconds. Only spacing differs.'],
 ['15-nanite-ornament-surface','Both complete five-sentence texts preserve ridges, occlusion, bright exterior and separate geometry/material/light budgets. 기하→기아 and 메시→메쉬 are preserved uncertainties. Final 사용합니다 appears once.'],
 ['16-nanite-debug-modes','Both complete five-sentence texts preserve Triangles→Clusters→material view and source-statistics limitations. 시연은→시어는 and 기하→기아 are retained uncertainties. Final 바꾸지 않겠습니다 ends at29.02 within29.04 seconds, once.'],
 ['17-nanite-distance','Both complete four-sentence texts preserve close face, distant facade, doubled-distance diagram and the warning that actual camera conditions change together. Final 이해하세요 appears once.'],
 ['18-nanite-bicycle','Both complete four-sentence texts preserve thin tubing/spokes/floor and separate geometry, texture, lighting budgets. 기하→기아 appears twice, aligned to the two expected uses. Final 설명하지는 않겠습니다 ends at24.78 within24.8 seconds, once.'],
 ['19-lumen-light-edit','Both complete four-sentence transcripts preserve directional-light selection, lit/shaded surfaces, separate camera movement and no update-time/brightness-ratio measurement. Final 계산하지 않겠습니다 ends at21.70 within22 seconds, once.'],
 ['20-lumen-interior-toggle','Both whole and independent full texts diverge substantially in the first roughly33seconds: 다음은 블루프린트를 다음은 재생하는 애니메이션 애니메이션 모션 애니메 replaces the expected first four sentences. Whole timestamps also regress from24.4 to20.0. The final three expected sentences appear once through47.18/47.08. Do not infer that the first four sentences were spoken correctly or that this is only a chunk-edge recognition error. Preserve current47.28sec PCM, hold audio approval and independently decode short PCM windows before any selective correction.']
];
const results=[];
for(const [id,note] of notes){
 const windows=['whole','context'].map(mode=>{const p=prod+'/local/native-guides-asr-v1/'+mode+'-'+id+'.json';const entry=state.results.find(x=>x.path===p);if(!entry||sha(p)!==entry.sha256)throw Error('Exact already-direct-read recognition missing '+p);const d=read(p);return {path:p,sha256:entry.sha256,input:d.input,expectedKo:d.expectedKo,actualFullText:d.text,firstWord:d.chunks[0],lastWord:d.chunks.at(-1),completeTextDirectlyRead:true};});
 results.push({id,windows,note,audioApproved:false,assembledJoinApproved:false,humanListening:'pending',humanPronunciation:'pending'});
}
const out=prod+'/native-guides-asr-direct-progress-v1.json';
const record={schemaVersion:1,reviewedAt:new Date().toISOString(),execution:prod+'/native-guides-asr-execution-v1.json',directlyReadWindows:results.length*2,expectedWindows:40,results,
 original84AsrRepeated:false,allGuideAsrApproved:false,finalMixedAsrApproved:false,endingHeuristicUsedAsApproval:false,
 unresolvedOnset:{id:'01-mesh-distance-field',expected:'지금 보는',whole:'보는',independent:'보는',actualMissingAudioConfirmed:false,requiresTargetedOnsetReview:true},
 unresolvedGuide20:{id:'20-lumen-interior-toggle',firstFourSentencesMismatch:true,actualMissingAudioConfirmed:false,requiresTargetedPcmReview:true},
 remainingWindowsPending:results.length<20,humanWholeListening:'pending',humanPronunciation:'pending'};
fs.writeFileSync(path.join(root,out),JSON.stringify(record,null,2)+'\n');
const cpPath='production/research/game-lighting-history/checkpoint.json',cp=read(cpPath);
cp.updatedAt=new Date().toISOString();cp.episode03GuideAsrDirectProgress={path:out,sha256:sha(out),directlyReadWindows:record.directlyReadWindows,total:40,allApproved:false,unresolvedOnset:true};
cp.episode03MeasuredTimelineCandidate={path:prod+'/measured-native-timeline-candidate-v13.json',sha256:sha(prod+'/measured-native-timeline-candidate-v13.json'),adopted:false,bodyFrames:93110,actualFrames:55866,explanationFrames:37244,original47WholeExplanations:true,rendered:false};
cp.episode03RetainedCleanScenePreparation={path:prod+'/retained-clean-scene-preparation-v1.json',sha256:sha(prod+'/retained-clean-scene-preparation-v1.json'),newImages:0,newMedia:0,rendered:false};
fs.writeFileSync(path.join(root,cpPath),JSON.stringify(cp,null,2)+'\n');console.log(JSON.stringify({out,directlyReadWindows:record.directlyReadWindows,allApproved:false,unresolvedOnset:true}));
