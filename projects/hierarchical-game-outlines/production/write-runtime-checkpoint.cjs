const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/hierarchical-game-outlines/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
function write(p,v){
 const file=path.join(root,p),tmp=file+'.'+process.pid+'.tmp';
 fs.writeFileSync(tmp,JSON.stringify(v,null,2)+'\n');fs.renameSync(tmp,file);
}
const now=new Date().toISOString(),runner=read(base+'resource-runner.json');
for(const input of runner.inputs)if(hash(input.path)!==input.sha256)throw Error('Locked input changed: '+input.path);
const processes=spawnSync('powershell',['-NoProfile','-Command',
 "Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(11952,8864) } | Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Compress"],
 {encoding:'utf8',windowsHide:true});
if(processes.status!==0)throw Error(processes.stderr);
const parsed=processes.stdout.trim()?JSON.parse(processes.stdout):[],rows=Array.isArray(parsed)?parsed:[parsed];
const controller=rows.find(row=>row.ProcessId===runner.pid);
const vite=rows.find(row=>row.ProcessId===8864);
const alive=!!controller&&/hierarchical-game-outlines\/production\/resource-runner.cjs/.test(controller.CommandLine);
const lookdev=read(base+'lookdev-v2/inspection.json');
if(lookdev.directVisualReview!=='passed-silent-layout-only')throw Error('Silent layout review missing.');
const bank=read('projects/hierarchical-game-outlines/sources/source-action-bank.json');
const checkpoint={observedAt:now,slug:'hierarchical-game-outlines',status:runner.status,
 runner:{toolSessionId:91180,pid:runner.pid,alive,command:controller?.CommandLine||null,
  state:base+'resource-runner.json',sessionProof:base+'runner-session.json',gpuObservation:runner.gpuObservation,
  stableSamples:runner.stableSamples,children:runner.children,logs:runner.logs,inputs:runner.inputs},
 sources:{research:'production/batches/sakurai-planning-game-design/proof-hierarchical-game-outlines/source-research/candidate-review.json',
  bank:'projects/hierarchical-game-outlines/sources/source-action-bank.json',candidateCuts:bank.cuts.length,
  candidateSeconds:bank.uniqueCandidateSeconds,sourceResearchFramesDirectlyReviewed:1221,
  sourceIds:['I-ccSZ5J1Bo','5rgASbqkeTI'],finalPlanSourceIds:['I-ccSZ5J1Bo'],
  sourceFullDecodeExitCodes:[0,0],selfCreatedGames:0,final60_40Measured:false,
  originalSourceAudioExcluded:true,rawInfoAndMediaExcludedFromGit:true},
 script:{scenes:12,paragraphs:60,KOENAligned:true,sourceFirstDirectReview:true,
  gate:base+'script-source-review.json',speechApproved:false,humanListening:'pending'},
 lookdev:{status:'passed-silent-layout-only',version:'v2',inspection:base+'lookdev-v2/inspection.json',
  seconds:48,frames:2880,width:1920,height:1080,fps:60,audioStreams:0,viewsDirectlyReviewed:24,
  typeScriptExitCode:0,fullDecodeExitCode:0,
  finishedSessions:[{toolSessionId:88428,pid:55724,status:'finished',exitCode:0},
   {toolSessionId:47808,pid:29960,status:'finished',exitCode:0}],
  v1RejectionPreserved:base+'lookdev-v1/inspection.json',finalNarratedVideo:false,finalCaptionsApproved:false},
 vite:{port:9216,pid:8864,toolSessionId:67127,alive:!!vite,command:vite?.CommandLine||null,
  previousMotionVite:{port:9214,pid:58552,status:'ended-observed-before-starting-own-server'},
  action:'Reuse only when actual process/config is alive. Preserve picking9212.'},
 publishingPreparation:{thumbnail:'projects/hierarchical-game-outlines/publishing/thumbnail-recipe.json',
  thumbnailDirectReview:'passed-local-layout-only',metadata:'projects/hierarchical-game-outlines/publishing/metadata-draft.json',
  finalChaptersReady:false,uploaded:false,videoId:null,privacyTarget:'private',
  pinnedComment:'pending-video-publication'},
 finalVideo:{timingMeasured:false,allCutsAndCaptionsApproved:false,mixed:false,rendered:false,qa:false,collected:false,
  privatelyDelivered:false,gitDelivered:false},
 progress:{delivered:8,duplicateExcluded:1,inProgress:1,queued:14},
 pending:['full-current-hash ASR direct comparison','measured actual cuts and60:40','all fixed Korean captions',
  'mix and KO/EN SRT','final render/QA/collection/private full settings','per-video commit/normal push',
  'human full listening','final public rights','original Nimbus bytes','truncated member handles','external backup'],
 nextAction:'Read the single live runner. Do not start another TTS/ASR, change locked inputs or stop other training. After its12-scene CPU-ASR completes, directly compare all60 paragraphs, repair only rejected speech and preserve unaffected PCM. Then measure source-fit/cuts/captions and body60:40 while preserving six explanations; final mix/SRT/chapters/outro/render/QA/private/Git remain pending.',
};
const filename=base+'checkpoint-'+now.replace(/[-:.]/g,'')+'.json';
write(filename,checkpoint);write(base+'latest-checkpoint.json',{...checkpoint,checkpointFile:filename});
const queuePath='production/batches/sakurai-planning-game-design/queue.json',queue=read(queuePath),item=queue.items.find(x=>x.slug==='hierarchical-game-outlines');
if(!item||item.status!=='in-progress')throw Error('Preserve changed queue ownership/state.');
item.execution={...item.execution,runtimeCheckpoint:filename,latestCheckpoint:base+'latest-checkpoint.json',
 vite:checkpoint.vite,lookdev:checkpoint.lookdev,publishingPreparation:checkpoint.publishingPreparation,
 runnerAliveObservedAt:now,runnerAlive:alive};
queue.updatedAt=now;write(queuePath,queue);
const readme=path.join(root,'production/batches/sakurai-planning-game-design/README.md');
fs.appendFileSync(readme,`\n\n## ${now} hierarchical-game-outlines source-first checkpoint\n\n`+
 '8편 비공개/Git 전달과1편 중복 제외를 보존하며 현재outline1편 진행,14편queued다. 최신distinct --check 뒤 새로운Two Point Museum/Against the Storm 공식 자료를 확보해 전체디코딩과1221개 연구/경계 화면을 직접 읽었다. 시간압축/제목/실물진행자/소스음악을 제외하고 현재계획은Museum32컷392초 후보와 독립한영12장60문단이다. 이는 최종60:40/자막 승인 수치가 아니다. 도식은 우리의 문서구성 제안이며 내부개발문서나 게임규칙의 자동이동으로 주장하지 않는다.\n\n'+
 `단일runner91180/PID${runner.pid}는 ${runner.status}, 실제생존${alive}, 자식${runner.children.length}개다. 고정입력해시가 모두 일치한다. 다른학습을중단하거나 합성/ASR를중복실행하지 않는다. 원래승인목소리/Nimbus를 재사용한다. 상태/로그와 ${filename}를 우선하며 종료된소스다운로드/검수와완료본을다시실행하지 않는다.\n\n`+
 '12개MC진입점과여섯흰2.5D설명을작성했다. 무음v1의 이동화살표/글자와접기전환겹침을거부·수정한v2는48초/2880프레임/1080p60/오디오0,18구성+6전환화면과전체디코딩/TypeScript검사를통과했다. 종료된88428/PID55724와47808/PID29960을기다리지않는다. Vite9216/PID8864/67127을살아있으면재사용한다. 새썸네일과한영설명/코칭고정댓글은로컬준비일뿐이며최종음성/소스컷/자막/믹스/렌더/수집/비공개전달/Git은미완료다.\n');
console.log(JSON.stringify({checkpoint:filename,status:runner.status,runnerAlive:alive,children:runner.children.length,
 candidateCuts:bank.cuts.length,candidateSeconds:bank.uniqueCandidateSeconds,finalVideo:false}));
