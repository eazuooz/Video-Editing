"""Record the operator's completed encoded-frame inspection, never human approval."""
import argparse
from prepare import WORK,OUTPUT,read,save
from finish_episode import sha

def main(ep,stage,note):
    if stage=='body':
        path=WORK/ep/'native-picture-review.json';v=read(path)
        samples_path=WORK/ep/'encoded-native-review/samples.json';samples=read(samples_path)
        assert v['fullDecode']=='passed'
        assert samples['captionedBodySha256']==v['pictures']['captioned.mp4']['sha256']
        v.update(visualReviewPassed=True,status='encoded-native-body-sampled-visual-pass',
                 visualInspection={'scope':note,'samples':str(samples_path),'humanReviewed':False})
        samples['visualReviewPending']=False;save(samples_path,samples)
    else:
        path=OUTPUT/ep/'delivery.json';v=read(path)
        samples_path=WORK/ep/'encoded-final-check/evidence.json';samples=read(samples_path)
        assert samples['captionedMasterSha256']==next(r['sha256'] for r in v['files'] if r['kind']=='captioned.mp4')
        assert samples['encodedSummaryAudioSimilarity']>.97
        contact=WORK/ep/'encoded-final-check/summary-contact.jpg'
        v.update(visualReviewPending=False,encodedSampleReview={'scope':note,'contactSha256':sha(contact),'humanReviewed':False})
        samples.update(visualReviewPending=False,inspection=note);save(samples_path,samples)
    assert not v['humanReviewed'];save(path,v)
    print(ep,stage,'sample inspection recorded; human final viewing remains pending.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('episode');p.add_argument('stage',choices=['body','final']);p.add_argument('--note',required=True)
    a=p.parse_args();main(a.episode,a.stage,a.note)
