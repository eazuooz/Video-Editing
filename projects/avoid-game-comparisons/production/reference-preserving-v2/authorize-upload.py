"""Record explicit user upload/next-video scope against the current collected master."""
from pathlib import Path
import json, hashlib, datetime
R=Path(__file__).resolve().parents[4]
P=R/'projects/avoid-game-comparisons'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def write(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
master=R/'output/avoid-game-comparisons/avoid-game-comparisons.captioned.mp4'
digest=hashlib.sha256(master.read_bytes()).hexdigest()
assert digest=='7138b6b9c51e8c2374aa0a4c64cece4defb6f7d6ab42b46cb0dadabb756e16e2'
auth={'userMessage':'이거 업로드해줘 그리고 다음영상 제작해줘~','recordedAt':now,'version':'reference-preserving-v2/screenshots-v1','captionedSha256':digest,'master':master.relative_to(R).as_posix(),'privacy':'private','scope':'Upload current collected screenshot-supported master and finish available settings; preserve existing uploads. Then produce next game-design video making-game-sequels only.','basis':'User approved screenshot style, then requested upload using the same canonical output link. Prior quoted395fcc1 handoff is historical; current link resolves to screenshot revision.','publicPublicationAuthorized':False,'baselineDeletionAuthorized':False,'humanWholeListeningClaimed':False}
cpath=R/'shared/publishing/video-production-control.json';c=read(cpath)
assert c['selectedVideo']=='avoid-game-comparisons'
c['selectedVideoFinalReview'].update(status='user-authorized-private-upload',userReview=auth,youtubeUploadAuthorized=True)
c['selectedVideoRevision']['youtubeAuthorized']=True
c['explicitNextVideoAuthorization']={'slug':'making-game-sequels','userMessage':auth['userMessage'],'recordedAt':now,'after':'avoid-game-comparisons private upload and available settings','scope':'One selected video through final-review delivery; no automatic further video'}
c['updatedAt']=now;write(cpath,c)
cp=P/'production/latest-checkpoint.json';d=read(cp);d['currentRevision'].update(youtubeUploadAuthorized=True,uploadAuthorization=auth,humanReview='User explicitly authorized current local master upload; whole-listening/pronunciation evidence remains separately pending');write(cp,d)
lp=P/'production/reference-preserving-v2/review-ledger.json';l=read(lp);l['uploadAuthorization']=auth;write(lp,l)
mp=P/'publishing/reference-preserving-v2/metadata.json';m=read(mp);m.update(titleEn='Why “Like Mario” Does Not Explain Your Game Idea',youtubeUploadAuthorized=True,userReview=auth,visualRevision='screenshots-v1');write(mp,m)
en=P/'publishing/reference-preserving-v2/description.en.txt'
s=en.read_text(encoding='utf8')
for a,b in [('익숙한 이름을 찾는 이유','Why familiar names come to mind'),('아직 없는 게임을 전달하기','Explaining a game that does not exist yet'),('왜 이 게임을 선택해야 할까','Why choose this game?'),('비교를 금지하는 규칙은 아니다','Comparison can still help'),('누군가에게 마리오는 이 장면','What Mario means to one player'),('다른 사람은 공간과 능력을 떠올린다','Another player imagines exploration and abilities'),('공통된 장면부터 만들기','Establishing a shared picture'),('세 문장으로 바꿔 말하기','Rewriting the idea in three sentences'),('잘 전달됐는지 확인하기','Checking what the listener understood'),('비교는 공통 이해 위에 얹기','Using comparisons after shared understanding'),('이름 없이도 남는 설명','An explanation that works without the name')]:s=s.replace(a,b)
en.write_text(s,encoding='utf8')
print('Current master verified; private upload and one next video explicitly authorized')
