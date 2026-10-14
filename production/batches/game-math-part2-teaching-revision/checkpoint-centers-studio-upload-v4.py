"""Checkpoint the actual in-flight Studio ID; never infer upload completion."""
from pathlib import Path
from datetime import datetime
import json
ROOT=Path(__file__).resolve().parents[3]
B=Path(__file__).parent;R=B/'cross-game-review-20261011'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.now().astimezone().isoformat()
p=ROOT/'projects/game-math-polygon-centers-v2/publishing/youtube-upload.json';d=read(p)
assert d['videoId'] in [None,'YgcN8vs0gNo']
d.update(videoId='YgcN8vs0gNo',url='https://youtu.be/YgcN8vs0gNo',status='actual-Studio-private-draft; uploading',uploadComplete=False,fullPublishingSettingsComplete=False)
d['studioProgress']={'observedAt':now,'uploadPercent':62,'remainingUi':'5분 남음','state':'비공개로 저장됨','koManualSubtitle':'한국어 번역: 나; 수정 button after timed-file save','aiDisclosure':'yes','paidPromotion':'no','monetization':'enabled; automatic suitability pending','adSelfRating':'lowest game-violence tier; submitted','playlist':'게임 수학(Game Math) PART 2'}
d['subtitles'][0]['status']='manual-timed-file-saved-in-upload-dialog; final-reopen-pending'
d['thumbnail']['status']='selected-in-Studio; final-reopen-pending'
write(p,d)
p=R/'polygons-v4-current-progress.json';d=read(p)
d.update(recordedAt=now,wholeMixedAudioReview='centers full25 compared and recorded; partition current24 CPU read-back running',currentCaptionedRender='Both current final renders fully decoded; centers approved/collected; partition current all140 cues and26 compositions plus10 bridge detail pages directly reviewed',newPlatformMutations=1,newUploadsComplete=0)
d['actualUploads']=[{'slug':'game-math-polygon-centers-v2','videoId':'YgcN8vs0gNo','uploadComplete':False,'privacy':'private-draft','scheduled':False}]
write(p,d)
print('Checkpointed actual YgcN8vs0gNo; upload and final settings remain pending.')
