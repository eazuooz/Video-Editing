"""Seal the actual same-ID Studio observations; no platform writes or future SHA."""
from pathlib import Path
import importlib.util, shutil
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
root=m.ROOT
p=root/'projects/game-lighting-history-04-3/publishing/youtube-upload.json'
j=m.read(p)
assert j['actualVideoId']=='ydW9Glmh0nM'
assert j['uploadVariant']=='captioned' and not j['cleanUploadAllowed']
assert m.sha(root/j['uploadPath'])==j['uploadSha256']
proof=root/'projects/game-lighting-history-04-3/publishing/local/proof-v164'
def full(name,*required):
    text=(proof/name).read_text(encoding='utf-8')
    for term in required: assert term in text,(name,term)
    return text
full('private-hd-saved.ax.txt','ydW9Glmh0nM','game-lighting-history-04-3.captioned.mp4','고화질 완료','표준 화질 완료','비공개')
full('private-unscheduled.ax.txt','비공개, Value: 1','공개, Value: 0')
full('card-saved-url.ax.txt',j['coaching']['url'],'프로그래밍 과외','0분 0초 0프레임')
for name in ('end-screen-subscribe-saved.ax.txt','end-screen-playlist-saved.ax.txt','end-screen-link-saved.ax.txt'):
    full(name,'25:23:58','25:33:58')
full('end-screen-subscribe-saved.ax.txt','구독: 얌얌코딩 (게임 개발)')
full('end-screen-playlist-saved.ax.txt','Physically Based Rendering (PBR) 물리 기반 렌더링')
full('end-screen-link-saved.ax.txt',j['coaching']['url'],'프로그래밍 과외')
full('ads-enabled-check-complete.ax.txt','text 사용','Value: 1')
full('no-claims-observed.ax.txt','동영상에서 소유권 주장이 발견되지 않았습니다')
full('declarations-saved.ax.txt','아니요, 동영상에 유료 프로모션이 포함되어 있지 않습니다., Value: 1','예, AI가 사용되었습니다., Value: 1')
full('english-saved.ax.txt',j['titleEn'])
for name in ('uploaded-game-cc-off.jpg','uploaded-explanation-cc-off.jpg','uploaded-membership.jpg','end-screen-saved.jpg','thumbnail-saved.jpg'):
    assert (proof/name).stat().st_size>10000
observed=m.stamp()
j.update(status='saved-private-reviewed-settings-verified',uploaded=True,privateSaved=True,checksPassed=True,fullSettingsVerified=True,verifiedAt=observed)
j['thumbnail'].update(saved=True,savedAndReopened=True,evidence=m.rel(proof/'thumbnail-saved.jpg'))
j['coaching'].update(cardSaved=True,endingLinkSaved=True,cardSavedAndReopened=True,cardEvidence=m.rel(proof/'card-saved-url.ax.txt'))
j['endScreen'].update(ownSubscribeSaved=True,externalCoachingLinkSaved=True,playlistSaved=True,verified=True,reopenVerificationPending=False,studioStart='25:23:58',studioEnd='25:33:58',studioTimeFormatFps=60,layoutSavedProof=m.rel(proof/'end-screen-saved.jpg'))
j['endScreen']['processingTimeFormatObservation']='Before HD completion Studio displayed 25:23:29–25:33:29 at30fps; saved editor after HD uses25:23:58–25:33:58 at60fps. Both represent1523.966667–1533.966667, exactly10 seconds. No retiming or resave.'
j['actualUploadProgress'].update(uploadPercent=100,uploadComplete=True,thumbnailReopenedVerified=True,observedAt=observed,next='Selective normal Git delivery, then resume remaining series parts from actual checkpoints.')
j['actualUploadProgress']['completionBasis']='Same ID playable1920x1080; Studio SD/HD complete, saved private selection and no schedule. Explicit wizard completion modal not observed and remains false.'
j['processing']={'sdComplete':True,'hdComplete':True,'watchVideoWidth':1920,'watchVideoHeight':1080,'watchDurationSeconds':1533.981,'localDurationSeconds':1533.9666666667,'evidence':m.rel(proof/'private-hd-saved.ax.txt')}
j['monetization'].update(enabledSavedAndReopened=True,automaticAdSuitability='enabled-after-checking',copyrightChecks='no-claims-observed',automaticResultBasis='Ads page changed from 검사 중 to 사용; details alert changed from 검토 중 to —. Claims page reports no claims; this is not public rights approval.',evidence=m.rel(proof/'ads-enabled-check-complete.ax.txt'))
j['declarations']['savedAndReopened']=True
j['uploadedPixels']={'ccOff':True,'resolution':'1920x1080','gameSeconds':144.330132,'explanationSeconds':10,'membershipSeconds':1525.57,'gameCaptionVisible':True,'blackProjectedExplanationAndCaptionVisible':True,'original12MemberRowsTitleLogoVisible':True,'evidence':[m.rel(proof/n) for n in ('uploaded-game-cc-off.jpg','uploaded-explanation-cc-off.jpg','uploaded-membership.jpg')],'optionalPlayerCcPropagation':'At watch verification optional CC still unavailable although both manual tracks were posted and reopened in Studio; burned captions were visible. Optional propagation remains pending.'}
j['scheduling'].update(saved=False,targetDate=None,reason='Preserve ascending physical publication order while earlier parts are still in production. This same ID is private and unscheduled.')
j['publishingFollowups']=[{'kind':'pinned-comment','status':'pending-private-comments-availability','preparedPath':'projects/game-lighting-history-04-3/publishing/pinned-comment.ko.txt'},{'kind':'optional-player-cc-propagation','status':'pending','manualStudioKoEnPublished':True},{'kind':'automatic-dubbing','status':'pending-platform-processing'}]
j['proofFiles']=[{'path':m.rel(q),'sha256':m.sha(q),'localOnly':True} for q in sorted(proof.iterdir()) if q.is_file()]
minimal=root/'projects/game-lighting-history-04-3/publishing/proof/private-hd-v164.jpg'
minimal.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(proof/'private-hd-saved.jpg',minimal)
j['minimalPublishingProof']={'path':m.rel(minimal),'sha256':m.sha(minimal),'reason':'One saved Studio view records actual ID, private state, captioned filename, illustrated thumbnail and completed SD/HD. Other repeated QA/screenshots stay local.'}
m.save(p,j)
manifest=root/'projects/game-lighting-history-04-3/project.json';mj=m.read(manifest)
mj.update(status='reviewed-private-delivered-git-pending',publishReady=False)
mj['publishing']={'receipt':m.rel(p),'actualVideoId':j['actualVideoId'],'privateSaved':True,'uploaded':True,'settingsVerified':True,'automaticChecksObserved':True,'scheduled':False,'humanWholeListening':'pending','publicRightsApproved':False}
m.save(manifest,mj)
ignore=root/'projects/game-lighting-history-04-3/.gitignore';text=ignore.read_text(encoding='utf-8')
for line in ('/publishing/local/','!/publishing/proof/private-hd-v164.jpg'):
    if line not in text.splitlines():text=text.rstrip()+'\n'+line+'\n'
ignore.write_text(text,encoding='utf-8')
regpath=root/'shared/git-essential-images.json';reg=m.read(regpath)
entry={'path':m.rel(minimal),'purpose':'minimal-publishing-proof','reason':j['minimalPublishingProof']['reason'],'reviewedAt':observed,'sha256':m.sha(minimal)}
old=[e for e in reg['entries'] if e['path']==entry['path']]
assert not old or old[0]['sha256']==entry['sha256']
if not old:reg['entries'].append(entry);m.save(regpath,reg)
cpfile=root/'production/research/game-lighting-history/checkpoint.json';cp=m.read(cpfile)
cp.update(updatedAt=observed,status='episode04-physical03-reviewed-private-delivered-git-pending')
cp['episode04Part3PrivateCompletedV164']={'actualVideoId':j['actualVideoId'],'receipt':m.rel(p),'uploaded':True,'privateSaved':True,'fullSettingsVerified':True,'checksObserved':True,'sdHdComplete':True,'ccOffGameExplanationPixelsReviewed':True,'singleUpload':True,'gitDelivery':'pending','humanListening':'pending','publicRightsApproved':False,'remainingSeriesComplete':False}
cp['nextAction']='Selectively push current04-3 reviewed delivery records using isolated index; preserve foreign staged cleanup. Then resume04-1/04-2 and earlier logical episodes from preserved media checkpoints. No repeat completed04-3 synthesis/render/upload.'
m.save(cpfile,cp)
print('Verified same-ID private delivery ydW9Glmh0nM: SD/HD, saved settings, ads enabled/no claims, CC-off game/black2.5D, original membership. Human/rights/comment/optionalCC pending; remaining series incomplete.')
