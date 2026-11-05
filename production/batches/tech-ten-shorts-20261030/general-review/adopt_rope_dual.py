"""Select just the rope cut in the existing nine-item local review collection."""
import json
import subprocess as sp
import sys
from rope_dual import BASE, SLUG, VERSION, REV, OLD, OUT, TEMP, HERE, editor

P=editor.ROOT/'projects'/SLUG
plan='planning/production-plan.json'
def pick():
    rec=editor.read(OUT/'delivery.json')
    assert editor.read(OUT/'dual-path-check.json')['captionedSHA256']==rec['files'][1]['sha256']
    manifest=editor.read(P/'project.json')
    manifest.update(currentRevision=REV,currentVisualVersion=REV,currentFinalDirectory='production/local/'+VERSION)
    for key in ('videoClean','videoBurnedCaptions','captionsKo','captionsEn','localReview'):
        manifest['paths'][key]='projects/'+SLUG+'/production/local/'+VERSION+'/'+manifest['paths'][key].split('/')[-1]
    manifest['paths']['currentVisualEdit']=(HERE/'rope_dual.py').relative_to(editor.ROOT).as_posix()
    editor.save(P/'project.json',manifest)
    info=editor.read(P/'publishing/metadata.json')
    info.update(revision=REV,description=rec['description'])
    editor.save(P/'publishing/metadata.json',info)

def worklist(doc,ev):
    row=next(r for r in doc['rows'] if r.get('slug')==SLUG)
    row.update(review='기존 밧줄과 숨은 팽팽한 경로의 동시 표시·모바일 재생 확인. 전체 청취·사용자 최종검수 대기.',humanReview='pending',currentFinalEvidence=ev)
    return doc

def record():
    d=editor.read(OUT/'delivery.json');q=editor.read(OUT/'feedback-check.json');z=editor.read(OUT/'dual-path-check.json')
    browser=editor.read(TEMP/'player-v4.json')
    digest=d['files'][1]['sha256']
    assert browser['master']==digest==q['master']==z['captionedSHA256'] and len(browser['played'])==3
    ledger=editor.read(P/'production/review-ledger.json');ev=dict(ledger['currentTechnicalReview'])
    ev.update(masterSHA256=digest,finalDirectory=str(OUT),deliveryPath=str(OUT/'delivery.json'),deliverySHA256=editor.sha(OUT/'delivery.json'),
              technicalEvidence=str(OUT/'feedback-check.json'),simultaneousPaths=z,player=browser,baseMasterSHA256=BASE)
    ledger.update(revision=REV,currentTechnicalReview=ev)
    if not any(x.get('masterSHA256')==digest for x in ledger['sampleVisualReviews']):
        ledger['sampleVisualReviews'].append(dict(revision=REV,masterSHA256=digest,sampleTimes=q['sampleTimes'],sheet=q['sampleSheet'],sheetSHA256=q['sampleSheetSha256'],
                                                 status='pass: simultaneous solid/dashed lines; focus sampled at 33, 42.7, 54.8 seconds',wholeRealtimePlaybackReviewed=False))
    editor.save(P/'production/review-ledger.json',ledger)
    cp=editor.read(P/'production/checkpoint.json');outputs=cp['finalOutputs'].copy()
    outputs.update(directory=str(OUT),files={x['name']:{k:v for k,v in x.items() if k!='name'} for x in d['files']},
                   masterSHA256=digest,reviewPage=str(OUT/'index.html'),delivery=str(OUT/'delivery.json'))
    cp.update(revision=REV,sampledFinalEvidence=ev,finalOutputs=outputs)
    if cp['feedbackRevision'].get('revision')!=REV:
        cp.setdefault('priorFeedbackRevisions',[]).append(cp['feedbackRevision'])
    cp['feedbackRevision']=dict(revision=REV,baseMaster=BASE,additionFrames=0,technicalEvidence=ev)
    editor.save(P/'production/checkpoint.json',cp)
    pl=editor.read(P/plan)
    pl['simultaneousRopeRevision']=dict(version=REV,source='general-review/RopeRig.cs and native-final/{side,wrapped,direct}/poses.csv; 91 poses per camera',
       renderer='Original Unity capture plus matching two-layer editorial comparison (rope_dual.py).',
       cues=['6.92–15.78 / 30.17–37.30: side view, actual fixed-length golden slack rope vs the mint dashed straight route',
             '15.78–30.17 / 37.30–51.65: overhead, same endpoints, moving yellow sampled rope vs corner-respecting mint dashed route. Only the illustrative failure span inside the post is red.',
             '51.65–60.30 / 66.30–70.13: both layers kept visible while the jeep moves; real game footage remains separate.'],
       limits='Two calculations for one rope. The overhead loose shape and the fault are illustrative, not a recording of the retail solver. No claims about production fallback threshold.')
    editor.save(P/plan,pl)
    batchp=HERE.parent/'batch.json';batch=editor.read(batchp)
    next(row for row in batch['projects'] if row['slug']==SLUG)['revision']=REV;editor.save(batchp,batch)
    path=HERE.parent/'checkpoint.json';bc=editor.read(path)
    next(row for row in bc['projects'] if row['slug']==SLUG).update(revision=REV,finalOutputs=outputs,sampledFinalEvidence=ev)
    bc['currentFinalEvidence'][SLUG]=ev
    wi=editor.ROOT/'shared/publishing/shorts-worklist.json';editor.save(wi,worklist(editor.read(wi),ev))
    overview=json.loads(sp.check_output([sys.executable,'-X','utf8',str(HERE.parent/'build-review-overview.py'),'--require-all'],encoding='utf8'))
    bc['localReviewCollection'].update(page=overview['index'],snapshot=overview['snapshot'],snapshotSHA256=editor.sha(overview['snapshot']))
    editor.save(path,bc)
if __name__=='__main__':
    (record if 'record' in sys.argv else pick)()
