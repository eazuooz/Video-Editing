"""Finite sequential source-locked voice/ASR work; no schedule or hidden retries."""
import argparse,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha,resource_guard
WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11')
DEFAULT=['01','02','03','11','12','14','17','18','19','22','23','24','25','26','32']
LOCKS={'01':'01-r2','03':'03-r2','12':'12-r3'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--episodes',nargs='+',default=DEFAULT);p.add_argument('--execute',action='store_true');a=p.parse_args()
    assert len(set(a.episodes))==len(a.episodes) and set(a.episodes)<=set(DEFAULT)
    paths=[HERE/'locked'/f'{LOCKS.get(n,n)}.json' for n in a.episodes]
    identity=dict(episodes=a.episodes,locks={str(f):sha(f) for f in paths},scripts={str(HERE/n):sha(HERE/n) for n in ['voice.py','voice_qa.py','resources.py']})
    fp=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest();dest=WORK/'voice-queue'/fp[:12]
    print(json.dumps(dict(fingerprint=fp,episodes=a.episodes,output=str(dest)),ensure_ascii=False),flush=True)
    if not a.execute:return
    dest.mkdir(parents=True,exist_ok=True);worker=resource_guard().SingleWorker(path=WORK/'finite-voice-queue-worker.json');worker.acquire()
    rows=[]
    try:
        for n,path in zip(a.episodes,paths):
            assert sha(path)==identity['locks'][str(path)]
            for f,d in identity['scripts'].items():assert sha(Path(f))==d
            lock=read(path);root=WORK/'voice'/n/sha(path)[:12];proof=root/'voice-generation-v2.json'
            if not proof.exists():
                command=[sys.executable,'-u','-X','utf8',str(HERE/'voice.py'),'--episode',n,'--lock',str(path),'--execute']
                with (dest/f'{n}-voice.log').open('a',encoding='utf8') as log:
                    print(f'{n}: generating approved voice',flush=True)
                    child=subprocess.Popen(command,cwd=HERE.parents[3],stdout=log,stderr=subprocess.STDOUT)
                    worker.update(child=resource_guard().identity(child.pid));code=child.wait();worker.update(child=None)
                if code or not proof.exists():
                    rows.append(dict(episode=n,state='guard-wait-or-source-job-failed',exitCode=code,log=str(dest/f'{n}-voice.log')));break
            generation=read(proof);assert generation['identity']['planSha256']==sha(path)
            for take in generation['takes'].values():assert sha(root/'approved-voice'/take['file'])==take['sha256']
            pending=[i for i in range(len(lock['narrationKo'])) if not (root/'voice-qa-source'/f'{n}-{i}.json').exists()]
            if pending:
                command=[sys.executable,'-u','-X','utf8',str(HERE/'voice_qa.py'),'--episode',n,'--lock',str(path),'--execute']
                with (dest/f'{n}-asr.log').open('a',encoding='utf8') as log:
                    print(f'{n}: checking {len(pending)} new takes',flush=True)
                    child=subprocess.Popen(command,cwd=HERE.parents[3],stdout=log,stderr=subprocess.STDOUT)
                    worker.update(child=resource_guard().identity(child.pid));code=child.wait();worker.update(child=None)
                pending=[i for i in range(len(lock['narrationKo'])) if not (root/'voice-qa-source'/f'{n}-{i}.json').exists()]
                if code or pending:
                    rows.append(dict(episode=n,state='guard-wait-or-asr-job-failed',exitCode=code,pending=pending));break
            reviews=[read(root/'voice-qa-source'/f'{n}-{i}.json') for i in range(len(lock['narrationKo']))]
            rows.append(dict(episode=n,state='source-generation-and-asr-finished; content-level-context-review-pending',
              proof=str(proof),sha256=sha(proof),similarities=[q['similarity'] for q in reviews],
              finalEpisodeComplete=False))
            save(dest/'progress.json',dict(identity=identity,rows=rows,finished=False,updatedUtc=datetime.now(timezone.utc).isoformat()))
            print(f'{n}: source audio and ASR recorded; final QA remains separate',flush=True)
        save(dest/'progress.json',dict(identity=identity,rows=rows,finished=len(rows)==len(paths) and all('finished;' in r['state'] for r in rows),
          finalEpisodeComplete=False,updatedUtc=datetime.now(timezone.utc).isoformat()))
    finally:worker.close()
if __name__=='__main__':main()
