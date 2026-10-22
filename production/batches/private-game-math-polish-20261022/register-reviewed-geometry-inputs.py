"""Reuse inspected explanation clips in the selected partial composition map."""
import datetime,sys
from polish_common import *
for ident in sys.argv[1:]:
 stems={'M09':'geometry','M10':'geometry','M11':'planes','M12':'planes','M17':'projection'}
 assert ident in stems;e=Episode(ident);e.authorized();stem=stems[ident]
 review=read(e.H/(stem+'-legibility-review.json'));render=read(e.H/(stem+'-legibility-render.json'))
 assert review['status']=='passed-source-visual-review' and review['renderManifestSha256']==sha(e.H/(stem+'-legibility-render.json'))
 if 'timelineSha256' in review:assert review['timelineSha256']==sha(e.P/'production/timeline.json')
 composition=read(e.H/'composition-polish.json');preflight=read(e.H/'observed-guide-preflight.json')
 assert preflight['status']=='passed-still-preflight'
 assert composition['globalAssSha256']==preflight['assSha256']==sha(R/composition['globalAss'])
 assert composition['planSha256']==preflight['planSha256']==sha(R/composition['plan'])
 for sid,item in render['scenes'].items():
  assert sha(R/item['path'])==item['sha256']
  assert next(s['classification'] for s in e.T['scenes'] if s['id']==sid)=='explanation'
  e.verify(R/item['path'],next(s['frames'] for s in e.T['scenes'] if s['id']==sid))
  composition['inputs'][sid]={'path':item['path'],'sha256':item['sha256'],'reason':item['reason']}
 composition.update(explanationEvidence={'path':rel(e.H/(stem+'-legibility-review.json')),'sha256':sha(e.H/(stem+'-legibility-review.json'))},
  partialPreflightEvidence={'status':'registered-current-partial-inputs','checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
   'stillReview':rel(e.H/'observed-guide-preflight.json'),'stillReviewSha256':sha(e.H/'observed-guide-preflight.json'),
   'movingReview':rel(e.H/'moving-available-guide-preflight.json'),'movingReviewSha256':sha(e.H/'moving-available-guide-preflight.json'),
   'fullMasterApproval':False})
 save(e.H/'composition-polish.json',composition)
 print(ident,len(render['scenes']),'already reviewed explanation clips registered; no rerender',flush=True)
