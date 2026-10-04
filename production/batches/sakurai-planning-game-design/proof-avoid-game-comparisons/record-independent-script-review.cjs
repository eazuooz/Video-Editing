const fs=require('fs'),path=require('path'),crypto=require('crypto'),cp=require('child_process');
const root=path.resolve(__dirname,'../../../..'),base='production/batches/sakurai-planning-game-design',proof=base+'/proof-avoid-game-comparisons',sr=proof+'/source-research',project='projects/avoid-game-comparisons';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const write=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const now=new Date().toISOString(),ko=read(project+'/script/narration.ko.json'),en=read(project+'/script/narration.en.json'),map=read(project+'/sources/action-map.json'),plan=read(project+'/planning/chapter-plan.json');
if(ko.scenes.length!==12||en.scenes.length!==12||map.clips.length!==68||map.candidateActualSeconds!==192.7)throw Error('Unexpected review input');
const gate=cp.spawnSync(process.execPath,['scripts/review-video-duplicates.cjs','avoid-game-comparisons','--check'],{cwd:root,encoding:'utf8',windowsHide:true});if(gate.status!==0)throw Error(gate.stdout+gate.stderr);
const paragraphSources={
 '02':[[1,2,3,4,9,10,17,19,25,28,32],[7,20,22,30],[72],[]],
 '04':[[35,36],[43,44,45,46],[60,61],[],[]],
 '06':[[5,6,15,18,26,27,31,33,34],[73,74],[63,64],[66],[]],
 '08':[[59],[65],[67],[]],
 '10':[[37,39,40,41,42],[75,76],[68,69,70],[49],[]],
 '12':[[47,48,50,51,52,53,54,56,57,58,71],[77,78,79,80],[],[],[]]
};
const decisions={
 '01':'Four independent sentences introduce the unbuilt-game question, verbs/space and conditions, three-sentence practice and listener questions; first case is yellow-terrain emergence. Promises occur in02/04/05/06/07/09/11/12.',
 '02':'Visible yellow/cave/air movement, hook and cannon shots match the native action bank. No exact control mapping or universal material rule is claimed.',
 '03':'Two listeners are explicitly hypothetical; no actual survey or original-source example name is asserted. Focus remains communicating an unbuilt concept.',
 '04':'Book surfaces, virtual3D desk, printed doors and cup-entry/exit are observed. Separate source shots are not made into a continuous control sequence. Real-life launch-advertisement footage is excluded.',
 '05':'Space/action/visible-change sentence is our explanatory method, illustrated by already observed cup/desk entry. Genre/title remains contextual rather than a complete specification.',
 '06':'Terrain, water, bridge, elastic surface, rocket rise/descent and a glowing object are within observed bounds. Fuel refilling, unlimited flight and button rules are explicitly unconfirmed.',
 '07':'Costs, duration and repeat conditions are proposed questions for the new concept, not facts about either reference game.',
 '08':'Desk attack/throw, flat blue-surface jumping/combat and cylinder-entry actions are kept separate.',
 '09':'Goal/action-condition/connection example is explicitly our description exercise; no actual developer pitch/document or complete game goal is reconstructed.',
 '10':'Lighting/text, balls, vehicle cuts and cylinder shooting are separate observed actions; no causal bridge across edits or default-assist/difficulty rule is inferred.',
 '11':'Restatement and the any-wall response are a proposed check with a hypothetical listener, not a measured study.',
 '12':'New nonreused ending action intervals support verb/space distinctions. Device cost/victory is not inferred; conclusion repeats the promised three-sentence practice and restatement.'
};
const scenes=ko.scenes.map((s,i)=>{
 const t=en.scenes[i],chapter=map.chapters.find(c=>c.id===s.id);if(s.id!==t.id||s.lines.length!==t.lines.length)throw Error('Bilingual topology mismatch');
 const groups=paragraphSources[s.id];if(groups&&groups.length!==s.lines.length)throw Error('Paragraph action links mismatch');
 return {id:s.id,role:chapter.role,paragraphs:s.lines.map((line,j)=>({paragraph:j+1,koSha256:crypto.createHash('sha256').update(line).digest('hex'),enSha256:crypto.createHash('sha256').update(t.lines[j]).digest('hex'),sourceActionIds:(groups?.[j]||[]).map(n=>'action-'+String(n).padStart(2,'0')),meaningOrderAndClaimScopeDirectlyCompared:true})),directReview:decisions[s.id],planningSourceSeconds:Number(map.clips.filter(c=>c.sceneId===s.id).reduce((a,c)=>a+c.seconds,0).toFixed(6)),measuredNarrationSeconds:null};
});
const inputs=[project+'/script/narration.ko.json',project+'/script/narration.en.json',project+'/planning/outline.md',project+'/planning/chapter-plan.json',project+'/sources/action-map.json',project+'/sources/game-candidates.json',sr+'/source-action-bank-v2.json',sr+'/direct-native-review-v1.json',sr+'/direct-pepper-drill-review.json'];
const scriptReview={schemaVersion:1,reviewedAt:now,status:'complete-independent-bilingual-text-and-source-claim-review; audio/visual timing pending',method:'All12 paired KO/EN scenes and50 whole paragraphs read back and directly compared against the independent outline, conservative native action bank and observed cut limits. This is text/meaning review, not human listening or final pixel approval.',inputs:inputs.map(p=>({path:p,sha256:hash(p)})),scenes,paragraphs:50,sourceAudioUsed:false,selfCreatedGameExamples:0,overviewPromiseReview:{question:{promise:'Different images recalled from familiar titles when describing an unbuilt game',fulfilledBy:['03.1','03.2','03.4']},orderedCases:{promise:'Pepper verbs, Plucky surface/desk conditions, then independent three-sentence practice and listener questions',fulfilledBy:['02','04','05','06','07','09','11']},outcome:{promise:'Write goal/action-condition/connection and identify missing conditions',fulfilledBy:['09.1','09.2','09.3','09.4','11.1','11.2','11.3','12.4','12.5']},firstCaseBridge:{promise:'Yellow terrain emergence',fulfilledBy:['02.1'],sourceActionIds:['action-01','action-02','action-19']}},wholeBilingualScriptReviewed:true,overviewTextPromisesFulfilled:true,ttsStarted:false,independentMotionCanvasScenesCreated:false,voiceAsrReview:false,finalCaptionAndCutPixelsReviewed:false,measuredRatioApproved:false,humanWholeListening:'pending',finalPublicRights:'pending'};
write(project+'/production/script-source-review.json',scriptReview);
plan.overview.fullBodyPromiseReviewComplete=true;plan.overview.independentNarrationFilesCreated=true;plan.overview.textReview=project+'/production/script-source-review.json';plan.updatedAt=now;write(project+'/planning/chapter-plan.json',plan);
const manifest=read(project+'/project.json');manifest.status='independent-bilingual-script-reviewed';manifest.editing.openingOverview=plan.overview;manifest.editing.scriptSourceReview=project+'/production/script-source-review.json';manifest.preflight.latestGateAt=now;manifest.preflight.latestInputsDigest=read(base+'/preflight/avoid-game-comparisons.json').inputsDigest;write(project+'/project.json',manifest);
fs.appendFileSync(path.join(root,project+'/planning/outline.md'),'\n## 전체 한영 대본 직접 검토 — '+now+'\n\n12장50문단의 독립KO/EN본문을 모두 다시 읽고 의미·순서·주장·출처 제한을 직접 대조했다. 도입의 질문은03, 이동과면/조건의 순서는02/04/05/06/07, 세 문장 실습은09, 청자의 되말하기는11, 결론의 실제 적용은12에 있다. 원본강의를 복사/번역하지 않았고 가상청자·세문장 실습·비용 질문은 우리의 설명 제안으로 표시했다. 현재 production/script-source-review.json은 텍스트 승인만 기록하며 음성·최종화면·고정자막·실측60:40을 승인하지 않는다. 실제 음성 시간을 측정한 뒤 부족한 관련 고유 행동을 추가하고 좋은 설명을 줄이지 않는다.\n');
// Refresh the text review hashes after its own approved planning updates.
scriptReview.inputs=inputs.map(p=>({path:p,sha256:hash(p)}));write(project+'/production/script-source-review.json',scriptReview);
const inputReview=read(project+'/production/planning-input-review.json');inputReview.updatedAt=now;inputReview.status='independent-plan-and-whole-bilingual-text-reviewed; measured audio and final pixels pending';inputReview.wholeScriptCreated=true;inputReview.scriptSourceReview=project+'/production/script-source-review.json';inputReview.inputs=[project+'/project.json',...inputs].map(p=>({path:p,sha256:hash(p)}));write(project+'/production/planning-input-review.json',inputReview);
console.log(JSON.stringify({scenes:12,paragraphs:50,wholeBilingualTextReviewed:true,overviewPromisesFulfilled:true,ttsStarted:false,measuredRatioApproved:false}));
