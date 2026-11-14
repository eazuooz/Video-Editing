"""Resume the selected render after exact wording proofs; reuse unchanged first bodies."""
import hashlib,json,time
from prepare import HERE,WORK,read,save
from finish_episode import sha
from run_body_queue import SOURCES
from run_selected_queue import run

def main():
    deadline=time.monotonic()+1800
    expected=read(HERE/'narration-patches.json')['records']
    while time.monotonic()<deadline:
        status=WORK/'wording-alignment-status.json'
        checked=read(WORK/'narration-patches-checked.json')['records']
        same=len(checked)==len(expected) and all(a['id']==b['id'] and a['ko']==b['ko'] for a,b in zip(expected,checked))
        if status.exists() and same and not read(WORK/'narration-patch-issues.json')['issues']:break
        time.sleep(3)
    else:raise TimeoutError('New exact sentence proofs still pending.')
    old=read(WORK/'configuration-review.json')
    assert all(sha(HERE/name)==old['sourceHashes'][name] for name in SOURCES if name!='narration-patches.json')
    assert sha(WORK/'game-banks/manifest.json')==old['gameBanksSha256']
    value=dict(old)
    value['sourceHashes']={name:sha(HERE/name) for name in SOURCES}
    value['inspection']='Prior inspected native staging/comparisons unchanged; 34 narration corrections individually read through and ASR/duration/caption-checked against these exact visuals. Human final viewing remains pending.'
    value.pop('signature',None)
    value['signature']=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
    for ep in ('A04','A05'):
        path=WORK/ep/'native-picture-review.json';body=read(path)
        assert body['configurationSignature']==old['signature'] and body['visualReviewPassed']
        current=[r for r in checked if r['episode']==ep]
        assert len(current)==body['changedSentenceCount']
        if current:
            rendered=read(WORK/ep/'body/narration-change-evidence.json')['replacements']
            assert [(r['id'],r['ko'],r['audioSha256']) for r in rendered]==[(r['id'],r['ko'],r['audioSha256']) for r in current]
        body['priorConfigurationSignature']=old['signature']
        body['configurationSignature']=value['signature']
        body['unchangedEpisodeReuse']='Additional wording corrections affect only later episodes; actual two delivered body hashes and their complete local inputs retained.'
        save(path,body)
    save(WORK/'configuration-review.json',value)
    run('run_body_queue.py')

if __name__=='__main__':main()
