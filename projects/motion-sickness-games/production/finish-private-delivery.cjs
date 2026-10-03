const fs = require('node:fs');
const crypto = require('node:crypto');
const root = 'projects/motion-sickness-games';
const read = p => JSON.parse(fs.readFileSync(p, 'utf8'));
const write = (p, v) => fs.writeFileSync(p, JSON.stringify(v, null, 2) + '\n');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const now = new Date().toISOString();
const receiptPath = `${root}/publishing/youtube-upload.json`;
const receipt = read(receiptPath);
const qa = read(`${root}/production/final-v1/qa.json`);
if (receipt.videoId !== 'vFhhQXgdeMs' || !qa.technicalApproval || receipt.burnedCaptionVerification.playerCaptionsOff !== true) throw Error('Actual upload/QA/CCoff evidence required');
const proofClaims = {
  'private-saved-details.png': 'Saved video reopened: private, correct Korean metadata, chapters, thumbnail, captioned filename and HD processing complete. Historical screenshot still shows initial ad-review alert.',
  'new-file-checks-pending.png': 'New upload copyright check completed with no problems; initial automatic ad review still in progress. Preserve this earlier observation.',
  'english-metadata-manual-srt-saved.png': 'English localized title/description and manually uploaded English timed subtitle track published and reopened.',
  'languages-saved.png': 'Saved original Korean and added English language rows; manual subtitle and localized metadata publication visible.',
  'korean-manual-srt-saved.png': 'Reopened manually uploaded Korean timed subtitle editor. Explicit publish was then clicked and saved.',
  'card-saved-zero.png': 'Reopened one programming coaching card at 0:00:00 with saved title/CTA/teaser.',
  'card-saved-url.png': 'Reopened card exact canonical coaching URL.',
  'end-screen-saved-members.png': 'Reopened last-ten-second playlist/own-channel subscribe/coaching elements and member-outro preview; identities/title/logo remain visible.',
  'end-screen-saved-url.png': 'Reopened external coaching URL and HD timeline 10:23:05–10:33:04. Boundary preview is not evidence of an extra outro frame.',
  'monetization-saved-enabled.png': 'Saved monetization setting is 사용, mid-roll enabled, no pending-review notice on this page.',
  'copyright-saved-no-claims.png': 'Saved new video has no copyright claims; Studio states revenue unaffected and monetizing according to settings.',
  'private-saved-no-review-alert.png': 'Actual channel row links to vFhhQXgdeMs, private/uploaded and alert column —; earlier ad-review alert resolved. Other videos were only read.',
  'cc-off-game.png': 'Actual uploaded game pixels retain Korean bottom-center captions with CC off.',
  'cc-off-explanation.png': 'Actual uploaded explanation pixels retain Korean bottom-center captions with CC off.',
  'cc-off-explanation-setting.png': 'Actual player settings explicitly display subtitles disabled while boxed Korean caption pixels remain.',
  'cc-off-game-HD.png': 'Actual uploaded HD game at 30 seconds, CC accessibility value 0; bottom-center caption and full game frame visible.',
  'cc-off-explanation-HD.png': 'Actual uploaded HD explanation at 60 seconds with CC off; boxed Korean caption pixels visible.'
};
receipt.evidence = Object.entries(proofClaims).map(([name, claim]) => {
  const path = `${root}/publishing/proof/${name}`;
  if (!fs.existsSync(path)) throw Error(`Missing actual proof ${path}`);
  return {path, claim, sha256: sha(path)};
});
receipt.status = 'uploaded-private-settings-verified';
receipt.completedAt = now;
receipt.privateSaved = true;
receipt.scheduled = false;
receipt.settingsVerified = true;
receipt.upload.status = 'uploaded-private-HD-processed';
receipt.upload.lastObservedUploadPercent = 100;
receipt.upload.processing = 'SD-and-HD-complete-observed';
receipt.upload.lastObservedAt = now;
receipt.englishMetadata.status = 'published-saved-and-reopened';
receipt.subtitles.forEach(t => { t.status = 'published-manual-upload-saved-and-reopened'; t.verifiedAt = now; });
receipt.coachingCard.status = 'saved-and-reopened-verified';
receipt.coachingCard.count = 1;
receipt.endScreen.status = 'saved-and-reopened-verified';
receipt.endScreen.observedUiStart = '10:23:05';
receipt.endScreen.observedUiEnd = '10:33:04';
receipt.endScreen.observedUiFrameRate = 60;
receipt.endScreen.uiEndIsInclusiveFrame = true;
receipt.endScreen.playlist = {name:'Planning & Game Design & Tech', channelId:'UCOgtkPoyC0VXhCs7Xk3jvjQ', savedAndReopened:true};
receipt.endScreen.subscribeChannelId = 'UCOgtkPoyC0VXhCs7Xk3jvjQ';
receipt.endScreen.memberIdentityNotObscured = true;
receipt.coachingEndingLink.status = 'saved-and-reopened-verified';
receipt.monetization.status = 'saved-ads-enabled-and-reopened';
receipt.monetization.automaticReviewStatus = 'initial-pending-alert-resolved-after-save';
receipt.monetization.savedClaimsStatus = 'no-claims-revenue-unaffected-monetizing-according-to-settings';
receipt.monetization.automaticReviewEvidence = 'Actual channel alert —, monetization 사용, saved claims page revenue unaffected. No separate completion wizard was reopened; do not claim an explicitly observed final wizard verdict.';
receipt.monetization.verifiedAt = now;
receipt.explicitWizardCompletionObserved = false;
receipt.burnedCaptionVerification.reviewedFrames.push({seconds:30,playerCcValue:0,evidence:`${root}/publishing/proof/cc-off-game-HD.png`,qualitySelected:'1080p60'});
receipt.burnedCaptionVerification.explicitCcOffSettingEvidence = `${root}/publishing/proof/cc-off-explanation-setting.png`;
receipt.platformAutomaticDubbing = {status:'unreviewed-platform-generated',doesNotReplaceManualSrtOrHumanListening:true};
receipt.pinnedComment.status = 'pending-video-publication';
receipt.pinnedComment.platformLimitationObserved = true;
receipt.publicPublishReady = false;
write(receiptPath, receipt);
const project = read(`${root}/project.json`);
project.status = 'uploaded-private-awaiting-user-review';
Object.assign(project.publishing, {videoId:receipt.videoId,videoUrl:receipt.videoUrl,receipt:receiptPath,status:receipt.status,privacyStatus:'private',scheduledPublishAt:null});
write(`${root}/project.json`,project);
const queuePath = 'production/batches/sakurai-planning-game-design/queue.json';
const queue = read(queuePath);
const item = queue.items.find(x=>x.slug==='motion-sickness-games');
Object.assign(item,{status:'uploaded-private-awaiting-git-delivery',stage:'render-qa-collected-private-settings-verified-awaiting-push',videoId:receipt.videoId,updatedAt:now,completedAt:now});
Object.assign(item.checkpoints,{privateUploadSaved:true,publishingSettingsVerified:true,uploaded:true});
item.privateUpload = {status:receipt.status,receipt:receiptPath,videoId:receipt.videoId,variant:'captioned',privateSaved:true,scheduled:false,settingsVerified:true,completedAt:now,automaticChecks:receipt.monetization.automaticReviewStatus,explicitWizardCompletionObserved:false};
item.publishing = {...item.privateUpload,privacyStatus:'private',publicDecision:'user-only'};
item.delivery = {directory:'output/motion-sickness-games',report:`${root}/production/delivery-output.json`,durationSeconds:633.0833333333334,cuesPerLanguage:166,publicPublishReady:false};
item.gitDelivery = {status:'pending-selected-commit-and-normal-push',mediaCommitted:false};
item.nextAction = 'Run rebuild/media checks, selectively commit and normally push this completed private video, verify remote SHA, then review hierarchical-game-outlines for content/Studio duplicates. Do not rerun any completed media or upload.';
Object.assign(item.execution,{phase:'private-upload-saved-settings-verified-awaiting-git',status:'finished-private-delivery',alive:false,pid:null,workerPid:null,sessionId:null,updatedAt:now,nextAction:item.nextAction});
item.execution.thumbnail.uploaded = true;
item.execution.publishingDraft.uploaded = true;
queue.progress = {...queue.progress,rendered:8,collected:8,uploaded:8,remaining:15,inProgress:0,queued:15};
queue.updatedAt = now;
queue.lastProgressAt = now;
const old = read(`${root}/production/latest-checkpoint.json`);
const path = `${root}/production/checkpoint-${now.replace(/[-:.]/g,'')}.json`;
const checkpoint = {...old,at:now,status:'private-delivery-complete-awaiting-git',privateDeliveryComplete:true,gitDeliveryComplete:false,receipt:receiptPath,nextAction:item.nextAction};
write(path,checkpoint);
write(`${root}/production/latest-checkpoint.json`,checkpoint);
item.execution.latestCheckpoint = path;
write(queuePath,queue);
fs.appendFileSync('production/batches/sakurai-planning-game-design/README.md',`\n\n## ${now} 실제 비공개 저장·전체 설정 검수 완료\n\nmotion-sickness-games의 고정 한글 MP4를 vFhhQXgdeMs에 한 번 업로드하고 비공개/예약 없음, 새 썸네일, KO/EN 수동 자막, 영어 제목/설명, 00초 과외 카드와 마지막10초 재생목록/자기 채널 구독/외부 과외 링크를 저장 후 다시 열어 확인했다. 실제 플레이어 CCoff의 게임/PPT에서 자막 픽셀이 보이며 HD 게임30초 화면도 확인했다. 새 파일 저작권 검사는 완료/문제 없음, 저장 후 소유권 주장 없음·수익에 영향 없음·설정에 따라 수익 창출을 실제 확인했다. 초기 광고 검토 알림은 해소됐으며 별도 완료 wizard 미관찰(false)은 보존한다. 고정댓글은 비공개 제한으로 pending-video-publication이다. 실제receipt/proof가 근거이며 현재8편 비공개 전달,1중복 제외,15대기다. 이번 편의 선택 커밋/일반 푸시는 아직 대기이며 사람청취/공개권리/원래Nimbus/잘린회원핸들/외부백업도pending을 보존한다.\n`);
console.log(JSON.stringify({videoId:receipt.videoId,status:receipt.status,checkpoint:path,git:'pending'}));
