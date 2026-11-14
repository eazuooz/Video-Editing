"""Record only images actually inspected by the caller, never automatic approval.

Do not call this merely because verify.py created images. View every supplied
board and each claimed full-size frame, assess content/timing/caption clearance,
and author the findings in visual-notes.json before recording a pass.
"""
import argparse
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from PIL import Image
from inventory import ROOT,HERE,read,save,sha
import progress


def main(eid,boards,full):
    e=next(e for e in read(HERE/'inventory.json')['episodes'] if e['id']==eid)
    folder=ROOT/'projects'/e['slug']/'production/local/teaching-sync-v2'
    encoded=read(folder/'encoded.json');pictures=read(folder/'picture-review.json')
    assert pictures['captionedSha256']==encoded['files']['captioned']['sha256']
    assert sorted(boards)==list(range(1,len(pictures['mobileBoards'])+1)), 'Inspect every changed board'
    note=read(HERE/'visual-notes.json')[eid]
    assert len(note['findings'])>=3 and not note['actualHumanViewing'] and not note['actualHumanListening']
    selected=[]
    for f in full:
        item=next(r for r in pictures['frames'] if r['frame']==f)
        assert sha(Path(item['png']))==item['sha256'];selected.append(item)
    assert selected, 'View representative full-size output, too'
    sheets=[dict(path=pictures['mobileBoards'][n-1],sha256=sha(Path(pictures['mobileBoards'][n-1]))) for n in boards]
    game_changes=[]
    for sid in sorted(set(r['scene'] for r in pictures['frames'] if r['role']=='paired-game')):
        rows=[r for r in pictures['frames'] if r['scene']==sid and r['role']=='paired-game']
        changes=[]
        for a,b in zip(rows,rows[1:]):
            if b['time']-a['time']<.5:continue
            with Image.open(a['png']) as first,Image.open(b['png']) as second:
                x=np.asarray(first.crop((70,325,920,803)),dtype=float)
                y=np.asarray(second.crop((70,325,920,803)),dtype=float)
                changes.append(dict(start=a['time'],end=b['time'],meanAbsoluteRgbDifference=float(np.mean(np.abs(x-y)))))
        game_changes.append(dict(scene=sid,sampledPictureChanges=changes,scope='Decoded game viewport motion evidence, not game-world measurement'))
    assert read(folder/'technical-qa.json')['status']=='pass'
    review=dict(status='pass',episode=eid,at=datetime.now(timezone.utc).isoformat(),
        captionedSha256=encoded['files']['captioned']['sha256'],
        inspectedMobileSheets=sheets,allChangedMobileFrames=len(pictures['frames']),
        inspectedFull1080Frames=selected,gameMotionSamples=game_changes,**note)
    save(folder/'visual-review.json',review)
    p=HERE/'pending-encoded-corrections.json';pending=read(p)
    if eid in pending['episodes']:
        assert eid not in ('M24','M26') or pending['episodes'][eid]['status']=='resolved', 'Complete the recorded picture correction first'
        pending['episodes'][eid].update(status='resolved',actualEncodedPictureReview='pass',
            newCaptionedSha256=encoded['files']['captioned']['sha256'])
        save(p,pending)
    progress.update();print(eid,'changed picture review recorded; human review remains pending')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('episode');parser.add_argument('--boards',type=int,nargs='+',required=True)
    parser.add_argument('--full-frames',type=int,nargs='+',required=True);a=parser.parse_args();main(a.episode,a.boards,a.full_frames)
