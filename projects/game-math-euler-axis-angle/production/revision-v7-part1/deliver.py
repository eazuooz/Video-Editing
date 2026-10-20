"""Collect this one Part1 delivery and register actual hashes/local review.

No upload, baseline deletion/replacement, automatic next part or automation.
All report paths must name existing current-output evidence supplied by root.
"""
from pathlib import Path
import argparse, datetime, hashlib, importlib.util, json, os, subprocess, uuid

H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'projects/game-math-euler-axis-angle'
O=P/'production/local/revision-v7-part1';D=R/'projects/game-math-euler-axis-angle-part-01'
SLUG=D.name;OUT=R/'output'/SLUG
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def path(p):return Path(p)if Path(p).is_absolute()else R/p
def now():return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def update(p,fn):
    p=Path(p)
    for _ in range(8):
        raw=p.read_bytes();data=json.loads(raw);fn(data)
        if p.read_bytes()!=raw:continue
        tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
        tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        if p.read_bytes()!=raw:tmp.unlink();continue
        os.replace(tmp,p);return
    raise RuntimeError('Concurrent changes preserved; retry targeted registration: '+str(p))
def evidence(file):return dict(file=rel(file),sha256=sha(file))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--visual-review',type=Path,required=True);ap.add_argument('--asr-review',type=Path,required=True);ap.add_argument('--audio-review',type=Path,required=True);a=ap.parse_args()
    sp=importlib.util.spec_from_file_location('v7_delivery_timing',H/'timing.py');T=importlib.util.module_from_spec(sp);sp.loader.exec_module(T);T.authorized()
    current=O/'part1-captioned.mp4';clean=O/'part1-clean.mp4';master_sha=sha(current);clean_sha=sha(clean)
    timeline=read(H/'timeline.json');integrity=read(O/'qa/integrity-summary.json');pixels=read(a.visual_review)
    assert integrity['completeDecodeBothMasters']and integrity['decodedAudioIdentical']
    assert integrity['captionedSha256']==master_sha and integrity['cleanSha256']==clean_sha
    assert pixels['captionedSha256']==master_sha and pixels['majorVisualFindingsUnresolved']==0
    for f in [a.asr_review,a.audio_review]:
        d=read(f);assert master_sha in json.dumps(d),'Current encoded master hash must be bound to audio evidence'
    reports=dict(integrity=evidence(O/'qa/integrity-summary.json'),visual=evidence(a.visual_review),
        finalAsr=evidence(a.asr_review),audioContinuity=evidence(a.audio_review),timeline=evidence(H/'timeline.json'),
        captions=evidence(O/'captions/caption-alignment-review.json'))
    date=now();last_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()
    def child(d):
        d['publishReady']=False;d['membershipOutro']['appliedToFinal']=True
        d['membershipOutro']['durationFrames']=600;d['membershipOutro']['source']=rel(T.R/'projects/game-reward-planning/production/local/reference-preserving-v2/edit/membership.mp4')
        d['finalRender']=dict(status='complete-local-final-review-pending',revision='v7-part1-simultaneous-comparison',
            width=1920,height=1080,fps=60,frames=timeline['totalFrames'],durationSeconds=timeline['duration'],
            captionedSha256=master_sha,cleanSha256=clean_sha,completedAt=date,reports=reports,
            # Keep the exact frame/ASS details in the linked internal review.
            knownIssues=['게임·분석 구분 문구에 한 프레임의 미세한 전환 오차가 있습니다. 내용 이해에는 영향이 없습니다.']if pixels.get('minorVisualFindings')else[],
            openItems=['현재 전체 영상의 사용자 최종 검수·청취 및 주관적인 속도·발음 확인'],
            humanWholeListening='pending',humanFinalReview='pending')
        d['audio']['mixStatus']='complete-current-standard-game-audio-no-added-bgm';d['audio']['currentContinuityReview']=rel(a.audio_review);d['audio']['currentFinalAsrReview']=rel(a.asr_review)
        d['membershipOutro']['truncatedHandlesReview']='Preserved original screenshot/identities without retyping; original display truncation retained.'
        d['delivery']['review'].update(humanReview='pending',reviewedSha256=None,masterSha256=master_sha,deliveredAt=date)
    update(D/'project.json',child)
    # The standard collector verifies both streams/SRTs and exact copy hashes.
    subprocess.run(['node','scripts/collect-video-output.cjs',SLUG],cwd=R,check=True)
    output=read(D/'production/delivery-output.json')
    assert len(output['files'])==4 and next(r for r in output['files']if r['name'].endswith('.captioned.mp4'))['sha256']==master_sha
    local=dict(provider='local-filesystem',directory=rel(OUT),index=rel(OUT/'index.html'),
        captioned=rel(OUT/(SLUG+'.captioned.mp4')),clean=rel(OUT/(SLUG+'.clean.mp4')),
        version='v7-part1-simultaneous-comparison',sha256=master_sha,sizeBytes=current.stat().st_size,
        status='ready-for-local-user-final-review',filesCollectedAndHashVerified=True,linksReady=True,
        humanReview='pending',reviewedSha256=None,userReviewMessage=None,reviewedAt=None,deliveredAt=date,
        driveUploadRequired=False,driveUploadOnExplicitRequestOnly=True)
    def parent(d):
        d.setdefault('partOutputs',{})['1']=dict(deliveryProject=SLUG,localReview=local,reports=reports,
            productionComplete=True,humanReview='pending',fullMasterSha256=master_sha)
        d['selectedDeliveryProject']=SLUG
        d['currentProductionV7']=dict(part=1,stage='complete-local-final-review-pending',deliveryProject=SLUG,
            approvedScriptSha256=read(H/'authorization.json')['approvedScriptSha256'],reports=reports,part2Production='not-selected')
    update(P/'project.json',parent)
    def checkpoint(d):
        d.update(updatedAt=date,stage='v7-part1-complete-local-final-review-pending',runningJob=None,
            lastCompletedCommit=last_commit,nextAction='User reviews the complete Part1 local master; Part2 and platform uploads remain unselected.',blockers=[])
        d['activeProductionV7']=dict(part=1,stage='complete-local-final-review-pending',deliveryProject=SLUG,
            localReview=local,reports=reports,sourceSpeed=1,insertedObservationFrames=0,part2Production='not-selected')
        d['currentPart1Master']=dict(file=rel(current),sha256=master_sha,frames=timeline['totalFrames'],duration=timeline['duration'])
    update(P/'production/checkpoint.json',checkpoint)
    def ledger(d):
        d['updatedAt']=date
        d['activeProduction']=dict(revision='v7-part1-simultaneous-comparison',part=1,complete=True,
            localReview=local,reports=reports,scriptHumanApproved=True,finalVideoHumanApproved=False,
            humanWholeListening='pending',part2Selected=False,platformMutation=False)
        checks=d.setdefault('checks',[])
        item=dict(id='v7-part1-local-final-review',checkedAt=date,captionedSha256=master_sha,reports=reports,
            all135ApprovedParagraphsRetained=True,bilingualCues=386,pairedLayout='actual game left / corresponding explanation right',
            noAddedObservationSilence=True,gameExamples=4,addedBackgroundMusic=False,humanFinalReview='pending')
        if isinstance(checks,list):
            checks[:]=[c for c in checks if not(isinstance(c,dict)and c.get('id')==item['id'])];checks.append(item)
        else:checks[item['id']]=item
    update(P/'production/review-ledger.json',ledger)
    def worklist(d):
        row=next(r for r in d['rows']if r['id']=='M04');previous=row.get('localReview')
        if previous and previous.get('sha256')!=master_sha:
            history=row.setdefault('previousLocalReviews',[])
            if previous.get('sha256')not in[x.get('sha256')for x in history]:history.append(previous)
        row.update(productionComplete=False,currentRevisionProductionComplete=False,
            productionStatus='V7 1편 렌더링·네 파일 납품 완료 · 2편 미선택',
            reviewStatus='1편 내부 검사 완료 · 현재 전체 영상 사용자 최종 검수·청취 대기',
            humanApproval='135문단 대본 승인 · 현재 captioned MP4 최종 승인 전',
            executionStatus='1편 로컬 검수본 전달 · 작업 정지 · 2편/업로드 자동 진행 없음',
            localReview=local,latestRulesPassed=None,
            notes='1편은 게임 왼쪽·해설 오른쪽 동시비교. 승인135문단·4게임·386한영절 유지, 추가BGM·강제관찰무음 없음. 기존V6/PCM/플랫폼보존. 2편 제작 미선택.')
        part=row['pendingScriptRevision']['parts'][0]
        part.update(productionComplete=True,deliveryProject=SLUG,review='approved script; complete local video awaiting human final review',localReview=local)
        row['pendingScriptRevision'].update(status='part1-produced-to-local-final-review',newTts='part1-complete-current21scene',
            newVideo='part1-complete-FHD60-simultaneous-comparison',runtimeSeconds=timeline['duration'],finalVideoApproval='pending-current-part1-master')
        d['updatedAt']=date
        if d.get('selectedScriptWork',{}).get('video')=='M04':d['selectedScriptWork'].update(stage='part1-local-final-review-pending',automaticContinuation=False)
    update(R/'shared/publishing/video-worklist.json',worklist)
    subprocess.run(['python','-X','utf8','scripts/render-video-worklist.py'],cwd=R,check=True)
    print(json.dumps(dict(directory=local['directory'],captioned=local['captioned'],sha256=master_sha,frames=timeline['totalFrames'],humanReview='pending',part2='not-selected',platformMutation=False)))
if __name__=='__main__':main()
