const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const base = 'projects/game-reward-planning/';
const read = rel => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));
const write = (rel, value) => fs.writeFileSync(path.join(root, rel), JSON.stringify(value, null, 2) + '\n');
const now = new Date().toISOString();
const receipt = read(base + 'publishing/youtube-upload.json');
if (receipt.actualVideoId !== 'D81WnOMytG4') throw Error('Unexpected actual video ID');
const names = [
  'new-file-wizard-checks-completed.png', 'new-file-wizard-checks-completed.ax.txt',
  'private-selected-no-schedule.png', 'content-private-uploaded.png',
  'details-private-HD-saved.png', 'private-no-schedule-reopened.png',
  'ads-enabled-saved.png', 'copyright-no-claims-saved.png',
  'languages-saved.png', 'english-reopened.png',
  'ko-published-reopened.png', 'ko-reopened-268.ax.txt', 'en-imported-109.ax.txt',
  'card-reopened.png', 'card-canonical-URL-reopened.png',
  'outro-subscribe-reopened.ax.txt', 'outro-playlist-reopened.ax.txt',
  'outro-link-reopened.ax.txt', 'outro-saved-mid-HD60.png',
  'cc-off-selected-1080p60.png', 'cc-off-game-40s-HD-clear.png',
  'cc-off-PPT-70s-HD-full.png', 'cc-off-PPT-70s-HD.ax.txt'
];
const proofs = names.map(name => {
  const rel = base + 'publishing/proof/' + name;
  const data = fs.readFileSync(path.join(root, rel));
  return {path: rel, bytes: data.length, sha256: crypto.createHash('sha256').update(data).digest('hex')};
});
receipt.historicalUploadObservations ??= [];
receipt.historicalUploadObservations.push({
  status: receipt.status, uploadStartedAt: receipt.uploadStartedAt,
  progressObservedPercent: receipt.upload.progressObservedPercent,
  privateAutosaveObserved: receipt.upload.privateAutosaveObserved,
  note: 'Initial 12% file progress is historical. Final saved private content row, HD player and reopened settings supersede this pending state.'
});
receipt.status = 'saved-private-available-settings-verified-thumbnail-followup';
receipt.privateUploadSaved = true;
receipt.availableSettingsVerified = true;
receipt.fullSettingsVerified = false;
receipt.scheduled = false;
receipt.watchUrl = 'https://youtu.be/D81WnOMytG4';
receipt.verifiedAt = now;
receipt.upload.status = 'uploaded-private';
receipt.upload.singleFileUpload = true;
receipt.upload.savedPrivateVerified = true;
receipt.upload.sdComplete = true;
receipt.upload.hdComplete = true;
receipt.upload.availableSettingsVerified = true;
delete receipt.upload.progressObservedPercent;
receipt.privacyVerification = {saved: 'private', scheduled: false, reopened: true, evidence: base + 'publishing/proof/private-no-schedule-reopened.png'};
receipt.metadataVerification = {koreanTitleExact: true, koreanDescriptionExact: true, englishTitleExact: true, englishDescriptionExact: true, retainedChannelFooterAndLinks: true, measuredChapters: true, category: 'Education', videoLanguage: 'ko', madeForKids: false, paidPromotion: false, alteredRealisticContent: false, rationale: 'Official actual gameplay and original coded explanation with the approved non-impersonating synthetic narrator; no realistic fabricated person/event.', reopened: true};
receipt.englishMetadata.status = 'published-saved-reopened-exact';
receipt.subtitles.forEach(track => {track.status = 'manually-published-verified'; track.reopened = true;});
receipt.subtitles[0].evidence = base + 'publishing/proof/ko-published-reopened.png';
receipt.subtitles[1].evidence = base + 'publishing/proof/languages-saved.png';
receipt.automaticChecks = {
  status: 'completed-no-issues-observed', newFileWizardObserved: true,
  copyright: '완료 · 발견된 문제가 없습니다', adSuitability: '완료 · 발견된 문제가 없습니다',
  savedCopyrightText: ['동영상에서 소유권 주장이 발견되지 않았습니다', '동영상에서 저작권 보호 콘텐츠가 발견되지 않았습니다'],
  savedMonetizationText: '동영상에서 설정에 따라 수익을 창출하고 있습니다', ads: '사용',
  evidence: names.filter(n => /wizard-checks|ads-enabled|copyright-no-claims/.test(n)).map(n => base + 'publishing/proof/' + n)
};
receipt.explicitWizardCompletionObserved = false;
receipt.burnedCaptionVerification = {
  required: true, position: [960, 970], playerCaptionsOff: true,
  actualSettingsLabel: '사용 안함', quality: '1080p60 HD', dimensions: [1920, 1080],
  status: 'verified-uploaded-HD-pixels',
  frames: [
    {seconds: 40, role: 'actual-game', directRead: '생긴 땅을 이용해', evidence: base + 'publishing/proof/cc-off-game-40s-HD-clear.png'},
    {seconds: 70, role: 'white-2.5D-explanation', directRead: '나누면 빠진 역할이 보입니다.', evidence: base + 'publishing/proof/cc-off-PPT-70s-HD-full.png'}
  ],
  playerTrackPropagationObservation: 'The already-open player still labelled its CC button 자막 사용 불가. This does not replace the separately observed published manual KO/EN Studio tracks. No claim that optional player tracks were independently available in this cached session.'
};
receipt.coachingCard.status = 'saved-reopened-verified';
receipt.coachingCard.count = 1;
receipt.coachingCard.uiStart = '00:00:00';
receipt.coachingCard.canonicalUrlReopenedExact = true;
receipt.coachingCard.image = 'shared/assets/branding/yamyamcoding-cats-original.png';
receipt.coachingCard.historicalUnsavedState = 'Card save initially lacked a required image. Normal filechooser original-cat image, Apply and Save resolved it; no second video upload.';
receipt.endScreen.status = 'saved-three-elements-reopened-verified';
receipt.endScreen.frameRate = 60;
receipt.endScreen.uiInclusive = {start: '7:14:53', end: '7:24:52'};
receipt.endScreen.targets = {playlist: {id: 'PLUU7_j2ihric', title: 'Planning & Game Design & Tech'}, subscribe: {channelId: 'UCOgtkPoyC0VXhCs7Xk3jvjQ', title: '얌얌코딩 (게임 개발)'}, link: receipt.coachingEndingLink.url};
receipt.endScreen.allThreeTimingReopened = true;
receipt.endScreen.noMemberTitleLogoOverlapDirectlyReviewed = true;
receipt.endScreen.membershipRowsPreserved = 12;
receipt.endScreen.linkPosition = {top: 52.0187, left: 152.52, width: 71.2773, height: 71.3606, units: 'CSS pixels relative to 460px Studio player', purpose: 'Blank space between coaching text and member column; no overlap with playlist, subscribe, identities, title or original logo.'};
receipt.endScreen.originalMediaRetimed = false;
receipt.coachingEndingLink.status = 'saved-reopened-canonical-url-verified';
receipt.pinnedComment.actualPrivateRestrictionObserved = true;
receipt.pinnedComment.actualText = '비공개 동영상에서는 댓글이 지원되지 않습니다.';
receipt.automaticDubbing = {status: 'unreviewed', observed: 'Automatic English (United States)/Indonesian audio processing in Studio; no quality approval inferred.'};
receipt.thumbnail.nonblocking = true;
receipt.thumbnail.limitEvidence = 'projects/hierarchical-game-outlines/publishing/proof/thumbnail-daily-limit.png';
receipt.thumbnail.limitObservedAt = '2026-10-03T14:50:04.773Z';
receipt.thumbnail.newVideoLimitDirectlyAttempted = false;
receipt.thumbnail.savedVerified = false;
receipt.proofs = proofs;
receipt.pendingHumanReviews = ['whole listening and pronunciation', 'final public rights', 'original Nimbus identity', 'truncated member handles', 'external media backup', 'automatic dubbing'];
write(base + 'publishing/youtube-upload.json', receipt);
const rendered = read(base + 'production/final-v1/render-result.json');
rendered.historicalStatus ??= rendered.status;
rendered.status = 'technical-approved-collected-saved-private-thumbnail-followup';
rendered.collection = base + 'production/delivery-output.json';
rendered.uploadReceipt = base + 'publishing/youtube-upload.json';
rendered.actualVideoId = receipt.actualVideoId;
write(base + 'production/final-v1/render-result.json', rendered);
console.log(JSON.stringify({videoId: receipt.actualVideoId, privateSaved: true, availableSettings: true, fullSettings: false, proofs: proofs.length}));
