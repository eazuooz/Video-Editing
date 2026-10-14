"""Prepare one new private captioned upload after actual four-output verification."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
out=O/'publishing/youtube-upload-v1.json';assert not out.exists()
cp=O/'current34-four-output-collection-verification-v1.json';collection=rd(cp);assert collection['fourOutputsCollected']
planp=O/'publishing/metadata-text-plan-v1.json';plan=rd(planp)
pair=rd(O/'current34-final-pair-execution-v5.json')
video=ROOT/'output/game-math-orientation-matrices/game-math-orientation-matrices.captioned.mp4'
assert sha(video)==pair['pair'][1]['sha256']
base=rd(ROOT/'projects/game-math-orientation-matrices/publishing/youtube-upload.json')
metadata={}
for lang in ['ko','en']:
 row=plan['texts'][lang];path=ROOT/row['path'];assert sha(path)==row['sha256']
 metadata[lang]=dict(title=row['title'],description=path.read_text('utf-8').rstrip(),language='ko' if lang=='ko' else 'en-US')
metadata['ko']['privacyStatus']='private'
thumb=base['thumbnail'];assert sha(ROOT/thumb['path'])==thumb['sha256']
tracks=[]
for lang in ['ko','en']:
 p=ROOT/f'output/game-math-orientation-matrices/game-math-orientation-matrices.{lang}.srt'
 text=p.read_text('utf-8-sig');assert text.count(' --> ')==244
 tracks.append(dict(language=lang,path=p.relative_to(ROOT).as_posix(),sha256=sha(p),cues=244,method='manual-file-upload-with-timing',status='pending-new-video-manual-upload'))
data=dict(schemaVersion=1,slug='game-math-orientation-matrices',preparedAt=datetime.now(timezone.utc).isoformat(),
 status='prepared-current34-private-captioned-upload-not-started',uploaded=False,actualVideoId=None,actualVideoUrl=None,
 scheduled=False,baselineVideoId='6-kP65hrZcI',baselinePreserved=True,baselineScheduleChanged=False,
 video=dict(path=video.relative_to(ROOT).as_posix(),sha256=sha(video),bytes=video.stat().st_size,seconds=pair['seconds'],width=1920,height=1080,fps=60),
 metadata=metadata['ko'],englishMetadata=dict(**metadata['en'],status='pending-new-video-localization'),
 descriptionBody={lang:plan['texts'][lang]['body'] for lang in ['ko','en']},subtitles=tracks,
 thumbnail=dict(path=thumb['path'],sha256=thumb['sha256'],status='pending-new-video-upload'),
 collectionEvidence=cp.relative_to(ROOT).as_posix(),collectionEvidenceSha256=sha(cp),metadataPlan=planp.relative_to(ROOT).as_posix(),metadataPlanSha256=sha(planp),
 coachingCard=dict(url='https://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328',startSeconds=0,title='프로그래밍 과외',teaser='프로그래밍 과외',status='pending-new-video'),
 endScreen=dict(startSeconds=65317/60,endSeconds=65917/60,timecodeFps=60,startTimecode='18:08:37',endTimecode='18:18:37',
    elements=['relevant-channel-playlist','subscribe-own-channel','programming-coaching-external-link'],playlistId=base['endScreen']['playlistId'],status='pending-new-video'),
 pinnedComment=plan['pinnedComment'],monetization=dict(status='pending-actual-new-video-ui'),
 burnedCaptionVerification=dict(required=True,position=[960,970],playerCaptionsOff=True,status='pending-real-uploaded-frame-review'),
 checks=dict(sdHd='pending',copyright='pending',adSuitability='pending'),fullSettingsComplete=False,
 humanListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,newGitMedia=0)
out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(receipt=out.relative_to(ROOT).as_posix(),videoSha256=data['video']['sha256'],prepared=True,uploaded=False)))
