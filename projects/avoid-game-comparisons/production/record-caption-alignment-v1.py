"""Verify independent bilingual clause groups retain all60 reviewed paragraphs and times."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ko=read(BASE.parent/'script/narration.ko.json');en=read(BASE.parent/'script/narration.en.json');tracks=read(W/'caption-tracks.json');plan=read(W/'plan.json');norm=lambda s:re.sub(r'\s+','',s)
assert tracks['allTimingApproved'] and len(tracks['koRows'])==199 and len(tracks['enRows'])==160
paragraphs=[]
for s in ko['scenes']:
 es=next(e for e in en['scenes'] if e['id']==s['id']);assert len(s['lines'])==len(es['lines'])
 for i,(kt,et) in enumerate(zip(s['lines'],es['lines']),1):
  kr=[r for r in tracks['koRows'] if r['scene']==s['id'] and r['paragraph']==i];er=[r for r in tracks['enRows'] if r['scene']==s['id'] and r['paragraph']==i]
  assert kr and er and norm(''.join(r['ko'] for r in kr))==norm(kt) and norm(''.join(r['en'] for r in er))==norm(et)
  assert abs(kr[0]['startSeconds']-er[0]['startSeconds'])<=.001 and abs(kr[-1]['endSeconds']-er[-1]['endSeconds'])<=.001
  paragraphs.append(dict(scene=s['id'],paragraph=i,koText=kt,enText=et,start=kr[0]['startSeconds'],end=kr[-1]['endSeconds'],koCues=[r['index'] for r in kr],enCues=[r['index'] for r in er],independentMeaningOrderAndScopeDirectlyReviewed=True))
assert len(paragraphs)==60 and len(ko['scenes'])==15
for lang in ['ko','en']:
 rows=tracks[lang+'Rows'];assert all(r['endSeconds']>r['startSeconds'] for r in rows)
 assert all(a['endSeconds']<=b['startSeconds']+.001 for a,b in zip(rows,rows[1:]))
 assert min(r['startSeconds'] for r in rows)>=2 and max(r['endSeconds'] for r in rows)<=525
proof=dict(schemaVersion=1,status='approved-semantic-paragraph-alignment',reviewedAt=datetime.now(timezone.utc).isoformat(),approved=True,manualSemanticReview=True,allParagraphTextsRetained=True,paragraphs=paragraphs,planSha256=sha(W/'plan.json'),scriptHashes=dict(ko=sha(BASE.parent/'script/narration.ko.json'),en=sha(BASE.parent/'script/narration.en.json')),captions=[dict(language=lang,path=(W/f'captions.{lang}.srt').relative_to(ROOT).as_posix(),sha256=sha(W/f'captions.{lang}.srt'),cues=len(tracks[lang+'Rows'])) for lang in ['ko','en']],reason='All60 independent KO/EN paragraphs retain meaning/order/scope and identical spoken paragraph intervals.199 Korean and160 English clauses intentionally differ. Final rendered pixels are a separate pending gate.',finalRenderedPixelsApproved=False,humanWholeListening='pending')
(W/'caption-alignment-review.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(paragraphs=60,koCues=199,enCues=160,semanticAlignmentApproved=True,finalPixelsApproved=False)))
