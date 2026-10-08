"""Current caption semantic map and measured platform text; no upload approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1';PUB=BASE.parent/'publishing'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat();rel=lambda p:p.relative_to(ROOT).as_posix()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(60):
  try:t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p);return
  except OSError:
   if n==59:raise
   time.sleep(.15)
target=W/'caption-alignment-review.json';meta=PUB/'metadata-final-prepared-v3.json'
assert not target.exists() and not meta.exists()
plan=read(W/'plan.json');c=read(ROOT/plan['captionSource']);timing=read(ROOT/plan['voiceTiming'])
assert sha(ROOT/plan['captionSource'])==plan['captionSourceSha256'] and c['allLiteralKoEnParagraphsPreserved']
assert len(c['paragraphs'])==64 and len(c['ko'])==415 and len(c['en'])==162
ko=read(ROOT/'projects/player-customization/script/narration.ko.v3.json');en=read(ROOT/'projects/player-customization/script/narration.en.v2.json')
ks={s['id']:s['lines'] for s in ko['scenes']};es={s['id']:s['lines'] for s in en['scenes']}
norm=lambda s:re.sub(r'\s+','',s)
paragraphs=[]
for p in c['paragraphs']:
 krows=[x for x in c['ko'] if x['scene']==p['scene'] and x['paragraph']==p['paragraph']]
 erows=[x for x in c['en'] if x['scene']==p['scene'] and x['paragraph']==p['paragraph']]
 assert norm(''.join(x['ko'] for x in krows))==norm(ks[p['scene']][p['paragraph']-1])==norm(p['ko'])
 assert norm(''.join(x['en'] for x in erows))==norm(es[p['scene']][p['paragraph']-1])==norm(p['en'])
 assert abs(krows[0]['startSeconds']-erows[0]['startSeconds'])<.001 and abs(krows[-1]['endSeconds']-erows[-1]['endSeconds'])<.001
 paragraphs.append(dict(scene=p['scene'],paragraph=p['paragraph'],start=round(p['startSeconds'],3),end=round(p['endSeconds'],3),ko=p['ko'],en=p['en'],
  koCues=[x['index'] for x in krows],enCues=[x['index'] for x in erows],allParagraphTextsRetained=True))
for lang in ['ko','en']:
 assert [i for p in paragraphs for i in p[lang+'Cues']]==list(range(1,len(c[lang])+1))
alignment=dict(schemaVersion=1,slug='player-customization',createdAt=now(),status='approved-semantic-paragraph-alignment',approved=True,
 manualSemanticReview=True,allParagraphTextsRetained=True,paragraphs=paragraphs,
 captions=[dict(language=l,path=rel(W/f'captions.{l}.srt'),sha256=sha(W/f'captions.{l}.srt'),cues=len(c[l])) for l in ['ko','en']],
 priorFullPairedContentReviews=['projects/player-customization/production/paired-script-direct-review-v1.json','projects/player-customization/production/observation-guides-paired-review-v1.json'],
 currentLiteralCaptionSourceSha256=plan['captionSourceSha256'],inputPixelsReview=plan['selectedInputReview'],
 scope='Retained directly reviewed64 independent KOEN paragraphs with complete literal cue coverage and identical paragraph endpoints; final burned pixels and current mixed ASR remain separate pending gates.',
 finalMixedAsrApproved=False,allFinalPixels=False,collected=False,uploaded=False)
save(target,alignment)
m=read(PUB/'metadata-preparation-v2.json')
assert len(m['chapterPlan'])==16
for chapter,row in zip(m['chapterPlan'],timing['rows']):
 assert chapter['id']==row['id'];chapter.update(startSeconds=row['startFrame']/60,startFrame=row['startFrame'])
for lang in ['ko','en']:
 draft=(PUB/f'description-body-draft.{lang}.v2.txt').read_text('utf-8-sig')
 marker="🎮 게임 개발은" if lang=='ko' else 'YamYamCoding helps developers'
 pos=draft.index(marker);body=draft[:pos];footer=draft[pos:]
 def chapterline(i,x):
  sec=0 if i==0 else int(x['startSeconds']);return f'{sec//60:02d}:{sec%60:02d} {x[lang]}'
 chaptertext='\n'.join(chapterline(i,x) for i,x in enumerate(m['chapterPlan']))
 text=body.rstrip()+'\n\n'+chaptertext+'\n\n'+footer
 destination=PUB/f'description-final-prepared.{lang}.v3.txt';assert not destination.exists();destination.write_text(text,'utf-8')
 assert destination.read_text('utf-8').endswith(footer)
 m['description'+lang.upper()]=rel(destination)
m.update(schemaVersion=3,preparedAt=now(),status='measured-platform-text-prepared-awaiting-final-QA-private-save',
 chapterPlan=m['chapterPlan'],chaptersMeasured=True,finalPlan=rel(W/'plan.json'),finalPlanSha256=sha(W/'plan.json'),
 durationSeconds=36041/60,measuredMembershipStartSeconds=35441/60,measuredMembershipStartFrame=35441,
 firstChapterAtZero=True,overviewActualStartSeconds=2,descriptionKo=rel(PUB/'description-final-prepared.ko.v3.txt'),descriptionEn=rel(PUB/'description-final-prepared.en.v3.txt'),
 descriptionKoSha256=sha(PUB/'description-final-prepared.ko.v3.txt'),descriptionEnSha256=sha(PUB/'description-final-prepared.en.v3.txt'),
 uploaded=False,videoId=None,privateSaved=False,actualPlatformChecksObserved=False,thumbnailSaved=False,fullSettingsVerified=False)
save(meta,m)
manifestPath=BASE.parent/'project.json';manifest=read(manifestPath);manifest['paths']['captionAlignmentReview']=rel(target);manifest['paths']['measuredPublishingPreparation']=rel(meta);manifest['updatedAt']=now();save(manifestPath,manifest)
print(json.dumps(dict(semanticParagraphs=64,ko=415,en=162,measuredChapters=16,privateSaved=False,uploaded=False)))
