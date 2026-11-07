"""Bind completed files to the finite local review; no platform actions."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys,html,os
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];L=B/'local/real-clips-v2'
sys.path.insert(0,str(R/'production/batches/design-25-30-review-actions-20261029'))
from scoped_json import load,patch
read=lambda p:json.loads(p.read_text('utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def relative(p):return p.relative_to(R).as_posix()

def main():
    plan=read(H/'revision-plan.json');qa=read(H/'qa-decisions.json');native=read(H/'editable-assets.json');now=datetime.now(timezone.utc).isoformat();records=[]
    retained={'A01':'이미 실제 GAS 걷기·정지·회전·손 뻗기 클립을 사용하는 시연 유지','A12':'눈·입·눈썹의 독립 제어와 표정 시연 유지','A17':'FK·IK·팔꿈치 힌트·관절 수 비교 유지','A18':'고개·손목·시선의 두 축 제어 시연 유지'}
    for e in plan['episodes']:
        ep=e['id'];p=R/'projects'/e['slug'];local=p/'production/local/real-clips-v2';revised=ep not in retained
        if revised:
            receipt=read(local/'verification.json');directory=R/receipt['directory'];digest=receipt['masters']['captioned']['sha256'];duration=receipt['durationSeconds'];changed=len(receipt['changedCuts'])
            assert qa[ep]['captionedSha256']==digest and qa[ep]['sampledVisualReview']=='passed'
            studies=[]
            for f in sorted((L/'studies').glob(ep+'-*.json')):
                if f.stem in ('A04-jab','A11-upper'):continue
                d=read(f);studies.append({k:v for k,v in d.items() if k not in ('tracks','animations','motionEvidence','collisionEvidence','trace')})
            description='실제 팩 클립 기반 시연 교체 · '+str(changed)+'개 설명 컷'
            proof={'masters':receipt['masters'],'baselineNarrationPreserved':True,'baselineAudioSHA256':receipt['baselineAudioSHA256'],'preservedCuts':receipt['preservedCuts'],'changedCuts':receipt['changedCuts'],'nativeStudies':studies}
        else:
            old=read(p/'production'/e['baselineRevision']/'checkpoint.json');directory=R/old['directory'];digest=old.get('captionedMasterSha256',old.get('masterSha256'));duration=old.get('durationSeconds');changed=0;description=retained[ep]
            if duration is None:
                import subprocess
                duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(directory/(e['slug']+'.captioned.mp4'))]))
            proof={'baselineCheckpoint':relative(p/'production'/e['baselineRevision']/'checkpoint.json'),'retentionReason':description,'originalBytesPreserved':True}
            assert qa[ep]['sampledVisualReview']=='passed' and qa[ep]['captionedSha256']==digest
        files=[]
        for kind in ('clean.mp4','captioned.mp4','ko.srt','en.srt'):
            f=directory/(e['slug']+'.'+kind);assert f.is_file();files.append(dict(kind=kind,path=relative(f),sha256=sha(f),bytes=f.stat().st_size))
        assert next(f['sha256'] for f in files if f['kind']=='captioned.mp4')==digest
        ledger=dict(episode=ep,revision='real-clips-v2' if revised else e['baselineRevision'],status='local-combined-review-ready',checkedAt=now,captionedMasterSha256=digest,durationSeconds=duration,directory=relative(directory),files=files,changeSummary=description,changedExplanationCuts=changed,technicalQA=proof,visualQA=qa[ep],humanReviewedThisHash=False,actualWholeListeningThisRevision=False,unchangedAudioReviewEvidenceReused=revised,platformMutation=False)
        dest=p/'production/real-clips-v2/checkpoint.json';write(dest,ledger)
        write(dest.with_name('rebuild-plan.json'),dict(episode=ep,revision=ledger['revision'],visualOnlyRevision=revised,baselineRevision=e['baselineRevision'],batchPlan=relative(H/'revision-plan.json'),producer=relative(H/'assemble_revision.py') if revised else None,nativeDefinitionProducer=relative(H/'prepare_all.py') if revised else None,nativeBuild=relative(H/'build_studies.py') if revised else None,sourceMotionRequest=relative(H/'source-motion-request.json'),sourceCatalog=relative(H/'source-motion-catalog.json'),assetRights=relative(H/'asset-use.json'),editableNativeAssets=relative(H/'editable-assets.json'),deliveryLedger=relative(dest),audioPolicy='Reuse baseline audio and captions; no new TTS',productionBoundary='Local final review; no automatic upload',prerequisites=['User-owned imported UE 5.8 packs in GameAnimationSample','Original baseline media and voice retained locally','Python numpy scipy Pillow, FFmpeg NVENC, UE 5.8 Python commandlets']))
        e.update(status='revised-local-review-ready' if revised else 'retained-specific-study-reviewed',selectedDelivery=relative(directory),captionedSha256=digest,changeSummary=description,ledger=relative(dest),finalHumanReview='pending')
        records.append(dict(id=ep,slug=e['slug'],title=read(p/'project.json')['title'],revision=ledger['revision'],revised=revised,description=description,reviewFocus=e['teachingPurpose'],durationSeconds=duration,captionedSha256=digest,directory=relative(directory),files=files,ledger=relative(dest)))
    plan.update(status='combined-local-review-ready',revisedVideos=sum(r['revised'] for r in records),retainedVideos=sum(not r['revised'] for r in records),humanReview='pending',platformMutation=False)
    write(H/'revision-plan.json',plan)
    write(H/'review-manifest.json',dict(createdAt=now,status='ready-for-human-review',records=records,totalSeconds=sum(r['durationSeconds'] for r in records),nativeAssetCount=len(native['files']),uploadAuthorized=False))
    cp=B/'checkpoint.json';raw=cp.read_bytes();section=load(raw)['fabPreparation20261107'];section.update(status='combined-local-review-ready',newVideoRenders=14,newFinalVideoRenders=14,retainedVideos=4,nativePrototypeStudies=len(native['studies']),editableAssets=relative(H/'editable-assets.json'),reviewManifest=relative(H/'review-manifest.json'),finalHumanReview='pending',nextAction='User reviews the eighteen-version local collection; no upload/publication/schedule/delete authorized.')
    cp.write_bytes(patch(raw,['fabPreparation20261107'],section))
    # Exact selected worklist rows only; platform/upload fields are untouched.
    wp=R/'shared/publishing/video-worklist.json';raw=wp.read_bytes();w=load(raw);fields=[]
    for rec in records:
        index=next(i for i,r in enumerate(w['rows']) if r['id']==rec['id']);changes=dict(productionComplete=True,productionStatus=rec['description'],reviewStarted=True,reviewStatus='1080p60·전체 디코딩·변경 화면 표본 검토 완료 · 통합 사용자 검수 대기',executionStatus='애니메이션 18편 통합 검수본 준비',localMasterAvailable=True,captionedMasterSha256=rec['captionedSha256'],deliveryLedger=rec['ledger'],updatedAt=now)
        for key,value in changes.items():raw=patch(raw,['rows',index,key],value)
        fields.append(dict(id=rec['id'],fields=changes))
    wp.write_bytes(raw);write(H/'worklist-overlay.json',fields)
    md=R/'docs/VIDEO_WORKLIST.md';raw=md.read_bytes();text=raw.decode('utf-8-sig');lines=text.splitlines(keepends=True)
    for rec in records:
        i=next(i for i,line in enumerate(lines) if line.startswith('| '+rec['id']+' | '));line=lines[i];last=line.rfind('|');before=line.rfind('|',0,last)
        newline='\r\n' if line.endswith('\r\n') else '\n' if line.endswith('\n') else ''
        lines[i]=line[:before+1]+' '+('실제 클립 수정본' if rec['revised'] else '전용 시연 유지')+' · 통합 검수 대기 |'+newline
    md.write_bytes((b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+''.join(lines).encode('utf-8'))
    print('Bound review records:',len(records),flush=True)
if __name__=='__main__':main()
