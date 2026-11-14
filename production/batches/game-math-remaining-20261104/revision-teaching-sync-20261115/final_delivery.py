"""Cross-check the exact thirteen local deliveries after actual picture review."""
from datetime import datetime,timezone
from pathlib import Path
from inventory import ROOT,HERE,read,save,sha
import progress


def main():
    state=progress.update()
    assert state['readyCount']==13, 'Never turn partial encoding into batch completion'
    assert read(HERE/'authoring-validation.json')['status']=='pass'
    maths=read(HERE/'mathematical-qa.json');assert maths['status']=='pass'
    assert maths['formulaAuthoringSha256']==sha(HERE/'workings.py')
    assert maths['motionAuthoringSha256']==sha(HERE/'motion_panels.py')
    rows=[]
    for episode in read(HERE/'inventory.json')['episodes']:
        folder=ROOT/'projects'/episode['slug']/'production/local/teaching-sync-v2'
        encoded=read(folder/'encoded.json');technical=read(folder/'technical-qa.json')
        visual=read(folder/'visual-review.json');mix=read(folder/'mix-review.json')
        assert technical['status']==visual['status']=='pass'
        assert mix['status'] in ('pass','reused')
        assert visual['captionedSha256']==encoded['files']['captioned']['sha256']
        for kind,record in encoded['files'].items():
            assert sha(Path(record['path']))==record['sha256']
            assert technical['files'][kind]['sha256']==record['sha256']
        assert not encoded['humanReviewed'] and not visual['actualHumanViewing'] and not visual['actualHumanListening']
        rows.append(dict(id=episode['id'],files=encoded['files'],frames=encoded['frames'],
            durationSeconds=encoded['duration'],resolution=[1920,1080],fps=60,
            localReviewIndex=(Path(encoded['files']['captioned']['path']).parent/'index.html').as_posix(),
            technicalEvidence=dict(path=str(folder/'technical-qa.json'),sha256=sha(folder/'technical-qa.json')),
            visualEvidence=dict(path=str(folder/'visual-review.json'),sha256=sha(folder/'visual-review.json')),
            audioEvidence=dict(path=str(folder/'mix-review.json'),sha256=sha(folder/'mix-review.json')),
            inspected375pxSheetCount=len(visual['inspectedMobileSheets']),
            inspectedFull1080FrameCount=len(visual['inspectedFull1080Frames']),
            narrationTempo=1,humanReviewed=False))
    report=dict(status='all-thirteen-local-user-review-pending',at=datetime.now(timezone.utc).isoformat(),
        episodes=rows,outputFileCount=sum(len(r['files']) for r in rows),
        addedBackgroundMusic=False,uploaded=False,scheduled=False,deleted=False,automation=False,
        limitations='Internal changed-frame, native-motion samples, whole-stream decode/PTS, formula and audio evidence checks. No actual human full viewing/listening or continuous realtime-playback approval is claimed.')
    save(HERE/'delivery.json',report)
    assert report['outputFileCount']==52
    print('13 complete local review deliveries / 52 verified files; user review and platform work remain separate.')


if __name__=='__main__':main()
