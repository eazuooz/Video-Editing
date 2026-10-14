"""Record explicit review approval and prepare its1080p60 production master."""
from pathlib import Path
import datetime, hashlib, json
R=Path(__file__).resolve().parents[2];S='ai-game-development-human-craft';P=R/'projects'/S
Q=R/f'shared/output/{S}/revision-v2';U=Q/'youtube-private';U.mkdir(exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
c=read(R/'shared/publishing/video-production-control.json');assert c['selectedVideo']==S
m=read(P/'project.json');cp=read(P/'production/checkpoint.json');plan=read(P/'planning/production-plan.json');ledger=read(P/'production/review-ledger.json')
d=m['delivery']['driveReview'];assert d['fileId']=='1alrcfkbKhWu4MdhrPCg935MrUBX1JU8j' and d['version']=='v2'
assert sha(R/d['localPath'])==d['localSha256']==d['remoteSha256']
assert read(R/d['qualityEvidence'])['status']=='pass-agent-mobile-review-copy'
master=R/d['sourceMasterPath'];master_sha=sha(master)
assert master_sha==d['sourceMasterSha256']==read(R/d['qualityEvidence'])['sourceSha256']
approval={'status':'approved-by-user','message':'좋다 업로드해줘 우리 업로드 규칙 따라서','recordedAt':now,'version':'v2','driveFileId':d['fileId'],'sha256':d['localSha256'],'scope':'User accepts this Drive version and requests upload under current rules. Private upload only; no publication, scheduling, replacement or next video.','listeningScope':'User accepted current version; no fabricated claim of detailed per-range human listening.'}
for target in [d,cp['finalReviewDelivery'],plan['finalReviewDelivery'],ledger['finalDriveReview'],c['finalReviewDelivery']]:
 target.update(userReviewMessage=approval['message'],reviewedAt=now,reviewDecision='approved-for-private-youtube-upload',approval=True)
plan['approvals']['finalDriveUserReview'].update(status='approved-by-user',userMessage=approval['message'],reviewedAt=now)
ledger['checks'].append({'id':'v2-user-final-review-and-private-upload-authorization','revision':'v2',**approval})
cp.update(updatedAt=now,stage='youtube-private-upload-authorized',pending=['Private YouTube upload and actual saved/reopened settings'],nextAction='Upload exact approved Drive v2 bytes once; verify available Studio settings and deliver selective Git.')
cp['revision']['status']='approved-for-private-upload'
m['status']=cp['stage'];m['revision']['status']='approved-for-private-upload'
c['updatedAt']=now;c['newProductionAuthorization']['latestUploadInstruction']=approval
f=P/'publishing/youtube-upload.json';assert not f.exists(),'Inspect an existing upload receipt before preparing another upload.'
meta={}
for lang in ['ko','en']:
 text=(P/f'publishing/youtube.{lang}.md').read_text(encoding='utf-8').strip();title,body=text.split('\n',1)
 assert len(title)<=100 and len(body.strip())<=5000
 meta[lang]={'title':title,'description':body.strip()}
 for url in ['https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328','https://www.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ/join']:
  assert url in body
subs=[{'language':lang,'path':f'output/{S}/{S}.{lang}.srt','sha256':sha(R/f'output/{S}/{S}.{lang}.srt'),'status':'pending','method':'manual-file-upload-with-timing'} for lang in ['ko','en']]
receipt={'schemaVersion':1,'status':'prepared-not-uploaded','videoId':None,'approval':approval,'video':{'path':d['sourceMasterPath'],'sha256':master_sha,'bytes':master.stat().st_size,'seconds':d['durationSeconds'],'width':1920,'height':1080,'fps':60,'variant':'captioned','selectionReason':'Publish the1080p60 captioned master corresponding to the approved Drive review copy; verify hash and conversion evidence. Never upload the mobile compression copy.'},'metadata':{**meta['ko'],'privacyStatus':'private','language':'ko','madeForKids':False},'englishMetadata':meta['en'],'thumbnail':{'path':f'projects/{S}/publishing/thumbnail-v1.png','sha256':sha(P/'publishing/thumbnail-v1.png'),'status':'pending'},'subtitles':subs,'coachingCard':{'url':'https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328','title':'프로그래밍 과외','teaser':'프로그래밍 과외','startSeconds':0,'status':'pending'},'endScreen':{'startSeconds':d['durationSeconds']-10,'endSeconds':d['durationSeconds'],'elements':['relevant-channel-playlist','subscribe-own-channel','programming-coaching-external-link'],'status':'pending'},'pinnedComment':{'path':f'projects/{S}/publishing/pinned-comment.ko.txt','status':'pending-video-publication','commentId':None,'pinnedVerified':False},'monetization':{'enable':True,'status':'pending-honest-content-self-review'},'scheduled':False,'fullSettings':False,'evidenceDirectory':U.relative_to(R).as_posix()}
write(f,receipt)
for path,obj in [(P/'project.json',m),(P/'production/checkpoint.json',cp),(P/'planning/production-plan.json',plan),(P/'production/review-ledger.json',ledger),(R/'shared/publishing/video-production-control.json',c)]:write(path,obj)
print(json.dumps({'approved':d['fileId'],'videoHash':receipt['video']['sha256'],'descriptionLengths':{k:len(v['description']) for k,v in meta.items()},'file':receipt['video']['path']}))
