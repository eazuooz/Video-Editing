const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../../../..');
const base='production/batches/sakurai-planning-game-design',proof=base+'/proof-avoid-game-comparisons',sr=proof+'/source-research';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const save=(p,d)=>fs.writeFileSync(path.join(root,p),JSON.stringify(d,null,2)+'\n');
const now=new Date().toISOString();
const bank=read(sr+'/source-action-bank-v1.json'),review=read(sr+'/direct-native-review-v1.json');
const gate=read(base+'/preflight/avoid-game-comparisons.json');
if(gate.verdict!=='distinct'||bank.clips.length!==71||review.totals.sheets!==67)throw Error('Unexpected reviewed checkpoint');
const workers=[
 {kind:'optional-Pest-Control-acquisition',sessionId:61561,pid:45456,state:sr+'/acquisition-pest-control.json',exitCode:1,status:'closed-held-HTTP403-no-retry'},
 {kind:'four-source-CPU-native-extraction',sessionId:34450,pid:58536,state:sr+'/native-review-v1.json',exitCode:0,status:'closed-all49sheets-read'},
 {kind:'official-Rocket-Ride-acquisition-decode',sessionId:83654,pid:55988,state:sr+'/acquisition-rocket-ride.json',exitCode:0,status:'closed-decode0-errors'},
 {kind:'Rocket-Ride-CPU-discovery',sessionId:50552,pid:3864,state:sr+'/discovery-rocket-ride.json',exitCode:0,status:'closed-all13sheets204frames-read'},
 {kind:'Rocket-Ride-CPU-native-extraction',sessionId:29671,pid:59520,state:sr+'/native-review-rocket-v1.json',exitCode:0,status:'closed-all18sheets-read'},
].map(w=>({...w,startedAt:read(w.state).startedAt,endedAt:read(w.state).endedAt||read(w.state).updatedAt,children:read(w.state).children||read(w.state).sources?.map(s=>({videoId:s.videoId,status:s.status,log:s.log,childPid:s.childPid}))||[]}));
const execution={observedAt:now,phase:'source-action-bank-and-independent-plan',status:'source-bank-selected-planning-pending',pid:null,sessionId:null,alive:false,activeTasks:[],gpuSynthesisJobs:0,cpuProductionJobs:0,renderJobs:0,uploads:0,newNarrationCreated:false,newSceneCreated:false,completedWorkers:workers,doNotWaitClosedSessions:[60174,33630,78586,61561,34450,83654,50552,29671],processObservation:'CIM query found no live node/python/ffmpeg command belonging to proof-avoid-game-comparisons. Other users processes were not changed.'};
const nextAction='Review selected source endpoints and concrete claim/action connections; then create the independent KO/EN whole-video overview/body plan after a fresh distinct --check. Measure narration before final60:40; obtain more relevant official action if needed. Do not re-download or wait on closed workers.';
const q=read(base+'/queue.json'),item=q.items.find(i=>i.slug==='avoid-game-comparisons');
item.historicalExecution=[...(item.historicalExecution||[]),item.execution];
item.execution=execution;item.stage='source-action-bank-and-independent-plan';item.updatedAt=now;item.nextAction=nextAction;
item.sourceActionBank={path:sr+'/source-action-bank-v1.json',sha256:sha(sr+'/source-action-bank-v1.json'),candidateIntervals:71,candidateSeconds:185,finalCutApproval:false,bodyRatioApproved:false};
item.sourceNativeReview={path:sr+'/direct-native-review-v1.json',sha256:sha(sr+'/direct-native-review-v1.json'),...review.totals};
item.duplicateReview.currentGatePassed=true;item.duplicateReview.inputsDigest=gate.inputsDigest;item.duplicateReview.reviewedAt=gate.reviewedAt;
item.checkpoints.script=false;item.checkpoints.narration=false;item.checkpoints.scenes=false;item.checkpoints.footage=false;
q.updatedAt=now;save(base+'/queue.json',q);
const checkpoint=read(proof+'/latest-checkpoint.json');
checkpoint.historicalExecution=[...(checkpoint.historicalExecution||[]),checkpoint.execution];
Object.assign(checkpoint,{updatedAt:now,stage:item.stage,execution,nextAction,sourceActionBank:item.sourceActionBank,sourceNativeReview:item.sourceNativeReview,newScriptCreated:false,ttsStarted:false,scenesCreated:false});
checkpoint.sourceAcquisition.additionalRocket={path:sr+'/acquisition-rocket-ride.json',sha256:sha(sr+'/acquisition-rocket-ride.json'),videoId:'h27ZF-hKKYM',bytes:94913064,sourceSha256:'d203f52c8686dc26d1231c6ca8b4aba62a63e5cab2ee34131e35c783e4162843',nativeFps:60,seconds:203.45,frames:12207,fullDecodeExitCode:0,decodeDiagnostics:0,alive:false};
checkpoint.sourceAcquisition.optionalPestFailure={videoId:'fMc0RUJQLqo',state:sr+'/acquisition-pest-control.json',reason:'HTTP403 at26.2%; partial files/log retained locally. Different verified official source acquired; no cookie/account bypass or repeated request.',alive:false};
checkpoint.duplicateDecision='distinct';checkpoint.currentPreflight={reviewedAt:gate.reviewedAt,inputsDigest:gate.inputsDigest,currentGatePassed:true,concurrentMetadataReview:'Entire current2D receipt and3D manifest directly reread; related full scripts unchanged.'};
save(proof+'/latest-checkpoint.json',checkpoint);
const uiFiles=['plucky-pest-control-search.ax.txt','plucky-pest-control-official.ax.txt','pepper-behind-grind-official.ax.txt','plucky-rocket-ride-official.ax.txt'];
save(sr+'/official-source-observations.json',{schemaVersion:1,observedAt:now,method:'Actual normal browser UI title, verified owner and descriptions directly read through CUA; full AX observations remain local-only to avoid copying unrelated page/comment inventories.',observations:[{videoId:'fMc0RUJQLqo',title:'The Plucky Squire | Sneak Peek | Pest Control',duration:'3:49',owner:'DevolverDigital',verified:true,uiDate:'2024-09-06',status:'held-download-HTTP403'},{videoId:'h27ZF-hKKYM',title:'The Plucky Squire | Sneak Peek: Rocket Ride Gameplay | Wishlist Now!',duration:'3:23',owner:'DevolverDigital',verified:true,channelId:'UCSc6s-ZJXKlSQr51dsox34g',uiDate:'2024-07-18',downloadMetadataDate:'20240717',dateDifference:'Preserve both observed values; no release/version equivalence inferred.',status:'acquired-decoded-directly-inspected'},{videoId:'KWDk-csu460',title:'Pepper Grinder | Behind the Grind',duration:'1:07',owner:'DevolverDigital',verified:true,status:'held-not-downloaded',reason:'Short promotional piece rather than a longer uninterrupted action source.'}],localObservationFiles:uiFiles.map(n=>({path:sr+'/'+n,sha256:sha(sr+'/'+n),gitDelivery:false})),noNewPermissionSubmitted:true,noMessageSent:true,pestRequestTimestampCaution:'request-pest-control.json nominal createdAt was written ahead of runner time; actual started/ended times in acquisition-pest-control.json are authoritative. The immutable failed request/hash is preserved.',sourceAudioUsed:false});
const readmePath=path.join(root,base,'README.md');
let text=fs.readFileSync(readmePath,'utf8');
text=text.replace(/^avoid-game-comparisons는 현재 distinct 검토.*$/m,'avoid-game-comparisons는 공식 기존5소스에 새 Rocket Ride(h27ZF-hKKYM)203.45초1080p60를 추가 취득·전체decode오류0로 확인했다.435기존 탐색/204새 탐색 및546native행동/144경계삼중화면(432타일), 총110연락판을 직접 읽었다. 중복 장면·실물광고·옵션저속·도움설정·대화·디졸브를 제외한71계획후보185초를 source-action-bank-v1.json에 기록했다. 최종 컷/자막구성/실측60:40 승인은 아직 아니다. 새 프로젝트/대본/TTS/씬은 없으며 현재30프로젝트 distinct를 재검증했다. 최신 direct-native-review-v1.json과 latest-checkpoint.json부터 독립 도입/본문 계획을 이어간다. 선택형 Pest Control403는 로컬 실패증거를 보존하고 재시도하지 않는다. 종료 취득/탐색/native세션61561/34450/83654/50552/29671을 기다리거나 다시 실행하지 않는다. 모든 새 추출 이미지와 전체watch AX는 local-only이며 새Git이미지0개다. 아래 기록은 이전 체크포인트의 역사로 보존한다.');
fs.writeFileSync(readmePath,text);
console.log(JSON.stringify({stage:item.stage,candidateIntervals:71,candidateSeconds:185,liveProductionJobs:0,newImagesForGit:0}));
