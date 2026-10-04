const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../../..'),base='production/batches/sakurai-planning-game-design',proof=base+'/proof-avoid-game-comparisons',sr=proof+'/source-research',project='projects/avoid-game-comparisons';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const write=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const now=new Date().toISOString(),bank=read(sr+'/source-action-bank-v2.json'),map=read(project+'/sources/action-map.json'),scriptReview=read(project+'/production/script-source-review.json'),gate=read(base+'/preflight/avoid-game-comparisons.json'),priorGit=read(proof+'/source-bank-git-verification.json');
if(bank.clips.length!==80||bank.uniqueSourceSeconds!==203||!scriptReview.wholeBilingualScriptReviewed)throw Error('Incomplete text/source review');
const official=read(sr+'/official-source-observations.json');
for(const [videoId,title,uiDate,metadataDate,observationFile,status] of [
 ['dkxNejWRGsA','Pepper Grinder | Reveal Trailer | Grinding in2023','2022-11-10','20221109','pepper-reveal-official.ax.txt','acquired-decoded-duplicate-actions-excluded-zero-new-seconds'],
 ['o3Fomp9HdHs','Pepper Grinder DRILLfomercial | Coming to PC & Switch on March28 | Download the Demo!','2024-03-06','20240305','pepper-drill-official.ax.txt','acquired-decoded-native-reviewed-nine-conservative-planning-intervals']
]){
 if(!official.observations.some(x=>x.videoId===videoId))official.observations.push({videoId,title,owner:'DevolverDigital',verified:true,channelId:'UCSc6s-ZJXKlSQr51dsox34g',uiDate,downloadMetadataDate:metadataDate,dateDifference:'Keep the normal browser date and downloader metadata date as separately observed values. Historical promotion is not a present release/version assertion.',status});
 const p=sr+'/'+observationFile;if(!official.localObservationFiles.some(x=>x.path===p))official.localObservationFiles.push({path:p,sha256:hash(p),gitDelivery:false});
}
official.latestObservedAt=now;write(sr+'/official-source-observations.json',official);
const specs=[
 ['official-Reveal-acquisition-full-decode','acquisition-pepper-reveal.json',8173,'closed-decode0-duplicate-actions-excluded'],
 ['Reveal-discovery','discovery-pepper-reveal.json',null,'closed-all5sheets72frames-read'],
 ['official-DRILL-acquisition-full-decode','acquisition-pepper-drill.json',7369,'closed-decode0-native-actions-reviewed'],
 ['DRILL-discovery','discovery-pepper-drill.json',null,'closed-all6sheets81frames-read'],
 ['DRILL-native-action-boundaries','native-review-drill-v1.json',14561,'closed-all10sheets58actions80boundary-tiles-read']
];
const workers=specs.map(([kind,file,sessionId,status])=>{const d=read(sr+'/'+file);return {kind,pid:d.pid,sessionId,state:sr+'/'+file,status,exitCode:0,alive:false,startedAt:d.startedAt,endedAt:d.endedAt||d.updatedAt,children:d.children||d.sources?.map(s=>({videoId:s.videoId,log:s.extractionLog||s.log,childPid:s.childPid||null}))};});
for(const [name,review] of [['acquisition-pepper-reveal.json','direct-pepper-reveal-review.json'],['discovery-pepper-reveal.json','direct-pepper-reveal-review.json'],['acquisition-pepper-drill.json','direct-pepper-drill-review.json'],['discovery-pepper-drill.json','direct-pepper-drill-review.json'],['native-review-drill-v1.json','direct-pepper-drill-review.json']]){
 const d=read(sr+'/'+name);d.historicalExtractionStatus=d.historicalExtractionStatus||d.status;d.status='closed-direct-action-review-complete-planning-only';d.directReview={path:sr+'/'+review,sha256:hash(sr+'/'+review),reviewedAt:now,finalCutCaptionApproval:false,sourceAudioUsed:false};write(sr+'/'+name,d);
}
const nextAction='Create twelve independent white2.5D/actual-footage Motion Canvas scene plans from the reviewed50-paragraph KO/EN script. Recheck current distinct before any new TTS/scene work; reuse approved Qwen/Nimbus and original cat/member assets. Measure actual narration, then acquire additional unique concept-matched official action as required to preserve explanation and meet60:40; no loops/slowing/idle, no completed media rerun.';
const q=read(base+'/queue.json'),item=q.items.find(x=>x.slug==='avoid-game-comparisons');
item.historicalExecution=[...(item.historicalExecution||[]),item.execution];
item.stage='independent-bilingual-script-reviewed-pre-TTS';item.project=project;item.updatedAt=now;item.nextAction=nextAction;item.checkpoints={...item.checkpoints,planning:true,script:true,narration:false,scenes:false,footage:false,mix:false,render:false,qa:false,collected:false};
item.execution={observedAt:now,phase:'reviewed-independent-script-and-source-plan',status:'ready-for-independent-scene-planning-and-measured-narration',pid:null,sessionId:null,alive:false,activeTasks:[],gpuSynthesisJobs:0,cpuProductionJobs:0,renderJobs:0,uploads:0,newScriptCreated:true,newNarrationCreated:false,newSceneCreated:false,completedWorkers:[...(item.execution.completedWorkers||[]),...workers],doNotWaitClosedSessions:[...new Set([...(item.execution.doNotWaitClosedSessions||[]),8173,7369,14561])],processObservation:'CIM directly found no live runner/child for53944/41680/39320/36800/9316. All finished workers have actual closed tool results; no unrelated process was stopped.'};
item.duplicateReview={...item.duplicateReview,reviewedAt:gate.reviewedAt,inputsDigest:gate.inputsDigest,currentGatePassed:true};
item.sourceActionBank={path:sr+'/source-action-bank-v2.json',sha256:hash(sr+'/source-action-bank-v2.json'),planningIntervals:80,planningUniqueSeconds:203,projectAssignedIntervals:68,projectAssignedSeconds:192.7,sourceAudioUsed:false,selfCreatedGames:0,measuredRatioApproved:false,finalCutAndCaptionApproval:false};
item.independentScript={ko:project+'/script/narration.ko.json',en:project+'/script/narration.en.json',review:project+'/production/script-source-review.json',scenes:12,paragraphs:50,wholeTextReviewed:true,overviewTextPromisesFulfilled:true,voiceAsrReviewed:false,finalPixelsReviewed:false};
item.sourceProgressGit={commit:priorGit.productionSourceProgressCommit,pushExitCode:priorGit.pushExitCode,localSha:priorGit.localSha,remoteSha:priorGit.remoteSha,verifiedAt:priorGit.verifiedAt,evidence:proof+'/source-bank-git-verification.json',normalPush:true,newRasterCommitted:0,scope:'Earlier native source review; current script/source expansion not yet delivered.'};
write(base+'/queue.json',q);
const old=read(proof+'/latest-checkpoint.json');old.historicalExecution=[...(old.historicalExecution||[]),old.execution];
Object.assign(old,{stage:item.stage,updatedAt:now,execution:item.execution,nextAction,newScriptCreated:true,ttsStarted:false,scenesCreated:false,sourceActionBank:item.sourceActionBank,independentScript:item.independentScript,currentPreflight:{path:base+'/preflight/avoid-game-comparisons.json',inputsDigest:gate.inputsDigest,reviewedAt:gate.reviewedAt,currentGatePassedAtScriptCreation:true},sourceProgressGit:item.sourceProgressGit,editorialProject:project});
old.progress={...old.progress,productionGitDelivered:10,privateAvailableSettingsVerified:10,thumbnailFollowups:0,confirmedDuplicates:1,currentVideoInProgress:1,queued:12,remainingNonduplicateProduction:13};
old.additionalSourceDecisions={Reveal:'Same actual-action edit as already reviewed z4 source;0new actual seconds, no native rerun.',DRILL:'9unique conservative intervals18seconds added. All6discovery/10native sheets read; actual29boundary candidates yield80deduplicated boundary tiles.',PestControl:'Historical HTTP403 held; no retry/bypass.',newGitImages:0};
write(proof+'/latest-checkpoint.json',old);
fs.mkdirSync(path.join(root,project+'/production'),{recursive:true});write(project+'/production/latest-checkpoint.json',old);
fs.writeFileSync(path.join(root,project+'/README.md'),'# 게임 기획 설명법: 작품명 대신 목표·행동·조건을 전달하기\n\n현재12장50문단의 독립KO/EN대본을 전체 직접 대조했고 도입의 질문·사례 순서·얻는 점·첫 사례 연결이 본문과 결론에 있음을 확인했다. planning/outline.md, chapter-plan.json, production/script-source-review.json부터 이어간다.\n\n공식 자료의 전체은행80후보203초 중68후보192.7초를 장별로 배정했다. Reveal의 중복 실제행동은0초로 제외하고 DRILL의9새후보18초를 추가했다. 이는 최종 편집/고정자막/실측60:40 승인이 아니다. TTS·MC·믹스·렌더·QA·수집·비공개 업로드는 아직 없다. 실측 후 관련 고유 행동이 부족하면 더 확보하고 좋은 설명을 줄이지 않는다.\n\n승인Qwen/Nimbus·원본고양이2초/원본회원10초와 아래가운데 자막을 유지한다. source오디오·자체게임0개다. 다운로드·원문·추출이미지·contact sheet·반복QA는 local-only이며 새Git이미지0개다. 완료10편을 다시 만들지 않는다.\n');
fs.appendFileSync(path.join(root,project+'/sources/SOURCES.md'),'\n## 최신 고유 행동 검토\n\nsource-action-bank-v2.json은80계획후보203초이며 현재 action-map.json에는68후보192.7초가 배정되어 있다. Pepper Reveal(dkxNejWRGsA)은 기존z4영상과 같은 실제행동/편집 순서로 새시간0초다. DRILLfomercial(o3Fomp9HdHs)의9고유후보18초는12장 본문에 분산했다. direct-pepper-reveal-review.json/direct-pepper-drill-review.json과 최소 official-source-observations.json을 우선한다. 정상UI의 날짜와 다운로드메타데이터 날짜는 각각 보존하며 과거데모를 현재출시사실로 바꾸지 않는다.\n');
const readme=path.join(root,base+'/README.md'),lines=fs.readFileSync(readme,'utf8').split(/\r?\n/);
lines[2]=now+' 현재: 제작·QA·4파일 수집·비공개 저장/Git 전달10편과 가능한 전체 비공개 게시설정10편, 중복제외1편을 보존한다. avoid-game-comparisons는 독립한영 전체대본 직접검토1편 진행,12queued이며 남은 비중복 제작13편이다. 썸네일후속0편이고 사람청취·발음·공개권리·Nimbus·잘린회원핸들·백업·자동더빙·비공개댓글 pending은 보존한다.';
lines[6]='avoid-game-comparisons는 현재30기존프로젝트/8전체대본/실제Studio 내용·영어메타데이터 비교의 distinct를 갱신한 뒤 독립12장50문단KO/EN대본과 전체안내 도입의 약속을 직접 대조했다. 공식6소스 은행에 Reveal/DRILL을 추가 취득·전체decode0오류로 확인했다. Reveal은 기존z4실제행동과 중복으로 새시간0초이며 DRILL의81탐색/58native동작/29경계후보80타일·16연락판을 모두 읽고9고유후보18초를 추가했다. 최신은행80후보203초/프로젝트배정68후보192.7초이며 최종컷/고정자막/실측60:40 승인은 아니다. source-action-bank-v2.json, script-source-review.json과latest-checkpoint.json을 우선한다. TTS/MC/믹스/렌더/업로드0개이며 종료8173/7369/14561과 이전취득·탐색·native세션을 기다리거나 다시 실행하지 않는다. PestControl403는 보존하고 재시도하지 않는다. 모든 새 추출이미지/전체AX는local-only, 새Git이미지0개다. 아래는 역사 기록이다.';
fs.writeFileSync(readme,lines.join('\n'));
// Local-only whole browser dumps have no repository ignore exception.
const exclude=path.join(root,'.git','info','exclude');let exclusions=fs.readFileSync(exclude,'utf8');
for(const file of ['pepper-reveal-official.ax.txt','pepper-drill-official.ax.txt','pepper-behind-grind-official.ax.txt','plucky-pest-control-official.ax.txt','plucky-pest-control-search.ax.txt','plucky-rocket-ride-official.ax.txt']){const pattern='/'+sr+'/'+file;if(!exclusions.split(/\r?\n/).includes(pattern))exclusions+='\n'+pattern;}
fs.writeFileSync(exclude,exclusions.replace(/\n+$/,'')+'\n');
console.log(JSON.stringify({stage:item.stage,scriptScenes:12,wholeParagraphs:50,sourceBankCandidates:80,sourceBankSeconds:203,assignedSeconds:192.7,workersClosed:workers.length,newGitImages:0,ttsStarted:false}));
