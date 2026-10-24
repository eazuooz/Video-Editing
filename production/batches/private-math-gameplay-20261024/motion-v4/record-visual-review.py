"""Record only explicitly inspected final frames; never infer human approval."""
from pathlib import Path
import json,hashlib,sys
from datetime import datetime
R=Path(__file__).resolve().parents[4];V=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for ep in sys.argv[1:]:
 p=read(V/(ep+'-plan.json'));H=R/'projects'/p['slug']/'production'/p['revision']
 out=read(H/'outputs.json');qa=read(H/'technical-qa.json')
 assert out['planSha256']==sha(V/(ep+'-plan.json'))
 assert {x['path']:x['sha256'] for x in out['outputs']}=={x['path']:x['sha256'] for x in qa['checks']}
 f=R/'shared/output/private-math-gameplay-20261024/motion-v4/final-review'/ep/'frames.json';frames=read(f)
 master=next(x for x in out['outputs'] if x['path'].endswith('.captioned.mp4'))
 assert master['sha256']==frames['masterSha256']
 evidence=dict(checkedAt=datetime.now().astimezone().isoformat(),episode=p['episode'],master=master['path'],masterSha256=master['sha256'],planSha256=out['planSha256'],scope='Agent inspected decoded final start/action/result/return frames for every changed insert, plus 375px mobile contact sheet; source action reviewed as ordered decoded frames.',frames=f.relative_to(R).as_posix(),sourceActionReview=p.get('sourceReview'),nativeSpeed=1,freezePaddingSeconds=0,explanationsPreserved=True,narrationPcmUnchanged=qa['exactNarrationPcmPreserved'],nativeContinuousPlayback=False,wholeAudioListening=False,humanReview='pending',limits=['Frame inspection is not continuous full-video viewing or full-audio listening.','Game imagery is observable evidence; exact hidden quantities are only in the labeled explanation model.'],status='changed-frames-checked-local-human-review-pending')
 if p.get('blockers'):
  evidence.update(status='changed-inserts-checked-source-blocker-remains',blockers=p['blockers'])
 (H/'visual-review.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(ep,'recorded inspected final frames',flush=True)
