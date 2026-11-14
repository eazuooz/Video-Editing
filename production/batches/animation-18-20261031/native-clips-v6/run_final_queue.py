"""Finish the eleven bodies only after their encoded visual inspection, serially."""
import time
from prepare import ROOT,WORK,OUTPUT,read,save
from native_visuals import REPAIR
from run_selected_queue import run

def main():
    deadline=time.monotonic()+18000
    while time.monotonic()<deadline:
        status=WORK/'body-queue-status.json'
        all_bodies=status.exists() and set(read(status).get('encodedBodiesReady',[]))==set(REPAIR)
        inspected=all((WORK/ep/'native-picture-review.json').exists() and
                      read(WORK/ep/'native-picture-review.json').get('visualReviewPassed') for ep in REPAIR)
        if all_bodies and inspected:break
        time.sleep(4)
    else:raise TimeoutError('Encoded body inspections remain; no unreviewed final assembly.')
    done=[]
    for ep in REPAIR:
        control=read(ROOT/'shared/publishing/video-production-control.json')['animationNativeClipsRevision20261114']
        assert control['renderAuthorized'] and ep in control['episodes'] and ep not in control['excludedUploaded']
        receipt=OUTPUT/ep/'delivery.json'
        current=read(WORK/ep/'native-picture-review.json')
        existing=read(receipt) if receipt.exists() else {}
        current_pictures={k:v['sha256'] for k,v in current['pictures'].items()}
        identity={k:v['sha256'] for k,v in existing.get('bodyPictures',{}).items()}
        if identity!=current_pictures:run('assemble_delivery.py',ep)
        run('sample_final_outputs.py',ep)
        done.append(ep)
        save(WORK/'final-queue-status.json',{'encodedFinalsReady':done,'stage':'final-summary-contact-inspection-pending','humanReviewed':False})
        print(ep,'final four files encoded and checked;',len(done),'of',len(REPAIR),flush=True)

if __name__=='__main__':main()
