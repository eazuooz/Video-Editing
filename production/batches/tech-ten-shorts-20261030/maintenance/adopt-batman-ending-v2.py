"""Adopt one verified ending-only revision; preserve all original attempts."""
from pathlib import Path
import argparse, copy, importlib.util, json, sys
ROOT=Path('D:/Github/VideoEditing'); B=ROOT/'production/batches/tech-ten-shorts-20261030'
sys.path.insert(0,str(B)); s=importlib.util.spec_from_file_location('adoption_runner',B/'run-batch.py')
r=importlib.util.module_from_spec(s); s.loader.exec_module(r)
SLUG='shorts-batman-origins-snow-below-camera'; P=ROOT/'projects'/SLUG; L=P/'production/local'
PROJECT=P/'project.json'; STATE=L/'finite-pipeline-v1/state.json'; READY=B/'readiness.json'
OUT=L/'final-reviewed-v2'; PREP=L/'ending-v2-preparation'; REPORT=PREP/'adoption.json'
MASTER='9205b33898525577f820d21d477ff070eb79e1707133d77698836632335cf181'

def preserve(path, folder):
    target=folder/(path.name+'.'+r.sha(path)+'.preserved')
    if not target.exists(): target.write_bytes(path.read_bytes())
    assert r.sha(target)==r.sha(path)
    return r.artifact(target)

def run(audit=None,audit_sha=None):
    assert not REPORT.exists(), 'Adoption already recorded; inspect it rather than repeat.'
    project=r.read(PROJECT); state=r.read(STATE); ready=r.read(READY)
    assert project['currentFinalDirectory']=='production/local/final-reviewed-v1'
    assert r.sha(OUT/'captioned.mp4')==MASTER
    complete=r.read(OUT/'ending-v2-complete.json'); integrity=r.read(OUT/'integrity.json')
    verify=r.read(OUT/'ending-v2-verification.json'); pair=r.read(OUT/'pair-build.json')
    assert complete['status']=='technical-output-complete-sampled-tail-review-pending'
    assert complete['originalInputsPreserved'] and complete['audioIdentical'] and complete['captionFilesIdentical']
    assert integrity['status']=='pass' and verify['aacPacketsAllIdentical']
    assert pair['endingCorrection']['blackTail']==[3040,3064]
    r.verify(complete['files'])
    for stage in r.STAGES:
        assert state['stages'][stage]['status']=='pass', stage
        r.verify(state['stages'][stage]['artifacts'])
    old_fp=r.fingerprints(P); assert old_fp==state['fingerprints']==ready['projects'][SLUG]['fingerprints']
    selected=copy.deepcopy(project); selected['currentFinalDirectory']='production/local/final-reviewed-v2'
    selected['currentVisualVersion']='ending-v2'
    for key in ['videoBurnedCaptions','videoClean','captionsKo','captionsEn','localReview']:
        assert '/final-reviewed-v1/' in selected['paths'][key]
        selected['paths'][key]=selected['paths'][key].replace('/final-reviewed-v1/','/final-reviewed-v2/')
    if audit is None:
        print(json.dumps(dict(readyForAdoptionAfterSampledAudit=True,previousProjectSha256=r.sha(PROJECT),
            previousStateSha256=r.sha(STATE),previousReadinessSha256=r.sha(READY),
            proposedManifest=selected,finalMasterSha256=MASTER),ensure_ascii=False,indent=2));return
    audit=Path(audit); assert r.sha(audit)==audit_sha
    proof=r.read(audit)
    assert proof['projectSlug']==SLUG and proof['master']['sha256']==MASTER
    assert proof['status']=='pass-sampled-visual-review'
    assert proof['sampledVisualReview']['status']=='pass-sampled-visual-review'
    assert proof['sampledVisualReview']['remainingDefects']==[]
    assert proof['sampledVisualReview']['humanFinalReview']=='pending'
    preservation=PREP/'adoption-preserved'; preservation.mkdir(exist_ok=True)
    saved=[preserve(p,preservation)for p in [PROJECT,STATE,READY]]
    before_ready_sha=r.sha(READY); other_ready={k:v for k,v in ready['projects'].items()if k!=SLUG}
    others={row['slug']:r.fingerprints(ROOT/'projects'/row['slug'])for row in r.inventory()[1]if row['slug']!=SLUG}
    r.save(PROJECT,selected); new_fp=r.fingerprints(P)
    assert old_fp['code']==new_fp['code']
    differing=[(a,b)for a,b in zip(old_fp['inputs'],new_fp['inputs'])if a!=b]
    assert len(differing)==1 and Path(differing[0][0]['path']).resolve()==PROJECT.resolve()
    stamp=r.now(); revised=copy.deepcopy(state)
    revised.setdefault('fingerprintHistory',[]).append(dict(previous=old_fp,replacedAt=stamp,
        reason='Selected final-directory metadata and ending visual version only. Same raw/native/PCM/timing/mix. Final pair alone adds the explicitly reviewed ending fade.',
        previousState=saved[1],preservedManifest=saved[0],reviewReceipt=r.artifact(audit)))
    final_stages={'video-pair':[OUT/'pair-build.json',OUT/'clean.mp4',OUT/'captioned.mp4',OUT/'captions.ko.srt',OUT/'captions.en.srt',OUT/'ending-v2-complete.json',OUT/'ending-v2-verification.json',PREP/'prepared.json',B/'maintenance/rebuild-batman-ending-v2.py'],
        'integrity':[OUT/'integrity.json'],
        'qa':[OUT/'mobile-review.mp4',OUT/('qa-sequential-'+MASTER[:12])/'index.json'],
        'review':[OUT/'index.html',OUT/'SHA256SUMS.txt',OUT/'delivery.json']}
    for name, record in revised['stages'].items():
        if name in final_stages:
            revised.setdefault('history',[]).append(dict(stage=name,record=copy.deepcopy(record),reason='Preserved v1 final before verified ending-v2 adoption'))
            record=dict(status='pass',startedAt=stamp,endedAt=stamp,
                operation='CPU adoption of existing verified ending-v2 output; no new render in this operation',
                resources=dict(stage=name,checkedAt=stamp,mode='CPU-only-evidence-adoption',foreignProcessesUntouched=True),
                dependencies=new_fp,artifacts=[r.artifact(p)for p in final_stages[name]],
                result=dict(directory=str(OUT.resolve()),actualHumanReview='pending',actualFullListening='pending',fullMovingReview='pending',boundedEndingCorrection=True))
            revised['stages'][name]=record
        elif name not in {'voice','voice-asr','captions'}:
            assert record['dependencies']==old_fp
            record['dependencies']=new_fp
            record['reusedAfterFinalSelectionChange']=dict(adoptedAt=stamp,previousDependencies=old_fp,
                reason='Only project final-output path/version metadata changed; every upstream code/input except this metadata and every recorded artifact is unchanged. Raw retains its original native tail; final encoder applies the bounded fade.',
                priorState=saved[1])
    revised.update(fingerprints=new_fp,status='review-files-generated-internal-review-pending',currentStage='review',updatedAt=stamp)
    r.save(STATE,revised)
    assert r.sha(READY)==before_ready_sha, 'Concurrent readiness update; preserve before applying keyed change.'
    entry=ready['projects'][SLUG];entry['fingerprints']=new_fp;entry['codeReadyForActualProduction']=True
    entry['selectedFinalVisualVersion']='ending-v2'
    entry['endingRevisionAdoption']=dict(helper=r.artifact(Path(__file__)),sampledReview=r.artifact(audit),
        previousState=saved[1],verification=r.artifact(OUT/'ending-v2-verification.json'),humanReview='pending',actualFullListening='pending')
    r.save(READY,ready)
    assert {k:v for k,v in r.read(READY)['projects'].items()if k!=SLUG}==other_ready
    assert all(r.fingerprints(ROOT/'projects'/slug)==fp for slug,fp in others.items())
    class NoMutationLock:
        def set_stage(self,*args): raise AssertionError('No stages may execute in adoption verification')
    pipeline=r.Pipeline(SLUG,NoMutationLock())
    checked=[]
    for name in r.STAGES:
        stage=pipeline.state['stages'][name];assert stage['status']=='pass'
        r.verify(stage['artifacts']);assert stage['dependencies']==pipeline.dependencies(name)
        checked.append(name)
    receipt=dict(adoptedAt=stamp,helper=r.artifact(Path(__file__)),masterSha256=MASTER,
        before=saved,after=[r.artifact(p)for p in [PROJECT,STATE,READY]],
        exactStagesReadOnlyVerified=checked,otherNineFingerprintsUnchanged=True,otherNineReadinessEntriesUnchanged=True,
        sourceRawNativePcmCaptionTimingUnchanged=True,oldFinalPreserved=True,
        sampledAudit=r.artifact(audit),humanReview='pending',actualFullListening='pending')
    r.save(REPORT,receipt);print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--audit');p.add_argument('--audit-sha256');a=p.parse_args()
    assert bool(a.audit)==bool(a.audit_sha256)
    run(a.audit,a.audit_sha256)
