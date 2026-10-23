from common import *
import sys
unit=sys.argv[1];slug={'m18':'game-math-projection-depth','m19':'game-math-mesh-uv','m20':'game-math-normal-transform-uv'}[unit]
P=R/'projects'/slug;H=P/'production/concept-fit-v2';assert read(H/'review-ledger.json')['status']=='local-review-ready-with-listening-notes'
paths={rel(p) for p in B.glob('*'+unit+'*.py')}|{rel(p) for p in B.glob(unit+'-*.json') if not p.name.endswith('-commit.json')}
paths|={rel(p) for p in H.glob('*.json')}
paths|={rel(p) for p in (P/'script/concept-fit-v2').glob('*.json')}
paths|={rel(p) for p in (P/'publishing/revisions/concept-fit-v2').glob('*.txt')}
shared=['docs/GAME_MATH_PRIVATE_POLISH.md','shared/publishing/video-worklist.json',rel(P/'project.json')]
paths.update(shared+[rel(B/'checkpoint.json')])
if unit=='m18':
 for s in ['game-math-camera-frustum','game-math-camera-projection']:
  paths.add(f'projects/{s}/publishing/revisions/concept-fit-v2/upload-description.en.txt');paths.add(f'projects/{s}/production/concept-fit-v2/description-drafts.json')
if unit in ['m19','m20']:paths.add(rel(B/'m19-m20-source-playback.json'))
if unit in ['m19','m20']:
 paths.update(rel(B/name) for name in ['caption_wrap_exact.py','record-last-preflight.py','prepare-commit-final-units.py','record-final-delivery.py','refresh-progress.py'])
if unit=='m20':
 shared+=['shared/publishing/video-production-control.json','docs/VIDEO_WORKLIST.md']
 paths.update(shared)
 paths.update(['scripts/render-video-worklist.py',rel(B/'finish-batch.py'),rel(B/'final-batch-check.json'),rel(B/'commit-unit.py')])
save(B/(unit+'-reviewed-delivery-commit.json'),dict(paths=sorted(paths),sharedPaths=shared,message=f'Match {unit.upper()} lecture examples to observed objects and surface changes'))
print(unit,len(paths),'owned paths prepared')
