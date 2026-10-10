"""Record the previously directly read literal37 paired paragraphs and clock."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel=lambda p:p.relative_to(ROOT).as_posix()
c=read(W/'captions.json');plan=read(W/'plan.json');dest=W/'semantic-caption-alignment-review-v1.json'
assert not dest.exists(),'Preserve completed current caption alignment'
assert c['allCurrentCueTextsDirectlyRead'] and c['allInputCuePixelsReviewed'] and c['allCurrent37KoEnParagraphsRetained'] and c['all35UnchangedParagraphsPreserved']
assert sha(ROOT/plan['selectedInputReview'])==plan['selectedInputReviewSha256']
clean=lambda text:re.sub(r'\s+','',text)
rows=[]
for a in c['paragraphs']:
 tracks={lang:[r for r in c[lang]if (r['scene'],r['paragraph'])==(a['scene'],a['paragraph'])]for lang in ['ko','en']}
 for lang,t in tracks.items():assert t and clean(''.join(r[lang]for r in t))==clean(a[lang]),(a['scene'],a['paragraph'],lang)
 ko,en=tracks['ko'],tracks['en'];assert abs(ko[0]['startSeconds']-en[0]['startSeconds'])<.002 and abs(ko[-1]['endSeconds']-en[-1]['endSeconds'])<.002
 rows.append(dict(id=a['scene']+'-p'+str(a['paragraph']),scene=a['scene'],paragraph=a['paragraph'],start=ko[0]['startSeconds'],end=ko[-1]['endSeconds'],koCues=[r['index']for r in ko],enCues=[r['index']for r in en],ko=a['ko'],en=a['en'],literalTextsRetained=True,manualParagraphComparison=True))
assert len(rows)==37
for lang,total in [('ko',201),('en',95)]:assert [v for r in rows for v in r[lang+'Cues']]==list(range(1,total+1))
proof=dict(status='approved-semantic-paragraph-alignment',approved=True,manualSemanticReview=True,allParagraphTextsRetained=True,reviewedAt=datetime.now(timezone.utc).isoformat(),
 captions=[dict(language=lang,path=rel(W/f'character-parameters.{lang}.srt'),sha256=sha(W/f'character-parameters.{lang}.srt'),cues=total)for lang,total in [('ko',201),('en',95)]],
 paragraphs=rows,captionJsonSha256=sha(W/'captions.json'),planSha256=sha(W/'plan.json'),
 approvalScope='Previously directly read literal37 KOEN paragraphs/current201KO95EN balanced cues and measured common paragraph boundaries; current final encoded pixels still pending.',
 allFinalPixels=False,humanPronunciationApproved=False,imagesGitAdded=0)
dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
mp=BASE.parent/'project.json';m=read(mp);m['paths']['captionAlignmentReview']=rel(dest);mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(approved=True,paragraphs=37,ko=201,en=95,allFinalPixels=False)))
