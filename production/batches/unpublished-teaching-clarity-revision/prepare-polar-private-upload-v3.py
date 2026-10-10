from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[3]
P = ROOT/'projects/game-math-polar-3d'
R = P/'revision-teaching-clarity-v1'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt=R/'publishing/youtube-upload-v3.json'
assert not receipt.exists()
receipt.parent.mkdir(exist_ok=True)
delivery=read(P/'production/delivery-output.json')
assert read(R/'final-media-adoption-v3.json')['allOtherProtectedInputsUnchanged']
files=[]
for f in delivery['files']:
    dest=ROOT/delivery['directory']/f['name']
    assert sha(dest)==f['sha256']==sha(ROOT/f['source'])
    files.append({'path':dest.relative_to(ROOT).as_posix(),'sha256':f['sha256'],'bytes':dest.stat().st_size})
old=read(P/'publishing/youtube-upload.json')
for lang,key in [('ko','metadata'),('en','englishMetadata')]:
    (receipt.parent/f'upload-description.{lang}.txt').write_text(old[key]['description']+'\n',encoding='utf-8')
thumbnail=P/'publish/assets/thumbnail.png'
assert sha(thumbnail)=='20b036117fc8b333a652a30803f1026cb3a93c250a6ca500f683ec3a1dc697a6'
write(R/'collection-private-preflight-v3.json',{'verifiedAt':datetime.now(timezone.utc).isoformat(),
    'actualCollectExitCode':0,'sessionId':38221,'exitObservedChunk':'894601',
    'sourceAndOutputAllFourHashesEqual':True,'files':files,
    'pixelEvidence':'projects/game-math-polar-3d/revision-teaching-clarity-v1/final-pixel-direct-review-v2.json',
    'audioEvidence':'projects/game-math-polar-3d/revision-teaching-clarity-v1/current-aac-complete-comparison-v2.json',
    'flowEvidence':'projects/game-math-polar-3d/revision-teaching-clarity-v1/final-flow-playback-direct-review-v3.json',
    'humanListeningApproved':False,'publicRightsApproved':False,'actualNewId':None})
write(receipt,{'slug':'game-math-polar-3d','status':'prepared-single-private-replacement',
    'baselineVideoId':'ZLOewk8JHXA','actualVideoId':None,'video':files[0],
    'metadata':old['metadata'],'englishMetadata':old['englishMetadata'],
    'files':files,'thumbnail':{'path':thumbnail.relative_to(ROOT).as_posix(),'sha256':sha(thumbnail),'savedAndReopened':False},
    'uploaded':False,'savedPrivate':False,'fullSettingsVerified':False,'checksVerified':False,
    'ccOffPixelsVerified':False,'gitDelivered':False,'scheduled':False,
    'humanListeningApproved':False,'pronunciationApproved':False,'publicRightsApproved':False,
    'baselineScheduleChanged':False,'pinnedCommentStatus':'pending-video-publication'})
qpath=ROOT/'production/batches/unpublished-teaching-clarity-revision/queue.json'
q=read(qpath);q['execution']['stage']='polar-collected-single-private-upload-pending'
q['execution']['collectionEvidence']=(R/'collection-private-preflight-v3.json').relative_to(ROOT).as_posix()
q['execution']['privateUploadReceipt']=receipt.relative_to(ROOT).as_posix();write(qpath,q)
print(json.dumps({'fourHashesMatch':True,'captionedSha256':files[0]['sha256'],'actualNewId':None}))
