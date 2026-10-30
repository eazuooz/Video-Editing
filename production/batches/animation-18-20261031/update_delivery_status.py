"""Record actual A01 delivery and A02 work without asserting human review."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, subprocess

ROOT=Path(__file__).resolve().parents[3]
B='production/batches/animation-18-20261031/'
W='shared/publishing/video-worklist.json'; D='docs/VIDEO_WORKLIST.md'
def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def write(p,v): (ROOT/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
    now=datetime.now(timezone.utc).isoformat()
    h='projects/animation-assigning/production/grid-v1/'
    directory='projects/animation-assigning/production/local/grid-v1/delivery/output/animation-assigning/'
    manifest=read(directory+'delivery-manifest.json')
    for f in manifest['files']:
        assert sha(directory+f['name'])==f['sha256']
    digest=manifest['captionedMasterSha256']
    assert manifest['review']['userFinalReview'] is False
    ledger={
        'episode':'A01','revision':'grid-v1','status':'local-delivery-user-review-pending',
        'createdAt':now,'directory':directory.rstrip('/'),
        'index':directory+'index.html','captionedMaster':directory+'animation-assigning.captioned.mp4',
        'captionedMasterSha256':digest,'deliveryManifest':{'path':directory+'delivery-manifest.json','sha256':sha(directory+'delivery-manifest.json')},
        'format':manifest['format'],'files':manifest['files'],
        'technicalChecks':manifest['verification'],
        'actualUserViewed':False,'actualWholeListening':False,'actualFullContinuousViewing':False,
        'reviewStatus':'Delivered local links; human review and final contextual listening remain pending.',
        'youtubeUploadAuthorized':False,'platformMutation':False,
        'nextAuthorizedWork':'A02 under the exact A01–A18 finite batch, not automatic next-video authority.'}
    write(h+'local-delivery-ledger.json',ledger)
    p=read('projects/animation-assigning/project.json')
    p['status']='local-delivery-user-review-pending'
    p['delivery'].update(status='four-outputs-complete',manifest=directory+'delivery-manifest.json',captionedMasterSha256=digest)
    p['editing'].update(measuredBodyGameplayShare=3201/24166,measuredBodyExplanationShare=1-3201/24166,
                        ratioChoiceRecord=h+'editorial-ratio-choice.json')
    p['publishReady']=False
    write('projects/animation-assigning/project.json',p)
    cp=read(h+'checkpoint.json')
    cp.update(status='local-delivery-user-review-pending',finalMasterRendered=True,updatedAt=now,
              currentWork='A01 four outputs delivered; actual user review/listening pending.',
              nextAction='Preserve this exact master for user review. Continue explicitly authorized A02; no platform mutation.',
              deliveryLedger=h+'local-delivery-ledger.json',captionedMasterSha256=digest)
    for line in ['All27 editable native Unity scenes captured','Full clean/captioned pair decoded and 24886 frames/60fps verified',
                 '177 burned KO captions checked at375px; all53cut/annotation samples inspected',
                 'Four outputs collected byte-identically and local review links delivered']:
        if line not in cp['completed']: cp['completed'].append(line)
    write(h+'checkpoint.json',cp)
    h2='projects/animation-exaggeration/production/grid-v1/'
    cp2=read(h2+'checkpoint.json')
    cp2.update(status='source-audio-review-native-preflight',updatedAt=now,
               currentWork='CPU full word-ASR completed after truncated GPU timestamps; comparison/recovery review and six native modes in progress.',
               nextAction='Validate full word timing, preserve the source PCM, bind captions and measured native profiles.')
    write(h2+'checkpoint.json',cp2)
    batch=read(B+'checkpoint.json')
    batch.update(currentEpisode='A02',completedLocalDeliveries=['A01'],completedLocalReviews=[],
                 currentWork=['A01 complete local four-output delivery, human review/listening pending',
                              'A02 continuous Sample B272.353s; CPU word-ASR review and six-mode Unity preflight',
                              'A03 caption/native design; A04 source readiness'],
                 nextAction='Finish A02 measured scene plan, capture, paired outputs and local review.',updatedAt=now)
    batch['costlyJobSummary'].update(currentJob='A02 Unity runtime preflight; source ASR finished',
                                    sourceAsr='A01 complete; A02 CPU word-timestamp validation/review',nativeFullCaptures=27)
    write(B+'checkpoint.json',batch)
    originals=[json.loads(subprocess.check_output(['git','show',ref+':'+W],cwd=ROOT)) for ref in ['HEAD','']]
    originals.append(read(W))
    values={
      'A01':{'slug':'animation-assigning','plannedSlug':'animation-assigning-animations',
             'productionComplete':True,'productionStatus':'로컬 검수본 완성 · 1080p60 · 6분55초 · 4개 산출물',
             'reviewStarted':True,'reviewStatus':'기술·자막 화면 검사 완료 · 사용자 시청/최종 청취 대기',
             'executionStatus':'검수본 전달 완료 · 업로드 미승인','localMasterAvailable':True,
             'deliveryLedger':h+'local-delivery-ledger.json','captionedMasterSha256':digest,'updatedAt':now},
      'A02':{'slug':'animation-exaggeration','plannedSlug':'animation-too-much-is-just-right',
             'productionStatus':'Sample B 음성 완료 · 자막 시간 검토·Unity 격자 비교 제작 중',
             'reviewStatus':'원본 흐름·대본 검토 완료 · 완성본 미생성',
             'executionStatus':'음성 보존·Unity 동작 검증 진행 중','updatedAt':now}}
    rows=[]
    for identity,fields in values.items():
        changes=[]
        for key,value in fields.items():
            expected=[]
            for old in originals:
                r=next(x for x in old['rows'] if x['id']==identity)
                v={'exists':key in r,'value':r.get(key)}
                if v not in expected:expected.append(v)
            changes.append({'field':key,'expected':expected,'value':value})
        rows.append({'id':identity,'changes':changes,'appendEvidence':[
            h+'local-delivery-ledger.json' if identity=='A01' else h2+'voice-generation-record.json']})
    markdown=[]
    current=(ROOT/D).read_text(encoding='utf-8-sig').splitlines()
    for identity,status in [('A01','로컬 6분55초·1080p60 검수본 완료 · 사용자 검수 대기'),
                            ('A02','음성 완료 · 자막 시간 검토·Unity 비교 장면 제작 중')]:
        line=next(x for x in current if x.startswith('| '+identity+' | '))
        # Last status column only; the title contains an escaped vertical bar.
        replacement=line[:line.rfind('|',0,line.rfind('|'))+1]+' '+status+' |'
        markdown.append({'id':identity,'expected':line,'value':replacement})
    owned=[h+'local-delivery-ledger.json',h+'checkpoint.json','projects/animation-assigning/project.json',
           h2+'checkpoint.json',B+'checkpoint.json',B+'update_delivery_status.py',B+'commit_delivery_status.py']
    write(B+'delivery-status-commit-plan.json',{'scope':'animation-A01-A02-delivery-status','rows':rows,
        'markdownRows':markdown,'seriesStatus':'active-production','ownedPaths':owned})
    print('Prepared exact A01/A02 state overlays; no shared file or Git changed.')
if __name__=='__main__': main()
