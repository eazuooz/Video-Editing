"""Save the direct preview review performed before this lecture's first TTS.

This records reviewed preview pixels, not final audio/captions/private delivery.
"""
from pathlib import Path
import json, hashlib
from datetime import datetime, timezone

R=Path(__file__).resolve().parents[3]
slug='game-math-mesh-uv'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
P=R/'projects'/slug
W=R/'shared/output'/slug/'lookdev'
samples=read(W/'inspection/generated-samples.json')
notes={
 '01':'Four overview steps: projected triangle plates, separately legible0–3 records, three orthogonal face directions, cube corner. Matches the independent narration overview.',
 '03':'Overlapping volumes, bored top face, projected open quad and diagonal. Shape/data representation is explicitly original, not inferred from game pixels.',
 '04':'All six copied records012023 and four unique0123 are now individually visible.192B/140B whole quad is distinguished from192B/44B one shared record.',
 '05':'Winding arrows, reversed cycle, shared edge02 and actual plate side faces are legible. Connectivity and attribute identity remain distinct.',
 '08':'Same six-sided silhouette with flat or interpolated face brightness and radial directions. Top and side faces remain spatially projected.',
 '09':'Shape is preserved between shading examples. Half-vector and normalized-vector arrows differ in length with matching.707 labels.',
 '12':'Complete zero/cross/face-unit/accumulate/final-unit flow. Face directions correspond to the explicitly declared logical-to-drawing axes; code variables, indices,normalization,zero and conditional have distinct semantic colors.',
 '13':'Same cube corner changes from mixed diagonal to separate face directions;8positions versus24 attribute records. No geometric separation is falsely implied.',
 '14':'Two votes for top versus one per side are visibly biased; angle-weighted result returns to diagonal, with.408/.816/.408 and90-degree labels.',
 '16':'Independent recap retains memory,attribute identity,complete accumulation and sharp-edge policy before the next lesson normal-transform/UV connection.'
}
assert set(notes)=={x['scene'] for x in samples}
for x in samples:
 assert sha(R/x['path'])==x['sha256']
 x['review']='passed-direct-preview-view'
 x['note']=notes[x['scene']]
 x['previewVideoSha256']=sha(W/f"videos/scene/480p15/Scene{x['scene']}.mp4")
record={
 'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
 'project':slug,'status':'all10-explanation-previews-directly-reviewed',
 'lessonSha256':sha(Path(__file__).with_name('lessons')/f'{slug}.json'),
 'rendererSha256':sha(R/'manim/projects/game-math-part2-full-series/mesh_uv.py'),
 'samples':samples,'explanationScenes':10,
 'narrationTimedFinalRenderReview':'pending-after-measured-narration',
 'voiceDryRun':{'passed':True,'lines':97,'deviceRequested':'cuda:0','gpuAllocated':False},
 'mathAudit':'projects/game-math-mesh-uv/production/math-review.json',
 'originalContentPreservation':'production/batches/game-math-part2-full-series/preflight/mesh-uv-episode-refinement.json',
 'actualFootageReview':'production/batches/game-math-part2-full-series/preflight/mesh-uv-content-duplicate-review.json',
 'humanListening':'pending','publicRights':'pending','publishReady':False
}
(P/'production/pre-tts-lookdev-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Saved direct10-scene preview review; final narrated video QA remains pending.')
