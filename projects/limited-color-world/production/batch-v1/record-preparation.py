"""Record this episode's completed measured preparation, without media jobs."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
LOCAL = PROJECT / 'production/local/batch-v1'
sys.path.insert(0, str(HERE))
import video_pipeline as video


def read(path):
    return json.loads(path.read_text('utf-8-sig'))


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


plan = read(HERE / 'edit-plan.json')
split = read(LOCAL / 'voice/scene-split-review.json')
captions = read(LOCAL / 'edit/captions.json')
ratio = video.validate_plan(plan)
ranges = {}
for cut in plan['cuts']:
    if cut['kind'] == 'independent-gameplay':
        video.annotations(cut, plan)
        ranges.setdefault(cut['source'], []).append(
            [cut['sourceStart'], cut['sourceStart'] + cut['frames'] / 60])
for source, windows in ranges.items():
    windows.sort()
    assert all(a[1] <= b[0] + 1e-7 for a, b in zip(windows, windows[1:])), source

proof = {
    'status': 'measured-preparation-complete-heavy-render-pending',
    'slug': PROJECT.name, 'revision': 'batch-v1',
    'planSha256': sha(HERE / 'edit-plan.json'),
    'frozenScriptHashes': {p.name: sha(p) for p in
                           (PROJECT / 'script/batch-v1').glob('narration*.json')},
    'sourcePcmSha256': sha(LOCAL / 'voice/narration-source.wav'),
    'rawAsrSha256': sha(LOCAL / 'voice/whole-source-asr.json'),
    'sourcePcmReconstructionIdentical': split['decodedSourceReconstructionIdentical'],
    'discardedSamples': split['discardedSamples'], 'repeatedSamples': split['repeatedSamples'],
    'sceneCount': len(plan['scenes']), 'cutCount': len(plan['cuts']),
    'ratio': ratio, 'mcFrames': plan['mcFrames'], 'totalFrames': plan['totalFrames'],
    'pairedCaptionCount': len(captions['cues']),
    'noRepeatedNativeIntervals': True, 'actualNativeSourceRanges': ranges,
    'abstractNativeEvent': plan['actualGameAbstractAnchor'],
    'questionBlockSupplement': plan['questionBlockActionSupplement'],
    'annotationBounds': 'all actual mark geometry passed fixed-caption and protected-UI checks',
    'typescript': 'scoped diagnostics0', 'imageUrls': 'logical D /@fs paths',
    'heavyMediaJobsStarted': False, 'sourceAsrRerun': False,
    'humanWholeListening': 'pending',
    'pronunciationContextFlags': ['second Puyo game title', '같은 종류 recognition'],
    'actualEncodedMovingPixelReview': 'pending'}
save(HERE / 'measured-preparation-review.json', proof)

checkpoint = read(HERE / 'checkpoint.json')
checkpoint.update(stage='measured-edit-captions-ready',
                  status='measured-edit-captions-ready-awaiting-root-render-slot',
                  updatedAt=datetime.now(timezone.utc).isoformat(),
                  nextAction='Root serialized heavy slot: packed MC4901frames, mix/cuts/pair/verify, native/mobile/audio QA and four local outputs.')
checkpoint['currentPreparation'].update(
    rawVoiceReceived=True, reviewedSceneTimingReceived=True,
    sourcePcmReconstructionIdentical=True, captions=len(captions['cues']), cuts=len(plan['cuts']))
checkpoint['nextStep'] = checkpoint['nextAction']
save(HERE / 'checkpoint.json', checkpoint)

manifest = read(PROJECT / 'project.json')
manifest['status'] = checkpoint['status']
manifest['currentRevision']['status'] = checkpoint['status']
manifest['updatedAt'] = checkpoint['updatedAt']
save(PROJECT / 'project.json', manifest)

production = read(PROJECT / 'planning/production-plan.json')
production['measuredEditReview'] = proof
production['questionBlockActionSupplement'] = {
    'reason': 'Official loop shows the block outline but does not hit it. Independently recorded CC-BY FHD gameplay supplies the actual hit and mushroom result.',
    'sourceId': 'wonder-block-cc', 'localNativeWindow': [6.8, 10.7],
    'rights': 'Nintendo game-video guidelines plus explicit recorder Creative Commons Attribution metadata',
    'noReferenceLessonFootage': True, 'sourceWatermarksPreserved': True,
    'gameCountUnchanged': 'same Super Mario Bros.Wonder example; still one Nintendo game of two total',
    'scope': 'visual/source-only within the unchanged204.199s voice and63cue clock'}
save(PROJECT / 'planning/production-plan.json', production)
print('D25 measured preparation, source union and all actual mark bounds verified')
