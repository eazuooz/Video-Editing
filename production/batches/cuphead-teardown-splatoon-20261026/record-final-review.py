"""Record verified local outputs after root actually inspects the sampled frames."""
from pathlib import Path
import argparse,sys,json,datetime,hashlib
B=Path(__file__).resolve().parent;R=B.parents[2]
ap=argparse.ArgumentParser();ap.add_argument('slug');ap.add_argument('--samples-reviewed',action='store_true');args=ap.parse_args()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert args.samples_reviewed,'Do not infer actual pixel review from successful encoding.'
batch=read(B/'batch.json');assert args.slug in [p['slug'] for p in batch['projects']]
P=R/'projects'/args.slug;sys.path.insert(0,str(P/'production'));import audio_revision as a
a.guard();project=read(P/'project.json');F=P/project.get('currentFinalDirectory','production/local/final-reviewed')
integrity=read(F/'integrity.json');assert integrity['status']=='pass'
captions=read(P/'script/captions.json');timing=read(P/'production/visual-timing.json')
outputs={}
for name in batch['output']['files']:
    p=F/name;outputs[name]=dict(path=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size)
for row in integrity['outputs']:
    assert outputs[row['name']+'.mp4']['sha256']==row['sha256']
qa=F/('qa-sequential-'+outputs['captioned.mp4']['sha256'][:12]);index=read(qa/'index.json')
assert index['masterSha256']==outputs['captioned.mp4']['sha256']
assert list(qa.glob('sheet-*.jpg'))
asrs=[dict(path=str(p.resolve()),sha256=sha(p),similarity=read(p).get('similarity'),normalizedMatch=read(p).get('normalizedMatch')) for p in a.L.glob('asr-*.json') if read(p).get('fullInput')]
assert any(read(Path(r['path'])).get('role')=='mix' for r in asrs),'Complete final mix ASR is required.'
audio=read(a.L/'audio-continuity.json')
assert not audio['sustainedEncodedAttenuationCandidates'] and not audio['sustainedMaskingCandidates'],'Resolve encoded attenuation/masking before delivery.'
d=dict(revision=a.REVISION,status='local-final-review-pending',outputDirectory=str(F.resolve()),outputs=outputs,width=1080,height=1920,fps=60,
       seconds=captions['durationSeconds'],actualGameSeconds=sum(s['end']-s['start'] for s in timing['nativeSegments']),sourcePlaybackRate=1,
       observedQa=['Full clean/captioned decode, exact60fps frame timing and identicalAAC streams','All caption midpoint, join and motion-state contact sheets actually inspected at mobile scale',
                   'Actual source/Unity captures and tracked target pixels reviewed; technical illustrations distinguished from commercial implementation'],
       asrEvidence=asrs,captionAlignmentEvidence=str((a.L/'caption-alignment.json').resolve()),audioContinuityEvidence=str((a.L/'audio-continuity.json').resolve()),
       notClaimed=['Full human listening','Continuous real-time moving playback','Actual human approval'],music='Pixel Peeker Polka - faster; CC BY4 credit included',humanReview='pending-not-yet-delivered',publishing='not-authorized')
save(P/'production/local-review.json',d)
project.update(status=d['status'],publishReady=False);save(P/'project.json',project)
cp=read(P/'production/checkpoint.json');cp.update(updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status=d['status'],localReview='production/local-review.json',captionedSha256=outputs['captioned.mp4']['sha256'],humanReview=d['humanReview'],notCompleted=d['notClaimed'],next=['Deliver exact local outputs for human final review.'])
save(P/'production/checkpoint.json',cp)
ledger=read(P/'production/review-ledger.json');ledger.setdefault('entries',[]).append(dict(id='actual-local-final-'+outputs['captioned.mp4']['sha256'][:12],status='technical-and-sampled-visual-pass; full-listening/moving-review-pending',evidence='production/local-review.json',captionedSha256=outputs['captioned.mp4']['sha256']))
ledger.update(actualUserReview=False,pending=d['notClaimed']);save(P/'production/review-ledger.json',ledger)
print(json.dumps(dict(slug=args.slug,seconds=d['seconds'],captioned=outputs['captioned.mp4']),ensure_ascii=False))
