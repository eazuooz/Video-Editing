"""Append observed official game demonstrations without selecting or approving footage."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os
R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(R).as_posix()
source = P / 'part2-primary-source-research-v267.json'
old = read(source)
record = {'recordedAt': datetime.now(timezone.utc).isoformat(), 'status': 'observed-candidates-not-selected',
 'physicalPart': 2, 'priorResearch': {'path': rel(source), 'sha256': sha(source)},
 'additionalObservations': [
  {'game': 'The Witcher 3', 'year': 2015, 'videoUrl': 'https://www.youtube.com/watch?v=Md4Hmgtl8q0',
   'officialPublisherObserved': 'NVIDIA verified channel;2015-05-18 original HairWorks demonstration.',
   'browser': {'tabId': '70', 'duration': 115.521, 'playbackRate': 1, 'endedObserved': True},
   'actualMovingPixelObservations': [
    {'time': 8.172, 'observation': 'Third-person Geralt combat with a bear; dense bear fur is visible. This is a fur/strand observation, not a volumetric-lighting measurement.'},
    {'time': 85.303, 'observation': 'Combat with a shaggy creature; character and creature move while dense fur remains the observable feature.'}],
   'primarySource': 'https://www.nvidia.com/en-us/geforce/news/the-witcher-3-wild-hunt-graphics-performance-and-tweaking-guide/',
   'primarySectionsActuallyRead': ['HairWorks description and implementation/LOD discussion', 'Off/Geralt-only/All choices and version-specific performance discussion'],
   'claimBoundaries': ['HairWorks hair/fur is separate from PhysX clothing.', 'Do not infer a particular OIT implementation from visible fur.', 'Original2015 settings and patch context cannot be transferred to a later remaster or current hardware.', 'The inaccessible GDC page remains unread.'],
   'selectedIntervals': [], 'allMovingPixelsReviewed': False, 'rightsApproved': False},
  {'game': 'Indiana Jones and the Great Circle', 'year': 2024, 'videoUrl': 'https://www.youtube.com/watch?v=7pOiUht8tc0',
   'officialPublisherObserved': 'NVIDIA GeForce verified channel; matching official2024 release article.',
   'browser': {'tabId': '71', 'duration': 52.601, 'playbackRate': 1, 'completePlaybackObserved': True},
   'actualMovingPixelObservations': [
    {'time': 24.692702, 'observation': 'Moving view of a classroom with windows, desks and floor. The original Ray-traced Global Illumination label is visible; do not call this an isolated reflection test.'},
    {'time': 28.202664, 'observation': 'Moving outdoor stone courtyard with foliage and arches; the original RTX ON and ray-tracing label are visible. A later source interval must retain comparison conditions.'},
    {'time': 42.58878, 'observation': 'Black/fade screen observed. This frame is not action footage and cannot fill the ratio.'}],
   'primarySource': 'https://www.nvidia.com/en-us/geforce/news/dlss-full-ray-tracing-indiana-jones-and-the-great-circle/',
   'primaryArticleActuallyRead': True,
   'claimBoundaries': ['The2024 release article identifies full-ray-traced GI, foliage subsurface scattering, indoor reflections and sun shadows.', 'DLSS3 Super Resolution and Frame Generation are separate parts of the advertised feature bundle.', 'Do not infer SER, BLAS update policy or a measured sample count from the game pixels.'],
   'selectedIntervals': [], 'allMovingPixelsReviewed': False, 'rightsApproved': False}],
 'fourGameCandidates': [c['game'] for c in old['candidates']], 'finalFourGameSelectionApproved': False,
 'rightsReview': 'pending-source-specific', 'recentUseReview': 'pending-before-selection',
 'newMediaAcquired': 0, 'newNarrationWritten': False, 'newTts': 0, 'newGitImages': 0,
 'rendered': False, 'uploaded': False,
 'next': 'Secure and directly review exact normal-speed unique action intervals before new narration; preserve all existing approved chapters/PCM.'}
dest = P / 'part2-candidate-observations-v278.json'
assert not dest.exists()
dest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
cp = R / 'production/research/game-lighting-history/checkpoint.json'
j = read(cp)
j['episode04Part2CandidateObservationsV278'] = {'path': rel(dest), 'sha256': sha(dest), 'status': record['status'], 'approved': False}
t = cp.with_name(cp.name + '.writing-' + str(os.getpid()))
t.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n', 'utf-8')
os.replace(t, cp)
print(json.dumps({'additionalObservedGames': 2, 'selected': 0, 'newTts': 0, 'approved': False}))
