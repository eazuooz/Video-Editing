"""Prepare measured metadata; never infer upload or scheduled completion."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;PUB=BASE.parent/'publishing';W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=read(W/'plan.json');prior=read(PUB/'publishing-text-preparation-v1.json');defaults=read(ROOT/'shared/publishing/youtube-defaults.json')
assert p['finalTimingApproved'] and p['allInputSegmentCaptionPixelsReviewed'] and len(p['chapters'])==12
dest=PUB/'publishing-text-preparation-v2.json';assert not dest.exists(),'Preserve current measured metadata'
chapters=[]
for index,(actual,old)in enumerate(zip(p['chapters'],prior['plannedChapters'])):
 assert actual['id']==old['scene']
 exact=actual['startFrame']/60;t=0 if index==0 else math.floor(exact)
 chapters.append(dict(scene=old['scene'],titleKo=old['titleKo'],titleEn=old['titleEn'],startFrame=0 if index==0 else actual['startFrame'],narrationChapterStartFrame=actual['startFrame'],narrationChapterExactSeconds=exact,displaySeconds=t,timestamp=f'{t//60:02d}:{t%60:02d}'))
t=math.floor(p['membershipStartFrame']/60)
chapters.append(dict(scene='membership',titleKo='멤버십 감사 인사',titleEn='Membership Thanks',startFrame=p['membershipStartFrame'],narrationChapterStartFrame=p['membershipStartFrame'],narrationChapterExactSeconds=p['membershipStartFrame']/60,displaySeconds=t,timestamp=f'{t//60:02d}:{t%60:02d}'))
assert chapters[0]['displaySeconds']==0 and all(y['displaySeconds']-x['displaySeconds']>=10 for x,y in zip(chapters,chapters[1:]))
files=[]
for lang in ['ko','en']:
 original=(PUB/f'description-prepared.{lang}.txt').read_text('utf-8-sig').strip();body=(PUB/f'description-body.{lang}.txt').read_text('utf-8-sig').strip()
 assert original.startswith(body) and all(url in original for url in prior['exactCanonicalLinks'].values())
 header='챕터'if lang=='ko'else'Chapters'
 text='\n'.join(c['timestamp']+' '+c['titleKo'if lang=='ko'else'titleEn']for c in chapters)
 out=body+'\n\n'+header+'\n'+text+original[len(body):]+'\n'
 desc=PUB/f'description-measured-v2.{lang}.txt';desc.write_text(out,'utf-8')
 title=PUB/f'title-measured-v2.{lang}.txt';title.write_text(prior['titles'][lang]+'\n','utf-8')
 files.extend(dict(path=v.relative_to(ROOT).as_posix(),sha256=sha(v))for v in [desc,title])
r=dict(prior,schemaVersion=2,preparedAt=datetime.now(timezone.utc).isoformat(),status='measured-metadata-prepared-only-final-QA-pending',
 priorPreparation='projects/character-parameters/publishing/publishing-text-preparation-v1.json',priorPreparationSha256=sha(PUB/'publishing-text-preparation-v1.json'),
 files=files,measuredChapters=chapters,measuredChaptersPrepared=True,planSha256=sha(W/'plan.json'),durationSeconds=p['finalFrames']/60,finalFrames=p['finalFrames'],
 chapterDisplayPolicy='Floor measured frame start; first00:00 includes original2sec intro, exact narrated start retained separately.',
 originalV1FilesPreserved=True,existingChannelIntroductionPreserved=True,actualVideoId=None,uploaded=False,
 midroll=dict(eligible=False,reason='389.95sec below8minutes'),finalMixedAsrApproved=False,allFinalPixels=False)
r['endScreen']=dict(prior['endScreen'],startSeconds=p['membershipStartFrame']/60,endSeconds=p['finalFrames']/60,saved=False)
assert r['card']['url']==defaults['coaching']['url']
dest.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(measuredChapters=13,outroStart=p['membershipStartFrame']/60,uploaded=False)))
