"""One cooperative GPU lease for all remaining reviewed episode narration.

No CUDA allocation until reviewed batch inputs exist. Research restoration is
owned by gpu-handoff.py even if preparation or any child fails.
"""
from pathlib import Path
import hashlib, json, os, subprocess, sys, time
import psutil

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT/'production/research/game-lighting-history'
LEASE = ROOT/'shared/output/GPU_HANDOFF.json'
READY = BASE/'remaining-tts-input-review-v1.json'
STATE = BASE/'remaining-tts-execution-v1.json'
SLUGS = ['game-lighting-history-02', 'game-lighting-history-03', 'game-lighting-history-04']

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, obj):
    temp = p.with_name(p.name+'.tmp-'+str(os.getpid()))
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    os.replace(temp, p)

def main():
    lease = read(LEASE)
    owner = lease['coordinator']
    ancestors = [psutil.Process(), *psutil.Process().parents()]
    if not any(p.pid == owner['pid'] and abs(p.create_time()-owner['createTime']) < .01 for p in ancestors):
        raise RuntimeError('Only the live cooperative coordinator may start this batch.')
    if lease['project'] != 'game-lighting-history-remaining-tts' or lease['state'] != 'tts_running':
        raise RuntimeError('Unexpected lease scope/state.')
    token = lease['token']
    state = dict(schemaVersion=1, requestedEpisodes=SLUGS, token=token,
                 status='waiting-for-reviewed-inputs', modelAllocated=False,
                 startedAt=time.time(), pid=os.getpid(), completed=[], current=None,
                 userEvidence=['2편 3편도 진행해줘야지~ tts 전부', '그리고나서 GPU 연구에 쓰라는거야'])
    write(STATE, state)
    deadline = time.monotonic()+1800
    while not READY.exists():
        if time.monotonic() > deadline:
            state.update(status='input-preparation-timeout', exitCode=1)
            write(STATE, state)
            raise RuntimeError('No reviewed inputs; research coordinator will restore queue.')
        time.sleep(5)
    review = read(READY)
    if review.get('allKoEnTextDirectlyReviewed') is not True or review.get('episodes') != SLUGS:
        raise RuntimeError('Full reviewed episode inputs required.')
    for rel, expected in review['inputHashes'].items():
        if sha(ROOT/rel) != expected:
            raise RuntimeError('Reviewed input changed: '+rel)
    for slug in SLUGS:
        state.update(status='synthesizing', current=slug, modelAllocated=False)
        write(STATE, state)
        current = read(LEASE)
        if current['token'] != token or current['coordinator'] != owner:
            raise RuntimeError('Lease ownership changed; preserve foreign lease.')
        current.update(project=slug, batchProject='game-lighting-history-remaining-tts',
                       reviewedBatchInput=str(READY.relative_to(ROOT)).replace('\\','/'),
                       currentEpisode=slug, updatedAt=time.time())
        write(LEASE, current)
        write(ROOT/'shared/output/gpu-handoff'/f'{token}.json', current)
        log_path = BASE/'local'/f'{slug}-tts-v1.log'
        log_path.parent.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, '-X', 'utf8', '-u', str(BASE/'render-reviewed-episode-v1.py'),
                   '--project', slug, '--device', 'cuda:0', '--batch-size', '1']
        with log_path.open('x', encoding='utf-8') as log:
            child = subprocess.Popen(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            proc = psutil.Process(child.pid)
            state.update(child=dict(pid=child.pid, createTime=proc.create_time(), command=proc.cmdline()),
                         log=str(log_path.relative_to(ROOT)).replace('\\','/'))
            write(STATE, state)
            code = child.wait()
        if code:
            state.update(status='child-failed', exitCode=code, modelAllocated=False)
            write(STATE, state)
            raise RuntimeError(f'{slug} TTS exit {code}; preserve chunks and restore research.')
        manifest = read(ROOT/'projects'/slug/'project.json')
        out = ROOT/manifest['tts']['outputDir']; stem=manifest['tts']['filenameStem']
        files = {ext: dict(path=str((out/(stem+ext)).relative_to(ROOT)).replace('\\','/'),
                          sha256=sha(out/(stem+ext))) for ext in ['.wav', '.srt', '.timing.json']}
        state['completed'].append(dict(slug=slug, exitCode=0, files=files, finishedAt=time.time(),
                                       humanListeningApproved=False, finalVideoProduced=False))
        state.update(modelAllocated=False, child=None)
        write(STATE, state)
    state.update(status='all-requested-tts-produced-awaiting-asr', current=None, exitCode=0, finishedAt=time.time())
    write(STATE, state)
    print(json.dumps(dict(completed=SLUGS, status=state['status']), ensure_ascii=False), flush=True)

if __name__ == '__main__': main()
