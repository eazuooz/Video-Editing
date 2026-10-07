"""Record actual Studio evidence and register only its reviewed delivery thumbnail.
Usage: python record-verified-private.py <slug>
Does not upload, approve pixels, regenerate media or claim a future Git SHA.
"""
import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BATCH=ROOT/'production/batches/visual-depth-revision'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
slug=sys.argv[1]
q=read(BATCH/'queue.json')
if slug not in q['scope']: raise SystemExit('Outside requested scope')
p=ROOT/'projects'/slug
r=read(p/'publishing/youtube-upload-depth-v1.json')
required=['uploaded','privateSaveVerified','thumbnailVerified','koSubtitlesVerified','enSubtitlesVerified','enMetadataVerified','cardVerified','endScreenVerified','burnedCaptionPixelsVerified','settingsExceptAutomaticChecksVerified']
if not all(r.get(k) is True for k in required): raise SystemExit('Available private settings not actually verified: '+','.join(k for k in required if r.get(k) is not True))
review=read(p/'production/visual-depth-v1/encoded-pixel-direct-review.json')
if not review.get('allFinalPixelsReviewed') or review['videoSha256']!=r['sourceSha256']: raise SystemExit('Current reviewed upload hash differs')
thumb=p/'publishing/thumbnail-depth-v1.png'
t=read(thumb.with_suffix('.json'))
if not all(t['review'].values()) or hashlib.sha256(thumb.read_bytes()).hexdigest()!=t['sha256']: raise SystemExit('Thumbnail bytes do not match direct review')
now=datetime.now(timezone.utc).isoformat()
rawdir=p/'publishing/evidence-depth-v1/raw-local'; rawdir.mkdir(parents=True,exist_ok=True)
normalization=[]
for ax in (p/'production/visual-depth-v1').glob('*.ax.txt'):
    raw=ax.read_bytes(); text=raw.decode('utf-8'); normalized='\n'.join(line.rstrip() for line in text.splitlines())+'\n'
    if normalized.encode('utf-8')!=raw:
        backup=rawdir/(hashlib.sha256(raw).hexdigest()+'-'+ax.name)
        if not backup.exists(): backup.write_bytes(raw)
        ax.write_text(normalized,encoding='utf-8')
        normalization.append({'file':ax.relative_to(ROOT).as_posix(),'rawBackup':backup.relative_to(ROOT).as_posix(),'rawSha256':hashlib.sha256(raw).hexdigest(),'normalizedSha256':hashlib.sha256(normalized.encode('utf-8')).hexdigest(),'change':'trailing whitespace only; raw evidence retained locally'})
if normalization: write(p/'production/visual-depth-v1/studio-ax-whitespace-normalization.json',{'recordedAt':now,'records':normalization})
thumbpath=thumb.relative_to(ROOT).as_posix()
registry=ROOT/'shared/git-essential-images.json'; reg=read(registry)
entry={'path':thumbpath,'purpose':'delivery-thumbnail','reason':'Directly reviewed illustrated replacement thumbnail and verified actual saved private Studio thumbnail. Exact single delivery image; QA frames, contact sheets and render sequences remain local.','reviewedAt':t['copiedFileDirectlyReviewedAt'],'sha256':t['sha256'],'project':slug}
old=next((e for e in reg['entries'] if e['path']==thumbpath),None)
if old and old['sha256']!=entry['sha256']: raise SystemExit('Conflicting registered image')
if not old: reg['entries'].append(entry); write(registry,reg)
ignore=ROOT/'.gitignore'; raw=ignore.read_text(encoding='utf-8'); exception='!'+thumbpath
if exception not in raw.splitlines(): ignore.write_text(raw.rstrip()+'\n'+exception+'\n',encoding='utf-8')
t.update(status='directly-reviewed-uploaded-private-thumbnail-verified',gitEssentialApproved=True,actualVideoId=r['videoId'],uploaded=True,verifiedAt=now); write(thumb.with_suffix('.json'),t)
project=read(p/'project.json'); project['status']='private-uploaded-visual-depth-correction-awaiting-user-review'
project['publishing'].update(videoId=r['videoId'],actualVideoId=r['videoId'],uploaded=True,privacyStatus='private',scheduled=False,scheduledPublishAt=None,fullSettingsVerified=r['fullSettingsVerified'],ccOffPixelVerification='verified')
project['visualDepthRevision'].update(status=r['stage'],privateUploadCompleted=True,actualVideoId=r['videoId'],receipt=f'projects/{slug}/publishing/youtube-upload-depth-v1.json')
write(p/'project.json',project)
item=next(i for i in q['items'] if i['slug']==slug)
item.update(newVideoId=r['videoId'],stage=r['stage'],uploaded=True,privateSaveVerified=True,thumbnailVerified=True,settingsExceptAutomaticChecksVerified=True,fullSettingsVerified=r['fullSettingsVerified'],automaticChecks=r['automaticChecksStatus'],uploadReceipt=f'projects/{slug}/publishing/youtube-upload-depth-v1.json')
q['updatedAt']=now; q['privateSavedCount']=sum(bool(i.get('privateSaveVerified')) for i in q['items']); write(BATCH/'queue.json',q)
print(json.dumps({'slug':slug,'videoId':r['videoId'],'registeredEssentialImage':thumbpath,'allOtherImagesLocalOnly':True}))
