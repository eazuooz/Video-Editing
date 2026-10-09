"""Prepare measured KO/EN metadata; no upload/settings completion is inferred."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;PUB=BASE.parent/'publishing';W=BASE/'final-v1'
r=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plan=r(W/'plan.json');prior=r(PUB/'publishing-text-preparation-v1.json');defaults=r(ROOT/'shared/publishing/youtube-defaults.json')
assert plan['finalTimingApproved'] and plan['allInputSegmentCaptionPixelsReviewed'] and len(plan['chapters'])==10
assert not (PUB/'publishing-text-preparation-v2.json').exists(),'Read the latest preparation; do not repeat.'
chapters=[]
for index,(actual,old)in enumerate(zip(plan['chapters'],prior['plannedChapters'])):
 assert actual['id']==old['scene'][:2]
 exact=actual['startFrame']/60;seconds=0 if index==0 else math.floor(exact)
 chapters.append(dict(scene=old['scene'],titleKo=old['titleKo'],titleEn=old['titleEn'],startFrame=0 if index==0 else actual['startFrame'],
  narrationChapterStartFrame=actual['startFrame'],narrationChapterExactSeconds=exact,displaySeconds=seconds,timestamp=f'{seconds//60:02d}:{seconds%60:02d}'))
t=math.floor(18452/60)
chapters.append(dict(scene='membership',titleKo='멤버십 감사 인사',titleEn='Membership thanks',startFrame=18452,
 narrationChapterStartFrame=18452,narrationChapterExactSeconds=18452/60,displaySeconds=t,timestamp=f'{t//60:02d}:{t%60:02d}'))
assert chapters[0]['displaySeconds']==0 and all(y['displaySeconds']-x['displaySeconds']>=10 for x,y in zip(chapters,chapters[1:]))
titles=dict(ko='게임 점수 디자인: 이름·단위·비교 기준으로 읽는 성과',en='Game Score Design: Names, Units, and Comparisons')
files=[]
for lang in ['ko','en']:
 original=(PUB/f'description-prepared.{lang}.txt').read_text('utf-8-sig').strip()
 assert all(url in original for url in prior['exactCanonicalLinks'].values())
 header='챕터' if lang=='ko' else 'Chapters'
 chapter_text='\n'.join(c['timestamp']+' '+c['titleKo' if lang=='ko' else 'titleEn']for c in chapters)
 body=(PUB/f'description-body.{lang}.txt').read_text('utf-8-sig').strip()
 assert original.startswith(body)
 final=body+'\n\n'+header+'\n'+chapter_text+original[len(body):]+'\n'
 path=PUB/f'description-measured-v2.{lang}.txt';path.write_text(final,'utf-8')
 title_path=PUB/f'title-measured-v2.{lang}.txt';title_path.write_text(titles[lang]+'\n','utf-8')
 for p in [path,title_path]:files.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
proof=dict(prior,schemaVersion=2,preparedAt=datetime.now(timezone.utc).isoformat(),
 status='measured-metadata-prepared-only-mixed-review-and-final-encoded-QA-pending',
 priorPreparation='projects/presenting-game-scores/publishing/publishing-text-preparation-v1.json',
 titles=titles,files=files,measuredChapters=chapters,measuredChaptersPrepared=True,plannedChapters=prior['plannedChapters'],
 planSha256=sha(W/'plan.json'),durationSeconds=19052/60,finalFrames=19052,
 chapterDisplayPolicy='Floor measured frame start to whole seconds; first00:00 includes unchanged2sec cat intro; exact narration starts retained separately.',
 originalV1FilesPreserved=True,existingChannelIntroductionPreserved=True,actualVideoId=None,uploaded=False,
 platformSettingsVerified=False,savedPlatformThumbnailVerified=False,actualAdChecksComplete=False,
 midroll=dict(eligible=False,reason='Measured317.533sec is below8min; do not request automatic mid-rolls.'),
 finalMixedAsrApproved=False,allFinalPixels=False)
proof['endScreen']=dict(prior['endScreen'],startSeconds=18452/60,endSeconds=19052/60,saved=False)
assert proof['card']['url']==defaults['coaching']['url']
(PUB/'publishing-text-preparation-v2.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(measuredChapters=11,startOuttro=18452/60,uploaded=False),ensure_ascii=False))
