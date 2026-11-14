"""Restore original AAC preroll without re-encoding a single picture or sample."""
import argparse
from datetime import datetime,timezone
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

from inventory import ROOT,HERE,read,save,sha
from render_revision import FF,CREATE,authorized,guard,check_stream
from inspect_audio_packets import run as inspect_packets
from verify import audio_hash


def video_hash(path):
    return subprocess.check_output([str(FF),'-v','error','-nostdin','-threads','1','-i',str(path),
        '-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-'],creationflags=CREATE).decode().strip()


def main(eid):
    state=read(HERE/'finite-worker.json');assert state['status']=='finite-job-ended-review-pending'
    episode=next(e for e in read(HERE/'inventory.json')['episodes'] if e['id']==eid);authorized(episode)
    folder=ROOT/'projects'/episode['slug']/'production/local/teaching-sync-v2'
    record=read(folder/'encoded.json');assert not record['addedGameAudioIntervals']
    assert 'Unchanged voice/game mix' in read(folder/'qa-failure.json')['error']
    diagnosis=inspect_packets(eid);assert diagnosis['leadingPacketOffset']==1, diagnosis
    G=guard();assert not G.idle_reason(), 'Preserve active applications and encoders'
    token=str(uuid.uuid4())
    with G.LEASE.open('x',encoding='utf8') as f:__import__('json').dump(dict(id=token,pid=os.getpid(),owner=episode['slug']+'-original-AAC-remux',createdAt=G.now()),f)
    archive_root=(Path(os.environ['LOCALAPPDATA'])/'YamyamCoding/VideoEditingScratch/teaching-sync-superseded').resolve()
    archive=(archive_root/(eid+'-before-AAC-preroll-restoration')).resolve()
    assert archive.is_relative_to(archive_root) and archive!=archive_root and not archive.exists()
    archive.mkdir(parents=True)
    old_record=record.copy();proof=[]
    try:
        original=Path(episode['baselineOutputs']['clean'])
        original_audio=audio_hash(original)
        for kind in ('clean','captioned'):
            path=Path(record['files'][kind]['path']).resolve()
            assert path.is_relative_to((ROOT/'output').resolve()) and sha(path)==record['files'][kind]['sha256']
            temp=(archive/(kind+'.restored.mp4')).resolve();previous=(archive/(kind+'.before.mp4')).resolve()
            assert temp.is_relative_to(archive) and previous.is_relative_to(archive)
            subprocess.run([str(FF),'-hide_banner','-nostdin','-v','error','-n','-threads','1','-i',str(path),'-i',str(original),
                '-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',str(temp)],check=True,creationflags=CREATE)
            check_stream(temp,record['frames'])
            before_video=video_hash(path);after_video=video_hash(temp)
            assert before_video==after_video and audio_hash(temp)==original_audio
            item=dict(kind=kind,previousSha256=sha(path),restoredSha256=sha(temp),videoBitstreamHash=before_video,
                audioBitstreamHash=original_audio,originalVideoFramesPreserved=record['frames'])
            shutil.move(str(path),str(previous));shutil.move(str(temp),str(path))
            record['files'][kind]['sha256']=sha(path);proof.append(item)
        evidence=dict(status='pass',episode=eid,at=datetime.now(timezone.utc).isoformat(),
            diagnosis=diagnosis,operations=proof,archive=str(archive),
            sourceAudio=str(original),reencodedVideo=False,reencodedAudio=False,humanReviewed=False)
        save(archive/'archive-receipt.json',dict(oldEncoded=old_record,restoration=evidence))
        save(folder/'audio-restoration.json',evidence)
        record['audioRestoration']=str(folder/'audio-restoration.json');save(folder/'encoded.json',record)
        failed=read(folder/'qa-failure.json');failed.update(status='resolved',resolution='audio-restoration.json')
        save(folder/'qa-failure.json',failed)
    finally:G.release_lease(token)
    subprocess.run([sys.executable,'-X','utf8',str(HERE/'verify.py'),eid,'--pictures'],cwd=ROOT,check=True,creationflags=CREATE)
    subprocess.run([sys.executable,'-X','utf8',str(HERE/'newmix.py'),eid],cwd=ROOT,check=True,creationflags=CREATE)
    state=read(HERE/'finite-worker.json');assert state['status']=='finite-job-ended-review-pending'
    failures=[r for r in state['failures'] if r['episode']==eid]
    state['failures']=[r for r in state['failures'] if r['episode']!=eid]
    state.setdefault('resolvedFailures',[]).extend([dict(**r,resolution=str(folder/'audio-restoration.json')) for r in failures])
    if eid not in state['completed']:state['completed'].append(eid)
    save(HERE/'finite-worker.json',state)
    print(eid,'original audio packets restored exactly; same video bitstream; final picture review pending',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('episodes',nargs='+')
    for eid in parser.parse_args().episodes:main(eid)
