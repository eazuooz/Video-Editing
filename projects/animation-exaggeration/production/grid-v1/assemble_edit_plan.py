"""Bind only actually completed A02 sources, preserving pending captures."""
from pathlib import Path
import audio_pipeline as ap
import video_pipeline as vp
H=Path(__file__).resolve().parent
L=H.parent/'local/grid-v1'
def main():
    plan=ap.read(H/'measured-edit-plan.proposal.json')
    profiles=ap.read(H/'measured-native-profiles.json')
    by={p['id']:p for p in profiles['presentations']}
    missing=[];queue=[]
    for c in plan['cuts']:
        if c['kind']=='independent-gameplay':continue
        if c['explanationMode']=='source-frame-analysis':
            spec=ap.read(H/'still-specs'/f'{c["id"]}.json')
            receipt_path=ap.repo_path(spec['outputDir'])/'explanation-render.json'
            receipt=ap.read(receipt_path)
            assert receipt['frames']==c['frames'] and receipt['sourceVideo']['sha256']==c['sourceSha256']
            assert receipt['sourceVideo']['frameTimeSeconds']==c['sourceStillTimestamp']
            c['renderedSource']=receipt['movie']['path'];c['renderedSourceSha256']=receipt['movie']['sha256']
            c['explanationRender']={'kind':'annotated-still','receipt':ap.relative(receipt_path),'receiptSha256':ap.sha(receipt_path)}
            c['captureState']='complete-exact-source-frame-plate'
            continue
        mode=c['explanationMode'];revision=c['id']+'-v1';directory=L/'render'/revision/mode
        source=directory/'unity.mp4';success=directory/'render-success.json';request=directory/'request.json'
        queue.append({'id':c['id'],'mode':mode,'revision':revision,'frames':c['frames'],
                      'presentation':c['id'],'startFrame':c['startFrame'],'endFrame':c['endFrame']})
        assert abs(by[c['id']]['duration']*60-c['frames'])<.001
        if all(p.exists() for p in [source,success,request]):
            r=ap.read(success);q=ap.read(request)
            assert r['status']=='complete' and r['completed']==c['frames'] and q['frames']==c['frames']
            assert q['presentationId']==c['id']
            c['renderedSourceSha256']=ap.sha(source)
            c['nativeCapture']={'movieSha256':c['renderedSourceSha256'],'successReceipt':ap.relative(success),
                'successSha256':ap.sha(success),'request':ap.relative(request),'requestSha256':ap.sha(request),
                'compiledFingerprint':r['compiledSourceFingerprint']}
            c['captureState']='complete-native-capture-final-QA-pending'
        else:missing.append(c['id'])
    plan['nativeCaptureQueue']=queue
    plan['pendingBeforeRender']={'nativeCaptures':missing,'actualAnnotations':False,
        'finalAudioListening':True,'finalEncodedQA':True}
    plan['actualAnnotationDecision']='Clean unique game actions, followed by source-pixel-verified pose/shape stills with anchored marks; no static boxes on rapidly changing occluded bodies.'
    audio_review=H/'final-mix-asr-review.json'
    audio_ok=False
    if audio_review.is_file():
        checked=ap.read(audio_review)
        audio_ok=(checked.get('fullTextDirectReview') is True and checked.get('all14ParagraphsRead') is True
            and any(x['sha256']==ap.sha(L/'edit/final-mix.m4a') for x in checked.get('evidence',[])
                    if x['path'].endswith('/final-mix.m4a')))
    plan['audioSourceReviewPending']=not audio_ok
    vp.validate_plan(plan)
    ap.save(H/'edit-plan.json',plan)
    print(f'Bound{len(plan["cuts"])} cuts; missing native captures:{len(missing)}')
if __name__=='__main__':main()
