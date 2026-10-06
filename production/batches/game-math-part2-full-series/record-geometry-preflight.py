"""Record inspected sources and the actual collision content comparison."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=B/'research/geometry-legacy-content-comparison.json';d=read(p)
legacy=[
 ('oI08Qvaiokk','CollisionManager·사각형(Rect) 충돌 | Windows API 자체엔진',
 ['Box/circle proxies and offsets;2D fighting hitboxes versus detailed meshes','Collision-layer bit sets and an upper-triangle pair matrix','Pair iteration, broad-phase structures and profiling; actual rectangle collision logic explicitly deferred'],
 'Does not derive3D componentwise point bounds or affine abs(A)*half-extents. Do not remake collision layers/pair iteration.'),
 ('6eBDz1GBrCc','원·원 충돌 판정(Circle–Circle) | 자체엔진 LV20',
 ['2D center distance versus summed radii; radius/component-type debugging','Circle–rectangle region/corner assignment and later library discussion'],
 'Two-circle collision already covered. New sphere coverage is point versus3D surface/solid, squared distance and measure scaling; do not relabel circle–circle collision as new.'),
 ('q5jnPa84Nhg','Collider(충돌체) 구성 | 자체 게임 엔진 LV20',
 ['Collider subclasses, offsets, component update order and default100x100 dimensions','Rectangle debug drawing, stock transparent brushes, background and pen debugging','Second object and planned collision function callbacks'],
 'Collider architecture/debug drawing already covered. New3D data enclosure and its affine transformation have a different viewer question.')]
for vid,title,claims,diff in legacy:
 f=R/f'tmp/game-math-part2-sources/part1-{vid}.local-asr.txt'
 e={'videoId':vid,'title':title,'url':f'https://www.youtube.com/watch?v={vid}',
    'transcript':f.relative_to(R).as_posix(),'sha256':sha(f),'fullTranscriptRead':True,
    'transcriptType':'Local Whisper large-v3-turbo read-back of the actual channel video audio; no native transcript available for the rectangle lecture',
    'limitations':'Raw ASR has repeated nonsense during quiet coding intervals and imperfect terminology. It supports a topical comparison only, not exact quotations or mathematical authority. All text was read, including the middle collider-drawing portion.',
    'content':claims,'geometryOverlap':diff}
 d['existingVideos']=[x for x in d['existingVideos'] if x['videoId']!=vid]+[e]
d['additionalStudioCollisionSearch']['remainingContentReview']=[]
proof=R/'shared/output/game-math-part2-full-series/preflight/studio-geometry-current.ax.txt'
d['currentStudioEvidence']=list(dict.fromkeys(d['currentStudioEvidence']+[proof.relative_to(R).as_posix()]))
d['geometryTitleSearch']={'proof':proof.relative_to(R).as_posix(),'sha256':sha(proof),'query':'기하','actualMatches':0,'observedAt':'2026-10-06'}
d['status']='actual-legacy-content-and-current-Studio-compared; creation-time inventory digest still required'
d['candidateDifferences'][0]['reuseLimit']='Briefly recall displacement/normalization and existing2D overlap; concentrate on geometric representations,3D point bounds, transformed-box enclosure and proxy limitations. Seven likely overlapping actual channel videos compared.'
write(p,d)
sources=read(B/'footage-index.json')
for vid,game,tag,permission,visible,approved in [
 ('SSekdYTL4Ck','A Story About My Uncle','geometry-uncle-fine','uncle-permission.ax.txt',
  'First-person grappling traversal among rock platforms, changing cyan beam endpoints and viewpoints; wooden village posts/rails viewed while walking. Visible rendering does not reveal raycast/collider code.',
  [[482,510],[559,576],[598,613],[632,669],[714,768],[1205,1277],[1305,1385],[1519,1598]]),
 ('4s7nMfXt8uQ','Serious Sam2','geometry-sam-fine','sam2-permission.ax.txt',
  'Actual combat/traversal with round projectile-like objects and explosion effects, tall creatures, long bridges, round huts and fences. Observe silhouettes, motion and enclosure questions; effect radius is not asserted to equal damage radius.',
  [[64,86.5],[96.5,122],[297,367],[374,430],[494,542],[566,570],[578,658],[678,740]])]:
 f=R/f'shared/output/game-math-part2-full-series/sources/{vid}.mp4';meta=f.with_suffix('.info.json')
 inspect=R/f'shared/output/game-math-part2-full-series/inspection/{tag}/generated-samples.json';records=read(inspect)['records']
 evidence=R/f'shared/output/game-math-part2-full-series/preflight/{permission}'
 sources[vid]={'id':vid,'game':game,'uploader':'NCR Gameplay','url':f'https://www.youtube.com/watch?v={vid}',
  'file':f.relative_to(R).as_posix(),'sha256':sha(f),'reviewedBeforeNarration':True,
  'recordingPermissionObserved':'Actual expanded uploader description read2026-10-06: explicitly free-to-use gameplay for your videos. Recording permission only, not a named CC license or independent game-IP clearance. No source audio/OST used.',
  'permissionProof':evidence.relative_to(R).as_posix(),'permissionProofSha256':sha(evidence),
  'licenseLabel':'uploader free-to-use permission','metadataProof':meta.relative_to(R).as_posix(),'metadataSha256':sha(meta),
  'sourceAudioUsed':False,'priorUse':'Game title and exact recording ID absent from earlier project source history at selection; fresh games chosen for this geometry chapter.',
  'visibleAction':visible,'inspection':'All listed dense contact sheets directly viewed at3-second intervals including end samples before dependent narration. Excluded menus, deaths/loading, story conversations and tutorial banners. Use only approved intervals; the observed first-person camera change is not proof of changing world-axis bounds.',
  'inspectionSheets':[x['sheet'] for x in records],
  'inspectionEvidence':[{'path':x['sheet'],'sha256':sha(R/x['sheet'])} for x in records],
  'approvedIntervals':approved,'publicGameIpReview':'pending'}
write(B/'footage-index.json',sources)
write(B/'research/geometry-footage-readiness.json',{'reviewedAt':'2026-10-06','dependentNarrationWrittenBeforeInspection':False,
 'directReviewComplete':True,'sources':{v:sources[v] for v in ['SSekdYTL4Ck','4s7nMfXt8uQ']},
 'legacyReview':p.relative_to(R).as_posix(),'limits':'Recording permission observed; human public-IP review remains pending. Contact-sheet files remain local, hashes only in Git.'})
print('Seven existing channel scripts compared; two fresh recordings inspected before narration.')
