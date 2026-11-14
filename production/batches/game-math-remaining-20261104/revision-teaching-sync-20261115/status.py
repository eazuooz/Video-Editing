"""Compact live status from the actual child encoder, not estimated completion."""
import json
import re
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


if __name__=='__main__':print(json.dumps(snapshot(),ensure_ascii=False))
