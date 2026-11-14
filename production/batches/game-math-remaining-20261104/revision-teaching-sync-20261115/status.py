"""Compact live status from the actual child encoder, not estimated completion."""
import json
import re
import time
import argparse
import psutil
from inventory import ROOT,HERE,read


def snapshot():
    job=read(HERE/'finite-worker.json');eid=job.get('current')
    result={k:job.get(k) for k in ('status','current','stage','completed','failures')}
    result['failures']=[dict(episode=r['episode'],state='Repair queued; not review-ready') for r in job.get('failures',[])]
    if eid:
        e=next(e for e in read(HERE/'inventory.json')['episodes'] if e['id']==eid)
        folder=ROOT/'projects'/e['slug']/'production/local/teaching-sync-v2'
        if (folder/'worker.json').exists():
            child=read(folder/'worker.json');result['encoder']=child['status']
            name='captioned.log' if child['status']=='rendering-captioned' else e['slug']+'.clean.log'
            log=folder/name
            if log.exists():
                rows=re.findall(r'frame=\s*(\d+)',log.read_text(encoding='utf8',errors='replace')[-5000:])
                if rows:result['encodedVideoSeconds']=round(int(rows[-1])/60,1)
        result['totalVideoSeconds']=round(e['scenes'][-1]['end']+10,1)
        result['picturesReady']=(folder/'picture-review.json').exists()
    return result


def watch():
    """Read-only monitor of this current job; never resumes or starts a stage."""
    while True:
        corrections=read(HERE/'pending-encoded-corrections.json')['episodes']
        for e in read(HERE/'inventory.json')['episodes']:
            folder=ROOT/'projects'/e['slug']/'production/local/teaching-sync-v2'
            if not all((folder/name).exists() for name in ('encoded.json','picture-review.json','technical-qa.json')):continue
            if e['id'] in ('M21','M22','M23','M24','M26') and corrections.get(e['id'],{}).get('status')!='resolved':continue
            encoded=read(folder/'encoded.json');pictures=read(folder/'picture-review.json')
            visual=read(folder/'visual-review.json') if (folder/'visual-review.json').exists() else {}
            digest=encoded['files']['captioned']['sha256']
            if pictures['captionedSha256']==digest and visual.get('captionedSha256')!=digest:
                print(e['id'],'new complete encoded pictures ready for direct inspection',flush=True);return
        lease=ROOT/'shared/output/GPU_HANDOFF.json'
        active=read(lease) if lease.exists() else {}
        if active.get('pid') and psutil.pid_exists(active['pid']):
            print('진행 중:',active.get('owner'),flush=True)
        else:
            print('현재 작업의 다음 단계·검수 자료 확인 중',flush=True)
        time.sleep(45)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--until-pictures',action='store_true');a=p.parse_args()
    if a.until_pictures:watch()
    else:print(json.dumps(snapshot(),ensure_ascii=False))
