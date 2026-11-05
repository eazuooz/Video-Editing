"""Adopt verified masters, exclude the withdrawn item, retain its last-master history."""
import subprocess
import sys
from pathlib import Path
from render import HERE, MEDIA, WORK, SPEC, DIRECTORY, SOURCES, EDITS, editor

ROOT=editor.ROOT
REV=SPEC['revision']
ORDER=list(EDITS)
RETIRED=SOURCES[8]
english={
    1:'Why Does the Water Stay Level When You Tip the Bottle?',
    2:'When Batman Steps in Snow, Who Takes the Footprint’s Picture?',
    3:'Waves Outside the Window. How Does the Cabin Stay Dry?',
    4:'The Plane Stays Put. Why Does It Look Like It Can Fly Forever?',
    5:'When the Jeep Pulls, How Does Its Rope Find a Way Around the Post?',
    6:'Why Can StarCraft Workers Slip Through Each Other on the Way to Minerals?',
    7:'The Bridge Looks Diagonal to Us. What Does a StarCraft Unit See?',
    9:'Why Do StarCraft Marines Start Together but Fire Out of Sync?',
    10:'The Match Is Over. How Can You Still Move the Camera in a StarCraft II Replay?'}

def withdrawn_entry():
    return dict(order=8,slug=RETIRED['slug'],reason='사용자가 이번 검수·게시 후보에서 삭제 요청',lastLocalMaster=RETIRED['masterSha256'])
def info(n):
    path=Path(SOURCES[n]['finalDirectory']).parent/DIRECTORY
    receipt=editor.read(path/'delivery.json')
    qa=editor.read(path/'feedback-check.json')
    files={x['name']:{k:v for k,v in x.items() if k!='name'} for x in receipt['files']}
    assert qa['master']==files['captioned.mp4']['sha256']
    final=dict(directory=str(path),fourOutputsVerified=True,reviewFilesGenerated=True,presentOutputNames=editor.FILES,
               issues=[],files=files,masterSHA256=qa['master'],reviewPage=str(path/'index.html'),delivery=str(path/'delivery.json'))
    ev=dict(masterSHA256=qa['master'],finalDirectory=str(path),deliveryPath=str(path/'delivery.json'),
            deliverySHA256=editor.sha(path/'delivery.json'),technicalEvidence=str(path/'feedback-check.json'),
            sampledVisualStatus='pass-at-sampled-times',fullListening='pending',fullRealtimePlayback='pending',humanFinalReview='pending')
    if n in (5,10):
        ev['additionalNarrationASR']=editor.read(WORK/f'{n:02}'/'speech-check.json')
    elif n==2:
        prior=SOURCES[n]['recordedReviewEvidence']['currentTechnicalReview']
        for k in ('listenAtSeconds','listeningNote'):ev[k]=prior[k]
    return receipt,qa,ev,final
def set_worklist(obj):
    slugs={SOURCES[n]['slug']:n for n in ORDER}
    obj['rows']=[r for r in obj['rows'] if r.get('slug')!=RETIRED['slug']]
    history=[r for r in obj.get('withdrawnShorts',[]) if r.get('slug')!=RETIRED['slug']]
    obj['withdrawnShorts']=history+[withdrawn_entry()]
    for row in obj['rows']:
        n=slugs.get(row.get('slug'))
        if n is None:continue
        d,qa,ev,final=info(n)
        row.update(title=d['title'],production='complete-local-files',status='local-feedback-reviewed-samples',
                   review='일반 시청자용 제목과 새 검수본의 재생·탐색 확인. 전체 청취와 사용자 검수 대기.',
                   humanReview='pending',currentFinalEvidence=ev)
    return obj
def set_control(obj):
    record=obj['explicitTechTenBatch20261030']
    record.update(activeReviewOrders=ORDER,withdrawnProjects=[withdrawn_entry()],localReviewVideosCompleted=len(ORDER),
                  sampledVisualPassCount=len(ORDER),currentStage='nine-revised-masters-await-local-human-review',
                  scope='2026-11-05 최신 요청으로 8번 EUD 제외. 원래 번호 1~7, 9, 10의 로컬 검수본까지. 게시 권한은 별도.')
    return obj
def main():
    checks=editor.read(WORK/'player-nine.json')
    assert [c['n'] for c in checks]==ORDER
    seen=editor.read(WORK/'inspected.json')
    assert set(seen)==set(map(str,ORDER))
    changed=[]
    batchpath=HERE.parent/'batch.json';checkpointpath=HERE.parent/'checkpoint.json'
    batch=editor.read(batchpath);cp=editor.read(checkpointpath)
    batch['projects']=[r for r in batch['projects'] if r['order'] in ORDER]
    batch.update(withdrawnProjects=[withdrawn_entry()],activeReviewOrders=ORDER)
    cp['projects']=[r for r in cp['projects'] if r['order'] in ORDER]
    for n in ORDER:
        d,q,ev,final=info(n);slug=SOURCES[n]['slug'];p=ROOT/'projects'/slug
        assert seen[str(n)]==ev['masterSHA256']==next(r['master'] for r in checks if r['n']==n)
        release=p/'publishing/metadata.json'
        meta=editor.read(release);meta.update(title=d['title'],englishTitle=english[n],description=d['description'],revision=REV,humanFinalReview='pending');editor.save(release,meta)
        project=p/'project.json';mf=editor.read(project);mf.update(title=d['title'],currentRevision=REV,currentVisualVersion=REV,currentFinalDirectory='production/local/'+DIRECTORY)
        for k,f in zip(['videoClean','videoBurnedCaptions','captionsKo','captionsEn','localReview'],[*editor.FILES,'index.html']):
            mf['paths'][k]=f'projects/{slug}/production/local/{DIRECTORY}/{f}'
        mf['paths']['feedbackEdit']=(HERE/'nine.json').relative_to(ROOT).as_posix();editor.save(project,mf)
        config=p/'production/visual-config.json';vc=editor.read(config);vc['head']=EDITS[n]['head'];editor.save(config,vc)
        ledger=p/'production/review-ledger.json';h=editor.read(ledger)
        h.update(revision=REV,currentTechnicalReview=ev,technicalChecks='pass',humanFinalReview='pending',actualCompleteHumanListening=False)
        h['sampleVisualReviews']=[v for v in h.get('sampleVisualReviews',[]) if v.get('masterSHA256')!=q['master']]+[dict(revision=REV,masterSHA256=q['master'],sampleTimes=q['sampleTimes'],sheet=q['sampleSheet'],status='passed-sampled-visual-review')]
        editor.save(ledger,h)
        checkpoint=p/'production/checkpoint.json';c=editor.read(checkpoint)
        c.update(revision=REV,sampledFinalEvidence=ev,finalOutputs=final,feedbackRevision=dict(baseMaster=SOURCES[n]['masterSha256'],edit=EDITS[n],revision=REV,additionFrames=d['additionFrames'],technicalEvidence=ev))
        editor.save(checkpoint,c)
        for row in (next(r for r in batch['projects'] if r['order']==n),next(r for r in cp['projects'] if r['order']==n)):
            row.update(title=d['title'],revision=REV)
        next(r for r in cp['projects'] if r['order']==n).update(finalOutputs=final,sampledFinalEvidence=ev)
        cp['currentFinalEvidence'][slug]=ev
        changed+=list((release,project,config,ledger,checkpoint))
    retired=ROOT/'projects'/RETIRED['slug']
    for file in ('project.json','publishing/metadata.json','production/checkpoint.json','production/review-ledger.json'):
        path=retired/file;record=editor.read(path)
        record.update(status='withdrawn-by-user',inCurrentReview=False,eligibleForPublishing=False)
        editor.save(path,record);changed.append(path)
    cp['currentFinalEvidence'].pop(RETIRED['slug'],None)
    cp['remainingProduction']=[r for r in cp.get('remainingProduction',[]) if r.get('slug')!=RETIRED['slug']]
    cp.update(withdrawnProjects=[withdrawn_entry()],revision=REV,status='nine-revised-local-masters-await-review',
              verifiedFourOutputSets=9,generatedReviewVideos=9,sampledVisualPassCount=9,activeReviewOrders=ORDER,
              sourceReadyCount=9,actualVoiceGeneratedCount=9,verifiedCaptionArtifactSets=9,
              next='9편의 새 로컬 검수본을 전달하고 전체 청취와 사용자 최종 검수를 기다린다.')
    editor.save(batchpath,batch);changed.append(batchpath)
    for path,fn in [(ROOT/'shared/publishing/shorts-worklist.json',set_worklist),(ROOT/'shared/publishing/video-production-control.json',set_control)]:
        editor.save(path,fn(editor.read(path)))
    sql=subprocess.check_output([sys.executable,'-X','utf8',str(HERE.parent/'build-review-overview.py'),'--require-all'],text=True,encoding='utf8')
    overview=__import__('json').loads(sql)
    cp['localReviewCollection']=dict(page=overview['index'],snapshot=overview['snapshot'],snapshotSHA256=editor.sha(overview['snapshot']),verifiedFinalCount=9)
    editor.save(checkpointpath,cp);changed.append(checkpointpath)
    changed.extend([HERE.parent/'build-review-overview.py',*(HERE.parent/'feedback-nov05'/f for f in ['build.py','check.py','check-player.cjs','CommandReplay.cs'])])
    editor.save(WORK/'git-include.json',[p.relative_to(ROOT).as_posix() for p in changed])
    print(sql)
if __name__=='__main__':main()
