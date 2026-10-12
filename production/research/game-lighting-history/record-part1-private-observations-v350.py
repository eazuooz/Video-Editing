"""Record actual same-ID private upload observations without approving pending checks."""
from pathlib import Path
import json, hashlib, shutil
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'projects/game-lighting-history-04-1'
PROOF = BASE / 'publishing/proof'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def require(name, *terms):
    text = (PROOF/name).read_text(encoding='utf-8')
    for term in terms: assert term in text, (name, term)
    return text

p = BASE/'publishing/youtube-upload.json'
j = read(p)
assert j['actualVideoId'] == 'YOsG939kaBw'
assert j['uploadVariant'] == 'captioned' and not j['cleanUploadAllowed']
assert sha(ROOT/j['uploadPath']) == j['video']['sha256']
qa = read(ROOT/'projects/game-lighting-history-04/production/part1-final-qa-v347.json')
assert qa['qaApproved'] and qa['captionedSha256'] == j['video']['sha256']
require('details-final-v350.dom.txt','YOsG939kaBw','game-lighting-history-04-1.captioned.mp4','고화질 완료','표준 화질 완료','비공개')
require('private-unscheduled-v350.dom.txt','radio "비공개" [checked]','radio "공개":')
require('card-reopened-v350.dom.txt','0분 0초 0프레임','프로그래밍 과외','"저장" [disabled]')
require('card-url-reopened-v350.dom.txt',j['coaching']['url'])
require('ko-manual-reopened-v350.dom.txt','한국어 세부정보','수동 자막','status: 게시됨')
require('en-manual-reopened-v350.dom.txt','영어 세부정보','수동 자막','status: 게시됨')
for name in ('endscreen-subscribe-reopened-v350.ax.txt','endscreen-playlist-reopened-v350.ax.txt','endscreen-link-reopened-v350.ax.txt'):
    require(name,'24:35:48','24:45:48')
require('endscreen-link-reopened-v350.ax.txt',j['coaching']['url'],'프로그래밍 과외')
require('no-claims-observed-v350.ax.txt','소유권 주장이 발견되지 않았습니다')
require('declarations-final-reopened-v350.ax.txt','아니요, 동영상에 유료 프로모션이 포함되어 있지 않습니다., Value: 1','예, AI가 사용되었습니다., Value: 1','제목 및 설명 언어 한국어')
require('watch-1080-ccoff-v350.ax.txt','사용 안함','1080p60','자막 사용 불가, Value: 0')
for name in ('watch-game-ccoff-v350.png','watch-ppt-ccoff-v350.png','watch-membership-full-ccoff-v350.png','endscreen-layout-v350.png','private-hd-v350.png'):
    assert (PROOF/name).stat().st_size > 10000
en = read(PROOF/'en-metadata-reopened-v350.json')
expected_en = (BASE/'publishing/upload-description.en.txt').read_text(encoding='utf-8').strip()
assert en[0]['value'].strip() == j['titleEn']
assert en[1]['value'].strip() == expected_en
ads = require('ads-final-v350.dom.txt','수익 창출 방법')
ads_passed = '- generic: 사용\n' in ads and '검사 중' not in ads
assert ads_passed or '검사 중' in ads
now = datetime.now(timezone.utc).isoformat()
thumb = BASE/'publishing/thumbnail-v1.png'
if not thumb.exists(): shutil.copyfile(ROOT/j['thumbnail']['path'], thumb)
assert sha(thumb) == j['thumbnail']['sha256']
j.update(status='saved-private-reviewed-settings-verified' if ads_passed else 'saved-private-reviewed-settings-awaiting-automatic-ad-check',uploaded=True,privateSaved=True,checksPassed=ads_passed,fullSettingsVerified=ads_passed,availableSettingsVerified=True,verifiedAt=now,descriptionEn=expected_en)
j['descriptionKo'] = (BASE/'publishing/upload-description.ko.txt').read_text(encoding='utf-8').strip()
j['thumbnail'].update(path=rel(thumb),saved=True,savedAndReopened=True,evidence=rel(PROOF/'private-hd-v350.png'))
for track in j['subtitles']: track.update(published=True,savedAndReopened=True,evidence=rel(PROOF/(track['language']+'-manual-reopened-v350.dom.txt')))
j['englishMetadata'].update(savedAndReopened=True,evidence=rel(PROOF/'en-metadata-reopened-v350.json'))
j['coaching'].update(cardSaved=True,endingLinkSaved=True,cardSavedAndReopened=True,cardEvidence=rel(PROOF/'card-url-reopened-v350.dom.txt'))
j['coachingCard'].update(status='saved-and-reopened-verified')
j['coachingEndingLink'].update(status='saved-and-reopened-verified')
j['endScreen'].update(ownSubscribeSaved=True,externalCoachingLinkSaved=True,playlistSaved=True,verified=True,reopenVerificationPending=False,playlistName=j['playlistAssignment']['name'],studioStart='24:35:48',studioEnd='24:45:48',studioTimeFormatFps=60,layoutSavedProof=rel(PROOF/'endscreen-layout-v350.png'))
j['endScreen']['processingTimeFormatObservation']='Before HD, Studio30fps displayed24:35:24–24:45:24. ReopenedHD60fps editor shows24:35:48–24:45:48: same1475.8–1485.8seconds/exact10seconds. No retiming.'
j['actualUpload'].update(observedProgressPercent=100,uploadCompleteObserved=True,verifiedAt=now,explicitWizardCompletionObserved=False,completionBasis='Same singleID saved private; actual SD/HD complete and uploaded1080p game/explanation/member pixels inspected. No duplicate upload.')
j['processing']={'sdComplete':True,'hdComplete':True,'watchVideoWidth':1920,'watchVideoHeight':1080,'watchDurationSeconds':1485.821,'localDurationSeconds':1485.8,'evidence':rel(PROOF/'details-final-v350.dom.txt')}
j['monetization'].update(automaticAdSuitability='enabled-after-checking' if ads_passed else 'pending-platform-checking',copyrightChecks='no-claims-observed',automaticResultBasis='Actual claims page reports no claims. Ads page '+('shows enabled' if ads_passed else 'still shows 검사 중')+'; pending is never a pass.',evidence=rel(PROOF/'ads-final-v350.dom.txt'),claimsEvidence=rel(PROOF/'no-claims-observed-v350.ax.txt'))
j['playlistAssignment']['reopenedVerified']=True
j['alteredContentDisclosure'].update(savedAndReopened=True,reason='Actual reopened AI yes selection; paid-promotion no, Korean audio/title-description language and Education verified.')
j['burnedCaptionVerification'].update(playerCaptionsOff=True,status='actual-uploaded-game-and-explanation-pixels-verified',resolution='1920x1080',gameSeconds=757.9,explanationSeconds=100,membershipSeconds=1477.22,evidence=[rel(PROOF/n) for n in ('watch-game-ccoff-v350.png','watch-ppt-ccoff-v350.png','watch-membership-full-ccoff-v350.png')])
j['uploadedPixels']={'ccOff':True,'gameCaptionVisible':True,'blackProjectedExplanationAndCaptionVisible':True,'original12MemberRowsTitleLogoVisible':True,'humanWholeListening':'pending','optionalPlayerCcPropagation':'Pending at actual watch check: optional CC unavailable despite both manual tracks published/reopened; burned captions visible.'}
j['schedulingAuthorized']=True
j['scheduling']={'saved':False,'targetDate':None,'reason':'Daily alternating09KST is authorized; preserve physical series order while earlier parts1/2 are unfinished. SameID private and unscheduled.'}
j['publishingFollowups']=[{'kind':'automatic-ad-suitability','status':'complete' if ads_passed else 'pending','actualVideoId':j['actualVideoId'],'evidence':rel(PROOF/'ads-final-v350.dom.txt')},{'kind':'pinned-comment','status':'pending-private-comments-availability','preparedPath':j['pinnedComment']['path']},{'kind':'optional-player-cc-propagation','status':'pending','manualStudioKoEnPublished':True},{'kind':'automatic-dubbing','status':'pending-platform-processing'}]
j['minimalPublishingProof']={'path':rel(PROOF/'private-hd-v350.png'),'sha256':sha(PROOF/'private-hd-v350.png'),'reason':'One saved Studio screenshot shows actual singleID, private state, captionedfilename, delivered illustrated thumbnail and SD/HD completion; pending automatic alert stays honest.'}
j['proofFiles']=[{'path':rel(f),'sha256':sha(f),'localOnly':f.name!='private-hd-v350.png'} for f in sorted(PROOF.iterdir()) if f.is_file()]
save(p,j)
manifest=BASE/'project.json'; mj=read(manifest)
mj.update(status='reviewed-private-delivered-git-pending' if ads_passed else 'reviewed-private-delivered-ad-check-and-git-pending',publishReady=False)
mj['publishing']={'receipt':rel(p),'actualVideoId':j['actualVideoId'],'uploaded':True,'privateSaved':True,'availableSettingsVerified':True,'settingsVerified':ads_passed,'automaticChecksObserved':ads_passed,'scheduled':False,'humanWholeListening':'pending','publicRightsApproved':False}
save(manifest,mj)
(BASE/'README.md').write_text('# Game rendering history 04-1\n\nActual private upload: https://youtu.be/YOsG939kaBw\n\nCurrent89148frames /1485.8seconds. Reviewed94bodyinputs,335KO/409EN cues,77 preserved narration paragraphs; exact60:40 body ratio(.2frame rounding). Final345 pair,347pixel/motion/audio QA and349four-file collection supersede historical candidates.\n\nBlack projected2.5D explanations and four distinct games: Horizon Forbidden West, The Outer Worlds2, Cyberpunk2077 and Fortnite; original branding and12-row10-second member ending retained. Actual1080p uploaded game/PPT captions verified withCCoff; manualKO/EN and English metadata posted and reopened, illustrated thumbnail/card/three end elements verified.\n\nAutomatic ad suitability '+('completed' if ads_passed else 'still pending')+'; no copyright claims observed. Whole human listening/pronunciation, final public rights, original Nimbus file, truncated original handles, backup, playerCC propagation, dubbing and private-comment posting remain pending. Private and unscheduled to preserve series order. Git delivery pending. Entire series unfinished.\n',encoding='utf-8')
(BASE/'.gitignore').write_text('/publishing/local/\n!/publishing/thumbnail-v1.png\n!/publishing/proof/private-hd-v350.png\n',encoding='utf-8')
regpath=ROOT/'shared/git-essential-images.json'; reg=read(regpath)
for f,purpose,reason in ((thumb,'delivery-thumbnail','Reviewed final illustrated yellow-header/white-ground channel-cat thumbnail explaining limited pixels and memory; actual saved/reopened thumbnail for singleIDYOsG939kaBw.'),(PROOF/'private-hd-v350.png','minimal-publishing-proof',j['minimalPublishingProof']['reason'])):
    entry={'path':rel(f),'purpose':purpose,'reason':reason,'reviewedAt':now,'sha256':sha(f)}
    old=[e for e in reg['entries'] if e['path']==entry['path']]
    assert not old or old[0]['sha256']==entry['sha256']
    if not old:reg['entries'].append(entry)
save(regpath,reg)
record={'schemaVersion':1,'observedAt':now,'actualVideoId':j['actualVideoId'],'receipt':rel(p),'uploaded':True,'privateSaved':True,'availableSettingsVerified':True,'fullSettingsVerified':ads_passed,'checksPassed':ads_passed,'fourOutputsCollected':True,'sdHdComplete':True,'ccOffGameExplanationPixelsReviewed':True,'manualKoEnPublishedReopened':True,'singleUpload':True,'gitDelivery':'pending','humanListening':'pending','publicRightsApproved':False,'remainingSeriesComplete':False,'nextAction':'Finish actual automatic ad result and guarded selective Git; then resume04-2/earlier parts from preserved checkpoints. Never repeat04-1TTS/mix/render/upload.'}
save(ROOT/'production/research/game-lighting-history/part1-private-observations-v350.json',record)
cpfile=ROOT/'production/research/game-lighting-history/checkpoint.json'; c=read(cpfile)
c['episode04Part1PrivateObservedV350']=record;c['episode04Part1LatestReality']={'updatedAt':now,**record};c['nextAction']=record['nextAction'];c['updatedAt']=now
save(cpfile,c)
print(json.dumps(record,ensure_ascii=False,indent=2))
