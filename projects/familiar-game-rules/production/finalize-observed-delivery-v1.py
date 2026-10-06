"""Save the already observed current delivery and its final distinct-content review."""
from final_cpu_common import ROOT, FINAL, read, write, now, sha
import subprocess

pub = ROOT / 'projects/familiar-game-rules/publishing'
proof = pub / 'proof'
assert '소유권 주장이 발견되지 않았습니다' in (proof / 'claims-none-saved-v1.ax.txt').read_text(encoding='utf-8')
observation = dict(
    schemaVersion=1, observedAt=now(), videoId='NLEHMC0XMtg',
    privateSaved=True, uploadComplete=True, transferPercent=100,
    sdProcessingComplete=True, hdProcessingComplete=True, noSchedule=True,
    burnedGameWithCcOff=True, burnedWhiteWithCcOff=True,
    gameFrameSeconds=38.392273, whiteFrameSeconds=77.474133,
    playerQuality='720p60 (actual 1280x720)', playerReadyState=4,
    playerCaptions='사용 안함', playerPaused=True,
    koManualPublished=True, enManualPublished=True,
    koScope='253 timed cues directly reopened, Publish clicked, processing dialog closed; separate primary-KO published table label not independently observed.',
    enScope='118 timed manual cues; published table and manual published dialog directly observed.',
    englishMetadataReopened=True, cardZeroReopened=True, cardExactUrlReopened=True,
    endThreeReopened=True, endScreenStart='6:22:25', endScreenEnd='6:32:25',
    endScreenTimebase='Studio 30fps display',
    explicitWizardCompletionObserved=False,
    wizardLimitation='Separate final upload-completion modal was not observed. Current private settings, 100% transfer, SD/HD completion, automatic checks and actual uploaded pixels were observed independently.',
    paidPromotion=False, alteredContentDisclosure=True, madeForKids=False,
    category='교육', language='한국어',
    thumbnailSaved=False, fullSettingsVerified=False,
    thumbnailFollowup='Actual daily limit; retry only through normal UI after user resumes.',
    optionalPlayerSubtitlePropagationVerified=False,
    humanWholeVideoListeningPronunciationPending=True,
    monetization=dict(status='saved-reopened-verified', enabled=True,
                      observedLabel='사용', midrollEligible=False,
                      reason='Current 392.833333-second video is under eight minutes.',
                      selfRatingSaved=True, selfRatingViolence='Low-level game violence after first seven seconds, minimal blood',
                      otherSelfRatingCategories='none'),
    automaticChecks=dict(status='complete-no-issues', copyright='문제 없음',
                         adSuitability='문제 없음', claims='동영상에서 소유권 주장이 발견되지 않았습니다',
                         protectedContent='동영상에서 저작권 보호 콘텐츠가 발견되지 않았습니다.'),
    proofs=[dict(path=p.relative_to(ROOT).as_posix(), sha256=sha(p))
            for p in sorted(proof.iterdir()) if p.suffix in ['.txt', '.png']],
    nextQueuedStarted=False, automation24='PAUSED')
write(proof / 'final-observations-v1.json', observation)

preflight = ROOT / 'production/batches/sakurai-planning-game-design/preflight/familiar-game-rules.json'
old = read(preflight)
changes = ['projects/game-math-lines-bounds/project.json',
           'projects/game-math-lines-bounds/publishing/youtube-upload.json']
note = '最新 직선/경계상자 manifest와 avLKKfQBV_U 실제 saved-private receipt의 두 변경파일 전체를 직접 읽었다. 직선·선분·반직선, 법선/수직거리, 구/경계상자와 abs(A)e의 기하 계산은 익숙한 조작 약속·버튼 재배치·장치 기능·동시 행동·상황 안내·대상 선택 범위라는 현재 질문과 구별된다. 새 대본 변경은 없으며 다른 강의 40:60/무BGM 예외와 GPU 보류를 보존했다. 현재 편은 사전 Studio 검색0건 이후 단일 ID NLEHMC0XMtg로만 저장했다.'
write(FINAL / 'current-lines-private-change-rereview-v1.json', dict(
    schemaVersion=1, reviewedAt=now(), changedFiles=[dict(path=p, sha256=sha(ROOT/p), fullBodyDirectlyRead=True) for p in changes],
    contentComparison=note, verdict='distinct', foreignFilesModified=False,
    studioEvidence=old['studioEvidence'], ownSinglePrivateVideoId='NLEHMC0XMtg'))
node = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
for args in [
    ['scripts/review-video-duplicates.cjs', 'familiar-game-rules', '--decision', 'distinct',
     '--reason', old['contentReview']+' '+note,
     '--studio-evidence', old['studioEvidence']],
    ['scripts/review-video-duplicates.cjs', 'familiar-game-rules', '--check']]:
    subprocess.run([node,*args], cwd=ROOT, check=True)
