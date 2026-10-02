const fs = require('node:fs');
const path = require('node:path');
const cp = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const commit = '3f1788c6b18a1eeaa15b078cf7ad0b85b8145fd5';
const git = (...args) => cp.execFileSync('git', args, {cwd: root, encoding: 'utf8'}).trim();
const head = git('rev-parse', 'HEAD');
const remote = git('ls-remote', 'origin', 'refs/heads/main').split(/\s+/)[0];
if (head !== commit || remote !== commit) throw Error('Production push must be verified before recording completion');
const now = new Date().toISOString();
const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const write = (p, data) => fs.writeFileSync(path.join(root, p), JSON.stringify(data, null, 2) + '\n');
const delivery = {
  productionCommit: commit, branch: 'main', remote: 'origin', pushStatus: 'verified',
  pushExitCode: 0, remoteMainShaAtVerification: remote, headMatchedRemote: true,
  verifiedAt: now, mediaCommitted: false,
  checks: ['node scripts/build-rebuild-manifests.cjs picking-sides', 'node scripts/media-policy.cjs', 'node scripts/build-rebuild-manifests.cjs --check', 'git diff --cached --check'],
  checkResults: 'passed-before-production-commit',
};
const receiptPath = 'projects/picking-sides/publishing/youtube-upload.json';
const receipt = read(receiptPath);
if (receipt.videoId !== 'sXd1RrPlGos' || !receipt.privacyVerification || !receipt.burnedCaptionVerification.playerCaptionsOff) throw Error('Private captioned delivery evidence required');
receipt.status = 'private-upload-completed';
receipt.gitDelivery = delivery;
write(receiptPath, receipt);
const queuePath = 'production/batches/sakurai-planning-game-design/queue.json';
const q = read(queuePath), i = q.items.find(x => x.slug === 'picking-sides');
i.status = 'uploaded-private-awaiting-user-review';
i.stage = 'captioned-private-delivery-and-git-push-verified';
i.gitDelivery = delivery;
i.checkpoints.gitDelivery = true;
i.execution.status = 'completed-private-delivery-and-git-verified';
i.execution.renderStarted = true;
i.execution.finalRenderComplete = true;
i.execution.updatedAt = now;
i.execution.latestCheckpoint = 'projects/picking-sides/production/final-v1/git-delivery.json';
i.execution.activeTasks = [];
i.execution.pendingV2Review.currentUse = 'historical-resolved-by-v3-composite-and-final-current-hash-direct-review';
i.execution.nextAction = i.nextAction = 'Completed. Never regenerate or reupload sXd1RrPlGos. Continue motion-sickness-games preflight: compare full related scripts and current Studio matches before creating a project.';
i.updatedAt = now;
q.progress = {...q.progress, remaining: 16, rendered: 7, collected: 7, uploaded: 7, duplicateExcluded: 1, inProgress: 0, queued: 16};
q.currentSlug = 'motion-sickness-games';
q.updatedAt = q.lastProgressAt = now;
write(queuePath, q);
write('projects/picking-sides/production/final-v1/git-delivery.json', delivery);
const checklistPath = path.join(root, 'projects/picking-sides/checklist.md');
fs.writeFileSync(checklistPath, fs.readFileSync(checklistPath, 'utf8').replace('- [ ] media/rebuild', '- [x] media/rebuild').trimEnd() + '\n');
const readmePath = path.join(root, 'projects/picking-sides/README.md');
fs.writeFileSync(readmePath, fs.readFileSync(readmePath, 'utf8').replace('Git전달은 아직미완료다.', `제작 커밋 ${commit}의 origin/main 일반 푸시와 실제 로컬·원격 SHA 일치를 확인했다.`));
const batchPath = path.join(root, 'production/batches/sakurai-planning-game-design/README.md');
const checkpoint = `2026-10-03 최신 실제 체크포인트: picking-sides final-v1 614.883333초를 검수·4파일 수집하고 https://youtu.be/sXd1RrPlGos 에 고정 한글 MP4로 비공개 전달했다. 새 썸네일·수동 KO/EN 자막·영어 메타데이터·00초 과외 카드·회원 엔딩의 재생목록/구독/과외 링크·광고 사용과 새 파일 검사 문제없음을 저장 후 다시 열어 확인했다. 실제 CCoff 게임/PPT 화면에 자막 픽셀이 보인다. 본편 실제361.733333초/설명241.15초(60:40오차0.2프레임), 45개 기존 게임 컷과151한영큐/183자막·컷 화면을 검수했으며 자체 게임은0개다. 제작 커밋 ${commit}을 origin/main에 일반 푸시하고 실제 SHA 일치를 확인했다. 현재7완료·1중복제외·16queued다. 다음 motion-sickness-games는 로컬24프로젝트 후보 스캔만 완료했으며 내용/현재 Studio 사전 검토가 남았다. 아직 새 프로젝트·대본·TTS·씬을 만들지 않는다. 종료된 picking 합성/렌더/업로드는 재실행하지 않는다. 사람 청취·공개 권리·Nimbus 원본·회원 핸들·외부 백업과 비공개 댓글 pending은 보존한다.`;
fs.writeFileSync(batchPath, fs.readFileSync(batchPath, 'utf8').replace(/^(# [^\n]+\r?\n\r?\n)[^\n]+/, '$1' + checkpoint));
const docPath = path.join(root, 'docs/VIDEO_ADDITIVE_REVISION.md');
let doc = fs.readFileSync(docPath, 'utf8');
const section = `## 실제 기존 게임 자료로 완성한 관전·응원 영상\n\n2026-10-03 \`picking-sides\` final-v1 [관전과 응원 대상의 게임 디자인: 왜 남의 플레이도 재미있을까?](https://youtu.be/sXd1RrPlGos)를 비공개 저장하고 모든 설정을 재열람했다. Ultimate Chicken Horse/Gang Beasts 공식 실제 플레이45컷을 여섯 설명 사이에 넣고 원래29개 설명 문단과PCM을 보존했다. 자체 Cloudpost 게임은 최종 영상에서 제외했다. 전체614.883333초, 본편 실제361.733333초/설명241.15초(60:40오차0.2프레임), 독립12장72문단, 한영151큐와183자막·컷 구간을 검수하고4파일을 수집했다. [현재 QA](../projects/picking-sides/production/final-v1/qa.json)와 [실제 비공개 업로드 증거](../projects/picking-sides/publishing/youtube-upload.json)를 따른다.\n\n아래 가운데 고정 한글 MP4를 올렸으며 실제 CCoff 게임/PPT 화면에서 자막을 확인했다. 새 썸네일·한영 수동 SRT·영어 제목/설명·00초 과외 카드·마지막10초 재생목록/구독/외부 과외 링크·광고 사용·새 파일 검사 문제없음을 저장 후 확인했다. 공개·예약은 없다. 제작 커밋 \`${commit}\`의 origin/main 일반 푸시와 원격 SHA 일치를 확인했다. 사람 청취·최종 공개 권리·원래 Nimbus·잘린 회원 핸들·외부 백업 및 비공개 댓글은 pending이다. 원래24개 대상은7편 전달·1편 중복 제외·16편 대기이며 다음 motion-sickness-games의 사전 내용/Studio 검토부터 이어간다.\n\n`;
if (!doc.includes('## 실제 기존 게임 자료로 완성한 관전·응원 영상')) doc = doc.replace('## 항상 적용할 제작 규칙', section + '## 항상 적용할 제작 규칙');
fs.writeFileSync(docPath, doc);
console.log(JSON.stringify({videoId: receipt.videoId, productionCommit: commit, remoteSha: remote, remaining: 16}));
