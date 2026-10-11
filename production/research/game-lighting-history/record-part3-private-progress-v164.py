"""Record actual single Studio upload; preparation and transfer are not completion."""
from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p=m.ROOT/'projects/game-lighting-history-04-3/publishing/youtube-upload.json'
j=m.read(p)
assert j['uploadVariant']=='captioned' and not j['cleanUploadAllowed']
assert m.sha(m.ROOT/j['uploadPath'])==j['uploadSha256']
assert j['actualVideoId'] in (None,'ydW9Glmh0nM')
j.update(actualVideoId='ydW9Glmh0nM',status='single-private-upload-in-progress',uploaded=False,privateSaved=False,fullSettingsVerified=False)
j['actualUploadProgress']=dict(observedAt=m.stamp(),tabId='21',actualUrl='https://youtu.be/ydW9Glmh0nM',uploadPercent=37,estimatedRemaining='10 minutes',privateAutosaveText='비공개로 저장됨',privateAutosaveObserved=True,uploadComplete=False,explicitWizardCompletionObserved=False,titleAndDescriptionEntered=True,playlistSelection='Physically Based Rendering (PBR) 물리 기반 렌더링',thumbnailEntered=True,thumbnailReopenedVerified=False,next='Finish single wizard settings and verify upload/processing, saved private settings and CC-off pixels on this same ID.')
m.save(p,j)
cp=m.read(m.ROOT/'production/research/game-lighting-history/checkpoint.json')
cp['updatedAt']=m.stamp()
cp['episode04Part3PrivateProgressV164']=dict(actualVideoId=j['actualVideoId'],receipt=m.rel(p),uploaded=False,privateAutosaveObserved=True,fullSettingsVerified=False,uploadPath=j['uploadPath'],uploadSha256=j['uploadSha256'],singleUpload=True,next=j['actualUploadProgress']['next'])
m.save(m.ROOT/'production/research/game-lighting-history/checkpoint.json',cp)
print('Recorded actual single upload ydW9Glmh0nM: 37%; completion gates remain false.')
