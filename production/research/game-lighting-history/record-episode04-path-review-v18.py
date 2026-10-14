"""Seal directly read path-chapter samples; leave continuous/final gates pending."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

ROOT = Path(__file__).resolve().parents[3]
P = ROOT/'projects/game-lighting-history-04/production'
read = lambda p: json.loads(p.read_text('utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rel = lambda p: p.relative_to(ROOT).as_posix()
stamp = lambda: datetime.now(timezone.utc).isoformat()
proof = lambda p: {'path':rel(p),'sha256':sha(p)}
EP = ROOT/'production/research/game-lighting-history/local/episode04-path-encoded-v18/execution.json'
RP = P/'path-encoded-direct-review-v18.json'
assert not RP.exists(), 'Preserve earlier review'
e = read(EP)
assert e['status']=='encoded-samples-ready'
assert len(e['items'])==318 and len(e['boards'])==80
assert len(e['commands'])==2 and all(c['exitCode']==0 for c in e['commands'])
s = read(EP.with_name('session.json'))
assert s['closed'] and s['exitCode']==0 and s['unifiedExecExitObserved']
boards=[]; items=[]
for b in e['boards']:
    assert sha(ROOT/b['path'])==b['sha256']
    boards.append({**b,'directlyViewed':True,'reviewedAt':stamp()})
for i in e['items']:
    assert sha(ROOT/i['path'])==i['sha256']
    items.append({**i,'directlyViewedOnBoard':True})
assert sum(b['source']=='clean' for b in boards)==14
assert sum(b['source']=='captioned' for b in boards)==66
assert sum(i['source']=='clean' for i in items)==55
assert sum(i['source']=='captioned' for i in items)==263
gates={k:False for k in ['allFinalPixelsReviewed','allMovingPixelsReviewed',
    'causalFlowApproved','finalMixedAsrApproved','wholeEpisode60to40Approved',
    'qaApproved','collected','uploaded']}
r={'reviewedAt':stamp(),
 'scope':'Path tracing chapter encoded sample review only; continuous playback and final episode approval pending',
 'plan':proof(P/'path-chapter-review-plan-v18.json'),
 'build':proof(P/'path-chapter-review-build-v18.json'),
 'execution':proof(EP),'session':proof(EP.with_name('session.json')),
 'boards':boards,'items':items,'all318SamplesDirectlyRead':True,'all80BoardsDirectlyRead':True,
 'cleanImages':55,'captionedImages':263,'captionCuesReviewed':list(range(124,169)),
 'sampledCaptionClearanceApproved':True,'sourceConditionLabelApproved':True,
 'findings':[
  'Clean001-014 and captioned001-066 directly read across the continued task. All45 cue boundary/middle samples,14 cut samples and the2 native source intervals reviewed; sampled caption, formula, footer and source-label clearance is good.',
  'Native8-12s interior/pyramid/neon montage and16-28.96s wet floor/red building comparison retain RTX feature tags. Cue131 right caption edge remains left of the bottom-right RTX tag. Title card13-15s excluded by the source cut; no presenter, desktop or FPS claim in sampled native points.',
  '2023 Overdrive tech preview conditions lead to camera/first surface/BSDF direction/next hit arrows. A sampled path is distinct from the complete lighting integral.',
  'Directional contribution f divided by sampling probability p is qualified. Independent two-direction f=(1,4),p=(0.5,0.5) gives values2/8 and mean5; p=(0.2,0.8) gives5/5. Prerequisite example separately uses target weights0.5 and proposal0.2/0.8; corrected contributions2*0.5/0.2=5 and8*0.5/0.8=5. Both5 is a special example, not a general reconstruction claim or sum10.',
  'Light/BSDF strategies refer to the same geometry. The equal-count balance example pA0.8,pB0.2 yields weights0.8,0.2 with sum1; repeated diagram geometry does not denote separate physical scenes.',
  'Survival probability0.8 gives surviving contribution1/0.8=1.25 and stopped contribution0. Expected value0.8*1.25+0.2*0=1 is preserved. This does not delete exactly one in every five paths, and individual variance can increase. Fixed-bounce truncation and other approximations may still bias the final implementation.',
  'Independent-sample relative error1/sqrt(N) compares N1/error1 with N4/error0.5. Temporal correlation/reconstruction qualifiers are retained. Allocation, reuse and final reconstruction appear as separate projected blocks with narration-timed arrows.',
  'Black background, white text, restrained yellow/teal/orange and projected top/front/side faces preserved. Bottom-centered960,970 white boxed forest-shadow captions stay48px,max2lines. Original0.72s silence and PCM preserved; chapter is an interim sample review, not a final body60:40 allocation.'
 ],**gates,'newTts':0,'sourceModelsRerendered':0,'newGitImages':0,
 'humanWholeListening':'pending','normalSpeedContinuousPlayback':'pending',
 'next':'Review reconstruction source conditions and prepare the denoising chapter using original8 KO/EN paragraphs and PCM.'}
RP.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
CP=ROOT/'production/research/game-lighting-history/checkpoint.json'
cp=read(CP)
cp['episode04PathEncodedDirectReviewV18']={'path':rel(RP),'sha256':sha(RP),
 'samples':318,'boards':80,'captionCues':45,
 'sampledCaptionClearanceApproved':True,'sourceConditionLabelApproved':True,**gates}
cp['ownedActiveWork']={'status':'no-active-owned-media-worker','next':r['next']}
cp['updatedAt']=stamp()
tmp=CP.with_suffix('.path-review-v18.tmp')
tmp.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n','utf-8');tmp.replace(CP)
print(json.dumps({'path':rel(RP),'sha256':sha(RP),'samples':318,'boards':80,'finalApproved':False}))
