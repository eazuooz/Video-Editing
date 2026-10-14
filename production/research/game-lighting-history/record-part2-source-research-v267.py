"""Preserve direct chapter reread and primary-source candidates, not production approval."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, os
R = Path(__file__).resolve().parents[3]
P = R / 'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(R).as_posix()
stamp = lambda: datetime.now(timezone.utc).isoformat()
chapters = []
for name in ['path-chapter-review-plan-v18.json', 'reconstruction-chapter-review-plan-v23.json', 'megalights-chapter-review-plan-v28.json', 'hair-chapter-review-plan-v30.json']:
    path = P / name
    j = read(path)
    chapters.append({'path': rel(path), 'sha256': sha(path), 'paragraphIds': [e['id'] for e in j['entries']],
                     'allFullKoreanAndEnglishParagraphsDirectlyRead': True,
                     'claim': 'Retain all original explanations, numerical examples and recorded PCM. New examples require inspected source intervals and independent matching narration.'})
record = {'recordedAt': stamp(), 'status': 'primary-source-research-candidates-only', 'physicalPart': 2,
          'directlyRereadChapters': chapters,
          'chapterConnections': [
              'Path sampling: preserve importance weighting, MIS, roulette, variance and limitations; actual footage illustrates surfaces and light paths without claiming measured sample counts.',
              'Reconstruction: distinguish noisy-light reconstruction from output-resolution reconstruction and display-frame generation. Preserve feature bundles in vendor comparisons.',
              'MegaLights: distinguish direct-light selection/visibility from Lumen indirect lighting; engine demos are not additional released-game identities.',
              'Transparency/hair: preserve alpha order, per-pixel intersections, peeling/list/weighted alternatives and strand visibility versus scattering; a current demo date is not an invention date.'
          ],
          'candidates': [
              {'game': 'Cyberpunk 2077', 'year': 2023, 'videoUrl': 'https://www.youtube.com/watch?v=Tk7Zbzd-6fs',
               'primaryUrl': 'https://www.nvidia.com/en-gb/geforce/news/cyberpunk-2077-ray-tracing-overdrive-update-launches-april-11/',
               'fit': 'Overdrive path-tracing preview; observe occluded surfaces and changing direct/indirect light.',
               'actualBrowserObservation': 'NVIDIA GeForce verified channel; normal-rate muted playback. At32.29s an overhead street view shows lit/shaded areas with RTX ON. At48.26s a text card is visible and cannot count as action. At78.87s moving first-person action is visible with RTX ON.',
               'conditions': 'The intro states RTX4090,4K,DLSS3 enabled. Preserve that bundle. Only selected local action intervals can become approved cuts.',
               'selectedIntervals': [], 'allMovingPixelsReviewed': False},
              {'game': 'Alan Wake 2', 'year': 2023, 'videoUrl': 'https://www.youtube.com/watch?v=HwGbQwoMCxM',
               'primaryUrl': 'https://www.nvidia.com/en-us/geforce/news/gfecnt/20238/alan-wake-2-cyberpunk-2077-phantom-liberty-dlss-3-5/',
               'fit': 'Full-ray-tracing and reconstruction observations in another actual game.',
               'actualBrowserObservation': 'Official article links this video. Browser title is Alan Wake2,4K NVIDIA DLSS3.5 World Premiere. At40.08s the game scene shows a third-person character and street surfaces, with31FPS and DLSS Off,Full RT On displayed.',
               'conditions': 'Read all enabled feature labels and hardware conditions before selecting a comparison; this snapshot is not an isolated Ray Reconstruction measurement.',
               'selectedIntervals': [], 'allMovingPixelsReviewed': False},
              {'game': 'Indiana Jones and the Great Circle', 'year': 2024, 'videoUrl': 'https://www.youtube.com/watch?v=7pOiUht8tc0',
               'primaryUrl': 'https://www.nvidia.com/en-us/geforce/news/dlss-full-ray-tracing-indiana-jones-and-the-great-circle/',
               'fit': 'Released-game path-tracing lighting, foliage transmission and reflection responsibilities.',
               'actualBrowserObservation': 'Video ID linked by the primary article; actual video pixels not yet inspected.',
               'conditions': 'Keep the2024 game/version context. Developer optimization details require their own source verification; do not infer SER or BLAS internals from gameplay.',
               'selectedIntervals': [], 'allMovingPixelsReviewed': False},
              {'game': 'The Witcher 3', 'year': 2015, 'videoUrl': 'https://www.youtube.com/watch?v=Md4Hmgtl8q0',
               'primaryUrl': 'https://www.gdcvault.com/play/1020664/The-Witcher-3-Enabling-Next',
               'fit': 'HairWorks hair/fur as a historical actual-game thin-strand case; distinguish it from transparency and volumetric algorithms.',
               'actualBrowserObservation': 'Candidate discovered from officialNVIDIA search; direct video review still pending. GDC source fetch was unavailable and is not treated as read evidence.',
               'conditions': 'Use original2015 HairWorks footage, not a later path-tracing remaster. Do not assert an unseen OIT implementation.',
               'selectedIntervals': [], 'allMovingPixelsReviewed': False}
          ],
          'rightsReview': 'pending-source-specific', 'recentUseReview': 'pending-before-selection',
          'finalFourGameSelectionApproved': False, 'newNarrationWritten': False, 'newTts': 0,
          'newMediaAcquired': 0, 'newGitImages': 0, 'rendered': False, 'uploaded': False,
          'next': 'Complete current physicalPart1 review/private delivery. Inspect and secure unique concept-matched source intervals before newPart2 narration/TTS; retain all approved models and PCM.'}
dest = P / 'part2-primary-source-research-v267.json'
dest.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', 'utf-8')
cp = R / 'production/research/game-lighting-history/checkpoint.json'
j = read(cp)
j['episode04Part2ResearchV267'] = {'path': rel(dest), 'sha256': sha(dest), 'status': record['status'], 'rendered': False, 'uploaded': False}
t = cp.with_name(cp.name + '.writing-' + str(os.getpid()))
t.write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n', 'utf-8')
os.replace(t, cp)
print(json.dumps({'chaptersDirectlyReread': len(chapters), 'paragraphs': sum(len(c['paragraphIds']) for c in chapters), 'candidatesOnly': 4, 'newTts': 0, 'approved': False}))
