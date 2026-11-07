"""Record an already-performed changed-visual sample review, tied to its master."""
from pathlib import Path
import json,sys,hashlib,datetime
H=Path(__file__).resolve().parent; B=H.parent; R=B.parents[2]; L=B/'local/pacing-v3'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
ep=sys.argv[1]; note=sys.argv[2]
row=next(x for x in read(B/'real-clips-v2/review-manifest.json')['records'] if x['id']==ep)
P=R/'projects'/row['slug']; local=P/'production/local/pacing-v3'
m=read(local/'delivery/output'/row['slug']/'delivery-manifest.json')
plan=read(P/'production/pacing-v3/edit-plan.json')
keys=['key','pictureAt','audioAt','sourceSHA256','sourceStartFrame','sourceEndFrame','repeatCount','frames']
signature=lambda events:[{k:e[k] for k in keys} for e in events]
assert signature(m['events'])==signature(plan['events']),'Render plan changed; review the new render instead'
f=next(x for x in m['files'] if x['kind']=='captioned.mp4')
assert hashlib.file_digest((R/f['path']).open('rb'),'sha256').hexdigest()==f['sha256']
q=local/'qa/final-samples.json'; assert q.exists()
samples=read(q); samples.update(modelVisualInspection='sampled-changed-visuals-reviewed',reviewedMasterSha256=f['sha256'],fullPlayback=False)
q.write_text(json.dumps(samples,ensure_ascii=False,indent=2)+'\n','utf-8')
target=L/'visual-review.json'; data=read(target) if target.exists() else {}
data[ep]=dict(status='sampled-changed-visuals-reviewed',masterSha256=f['sha256'],sampleFile=q.relative_to(R).as_posix(),sampleCount=4*len(m['events']),scope='Before, inside, end and following each insertion, temporal contact sheets rendered at 375px width',fullPlayback=False,humanViewed=False,wholeHumanListening=False,notes=note,reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat())
target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(ep,'review tied to',f['sha256'])
