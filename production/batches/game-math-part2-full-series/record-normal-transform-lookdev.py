"""Record the actually inspected51 preview states; final narrated QA is pending."""
from pathlib import Path
import hashlib,json,datetime
R=Path(__file__).resolve().parents[3];slug='game-math-normal-transform-uv';P=R/f'projects/{slug}';B=Path(__file__).parent;W=R/f'shared/output/{slug}/lookdev'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
d=read(B/f'lessons/{slug}.json')
d['sourceDependencies']=[p for p in d['sourceDependencies'] if p!='motion-canvas/src/styles/research-dark.ts']
write(B/f'lessons/{slug}.json',d)
samples=read(W/'inspection/generated-samples.json')
notes={
 '01':'Four ordered overview states: wrong versus perpendicular transformed normals, original numbered UV image and repeated lookup. Actual projected thickness and semantic color contrast directly viewed.',
 '02':'Column-vector cancellation, old normal explicitly labeled before transformation, correct right-angle marker only on zero dot. Invertibility, positive scales and reflection/winding limitations retained.',
 '03':'Seven states independently match dot0, changed tangent, naive dot3, still-wrong normalized vector, inverse-transpose dot0 and(.447,.894). No length correction is mistaken for a direction correction.',
 '06':'Dark top/front/side plate faces and asymmetric original image. Explicit v-down corner pins now outside the artwork; texel/pixel and mapping/perspective prerequisites are legible.',
 '07':'Same plate positions with whole image, visibly enlarged central cross and omitted outside numbers, UV rotation and1-u flip. Corner pins follow exact mapped coordinates without overlapping pattern numerals.',
 '10':'Repeat, floor/trunc negative example, clamp and mirror differ visibly. Clamp retains numbers only inside original image region, with actual edge continuation outside; no repeated-label error remains.',
 '11':'Unmodified0→2 span retains repetitions; wrapping u endpoints first produces a single edge sample. Original v interpolation is retained. Perspective-correct interpolation stays a separate prerequisite.',
 '13':'Independent spatial record blocks, cube corner directions, normalized perpendicular vector and original UV plate recap.140B and three data roles are preserved before the next lighting lesson.'}
assert set(notes)=={x['scene'] for x in samples} and sum(len(x['sampleTimes']) for x in samples)==51
for x in samples:
 assert sha(R/x['path'])==x['sha256']
 assert sha(W/f'videos/scene/480p15/Scene{x["scene"]}.mp4')==x['previewVideoSha256']
 x.update(review='passed-direct-preview-view',note=notes[x['scene']])
record=dict(schemaVersion=1,reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),project=slug,status='all8-explanation-previews-directly-reviewed',lessonSha256=sha(B/f'lessons/{slug}.json'),rendererSha256=sha(R/'manim/projects/game-math-part2-full-series/normal_transform_uv.py'),samples=samples,explanationScenes=8,previewBeatStates=51,style='research-black-v1',palette=read(R/'shared/publishing/explanation-style-policy.json')['palette'],visualGeometry='Projected actual top/front/side faces, correct tangent-normal changes, preserved geometry with meaningful UV motion/comparison; no flat card substitute',voiceDryRun=dict(passed=True,lines=81,deviceRequested='cuda:0',gpuAllocated=False),mathAudit=f'projects/{slug}/production/math-review.json',narrationTimedFinalRenderReview='pending-after-measured-narration',humanListening='pending',publicRights='pending',publishReady=False)
write(P/'production/pre-tts-lookdev-review.json',record)
q=read(B/'queue.json');item=next(x for x in q['items'] if x['slug']==slug)
item.update(preflightComplete=True,status='reviewed-script-and-dark-spatial-previews-awaiting-safe-GPU-TTS',checkpoint='Full51-project and actual current Studio overlap reviewed;81matched bilingual paragraphs;8dark projected explanation previews/51states directly inspected; no BGM, unchanged narrator, fresh nonoverlapping existing-game intervals. Final narration/render/QA/private delivery pending.')
write(B/'queue.json',q)
print(json.dumps(dict(reviewedScenes=8,reviewedBeatStates=51,finalNarratedQa='pending')))
