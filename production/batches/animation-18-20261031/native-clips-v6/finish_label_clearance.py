"""Repair A17 labels after the remaining unchanged body reaches its safe boundary."""
import hashlib,json,time
from prepare import HERE,WORK,read,save
from finish_episode import sha
from run_body_queue import SOURCES
from run_selected_queue import run

def main():
    deadline=time.monotonic()+3600
    while time.monotonic()<deadline:
        ready=read(WORK/'body-queue-status.json')['encodedBodiesReady']
        if len(ready)==11 and all(read(WORK/ep/'native-picture-review.json').get('visualReviewPassed') for ep in ready if ep!='A17'):break
        time.sleep(3)
    else:raise TimeoutError('The existing final body/inspection has not finished.')
    proof=read(HERE/'label-clearance-fix.json');assert proof['affectedEpisodes']==['A17'] and proof['allOtherSemanticAstUnchanged']
    old=read(WORK/'configuration-review.json')
    assert old['sourceHashes']['native_specials.py']==proof['oldSha256']
    assert sha(HERE/'native_specials.py')==proof['newSha256']
    assert all(sha(HERE/name)==old['sourceHashes'][name] for name in SOURCES if name!='native_specials.py')
    value=dict(old);value['sourceHashes']={name:sha(HERE/name) for name in SOURCES}
    value['scopedVisualCorrection']=dict(proof,preflightInspected=True,humanReviewed=False)
    value.pop('signature',None);value['signature']=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
    for ep in ready:
        if ep=='A17':continue
        path=WORK/ep/'native-picture-review.json';body=read(path)
        assert body['configurationSignature']==old['signature']
        body['priorConfigurationSignature']=old['signature'];body['configurationSignature']=value['signature']
        body['unaffectedScopedCorrection']='Only A17 arm-diagram labels moved; all other semantic AST and frozen inputs unchanged.'
        save(path,body)
    save(WORK/'configuration-review.json',value)
    run('render_replacements.py','A17');run('assemble_native_body.py','A17')
    path=WORK/'A17/native-picture-review.json';body=read(path);body['configurationSignature']=value['signature'];save(path,body)
    run('sample_native_body.py','A17')
    print('A17 label clearance encoded; actual sample inspection pending.',flush=True)

if __name__=='__main__':main()
