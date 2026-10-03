const fs = require('node:fs');
const cp = require('node:child_process');
const root = 'projects/motion-sickness-games';
const git = args => cp.execFileSync('git',args,{encoding:'utf8',windowsHide:true}).trim();
const sha = process.argv[2];
if (!/^[0-9a-f]{40}$/.test(sha||'')) throw Error('Provide actual production SHA');
const head = git(['rev-parse','HEAD']);
const remote = git(['ls-remote','origin','refs/heads/main']).split(/\s+/)[0];
if(head!==sha || remote!==sha) throw Error('Actual production push must match HEAD and remote/main first');
const read = p=>JSON.parse(fs.readFileSync(p,'utf8'));
const write = (p,v)=>fs.writeFileSync(p,JSON.stringify(v,null,2)+'\n');
const receipt = read(`${root}/publishing/youtube-upload.json`);
if(receipt.status!=='uploaded-private-settings-verified') throw Error('Private delivery incomplete');
const now = new Date().toISOString();
const record = {
  productionCommit:sha,branch:'main',remote:'origin',pushStatus:'verified',pushExitCode:0,
  remoteMainShaAtVerification:remote,headMatchedRemote:true,verifiedAt:now,mediaCommitted:false,
  checks:['node scripts/build-rebuild-manifests.cjs motion-sickness-games','node scripts/media-policy.cjs','node scripts/build-rebuild-manifests.cjs --check','git diff --cached --check'],
  checkResults:'passed-before-production-commit; npm absent, exact Node hook targets used',
  selectedWork:'Approved motion video scripts/scenes, sources, rebuild, compact QA contact pages and actual Studio evidence only. Other user library/blank-project changes preserved.',
  note:'This file records the already verified production push. A later evidence commit contains this record; its own SHA is verified separately in the terminal and automation checkpoint.'
};
write(`${root}/production/final-v1/git-delivery.json`,record);
const queuePath = 'production/batches/sakurai-planning-game-design/queue.json';
const queue = read(queuePath);
const item = queue.items.find(x=>x.slug==='motion-sickness-games');
item.status = 'uploaded-private-awaiting-user-review';
item.stage = 'render-qa-collected-private-settings-verified-and-pushed';
item.gitDelivery = {...record,status:'committed-and-pushed'};
item.nextAction = 'Private review and public publication belong to the user; keep pending listening/rights/comment states. Continue hierarchical-game-outlines content and actual current Studio duplicate review. Do not recreate completed work.';
item.execution.status = 'finished-private-and-git-delivery';
item.execution.phase = 'complete';
item.execution.alive = false;
item.execution.nextAction = item.nextAction;
item.updatedAt = now;
queue.updatedAt = now;
queue.lastProgressAt = now;
queue.currentSlug = 'hierarchical-game-outlines';
const old = read(`${root}/production/latest-checkpoint.json`);
const checkpoint = {...old,at:now,status:'private-and-git-delivery-complete',privateDeliveryComplete:true,gitDeliveryComplete:true,gitDelivery:record,nextAction:item.nextAction};
const checkpointPath = `${root}/production/checkpoint-${now.replace(/[-:.]/g,'')}.json`;
write(checkpointPath,checkpoint);
write(`${root}/production/latest-checkpoint.json`,checkpoint);
item.execution.latestCheckpoint = checkpointPath;
write(queuePath,queue);
fs.appendFileSync('production/batches/sakurai-planning-game-design/README.md',`\n\n## ${now} motion-sickness-games Git 전달 완료\n\n제작 커밋 ${sha}를 origin/main에 일반 푸시하고 실제HEAD/원격main 일치를 확인했다. media/rebuild/선택diff검사를 통과했고 영상·음성·BGM·압축미디어·원본다운로드info.json은 Git에서 제외했다. 다른 사용자 라이브러리/공유파일 변경과 모든 로컬 원본/검수프레임은 보존했다. 실제633.083333초 비공개 자막판 vFhhQXgdeMs와4파일 전달을 완료했으며8편전달·1중복제외·15queued다. 다음 hierarchical-game-outlines는 전체 내용/현재Studio 중복 사전 검토부터 이어간다.\n`);
fs.appendFileSync('docs/VIDEO_ADDITIVE_REVISION.md',`\n\n## 실제 게임의 카메라 동작으로 완성한 멀미·선택 설계 영상\n\n2026-10-03 motion-sickness-games final-v1 [게임 멀미와 카메라 설계: 화면 움직임을 선택하게 만들기](https://youtu.be/vFhhQXgdeMs)를 고정 한글 MP4로 비공개 저장하고 전체 설정을 재열람했다. PowerWash Simulator의 FuturLab 개발 시연(2022 WIP)과 The Talos Principle2의 공식 실제 플레이34컷을 여섯 흰2.5D 설명 사이에 넣었으며 자체 게임은0개다.53개 원래 문단/PCM과 여섯 설명 길이를 보존했다. 전체633.083333초/37985프레임, 본편 실제372.65초/설명248.433333초로60:40 오차0프레임이다. 독립12장60문단, 한영166큐와174자막·컷 구간/20구성 화면/102인코딩 컷 경계, 전체현재해시 및 최종믹스ASR, 두 전체디코딩·동일AAC·−16.12LUFS/−2.14dBTP를 검수하고4파일을 수집했다. [현재QA](../projects/motion-sickness-games/production/final-v1/qa.json), [실제 업로드 영수증](../projects/motion-sickness-games/publishing/youtube-upload.json), [Git 증거](../projects/motion-sickness-games/production/final-v1/git-delivery.json)를 따른다.\n\n실제 업로드 CCoff 게임/PPT에서 아래 가운데 한글 자막이 보인다. 새 썸네일·KO/EN 수동SRT·영어 제목/설명·00초 과외 카드·마지막10초 재생목록/자기채널구독/외부과외링크를 저장 후 확인했다. 비공개·예약 없음, 새 파일 저작권 검사 완료/문제 없음, 저장 후 소유권 주장 없음·설정에 따라 수익 창출·초기 광고 검토 알림 해소를 관찰했다. 별도 완료 wizard 미관찰(false), 플랫폼 자동더빙 미검수와 비공개 고정댓글 pending-video-publication을 보존한다. 제작 커밋 ${sha}의 origin/main 일반 푸시 및 원격SHA 일치를 확인했고 미디어는 커밋하지 않았다. 사람 전체 청취·최종 공개 권리·원래 Nimbus·잘린 회원 핸들·외부 미디어 백업은pending이다. 원래24편은8편전달·1중복제외·15대기며 다음 hierarchical-game-outlines를 검토한다. 기존 영상의 현재 공개/예약을 변경하지 않았다.\n`);
console.log(JSON.stringify({productionCommit:sha,remote,status:item.stage,next:queue.currentSlug,checkpoint:checkpointPath}));
