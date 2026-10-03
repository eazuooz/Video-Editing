// Save current observations without rewriting the previous08:20 history or frozen inputs.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),{spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'../../..'),base='projects/motion-sickness-games/production/';
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const write=(p,o)=>fs.writeFileSync(path.join(root,p),JSON.stringify(o,null,2)+'\n');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(path.join(root,p))).digest('hex');
const at=new Date().toISOString(),request=read(base+'repair1/request.json');
for(const input of request.inputs)if(sha(input.path)!==input.sha256)throw Error('Frozen input changed: '+input.path);
const repair=read(base+'repair-phrases1.json');
const pids=[47052,58552,...repair.children.map(c=>c.pid)];
const p=spawnSync('powershell',['-NoProfile','-Command',`Get-CimInstance Win32_Process | Where-Object { $_.ProcessId -in @(${pids.join(',')}) } | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Compress`],{encoding:'utf8',windowsHide:true});
if(p.status!==0)throw Error(p.stderr);
const raw=p.stdout.trim()?JSON.parse(p.stdout):[],processes=Array.isArray(raw)?raw:[raw],alive=pid=>processes.some(p=>p.ProcessId===pid);
if(repair.status==='failed')throw Error('Review actual failure before recording a healthy checkpoint.');
const chunks='shared/output/narration/motion-sickness-games/qwen3-1.7b-balanced-v1-phrase-repair1/chunks';
const candidates=fs.existsSync(path.join(root,chunks))?fs.readdirSync(path.join(root,chunks)).filter(n=>n.endsWith('-scene.wav')).map(n=>({file:chunks+'/'+n,sha256:sha(chunks+'/'+n),contentApproval:false})):[];
const session={recordedAt:at,toolSessionId:8552,pid:47052,runnerAlive:alive(47052),statusAtObservation:repair.status,state:base+'repair-phrases1.json',runner:base+'repair-phrases1.cjs',currentChildren:repair.children,inputsLocked:true,doNotDuplicate:true,automaticallyApproved:false,humanListening:'pending'};
write(base+'repair1/runner-session.json',session);
const checkpointPath=base+'checkpoint-20261003-0920.json';
const checkpoint={recordedAt:at,slug:'motion-sickness-games',previousCheckpoint:base+'checkpoint-20261003-0820.json',
  targetedRepair:{...session,candidateParagraphs:7,observedCandidates:candidates,candidateReview:'pending-single-runner-CPU-ASR',initialPipelineFinished:true,initialPipelineDoNotRestart:true},
  sourceFit:{audit:base+'source-fit-followup/initial-audit.json',directVisualReview:base+'source-fit-followup/direct-review.json',reviewedImageEntries:129,finalTimingApproved:false,
    findings:'Original bank totals do not prove paragraph fit. Allocate unused normal-speed PWS actions, reallocate05/07 overlapping post footage, and correct Talos title/snow boundaries. Do not modify frozen inputs while the runner is active.'},
  composer:{path:base+'compose-repaired-v2.py',sha256:sha(base+'compose-repaired-v2.py'),status:'syntax-checked-not-run',preflight:'Checks all candidate/source hashes, PCM bounds and explanation duration before writing any v2 file.',gate:'Seven current-hash readbacks accepted first; then separate v2 PCM proof and full12-scene current-hash ASR direct review.'},
  auxiliaryResearch:{sourceResearchSession:43025,linearEdgeSession:90652,status:'finished-exit0',talosExtraProbe:'finished-exit0-no-stderr',fastSeekWarningsRecoveredThroughLinearDecode:2},
  vite:{port:9214,pid:58552,toolSessionId:40370,alive:alive(58552),reuseWhenAlive:true},observedProcesses:processes,
  measuredSourceCutsApproved:false,bodyRatioApproved:false,finalMix:false,finalRender:false,collected:false,privateUploaded:false,gitDelivered:false,humanListening:'pending',
  nextAction:'Reuse repair8552/PID47052 and its current child. When its CPU-ASR finishes, directly review all seven paragraphs and ending/tail evidence. Do not approve best-of-three or endingHeuristic alone. Compose only accepted candidates while preserving unaffected v1 PCM/explanation length, then directly review full current-hash12-scene ASR. Use source-fit-followup/direct-review.json to select exact normal-speed, non-repeated action intervals; Talos title42.1+ and snow52.2+ cannot extend this action example.'};
write(checkpointPath,checkpoint);
const qpath='production/batches/sakurai-planning-game-design/queue.json';
const q=read(qpath),item=q.items.find(i=>i.slug==='motion-sickness-games');
if(item.status!=='in-progress')throw Error('Queue item changed; do not overwrite.');
Object.assign(item.execution,{sessionId:8552,toolSessionId:8552,pid:47052,workerPid:repair.children.find(c=>c.status==='running')?.pid??null,
  status:repair.status,phase:'targeted-repair-candidates-running-source-fit-research-complete',updatedAt:at,children:repair.children,
  repair1:{...item.execution.repair1,...repair,toolSessionId:8552,alive:alive(47052),runner:base+'repair-phrases1.cjs',state:base+'repair-phrases1.json'},
  latestCheckpoint:checkpointPath,actualSessionObservedAt:at,sourceFitFollowup:checkpoint.sourceFit,activeTasks:repair.children.filter(c=>c.status==='running'),vite:checkpoint.vite});
item.updatedAt=at;item.nextAction=checkpoint.nextAction;q.updatedAt=at;write(qpath,q);
const localSection=`\n## 2026-10-03 09:20KST 관찰 및 소스 연결 검토\n\n최신 관찰은 production/checkpoint-20261003-0920.json과 queue.execution을 따른다. 같은 표적복구8552/PID47052가00:08:35Z에 GPU 여유3회 관찰을 통과하고 후보 합성 PID42240을 시작했다. 기록 시점의 실제 상태는 ${repair.status}이며 일곱 문단의 단일 CPU-ASR/직접 내용 승인/접합은 아직 완료로 기록하지 않는다. 생성된 후보 파일 수${candidates.length}개는 음성 승인 수가 아니다. 잠긴 대본/manifest/action-map/gate 해시는 그대로다. 다른 사용자 작업을 중단하지 않았으며 살아 있는 runner/자식을 중복 시작하지 않는다.\n\n초기 음성 실측과 출처 은행을 문단별로 대조해 일부 연결 구간이 부족한 것을 찾았다. 추가129개 연구 화면을 직접 확인하고 production/source-fit-followup/direct-review.json에 정상 속도 실제 동작과 사용 제한을 기록했다. PWS90.5–98.9의 조준 이동·169–187의 회전 놀이기구 청소·339–367의 위치 이동/기둥 청소·미사용 상부 판자/후반 구조물 꼬리 구간을 현재 복구 음성에 맞춰 배분한다. 05에서359–367을 늘리면07과 겹치지 않게 다시 배분한다. 메뉴/무관한 대기와 공룡 표면을 판자/기둥 문장 아래 넣는 방법은 거부한다. 전체 은행394.4초와 이 연구를 최종60:40·모든 큐/컷 승인으로 쓰지 않는다.\n\nTalos42.1초에는 제목이,52.2초에는 눈 덮인 다리 장면이 보인다. 기존42.2/52.2 경계를 그대로 실행하지 않는다. 47.5–52와40.2–42의 실제 벽/레이저 기울기,16–20.7333/23.0333–30.1667의 독립 퍼즐 동작,31.0333–35.8667/36–39.8333의 발판/상부 장치 동작을 새 음성 경계와 다시 맞춘다. 새25 경계 화면까지 직접 읽었으며 빠른 탐색의 mmco 경고2건은 원본 선형 디코딩·네이티브 프레임 선택으로 재확인했다. 정확한 모든 컷/자막 경계는 여전히 미완료다.\n\ncompose-repaired-v2.py는 모든 입력/후보 해시·PCM 구간·설명 길이를 쓰기 전에 확인하도록 보완하고 구문검사만 통과했다. 짧은 후보가 설명 시간을 줄이면 파일을 만들기 전에 실패한다. 일곱 후보 직접 승인 뒤에만 실행하고 v1 보존 PCM과 별도v2 전체12장 ASR/접합부/끝소리를 직접 검수한다. 최종 믹스·렌더·수집·비공개 전달·Git은 미완료이고 사람 청취는pending이다.\n`;
fs.appendFileSync(path.join(root,'projects/motion-sickness-games/README.md'),localSection);
fs.appendFileSync(path.join(root,'production/batches/sakurai-planning-game-design/README.md'),`\n## 2026-10-03 09:20KST 최신 소스·음성 체크포인트\n\nmotion-sickness-games의 같은 표적복구8552/PID47052가 GPU 여유 관찰 뒤 후보합성42240을 시작했다. 실제 ${repair.status}·현재파일${candidates.length}개는 내용/접합 승인이 아니다. 최신 근거는 projects/motion-sickness-games/production/checkpoint-20261003-0920.json이다. 추가129 소스 연구 화면으로 문단별 부족 구간·미사용 실제 행동·05/07 중복 방지·Talos 제목42.1초와 눈 장면52.2초의 제외를 기록했다. 잠긴 입력은 바꾸지 않았다. 원래 은행394.4초를 최종60:40으로 계산하지 않으며 새 음성 전체ASR와 정확한 모든 자막/컷 검수 후에만 렌더한다. 최종수집/비공개전달/Git은 미완료이며7편전달·1편중복제외·motion1진행·15queued를 유지한다. 이전08:20절의GPU 대기는 당시 기록이다. 다른 사용자 변경/학습과 완료본을 보존한다.\n`);
console.log(JSON.stringify({checkpoint:checkpointPath,status:repair.status,candidates:candidates.length,runnerAlive:alive(47052),child:repair.children,reviewedResearchImages:129,finalRender:false,uploaded:false}));
