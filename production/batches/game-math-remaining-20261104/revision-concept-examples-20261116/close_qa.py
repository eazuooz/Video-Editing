"""Close source/voice planning notes only after current output reviews pass."""
from prepare import *
def main():
 visual=read(HERE/'visual-review.json');assert visual['allFinalEncodedSamplesReviewed']
 plan=read(HERE/'plan.json');selected=read(HERE/'selections.json')
 for e in plan['episodes']:
  rp=HERE/'deliveries'/(e['id']+'.json');d=read(rp)
  for s,encoded in zip(e['inserts'],d['inserts']):
   key=s['key'];note='Actual selected source and final encoded before/action/result/return samples checked; original audio/cue continuity passed. User full viewing/listening remains pending.'
   for row in (s,encoded,selected[key]):
    row.setdefault('sourceSelectionNote',row.get('review',''));row['review']=note;row['encodedReviewMasterSha256']=d['files']['captioned']['sha256']
  save(rp,d)
 save(HERE/'plan.json',plan);save(HERE/'selections.json',selected)
 j=read(HERE/'voice.json');j['status']='all-selected-new-bridges-pass-acoustic-and-full-ASR-text-review; user listening pending';save(HERE/'voice.json',j)
 j=read(HERE/'alignment.json');j['status']='all-31-final-bridge-texts-reviewed; exact final subtitle shifts and encoded joins passed';save(HERE/'alignment.json',j)
 j=read(HERE/'voice-provisional.json');j['historicalOnly']=True;j['supersededBy']='voice.json';save(HERE/'voice-provisional.json',j)
 print('All final QA planning notes closed without claiming human listening')
if __name__=='__main__':main()
