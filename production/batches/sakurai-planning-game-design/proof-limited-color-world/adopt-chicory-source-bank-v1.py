"""Adopt bounded, reviewed source actions for independent narration planning."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, subprocess

ROOT = Path(__file__).resolve().parents[4]
P = Path(__file__).resolve().parent
NODE = 'C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def rel(p): return p.relative_to(ROOT).as_posix()
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''): h.update(b)
    return h.hexdigest()
def new(p, data):
    assert not p.exists(), str(p)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

out = P / 'source-action-bank-v1.json'
assert not out.exists() and not (ROOT / 'projects/limited-color-world').exists()
check = subprocess.run([NODE, 'scripts/review-video-duplicates.cjs', 'limited-color-world', '--check'], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
assert check.returncode == 0, check.stdout + check.stderr
stamp = datetime.now(timezone.utc).isoformat()
trim = read(P / 'chicory-trimmed-sample-direct-review-v2.json')
plan = read(P / 'chicory-trimmed-framing-plan-v2.json')
native = read(P / 'chicory-native-sample-direct-review-v1.json')
play = read(P / 'chicory-native-playback-observations-v1.json')
acq = read(P / 'chicory-official-acquisition-v1.json')
assert trim['allSamplesAndBoardsDirectlyRead'] and trim['allHashesAndSelectedNativePtsVerified']
assert trim['exactTrimmedSampleBoundariesApproved'] and trim['fixed48pxTwoLinePlaceholderFramingSamplesApproved']
assert len(trim['verifiedCuts']) == len(plan['cuts']) == 16
assert native['allSamplesAndBoardsDirectlyRead']
assert len([e for e in play['events'] if e['kind'] == 'start']) == 16
assert len([e for e in play['events'] if e['kind'] == 'end']) == 16
proof_names = ['chicory-official-acquisition-v1.json', 'chicory-coarse-direct-review-v1.json',
    'chicory-native-sample-direct-review-v1.json', 'chicory-native-playback-observations-v1.json',
    'chicory-trimmed-sample-direct-review-v2.json', 'chicory-trimmed-observations-v2.json',
    'source-visual-concept-direct-review-v2.json', 'content-studio-change-review-v3.json']
proofs = [{'path': rel(P / x), 'sha256': sha(P / x)} for x in proof_names]
sources = []
for s in acq['sources']:
    assert sha(ROOT / s['localPath']) == s['sha256']
    sources.append({'sourceKey': s['key'], 'sourcePath': s['localPath'], 'sourceSha256': s['sha256'],
        'bytes': s['bytes'], 'title': s['title'], 'developer': s['developer'], 'publisher': s['publisher'],
        'officialDiscoveryUrl': s['discoveryUrl'], 'officialFolderUrl': s['officialFolderUrl'], 'fileUrl': s['fileUrl'],
        'nativeVideo': {'width': 1920, 'height': 1080, 'frameRate': '60/1', 'timeBase': '1/15360', 'selectedPtsRule': 'nativeFrame * 256'},
        'sourceAudioUse': False, 'publicRightsApproved': False})

links = {
    'outline-room': ('02-contours', 'Paint changes room fills while contours remain', 'Floor, plant and portrait outlines', 'Outline and fill as separate projected layers'),
    'outline-town': ('02-contours', 'Painting tree, path and building while contours remain', 'Path edge, hatching and moving character', 'Separate outline and fill layers'),
    'palette-contours': ('02-contours', 'Painting path, windows, roof and wall in different fills', 'Persistent contours despite changing fills', 'Separate outline and fill layers'),
    'roof-pattern': ('03-pattern-and-erasing', 'Paint covers roof, wall and door', 'Roof hatching, door and window shape', 'Pattern and contour remain when color layer changes'),
    'erase-structure': ('03-pattern-and-erasing', 'Eraser clears selected fills while contours remain', 'Persistent roof hatching and residual paint', 'Erase only the fill layer, preserve structure'),
    'mushroom-first': ('04-height-and-motion', 'Paint raises mushrooms, then character bounces across', 'Top height, silhouette and compression after bounce', 'Projected platforms raise and compress with traversal'),
    'mushroom-four': ('04-height-and-motion', 'Paint four mushrooms in different colors, then bounce across', 'Common shape/height change despite different source hues', 'Color choice and traversal state as separate attributes'),
    'flower-first-part1': ('05-state-not-hue', 'Paint lowers flowers', 'Reduced height and newly visible path', 'Painted flower compresses; no permanent unlock'),
    'flower-first-part2': ('05-state-not-hue', 'Character crosses lowered flowers and one returns tall', 'Current height, actor movement and returning plant', 'Current state transitions, not a permanent label'),
    'flower-second': ('05-state-not-hue', 'Paint shrinks plants and character reaches upper route', 'Plant silhouette and traversable height', 'State represented by geometry and movement'),
    'erase-flower': ('05-state-not-hue', 'Erasing fill restores taller plants while other paint remains', 'Increased height and remaining ground fill', 'Reverse state transition distinct from erasing all paint'),
    'flower-stack': ('06-route-information', 'Paint and cross flowers of different heights', 'Platform tops, edges and direction of travel', 'Route surfaces in projected depth'),
    'flower-route-part1': ('06-route-information', 'Cross upper flower tops', 'Actor position, ledge edge and destination', 'Keep route above fixed captions'),
    'flower-route-part2': ('06-route-information', 'Paint and cross toward lower right', 'Shrinking plant and destination edge', 'Separate source shots; no optimal route claim'),
    'dark-cave-first': ('07-local-contrast', 'Move and paint inside a localized pale illuminated circle', 'Character and outlines against dark surroundings', 'Local lightness boundary and foreground silhouettes'),
    'dark-cave-second': ('07-local-contrast', 'Move and paint across cave objects within the pale circle', 'Still-dark surroundings and nearby outlined objects', 'Move limited light area without claiming whole-scene brightening'),
}
windows = []
for c in plan['cuts']:
    review = next(x for x in trim['verifiedCuts'] if x['key'] == c['key'])
    assert review['startFrame'] == c['startFrame'] and review['endFrameExclusive'] == c['endFrameExclusive']
    assert review['startPts'] == c['startFrame'] * 256 and review['endPtsExclusive'] == c['endFrameExclusive'] * 256
    ident, action, focus, diagram = links[c['key']]
    s = next(s for s in sources if s['sourceKey'] == c['source'])
    windows.append({'key': c['key'], 'sourceKey': c['source'], 'sourceSha256': s['sourceSha256'],
        'startFrame': c['startFrame'], 'endFrameExclusive': c['endFrameExclusive'], 'startPts': c['startPts'], 'endPtsExclusive': c['endPtsExclusive'],
        'timeBase': '1/15360', 'frameRate': '60/1', 'durationSeconds': (c['endFrameExclusive'] - c['startFrame']) / 60,
        'framingUpPixels': c['framingUpPixels'], 'sameFrameBottomBlurPixels': c['sameFrameBottomBlurPixels'],
        'boundaryDirectReviewApproved': True, 'placeholderFramingSampleReviewApproved': True,
        'normalSourcePlaybackBasis': '16 original candidate windows actually started and ended at 1x muted; browser endpoints are not native in/out',
        'provisionalInsertion': ident, 'visibleAction': action, 'viewerFocus': focus, 'diagramConnection': diagram,
        'observation': review['observation']['note'], 'normalPlaybackRate': 1, 'loop': False, 'slowdown': False, 'sourceAudioUse': False,
        'selectedForNarrationPlanning': True, 'finalUseDurationSeconds': None, 'allFinalCueUiApproved': False,
        'trimmedDynamicFramingPlaybackApproved': False, 'allContinuousFramesReviewed': False})
assert sum(w['durationSeconds'] for w in windows) == 101.5
for s in sources:
    ordered = sorted([w for w in windows if w['sourceKey'] == s['sourceKey']], key=lambda w: w['startFrame'])
    assert all(a['endFrameExclusive'] <= b['startFrame'] for a, b in zip(ordered, ordered[1:]))

recent_inputs, matches = [], []
for p in sorted((ROOT / 'projects').rglob('*')):
    if not p.is_file() or not (p.name == 'project.json' or ('sources' in p.parts and p.suffix.lower() in {'.json', '.md'})): continue
    content = p.read_text(encoding='utf-8-sig', errors='replace')
    recent_inputs.append({'path': rel(p), 'sha256': sha(p)})
    if any(t in content.lower() for t in ['chicory', 'minit', 'into the breach']):
        matches.append({'path': rel(p), 'titles': [t for t in ['Chicory', 'Minit', 'Into the Breach'] if t.lower() in content.lower()]})
chicory_prior = [m for m in matches if 'Chicory' in m['titles']]
assert not chicory_prior, chicory_prior
new(P / 'chicory-trimmed-playback-limitation-v3.json', {'schemaVersion': 1, 'recordedAt': stamp,
    'dom': rel(P / 'chicory-trimmed-playback-v3.dom.txt'), 'domSha256': sha(P / 'chicory-trimmed-playback-v3.dom.txt'),
    'actualState': read(P / 'chicory-trimmed-playback-v3.dom.txt'), 'actualV3PreparedWindows': 1, 'actualV3PlaybackStarts': 0,
    'observedFailure': 'Page.captureScreenshot timed out; subsequent Input.dispatchMouseEvent timed out. Read-only DOM shows outline-room paused at155, no new start event.',
    'trimmedDynamicPlaybackOrFinalPixelsApproved': False, 'sourceSourcePlaybackAndNativeSamplesPreserved': True,
    'nextReview': 'Actual rendered continuous animation and every narration cue/UI must be directly reviewed before final QA; no unseen browser pixel approval.'})
data = {'schemaVersion': 1, 'slug': 'limited-color-world', 'recordedAt': stamp,
    'status': 'bounded-source-actions-adopted-for-independent-narration-planning', 'sourceAdoptionApproved': True,
    'adoptionScope': 'Official press B-roll candidate action-to-claim planning: original normal-speed playback, native boundary samples and actual-caption-size framing samples. Current final cue, all intermediate motion and public-rights approval remain false.',
    'sources': sources, 'windows': windows, 'maximumUniqueSeconds': 101.5, 'maximumUniqueNativeFrames': 6090,
    'proofs': proofs, 'currentDistinctCheck': {'exitCode': 0, 'stdout': check.stdout},
    'rights': {'directlyRead': True, 'officialPressKit': acq['sources'][0]['discoveryUrl'],
        'observedScope': 'Official developer supplied B-Roll1/2 under the Video folder linked from its press kit.',
        'broadMonetizedReuseLicenseObserved': False, 'thirdPartyRecordingAdopted': False, 'sourceMusicOrAudioAdopted': False,
        'publicDescriptionCreditRequirementObserved': False, 'finalHumanRightsReviewPending': True},
    'sourceOwners': ['Wishes Ultd / Greg Lobanov', 'Finji'],
    'recentUseReview': {'method': 'Full current project manifests and source JSON/Markdown scan; separate from complete content/Studio duplicate review.',
        'filesScanned': len(recent_inputs), 'inputHashes': recent_inputs, 'matches': matches, 'earlierCompletedChicoryUseObserved': False},
    'candidates': [
        {'game': 'Chicory: A Colorful Tale', 'decision': 'selected-bounded-official-actions', 'reason': 'First channel use observed; outline, pattern, height/motion and local contrast directly illustrate hue-independent information.'},
        {'game': 'Minit', 'decision': 'held', 'officialSite': 'https://minitgame.com/', 'officialTrailer': 'https://www.youtube.com/watch?v=svUtAAFaokM',
            'policy': 'https://canipostandmonetizevideosofdevolvergames.com/', 'policyDirectlyRead': True,
            'reason': 'Observed mobile promo has parallel insets and zoomed promotion. No adequate native continuous action source secured; download/decode/adoption0.'},
        {'game': 'Into the Breach', 'decision': 'rejected-for-current-selection', 'reason': 'Recent use in several project sources; prioritize the new concept-matched Chicory title.'}],
    'exclusions': ['Chicory reveal/intro cinematic/chill idle/promotional footage', 'Dialogue/sign/letterbox/pickup intervals', 'Repeated mushroom traversal33–39 and flower78–87', 'Source audio and music'],
    'gameCaptionConstraint': {'style': 'boxed-white-forest-v1', 'center': [960,970], 'fontSize':48, 'measuredWidthRequired':True,
        'longCueRemedy': 'Split cue or adjust the source framing; never move the caption anchor.'},
    'sourceFraming': {'up120': 'Crop original top120 and use same-frame bottom120 blur; source colors preserved.', 'source0': 'Preserve original full-width framing.'},
    'actualBodyRatioApproved': False, 'allFinalPixelsApproved': False, 'allNativeFramesReviewed': False,
    'wholeContinuousViewingOrListeningApproved': False, 'trimmedDynamicFramingPlaybackApproved': False,
    'humanListeningApproved': False, 'publicRightsApproved': False, 'newSourceAcquisitionOrDecodeOrExtraction': False,
    'externalResearchChanges': 0, 'rasterGitAdditions': 0}
new(out, data)
qp = ROOT / 'production/batches/sakurai-planning-game-design/queue.json'
original = qp.read_bytes(); q = json.loads(original)
foreign = json.dumps([x for x in q['items'] if x['slug'] != 'limited-color-world'], ensure_ascii=False, sort_keys=True)
i = next(x for x in q['items'] if x['slug'] == 'limited-color-world')
i.update(stage='bounded-source-bank-adopted-independent-script-next', sourceActionBank=rel(out), sourceActionBankSha256=sha(out),
    sourcePlanningAdopted=True, duplicateInventoryDigest=read(ROOT / 'production/batches/sakurai-planning-game-design/preflight/limited-color-world.json')['inputsDigest'], updatedAt=stamp,
    nextAction='Create and directly compare independent KOEN and overview promises against this bounded action bank; measure voice before final unique60:40 assignment. Continuous final cue/UI approval remains pending.')
assert foreign == json.dumps([x for x in q['items'] if x['slug'] != 'limited-color-world'], ensure_ascii=False, sort_keys=True) and qp.read_bytes() == original
tmp = qp.with_suffix('.limited-bank.tmp'); tmp.write_text(json.dumps(q, ensure_ascii=False, indent=2)+'\n', encoding='utf-8'); os.replace(tmp, qp)
print(json.dumps({'sourcePlanningAdopted':True, 'windows':16, 'uniqueSeconds':101.5, 'finalPixelsApproved':False, 'publicRightsApproved':False}))
