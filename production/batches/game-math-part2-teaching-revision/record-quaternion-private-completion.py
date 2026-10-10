"""Seal actual HD/private/player evidence; listening and rights stay separate."""
from pathlib import Path
import json,hashlib,datetime,shutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
S=ROOT/'shared/output/game-math-part2-teaching-revision/studio-quaternion'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
now=datetime.datetime.now().astimezone().isoformat()
q=read(B/'queue.json');checkpoint=read(B/'quaternion-current-render-checkpoint.json')
registry=read(ROOT/'shared/git-essential-images.json');ignore=(ROOT/'.gitignore').read_text(encoding='utf8')
records=[]
for part,slug,ident in [('foundations','game-math-quaternion-foundations-v2','HdJw7bgKlbM'),('calculations','game-math-quaternion-calculations-v2','SPq_41LyOG0')]:
    P=ROOT/'projects'/slug;receipt=read(P/'publishing/youtube-upload.json');m=read(P/'project.json');t=read(P/'production/timeline.json')
    assert receipt['videoId']==ident and receipt['metadata']['privacyStatus']=='private'
    assert sha(ROOT/receipt['video']['path'])==receipt['video']['sha256']
    details=(S/f'{part}-processed-details.ax.txt').read_text(encoding='utf8')
    claims=(S/f'{part}-claims-none.ax.txt').read_text(encoding='utf8')
    monetization=(S/f'{part}-monetization-reopened.ax.txt').read_text(encoding='utf8')
    assert ident in details and '고화질 완료' in details and '비공개' in details and 'captioned.mp4' in details
    assert '동영상에서 소유권 주장이 발견되지 않았습니다' in claims and '수익에 영향을 미치지 않음' in claims
    assert 'text 사용' in monetization
    player=read(S/f'{part}-uploaded-cc-off.json');assert player['videoId']==ident
    observed=player['observation'];assert observed['cc'] and all(c['pressed']=='false' for c in observed['cc'])
    assert abs(observed['video'][0]['duration']-t['seconds'])<.1
    assert receipt['englishMetadata']['status']=='saved-published-in-English-language-row'
    assert all(s['status']=='manual-timed-file-saved-in-Studio' for s in receipt['subtitles'])
    assert receipt['endScreen']['status']=='saved-and-reopened-in-Studio' and receipt['endScreen']['memberProfilesNamesBadgesClear']
    proof=P/'publishing/proof';proof.mkdir(exist_ok=True)
    for name in ['processed-details.ax.txt','monetization-reopened.ax.txt','claims-none.ax.txt','uploaded-cc-off.json','uploaded-cc-off.png','english-saved.ax.txt','end-elements-reopened.ax.txt']:
        shutil.copy2(S/f'{part}-{name}',proof/name)
    image=proof/'uploaded-cc-off.png';rel=image.relative_to(ROOT).as_posix()
    registry['entries']=[x for x in registry['entries'] if x['path']!=rel]+[{'path':rel,'purpose':'minimal-publishing-proof','reason':'Directly viewed actual private YouTube player: burned Korean bottom-center captions with CC off; uploaded revision title and private identity visible.','sha256':sha(image),'reviewedAt':now,'project':slug}]
    exception='!/'+rel
    if exception not in ignore.splitlines():ignore=ignore.rstrip()+'\n'+exception+'\n'
    receipt.update(status='reviewed Korean-captioned revision uploaded privately; HD and saved bilingual publishing settings verified',privateUploadComplete=True,fullPublishingSettingsComplete=True,transferAndProcessing='complete; actual HD badge and uploaded-player pixels verified',completedAt=now)
    receipt['burnedCaptionVerification'].update(status='verified-in-actual-uploaded-player',playerCaptionsOff=True,proof=rel,playerObservation='publishing/proof/uploaded-cc-off.json')
    receipt['studioSettingsObserved'].update(processing='SD and HD complete',automaticAdAndRightsChecks='Actual claims UI: none found; no revenue effect. Reopened monetization: enabled. Platform review is not human listening or game-IP permission.',postProcessingProof='publishing/proof')
    receipt['humanListening']='pending';receipt['rightsReview']='Recording reuse statements retained; game-IP/human review pending'
    write(P/'publishing/youtube-upload.json',receipt)
    m['status']='reviewed-private-revision-delivered; schedule transition pending'
    m['publishing'].update(actualVideoId=ident,availableStudioSettingsSaved=True,privateUploadComplete=True,fullPublishingSettingsComplete=True)
    m['finalRender']['openItems']=['사람의 전체 청취 및 게임 IP 공개 권리 검토는 별도 미완료입니다.','늘어난 편수의 예약 교체는 검수된 수정본 순서와 실제 슬롯을 확인한 뒤 진행합니다.']
    m['publishReady']=False;write(P/'project.json',m)
    pixel=read(P/'production/current-pixel-review.json');pixel['uploadedPlayerCaptionProof']='publishing/proof/uploaded-cc-off.json';pixel['platformComplete']=True;write(P/'production/current-pixel-review.json',pixel)
    for e in checkpoint['episodes']:
        if e['slug']==slug:e.update(uploadComplete=True,actualVideoId=ident,privateSettingsComplete=True)
    records.append({'slug':slug,'videoId':ident,'url':'https://youtu.be/'+ident,'privateUploadComplete':True,'fullPrivateSettingsComplete':True,'sha256':receipt['video']['sha256'],'humanListening':'pending','gameIPHumanRights':'pending','scheduled':False})
write(ROOT/'shared/git-essential-images.json',registry);(ROOT/'.gitignore').write_text(ignore,encoding='utf8')
write(B/'quaternion-current-render-checkpoint.json',checkpoint)
rev=q['items'][0]['revision'];rev.update(privateUploadComplete=True,footageComparisonPassed=True,annotationMotionReviewPassed=True,uploadedPlayerCaptionProof=True,privateCompletion='quaternion-private-completion.json')
q['items'][0]['status']='reviewed-private-revision-delivered; schedule-and-git-pending'
q['execution'].update(currentSlug='game-math-rotation-interpolation',stage='Quaternion two private revisions verified after HD processing; interpolation single exclusive TTS batch and editable gameplay annotation preparation in progress.')
q['updatedAt']=now;write(B/'queue.json',q)
write(B/'quaternion-private-completion.json',{'observedAt':now,'episodes':records,'baselineScheduledUploadPreserved':True,'sourceComparison':'quaternion-source-corrections-v5.json','localMovingReview':'quaternion-native-review-history.json','currentRender':'quaternion-current-render-checkpoint.json','gitDelivery':'pending','scheduleReplacement':'pending','fullBatchCompleted':False})
print(json.dumps(records,ensure_ascii=False))
