"""Preserve first-pass unapproved attempts without consuming the D render reserve."""
import os
from pathlib import Path
import shutil
from datetime import datetime,timezone
from inventory import ROOT,HERE,read,save,sha
from render_revision import guard,authorized


def main():
    assert read(HERE/'finite-worker.json')['status']=='finite-job-ended-review-pending'
    assert not guard().idle_reason(), 'Preserve active applications and jobs'
    root=(Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingScratch/teaching-sync-superseded').resolve()
    receipt={}
    for episode in read(HERE/'inventory.json')['episodes']:
        eid=episode['id']
        if eid not in ('M24','M25','M26'):continue
        authorized(episode)
        src=(ROOT/'projects'/episode['slug']/'production/local/teaching-sync-v2').resolve()
        output=(ROOT/'output'/(episode['slug']+'-teaching-sync-v2')).resolve()
        dest=(root/eid).resolve()
        assert src.is_relative_to(ROOT.resolve()) and output.is_relative_to(ROOT.resolve())
        assert dest.is_relative_to(root) and dest!=root
        assert not dest.exists(), 'Do not overwrite an earlier archive'
        encoded=read(src/'encoded.json')
        for file in encoded['files'].values():assert sha(Path(file['path']))==file['sha256']
        dest.mkdir(parents=True)
        item=dict(episode=eid,at=datetime.now(timezone.utc).isoformat(),
            sourceProduction=str(src),sourceOutput=str(output),
            archivedProduction=str(dest/'production'),archivedOutput=str(dest/'output'),
            encoded=encoded,baselineTouched=False,humanReviewed=False,
            reason='Reload inspected word-accurate operations and visual corrections. Earlier unapproved files preserved in full.')
        save(dest/'archive-receipt.json',item)
        shutil.move(str(src),str(dest/'production'))
        shutil.move(str(output),str(dest/'output'))
        receipt[eid]=item
        print(eid,'preserved at',dest,flush=True)
    save(HERE/'superseded-attempts.json',receipt)


if __name__=='__main__':main()
