"""Record an actually verified A02 delivery, preserving A01 and platform state."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
R=Path(__file__).resolve().parents[3]
B='production/batches/animation-18-20261031/'
H='projects/animation-exaggeration/production/grid-v1/'
P='projects/animation-exaggeration/'
D=P+'production/local/grid-v1/delivery/output/animation-exaggeration/'
W='shared/publishing/video-worklist.json';MD='docs/VIDEO_WORKLIST.md'
def read(p):return json.loads((R/p).read_text(encoding='utf-8-sig'))
def write(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def digest(p):
    h=hashlib.sha256()
    with (R/p).open('rb') as f:
        for block in iter(lambda:f.read(4*1024*1024),b''):h.update(block)
    return h.hexdigest()
def main():
    now=datetime.now(timezone.utc).isoformat();m=read(D+'delivery-manifest.json')
    assert m['episode']=='A02' and m['verification']['structuralFinalPair']=='pass'
    assert m['review']['userFinalReview'] is False and len(m['files'])==4
    for f in m['files']:assert digest(D+f['name'])==f['sha256']
    for name in ['final-caption-pixel-review.json','final-screen-review.json']:
        assert read(H+name)['blockingIssues']==[]
    sha=m['captionedMasterSha256']
    ledger={'episode':'A02','revision':'grid-v1','status':'local-delivery-user-review-pending',
        'createdAt':now,'directory':D.rstrip('/'),'index':D+'index.html',
        'captionedMaster':D+'animation-exaggeration.captioned.mp4','captionedMasterSha256':sha,
        'deliveryManifest':{'path':D+'delivery-manifest.json','sha256':digest(D+'delivery-manifest.json')},
        'format':m['format'],'files':m['files'],'technicalChecks':m['verification'],
        'actualUserViewed':False,'actualWholeListening':False,'actualFullContinuousViewing':False,
        'reviewStatus':'Local four-output review master ready. Sampled encoded pixels and signal/text audio QA complete; actual human viewing/listening pending.',
        'youtubeUploadAuthorized':False,'platformMutation':False,
        'evidence':[H+'final-caption-pixel-review.json',H+'final-screen-review.json',H+'final-mix-asr-review.json']}
    write(H+'local-delivery-ledger.json',ledger)
    project=read(P+'project.json');project.update(status='local-delivery-user-review-pending',publishReady=False,updatedAt=now)
    project['delivery'].update(status='four-outputs-complete',manifest=D+'delivery-manifest.json',captionedMasterSha256=sha)
    project['editing']={'measuredBodyGameplayShare':618/16342,'measuredBodyExplanationShare':1-618/16342,
        'ratioChoiceRecord':H+'editorial-ratio-choice.json','savedNativeScenes':23}
    write(P+'project.json',project)
    cp=read(H+'checkpoint.json');cp.update(status='local-delivery-user-review-pending',updatedAt=now,
        finalMasterRendered=True,completedNativeCaptures=23,currentWork='A02 complete local four outputs; actual user review and full listening pending.',
        nextAction='Preserve this exact review master and continue only within the current explicit production scope; no platform mutation.',
        deliveryLedger=H+'local-delivery-ledger.json',captionedMasterSha256=sha)
    cp['completed']+=['23editableUnityscenes captured;31cuts assembled at1920x1080/60',
        'Full paired masters decoded;17062frames and identical continuousAAC verified',
        'All100caption midpoints and31cut first/middle/last samples reviewed',
        'Four outputs copied byte-identically to local delivery']
    write(H+'checkpoint.json',cp)
    batch=read(B+'checkpoint.json')
    batch.update(updatedAt=now,currentEpisode='A02',completedLocalDeliveries=['A01','A02'],
        currentWork=['A01 and A02 complete local review masters; human review pending',
            'A03 source/scene readiness prepared; no A03TTS or render yet'],
        nextAction='Deliver A02 local links; retain A03 independent-source readiness evidence for the next authorized production stage.')
    batch['costlyJobSummary'].update(nativeFullCaptures=50,currentJob='A02 local delivery complete; no running costly job',sourceAsr='A01/A02 source and finalAAC full text review complete')
    write(B+'checkpoint.json',batch)
    originals=[json.loads(subprocess.check_output(['git','show',ref+':'+W],cwd=R)) for ref in ('HEAD','')]+[read(W)]
    fields={'slug':'animation-exaggeration','plannedSlug':'animation-too-much-is-just-right',
        'productionComplete':True,'productionStatus':'로컬 검수본 완성 · 1080p60 · 4분44초 · 4개 산출물',
        'reviewStarted':True,'reviewStatus':'자막·장면 표본·음성 연속성 검사 완료 · 사용자 시청/최종 청취 대기',
        'executionStatus':'검수본 전달 · 업로드 미승인','localMasterAvailable':True,
        'deliveryLedger':H+'local-delivery-ledger.json','captionedMasterSha256':sha,'updatedAt':now}
    changes=[]
    for key,value in fields.items():
        expected=[]
        for original in originals:
            row=next(x for x in original['rows'] if x['id']=='A02');state={'exists':key in row,'value':row.get(key)}
            if state not in expected:expected.append(state)
        changes.append({'field':key,'expected':expected,'value':value})
    current=(R/MD).read_text(encoding='utf-8-sig').splitlines();markdown=[]
    for eid in ('A01','A02'):
        line=next(x for x in current if x.startswith('| '+eid+' | '));new=line
        if eid=='A02':new=line[:line.rfind('|',0,line.rfind('|'))+1]+' 로컬 4분44초·1080p60 검수본 완료 · 사용자 검수 대기 |'
        markdown.append({'id':eid,'expected':line,'value':new})
    write(B+'a02-delivery-status-commit-plan.json',{'scope':'animation-A01-A02-delivery-status',
        'rows':[{'id':'A01','changes':[],'appendEvidence':[]},{'id':'A02','changes':changes,'appendEvidence':[H+'local-delivery-ledger.json']}],
        'markdownRows':markdown,'seriesStatus':'active-production',
        'ownedPaths':[P+'project.json',H+'checkpoint.json',H+'local-delivery-ledger.json',B+'checkpoint.json',B+'record_a02_delivery.py']})
    print('Prepared A02 completion ledger and exact shared-row overlay; A01/platform state untouched.')
if __name__=='__main__':main()
