"""Persist actually saved Studio settings while the media transfers continue."""
from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
D=ROOT/'shared/output/game-math-part2-teaching-revision/studio-quaternion'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
records=[('game-math-quaternion-foundations-v2','foundations','HdJw7bgKlbM','20:00:15','20:10:15'),('game-math-quaternion-calculations-v2','calculations','SPq_41LyOG0','19:03:08','19:13:07')]
for slug,prefix,video_id,start,end in records:
    P=ROOT/'projects'/slug;p=P/'publishing/youtube-upload.json';d=read(p)
    assert d['videoId']==video_id
    proof={}
    for name in ['private-upload-in-progress','english-saved','end-elements-reopened']:
        ax=D/f'{prefix}-{name}.ax.txt';png=D/f'{prefix}-{name}.png'
        assert ax.exists() and png.exists()
        text=ax.read_text(encoding='utf8')
        if name=='english-saved':assert '게시됨' in text and '영어' in text and '1개 게시됨' in text
        if name=='private-upload-in-progress':assert '비공개' in text and '업로드' in text
        proof[name]={'ax':ax.relative_to(ROOT).as_posix(),'axSha256':hashlib.sha256(ax.read_bytes()).hexdigest(),'screenshot':png.relative_to(ROOT).as_posix(),'screenshotSha256':hashlib.sha256(png.read_bytes()).hexdigest()}
    d['status']='private saved; media upload ongoing; available bilingual and publishing settings saved'
    d['metadata']['privacyStatus']='private'
    d['englishMetadata'].update(status='saved-published-in-English-language-row',platformLanguageLabel='영어',platformLanguageCodeVerified=False)
    for s in d['subtitles']:s.update(status='manual-timed-file-saved-in-Studio',platformLanguageLabel='한국어' if s['language']=='ko' else '영어')
    d['thumbnail']['status']='saved-prepared-reviewed-thumbnail-in-Studio'
    d['coachingCard'].update(status='saved-in-Studio',startSeconds=0,teaser='게임 개발 1:1 코칭',originalCatIdentityUsed=True)
    d['endScreen'].update(status='saved-and-reopened-in-Studio',platformTimebase='30fps display',observedStart=start,observedEnd=end,threeElementsVisible=True,memberProfilesNamesBadgesClear=True)
    d['coachingEndingLink'].update(status='saved-and-reopened-in-Studio',originalCatIdentityUsed=True)
    d['studioSettingsObserved']={'observedAt':now,'playlist':'게임수학 PART2','originalLanguage':'한국어','category':'교육','madeForKids':False,'alteredOrSyntheticContent':True,'paidPromotion':False,'monetization':'사용','adSelfAssessment':'none; submitted and locked','automaticAdAndRightsChecks':'pending media upload/processing','proof':proof}
    d['privateUploadComplete']=False;d['fullPublishingSettingsComplete']=False
    d['transferAndProcessing']='in progress; do not close uploading tabs; no upload completion inferred from saved settings'
    d['humanListening']='pending';d['burnedCaptionVerification']['status']='pending-real-uploaded-frame-review'
    write(p,d)
    m=read(P/'project.json');m['publishing'].update(actualVideoId=video_id,availableStudioSettingsSaved=True,privateUploadComplete=False,fullPublishingSettingsComplete=False);write(P/'project.json',m)
q=read(B/'queue.json');q['items'][0]['revision']['availableStudioSettingsSaved']=True
q['execution']['stage']='Both quaternion current deliveries collected and played1x; private drafts saved with KO/EN/metadata/cards/end screens; media transfer and uploaded-player QA pending. Interpolation CPU preparation progressing.'
q['updatedAt']=now;write(B/'queue.json',q)
print('Both actual private drafts retain saved bilingual settings; transfer/processing/caption proof are explicitly pending.')
