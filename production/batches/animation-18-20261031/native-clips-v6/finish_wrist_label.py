"""Correct the final wrist source-kind label after A17's visual repair is inspected."""
import hashlib,json,time
from prepare import HERE,WORK,read,save
from finish_episode import sha
from run_body_queue import SOURCES
from run_selected_queue import run

def main():
    deadline=time.monotonic()+3600
    while time.monotonic()<deadline:
        ready=read(WORK/'body-queue-status.json')['encodedBodiesReady']
        if len(ready)==11 and all(read(WORK/ep/'native-picture-review.json').get('visualReviewPassed') for ep in ready if ep!='A18'):break
        time.sleep(3)
    else:raise TimeoutError('A17 exact encoded repair still awaits inspection.')
    proof=read(HERE/'wrist-source-label-fix.json');assert proof['affectedEpisode']=='A18' and proof['affectedKey']=='wrist'
    old=read(WORK/'configuration-review.json')
    assert old['sourceHashes']['native_specials.py']==proof['oldSha256']
    assert sha(HERE/'native_specials.py')==proof['newSha256']
    assert all(sha(HERE/name)==old['sourceHashes'][name] for name in SOURCES if name!='native_specials.py')
    value=dict(old);value['sourceHashes']={name:sha(HERE/name) for name in SOURCES}
    value['scopedSourceKindCorrection']=dict(proof,preflightInspected=True,humanReviewed=False)
    value.pop('signature',None);value['signature']=hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()
    for ep in ready:
        if ep=='A18':continue
        path=WORK/ep/'native-picture-review.json';body=read(path)
        assert body['configurationSignature']==old['signature'] and body['visualReviewPassed']
        body['priorConfigurationSignature']=old['signature'];body['configurationSignature']=value['signature']
        body['unaffectedSourceKindCorrection']='Only the A18/wrist source-label branch changed; exact completed pictures and narration preserved.'
        save(path,body)
    save(WORK/'configuration-review.json',value)
    run('render_replacements.py','A18');run('assemble_native_body.py','A18')
    path=WORK/'A18/native-picture-review.json';body=read(path);body['configurationSignature']=value['signature'];save(path,body)
    run('sample_native_body.py','A18')
    print('A18 source-kind correction encoded; final sample inspection pending.',flush=True)

if __name__=='__main__':main()
