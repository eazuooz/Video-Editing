const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../..'),p='projects/game-lighting-history-03',b='production/research/game-lighting-history';
const read=x=>JSON.parse(fs.readFileSync(path.join(root,x),'utf8')),sha=x=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,x))).digest('hex');
const write=(x,v)=>fs.writeFileSync(path.join(root,x),JSON.stringify(v,null,2)+'\n');
const previous=p+'/production/native-integration-plan-v10.json',plan=read(previous);
const out=p+'/production/native-integration-plan-v11.json',draft=p+'/script/native-observation-guides.draft-v3.json';
if([out,draft].some(x=>fs.existsSync(path.join(root,x))))throw Error('Preserve completed preparation');
for(const x of plan.inputHashes)if(sha(x.path)!==x.sha256)throw Error('Original input changed: '+x.path);
const reviews=['native-crop-direct-review-v10.json','native-lumen-action-direct-review-v11.json','native-nanite-action-direct-review-v11.json','native-lighting-action-direct-review-v11.json','native-nanite-support-direct-review-v12.json','native-lighting-support-direct-review-v12.json'].map(x=>({path:p+'/production/'+x,sha256:sha(p+'/production/'+x)}));
for(const i of [19,72]){const x=plan.paragraphs.find(x=>x.index===i);if(plan.explanationRetention.paragraphs.includes(i))throw Error('Already retained');plan.explanationRetention.paragraphs.push(i);plan.explanationRetention.minimumFrames+=x.frames;x.plannedRole='explanation';}
plan.explanationRetention.paragraphs.sort((a,b)=>a-b);plan.explanationRetention.seconds=plan.explanationRetention.minimumFrames/60;
plan.explanationRetention.reason+=' Keep19 BLAS/TLAS update distinction and72 SurfaceCache capture definition as complete spatial explanations: the native footage does not display these internal processes.';
const selections={
 'guide-mesh-distance-field':[[237,247],[249,261],[263,269]],
 'guide-ray-shadow':[[168,173],[176,182],[186,191],[200,213]],
 'guide-nvrtx-result':[[25,38],[39,48],[69,79]],
 'guide-dlss-helmet':[[3,18],[19,33]],
 'guide-dlss-thin-lines':[[3,18],[39,48]],
 'guide-dlss-engine-modes':[[179,204],[213.5,217.5],[253,273]],
 'guide-ddgi-volume':[[205,220],[226,240]],
 'guide-ddgi-spacing':[[258,263],[279,293],[294,303],[310,313]],
 'guide-ddgi-city':[[366,372],[402,406]],
 'guide-rtxdi-boulevard':[[5,35],[35,65]],
 'guide-nanite-occlusion':[[453,476],[528,543]],
 'guide-nanite-debug-modes':[[110,114],[127,144],[151,178],[202,210],[514,517]],
 'guide-nanite-distance':[[666,691],[695,709],[720,736]],
 'guide-nanite-bicycle':[[596,602],[605,625],[630,635]],
 'guide-lumen-light-edit':[[390,402],[460,478],[490,511],[514,523]],
 'guide-lumen-interior-toggle':[[658,680],[682,701],[710,720]]
};
for(const g of plan.guides)g.ranges=selections[g.id];
const city=plan.guides.find(x=>x.id==='guide-ddgi-city');
city.ko='이번 도시 예제에서는 건물 사이에 놓인 프로브를 보세요. 원본의 격자 수치는 이 시연의 설정이며 모든 게임의 기본값은 아닙니다.';
city.en='In this city example, inspect the probes between buildings. The grid count shown in the source is specific to this demonstration, rather than a default for every game.';
const interior=plan.guides.find(x=>x.id==='guide-lumen-interior-toggle');
interior.ko='다음은 창문이 있는 실내 예제입니다. 루멘 글로벌 일루미네이션 항목을 바꾸는 동작을 확인하고, 밝은 창문 가까운 곳과 소파 뒤쪽의 벽과 천장을 나누어 보겠습니다. 창문이 밝다고 해서 방 전체에 간접광이 충분히 들어왔다는 뜻은 아닙니다. 화면이 어두워지는 전환과 다시 밝아진 상태를 확인하고, 이어지는 카메라 이동은 별도의 관찰로 읽으세요. 이 원본은 노출을 고정한 계측 실험이 아닙니다. 그래도 직접 빛을 받는 영역과 방의 나머지 표면을 구별해 보는 출발점이 됩니다. 앞에서 계산한 저장과 갱신의 구조를 실제 실내 결과에 연결해 보겠습니다.';
interior.en='The next example is an interior with windows. Identify the edit to Lumen Global Illumination, then inspect the region near the bright windows separately from the wall behind the sofa and the ceiling. A bright window does not establish sufficient indirect illumination throughout the room. Identify the darkening transition and the bright state, then treat the following camera movement as a separate observation. The source is not an exposure-locked measurement experiment. It still provides a starting point for distinguishing directly illuminated regions from the other room surfaces. Connect the storage and update structure explained earlier to this actual interior result.';
plan.guides.push(
 {id:'guide-global-distance-field',after:8,source:'lumen-content-examples-2021',ranges:[[270,282]],ko:'이제 글로벌 디스턴스 필드 표시로 바뀝니다. 같은 바위를 카메라로 따라가며 앞의 메시별 거리장과 거친 표현의 차이를 보세요. 색이 비슷해도 저장 단위는 구별해야 합니다.',en:'The view now switches to Global DistanceField. Follow the same rocks with the camera and compare this coarse representation with the earlier per-mesh fields. Similar colors do not make the storage units identical.'},
 {id:'guide-ddgi-light-change',after:37,source:'rtxgi-ue5-preview2-2022',ranges:[[115,122],[157,167]],ko:'두 상자에서는 햇빛과 그림자가 움직입니다. 다음 조작은 간접광 메서드를 없음에서 플러그인으로 바꾸며, 어두웠던 벽에 색이 다시 나타납니다. 동작과 결과를 확인하되 이 시연만으로 갱신 지연을 재지는 않겠습니다.',en:'Sunlight and shadows move in the two boxes. The next edit changes the indirect-light method from None to Plugin, and color returns to the previously dark walls. Observe the action and result without treating this demonstration as a measurement of update latency.'},
 {id:'guide-nanite-cave-visibility',after:55,source:'nanite-editor-motion-2021',ranges:[[318,338],[340,347],[350,359]],ko:'동굴 안에서는 가까운 바위가 출구와 건물의 일부를 가리고 있습니다. 카메라가 움직이면 가렸던 표면이 차례로 드러납니다. 화면 안에 들어온 후보와 지금 보이는 표면이 다르다는 앞의 계산을 이 움직임에 연결해 보세요. 출구를 지날 때 같은 건물의 화면 크기와 가림도 함께 달라집니다. 이런 관찰은 가시성 문제를 보여 주지만, 개별 컬링 단계의 실행 시간을 분리한 실험은 아닙니다. 내부 계산은 앞의 깊이 피라미드 도식으로 다시 따라갈 수 있습니다.',en:'Inside the cave, nearby rocks hide parts of the exit and building. Moving the camera reveals these surfaces in turn. Connect this motion to the earlier distinction between candidates within the image and surfaces currently visible. Passing through the exit also changes the building’s screen size and occlusion. These observations illustrate the visibility problem, while not isolating the execution time of an individual culling stage. The internal calculation can be followed separately in the depth-pyramid diagram.'},
 {id:'guide-nanite-ornament-surface',after:61,source:'nanite-editor-motion-2021',ranges:[[386,404],[432,444]],ko:'이번 장식 벽에서는 작은 굴곡의 모양과 표면의 색을 나누어 보겠습니다. 가까이 다가가며 옆으로 움직이면 가는 틈과 돌출된 부분이 서로 가리는 관계가 달라집니다. 단순히 텍스처가 선명해졌다는 말만으로는 이 기하의 변화를 설명할 수 없습니다. 이어서 밝은 바깥으로 나오면 멀리 있는 조각상과 건물이 한 화면에 들어옵니다. 가까운 세부와 넓은 장면을 처리하는 일은 모두 필요하지만, 메시의 선택과 재질의 평가와 빛의 계산은 각각 다른 예산을 사용합니다.',en:'On this ornamented wall, distinguish the shapes of small ridges from the surface colors. Moving closer and sideways changes the occlusion between narrow gaps and projecting parts. Saying only that the texture became sharper does not explain these geometric relationships. Emerging into the bright exterior then brings distant statues and buildings into one image. Both nearby detail and a broad scene must be handled, but mesh selection, material evaluation and lighting use separate budgets.'}
);
const timing=read(plan.inputHashes.find(x=>x.path.endsWith('.timing.json')).path),speed=timing.entries.reduce((s,e)=>s+e.text.length,0)/timing.entries.reduce((s,e)=>s+e.end-e.start,0);
for(const g of plan.guides){g.estimatedSeconds=g.ko.length/speed;g.sourceRangesProvisional=true;g.nativeTemporalSamplesAndCropDirectRead=true;g.sourceMotionAndCropReviewed=false;g.sourceMotionAndCropApproved=false;g.sourceAudioUsed=false;g.plannedRole='actual';g.ttsApproved=false;g.ttsGenerated=false;g.generated=false;g.koEnDraftDirectRead=false;g.nativeSelectionReviewPending=true;g.finalUseApproved=false;}
plan.guides.sort((a,b)=>a.after-b.after);
plan.preparedAt=new Date().toISOString();plan.status='exact-action-guides-prepared-awaiting-full-text-and-current-duplicate-review';plan.previousPlan={path:previous,sha256:sha(previous)};plan.nativeDirectReviews=reviews;
plan.exactControlObservations=[{source:'lumen-content-examples-2021',localSeconds:270,checked:'MeshDistanceFields'},{source:'lumen-content-examples-2021',localSeconds:272,selected:'GlobalDistanceField'},{source:'lumen-content-examples-2021',localSeconds:670,menuLabel:'LumenGlobalIllumination'},{source:'rtxgi-ue5-preview2-2022',localSeconds:164,method:'None',hoveredOption:'Plugin',tooltip:'Use plugin for GlobalIllumination'},{source:'rtxgi-ue5-preview2-2022',localSeconds:166.5,method:'Plugin',result:'Colored indirect-light appearance returns in both boxes',methodOfReview:'CUA actual raw video pixel; nominal1fps frame165 and exact165 seek differ at boundary, no exact transition timestamp/latency claimed'}];
plan.minimumBodyFramesAt60To40=Math.ceil(plan.explanationRetention.minimumFrames/0.4);plan.minimumAddedActualFrames=plan.minimumBodyFramesAt60To40-plan.originalBodyFrames;plan.minimumAddedActualSeconds=plan.minimumAddedActualFrames/60;plan.approximateEpisodeMinutes=plan.minimumBodyFramesAt60To40/3600;plan.plannedGuideSeconds=plan.guides.reduce((s,g)=>s+g.estimatedSeconds,0);
plan.timingMeasured=false;plan.bodyRatioApproved=false;plan.gates.sourceMotionAndCrop=false;plan.gates.guideTtsInputApproval=false;plan.gates.currentDistinctBeforeNewTts=false;plan.gates.gpuHandoff=false;
plan.nativeLongHoldsExcluded=['Nanite178–201,218–242,282–295,567–582,792–815,819–835,841–855','Lumen442–457,656–657presenters','RTXGI108–114,183–192,245–257,263–278,303–309,372–401','HWRT105–107artifact,191–199,244–251,323–333','DLSS204–213hover,218–240,242–252'];
plan.next='Full20 KOEN direct text read, fresh inventory/Studio currentdistinct, guarded guide-only exclusive TTS after sealed research boundary. Measure and directly review all guide PCM/ASR; allocate unique action cuts and adopt current spatial models without removing original84 text/audio. Final motion/caption/60:40/pair/upload gates remain false.';
write(out,plan);write(draft,{schemaVersion:1,status:'prepared-only-not-approved-for-tts',preparedAt:plan.preparedAt,originalKoEnUntouched:true,previousDraft:p+'/script/native-observation-guides.draft-v2.json',sourcePlan:out,guides:plan.guides});
console.log(JSON.stringify({out,draft,guides:plan.guides.length,retainedPptParagraphs:plan.explanationRetention.paragraphs.length,explanationFrames:plan.explanationRetention.minimumFrames,minimumAddedSeconds:plan.minimumAddedActualSeconds,estimatedGuidesSeconds:plan.plannedGuideSeconds,minMinutes:plan.approximateEpisodeMinutes,ttsStarted:false}));
