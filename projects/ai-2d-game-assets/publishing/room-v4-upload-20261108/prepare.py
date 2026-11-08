"""Prepare the explicitly approved latest-game master; no platform calls."""
from pathlib import Path
import json,hashlib,shutil
from datetime import datetime
from zoneinfo import ZoneInfo
H=Path(__file__).resolve().parent;R=H.parents[3];P=R/'projects/ai-2d-game-assets';V=P/'production/room-v4-video'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
t=datetime.now(ZoneInfo('Asia/Seoul')).isoformat()
delivery=read(V/'delivery.json');master=next(f for f in delivery['files'] if f['name'].endswith('captioned.mp4'))
assert sha(Path(master['path']))==master['sha256']=='97003cf1db875a25aa862f1cf0acdf68fe21d8667b094b268af0be4b12ed848f'
auth=dict(at=t,userText='새 검수본 확인했어. 이 버전 업로드',reviewUrl='http://127.0.0.1:9287/',
          sameVersionUserReview=True,masterPath=master['path'],masterSha256=master['sha256'],youtubeUploadAuthorized=True,
          privacy='private',publication=False,scheduling=False,deletion=False,oldDraftPreserved='t7Li-IzqJyk',
          advertiserAssessment='user-only submission',scope='Upload this reviewed file once and finish available settings; preserve site v6 and existing uploads.')
save(H/'authorization.json',auth)
old=P/'publishing/room-v3-upload-20261108'
for name in ['title.ko.txt','title.en.txt','tags.json','tags.txt','pinned-comment.ko.txt','pinned-comment.en.txt']:
    shutil.copyfile(old/name,H/name)
for name in ['description.ko.txt','description.en.txt','chapters.json']:
    shutil.copyfile(V/name,H/name)
packet=dict(preparedAt=t,authorization=auth,master=master,delivery=delivery,
            title={lang:(H/f'title.{lang}.txt').read_text('utf-8').strip() for lang in ['ko','en']},
            descriptions={lang:(H/f'description.{lang}.txt').as_posix() for lang in ['ko','en']},
            thumbnail=(old/'thumbnail-v1.png').as_posix(),thumbnailSha256=sha(old/'thumbnail-v1.png'),
            videoLanguage='ko',titleDescriptionLanguage='ko',category='Education',oldDraftPreserved='t7Li-IzqJyk')
for lang in ['ko','en']:assert len((H/f'description.{lang}.txt').read_text('utf-8'))<=5000
save(H/'upload-packet.json',packet)
path=R/'shared/publishing/video-production-control.json';control=read(path);entry=control['ai2dLatestGameVideo20261108']
entry.update(sameVersionUserReview=True,youtubeAuthorizedNow=True,status='reviewed-upload-authorized',userApproval=auth,updatedAt=t)
save(path,control)
for name in ['checkpoint.json','delivery.json','final-review.json']:
    path=V/name;j=read(path);j['userReview']=auth;j['youtubeAuthorizedNow']=True
    if name=='checkpoint.json':j.update(stage='reviewed-upload-authorized',next='Upload approved latest-game master privately once; complete settings; user handles ad suitability',humanReview=True)
    save(path,j)
ledger_path=P/'production/review-ledger.json';ledger=read(ledger_path);ledger['latestVersionUserReview']=auth;save(ledger_path,ledger)
print(json.dumps({'authorizedMaster':master['sha256'],'packet':str(H/'upload-packet.json')},ensure_ascii=False))
