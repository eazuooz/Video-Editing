"""Current physical-part content comparison; no foreign project mutation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT = Path(__file__).resolve().parents[3]
R = ROOT / 'production/research/game-lighting-history'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text('utf-8-sig'))
previous = read(ROOT / 'production/preflight/game-lighting-history-04-3.json')
unchanged = []
for r in previous['inputFiles']:
    p = ROOT / r['path']
    assert p.exists() and sha(p) == r['sha256'], 'Changed input requires direct review: ' + r['path']
    unchanged.append(r)
direct = [
 'projects/frame-rate-modern-rendering/script/narration.ko.json',
 'production/research/game-lighting-history/local/channel-dlss5-transcript.txt',
 'projects/game-math-interpolation-cross-game-additions-v3/script/narration.ko.json',
 'projects/game-math-interpolation-cross-game-additions-v3/script/narration.en.json']
review = {
 'reviewedAt': datetime.now(timezone.utc).isoformat(),
 'candidate': 'game-lighting-history-04-3', 'priorPreflightInputsDigest': previous['inputsDigest'],
 'all511PriorInventoryPathsUnchanged': True, 'unchangedInputs': unchanged,
 'currentFullBodiesDirectlyReread': [{'path': s, 'sha256': sha(ROOT / s)} for s in direct],
 'priorFullContentReviews': [
  'production/research/game-lighting-history/episode04-current-text-rereview-v97.json',
  'production/research/game-lighting-history/episode04-current-wording-rereview-v91.json',
  'production/research/game-lighting-history/episode04-current-duplicate-rereview-v68.json'],
 'earlierCurrentChangedInputReview': 'Parent current85 paragraphs plus current quaternion publishing metadata and eight paired interpolation/cross-game additions were directly read in the preceding production continuation; no511-path inventory change since that preflight snapshot.',
 'studio': {
  'observation': 'CUA, own tab54, current channel Videos; applied title DLSS filter returned exactly2 rows; each actual video edit href read from rendered DOM.',
  'results': [
   {'id': 'mAO_tit6Qjs', 'title': '30·60·120 FPS 차이, 왜 중요할까? | 게임 프레임과 DLSS', 'duration': '7:26', 'state': 'public', 'date': '2026-09-06',
    'comparison': 'Existing20-scene whole Korean script directly reread: FPS/time budget/deltaTime/TV standards/modes/SR/FG/MFG/latency. Shared MFG distinction is a prerequisite here; this episode asks how final appearance differs from calculation and follows exposure, bloom, focus and event-resource frame inspection.'},
   {'id': 'iDz12leT0T4', 'title': 'NVIDIA DLSS 5 | AI 기반 게임 그래픽스 소개', 'duration': '10:52', 'state': 'public', 'date': '2026-03-18',
    'comparison': 'Full10:52 channel transcript directly reread: announcement/news reading and visual opinion/preview. Current Studio description explicitly scopes it to production-time introduction, not latest support/timing/performance. New teaching distinguishes MFG4/4.5 from appearance5, preview versus September NBA release, then uses four-game surfaces, engine exposure/color/focus and frame input-output inspection.'}],
  'otherObservedCurrentRows': ['lIDe30dqC28 private rendering03, Oct10,25:52', 'Rck2eL8VtqM quaternion calculations Oct19 scheduled', 'wreXZkEtLqA quaternion foundations Oct17 scheduled, review pending'],
  'existingUploadsChanged': False, 'noExistingPhysicalPart3IdObserved': True},
 'crossGameMathComparison': 'Eight paired IPF/RCF additions teach orientation interpolation, time remapping, matrix columns, determinant/reflection and model axis equality through aircraft; not image exposure/reconstruction or GPU event-resource inspection. Unchanged quaternion content/receipts remain separate.',
 'physicalSplit': 'Logical04 is an authorized disjoint split. Parts1/2 retain earlier visibility/VSM/mobile and path/reconstruction/MegaLights/transparency coverage. The85 current paragraphs in this physical part retain DLSS/postprocessing/inspection/conclusion once, with its independent overview and four-game comparison.',
 'verdict': 'distinct', 'basis': 'Viewer question, all current chapter arguments and full related scripts/transcripts, not title/ID count alone.',
 'foreignFilesModified': False, 'uploaded': False}
(R / 'part3-current-duplicate-direct-review-v153.json').write_text(json.dumps(review, ensure_ascii=False, indent=2)+'\n', 'utf-8')
print(json.dumps({'inventoryPathsUnchanged': len(unchanged), 'currentFullBodiesReread': len(direct), 'actualStudioDlssRows': 2}))
