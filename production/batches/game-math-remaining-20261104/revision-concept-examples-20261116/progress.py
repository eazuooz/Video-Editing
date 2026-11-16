"""Snapshot this finite local batch, without creating an automation."""
import datetime
from prepare import *
from review import pages,OUT
def main():
 plan=read(HERE/'plan.json');done=[]
 for e in plan['episodes']:
  rp=HERE/'deliveries'/(e['id']+'.json')
  if rp.exists():done.append(e['id'])
 v=read(HERE/'visual-review.json');c=read(HERE/'continuity.json')
 state=dict(scope=[e['id'] for e in plan['episodes']],status='local-render-and-encoded-review-in-progress',encodedCount=len(done),encoded=done,visualSampleQaCount=len(v['episodes']),technicalSignalQaCount=len(c['episodes']),newExamples=sum(len(e['inserts']) for e in plan['episodes']),retainedAppropriateFollowingCases=5,reviewHub=str(OUT/'index.html'),originalExplanationsAndPacePreserved=True,upload=False,humanReviewed=False,at=datetime.datetime.now().astimezone().isoformat())
 save(HERE/'checkpoint.json',state);pages();print(state)
if __name__=='__main__':main()
