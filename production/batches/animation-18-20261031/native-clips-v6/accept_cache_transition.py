"""Accept a bounded memoization-only change after the prior worker's safe boundary."""
import hashlib,json
from prepare import HERE,WORK,read,save
from finish_episode import sha
from run_body_queue import SOURCES
from run_selected_queue import run

def main():
    proof=read(HERE/'frame-cache-optimization.json');assert proof['semanticAstUnchanged']
    old=read(WORK/'configuration-review.json')
    assert old['sourceHashes']['render_replacements.py']==proof['oldRendererSha256']
    assert sha(HERE/'render_replacements.py')==proof['newRendererSha256']
    assert all(sha(HERE/name)==old['sourceHashes'][name] for name in SOURCES if name!='render_replacements.py')
    assert sha(WORK/'game-banks/manifest.json')==old['gameBanksSha256']
    completed=read(WORK/'body-queue-status.json')['encodedBodiesReady']
    assert completed==['A04','A05','A07','A08']
    value=dict(old);value['sourceHashes']={name:sha(HERE/name) for name in SOURCES}
    value['performanceOnlyChange']=dict(proof,proofSha256=sha(HERE/'frame-cache-optimization.json'))
    value.pop('signature',None);value['signature']=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
    for ep in completed:
        path=WORK/ep/'native-picture-review.json';body=read(path)
        assert body['visualReviewPassed'] and body['configurationSignature']==old['signature']
        body['priorConfigurationSignature']=old['signature'];body['configurationSignature']=value['signature']
        body['cacheOnlyReuse']='Exact completed pictures preserved; only future deterministic frame memoization capacity changes, with unchanged semantic AST and frozen media inputs.'
        save(path,body)
    save(WORK/'configuration-review.json',value)
    run('run_body_queue.py')

if __name__=='__main__':main()
