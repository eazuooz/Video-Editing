"""Record observed internal checks without asserting human approval."""
from common import *
import sys

def main(ep,notes,times):
 p=OUTPUT/ep/'delivery.json';d=read(p);assert ep in SCOPE
 assert all(sha(f['path'])==f['sha256'] for f in d['files'])
 qa=WORK/ep/'encoded-qa';captions=read(qa/'caption-presence.json');assert captions['passed']
 posters=read(qa/'posters.json');evidence=[dict(path=r['path'],sha256=sha(r['path'])) for r in posters]
 row=dict(episode=ep,masterSha256=next(f['sha256'] for f in d['files'] if f['kind']=='captioned.mp4'),
  encodedPosters=evidence,browserPlaybackSeconds=times,notes=notes,
  reviewedScope='Encoded overview/recap and all topic contact images; representative moving playback through local player;375px output samples. Full human listening remains pending.',
  automaticCaptionChecks=captions['allCues'],humanReviewed=False,checkedAt=stamp())
 log=read(HERE/'internal-review-log.json');log['encodedEpisodes'][ep]=row;log['updatedAt']=stamp();save(HERE/'internal-review-log.json',log)
 d.update(visualReviewPending=False,internalQa='Passed full decode, FHD60/PTS/AAC, all-caption presence and scoped encoded topic/overview/recap/mobile/motion review.',
  visualInspection=row,humanReviewed=False,fullHumanListening='pending-user-review',updatedAt=stamp());save(p,d)
 plan=read(HERE/'plan.json');item=next(e for e in plan['episodes'] if e['id']==ep);item['status']='local-final-user-review-pending'
 if item.get('queuedVisualEnhancement'):item['queuedVisualEnhancement']['stage']='internally-reviewed'
 save(HERE/'plan.json',plan)
 cp=read(HERE/'checkpoint.json');done=['A06']+list(log['encodedEpisodes']);cp.update(completed=sorted(done),remaining=[k for k in SCOPE if k not in done],updatedAt=stamp());save(HERE/'checkpoint.json',cp)
 print(ep,'internal scoped review recorded; human review pending')
if __name__=='__main__':main(sys.argv[1],sys.argv[2],[float(x) for x in sys.argv[3:]])
