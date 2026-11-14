"""Produce only the eleven selected native-body revisions, one costly job at a time."""
import time

from prepare import HERE,ROOT,WORK,read,save
from finish_episode import sha
from native_visuals import REPAIR
from run_selected_queue import run

SOURCES=('native_visuals.py','native_specials.py','render_replacements.py','assemble_native_body.py','narration-patches.json')


def main():
    deadline=time.monotonic()+3600
    review=WORK/'configuration-review.json'
    while time.monotonic()<deadline:
        if review.exists() and read(review).get('configurationReviewed'):break
        time.sleep(3)
    else:raise TimeoutError('Internal source/caption preflight pending; do not produce unreviewed staging.')
    accepted=read(review)
    complete=[]
    for ep in REPAIR:
        control=read(ROOT/'shared/publishing/video-production-control.json')['animationNativeClipsRevision20261114']
        assert control['renderAuthorized'] and ep in control['episodes'] and ep not in control['excludedUploaded']
        assert all(sha(HERE/name)==accepted['sourceHashes'][name] for name in SOURCES), 'Configuration changed: inspect its updated samples before continuing.'
        assert sha(WORK/'game-banks/manifest.json')==accepted['gameBanksSha256']
        path=WORK/ep/'native-picture-review.json'
        ready=path.exists() and read(path).get('configurationSignature')==accepted['signature']
        if not ready:
            run('render_replacements.py',ep)
            run('assemble_native_body.py',ep)
            value=read(path);value['configurationSignature']=accepted['signature'];save(path,value)
            run('sample_native_body.py',ep)
        complete.append(ep)
        save(WORK/'body-queue-status.json',{'selectedEpisodes':list(REPAIR),'encodedBodiesReady':complete,
             'stage':'encoded-bodies-awaiting-internal-visual-inspection','humanReviewed':False})
        print(ep,'native body ready;',len(complete),'of',len(REPAIR),flush=True)
    print('All eleven revised bodies prepared. Final delivery waits for their encoded visual inspection.',flush=True)


if __name__=='__main__':main()
