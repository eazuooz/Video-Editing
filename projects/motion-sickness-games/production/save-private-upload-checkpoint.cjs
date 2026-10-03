const fs = require('node:fs');
const root = 'projects/motion-sickness-games';
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const write = (p, x) => fs.writeFileSync(p, JSON.stringify(x, null, 2) + '\n');
const now = new Date().toISOString();
const receipt = read(`${root}/publishing/youtube-upload.json`);
const qa = read(`${root}/production/final-v1/qa.json`);
if (!qa.technicalApproval || !receipt.videoId) throw Error('Actual QA and observed upload ID required');
const queuePath = 'production/batches/sakurai-planning-game-design/queue.json';
const queue = read(queuePath);
const item = queue.items.find(x => x.slug === 'motion-sickness-games');
const sessions = item.execution.measuredProductionSessions;
for (const x of sessions) {
  x.alive = false;
  x.status = 'finished-exit0';
  x.exitCode = 0;
  if (x.directReview) x.directReview = 'approved-see-final-v1-qa';
}
for (const x of [
  {kind:'final-mixed04-two-paragraph-context',sessionId:9579,pid:9368,report:`${root}/production/final-v1/mixed-input-context/asr.json`},
  {kind:'final-mixed04-unprompted-beam5-context',sessionId:28637,pid:null,report:`${root}/production/final-v1/mixed-input-beam-context/asr.json`}
]) {
  if (!sessions.some(s => s.sessionId === x.sessionId)) sessions.push({...x,alive:false,status:'finished-exit0',exitCode:0,doNotRestart:true});
}
write(`${root}/production/current-production-sessions.json`, sessions);
item.nextAction = 'Continue the existing vFhhQXgdeMs captioned upload; save private/no schedule, verify all settings and CCoff game/PPT captions, then per-video selected commit and normal push. Never duplicate upload or rerun completed production.';
item.updatedAt = now;
item.execution.updatedAt = now;
item.execution.nextAction = item.nextAction;
item.execution.sceneCode.measuredTimingInstalled = true;
item.execution.sceneCode.visualApproval = true;
item.execution.sourceResearch.finalCutApproval = true;
item.execution.sourceFitFollowup.finalTimingApproved = true;
item.execution.publishingDraft.finalChapters = true;
item.execution.publishingDraft.draft = `${root}/publishing/metadata-final.json`;
item.execution.historicalRepair2 = {runner:item.execution.runner,state:item.execution.state,logs:item.execution.logs,finished:true,doNotRestart:true};
item.execution.phase = 'captioned-private-Studio-upload';
item.execution.runner = null;
item.execution.state = `${root}/publishing/youtube-upload.json`;
item.execution.log = null;
item.execution.logs = {};
item.execution.device = 'Studio UI through cua_repl';
item.execution.startedAt = item.privateUpload.newUploadStartedAt;
item.execution.studioTabId = '18';
item.execution.toolSessionId = null;
item.privateUpload.videoId = receipt.videoId;
const checkpointPath = `${root}/production/checkpoint-${now.replace(/[-:.]/g,'')}.json`;
const checkpoint = {at:now,slug:item.slug,status:item.stage,videoId:receipt.videoId,upload:receipt.upload,qa:`${root}/production/final-v1/qa.json`,voice:`${root}/production/final-v1/full-mix-asr-review.json`,measuredPlan:item.measuredPlan,completedComputeSessions:sessions,privateDeliveryComplete:false,gitDeliveryComplete:false,nextAction:item.nextAction,pendingPublicReview:receipt.pendingPublicReview,otherUserProcessesStopped:false};
write(checkpointPath, checkpoint);
write(`${root}/production/latest-checkpoint.json`,checkpoint);
item.execution.latestCheckpoint = checkpointPath;
queue.lastProgressAt = now;
queue.updatedAt = now;
write(queuePath,queue);
fs.appendFileSync('production/batches/sakurai-planning-game-design/README.md',`\n\n## ${now} 실제 최종 QA·업로드 체크포인트\n\nmotion-sickness-games final-v1은633.083333초/37985프레임, 실제 기존 게임34컷372.65초/설명248.433333초로 본편60:40오차0프레임이다. 별도v2의53개 원문/PCM과 여섯 설명 시간을 보존하고 전체12장60문단 및 최종믹스 ASR을 직접 대조했다.04의 입력/인력 ASR 혼동은 독립 무프롬프트beam5 문맥에서 정확한 입력을 확인해 원래 보고서와 추가 근거를 함께 남겼다.174자막·컷 화면/20구성화면/102실제인코딩경계, 두 전체디코딩과 동일AAC, -16.12LUFS/-2.14dBTP를 검수했다.4개 output파일 수집과 한영 실측 챕터 준비는 완료됐다.\n\n새 고정한글MP4의 실제Studio ID는 ${receipt.videoId}이며 동일 업로드를 이어간다. 비공개 업로드 진행 중으로 전체 설정·검사·CCoff 실제게임/PPT 화면·Git 전달은 아직 완료가 아니다. 종료된 합성/복구/ASR/렌더를 다시 실행하지 않는다. 현재 근거는 ${checkpointPath}, receipt와queue다. 사람청취/공개권리/원래Nimbus/잘린회원핸들/외부백업은pending이며 기존7편과 다른 사용자 작업을 보존한다.\n`);
console.log(checkpointPath);
