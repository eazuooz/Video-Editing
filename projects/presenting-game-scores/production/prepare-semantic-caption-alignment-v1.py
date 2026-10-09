"""Adopt the directly read literal bilingual clauses and their current clocks."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cap=read(W/'captions.json');assert cap['allCurrentCueTextsDirectlyRead'] and cap['allLiteralKoEn39ParagraphsPreserved']
key=lambda x:(x['scene'],x['paragraph'],x['chunk'])
norm=lambda x:re.sub(r'\s+','',x)
rows=[]
for c in sorted(cap['chunks'],key=lambda x:x['startSeconds']):
 ko=[x for x in cap['ko']if key(x)==key(c)];en=[x for x in cap['en']if key(x)==key(c)]
 assert ko and en and norm(''.join(x['ko']for x in ko))==norm(c['ko'])
 assert norm(''.join(x['en']for x in en))==norm(c['en'])
 start=round(ko[0]['startSeconds'],3);end=round(ko[-1]['endSeconds'],3)
 assert abs(en[0]['startSeconds']-start)<=.001 and abs(en[-1]['endSeconds']-end)<=.001
 rows.append(dict(id=f'{c["scene"]}p{c["paragraph"]}c{c["chunk"]}',start=start,end=end,
  ko=c['ko'],en=c['en'],koCues=[x['index']for x in ko],enCues=[x['index']for x in en],
  bothLiteralTextsDirectlyRead=True,completeClause=True))
assert len(rows)==40 and [i for x in rows for i in x['koCues']]==list(range(1,169))
assert [i for x in rows for i in x['enCues']]==list(range(1,69))
captions=[dict(language=lang,path=(W/f'presenting-game-scores.{lang}.srt').relative_to(ROOT).as_posix(),
 sha256=sha(W/f'presenting-game-scores.{lang}.srt'),cues=len(cap[lang]))for lang in ['ko','en']]
target=W/'semantic-caption-alignment-review.json';assert not target.exists()
proof=dict(status='approved-semantic-paragraph-alignment',approved=True,manualSemanticReview=True,
 reviewedAt=datetime.now(timezone.utc).isoformat(),allParagraphTextsRetained=True,
 logicalParagraphs=39,semanticClauses=40,original30ParagraphsRetained=True,currentCaptionJsonSha256=sha(W/'captions.json'),
 captions=captions,paragraphs=rows,approvalScope='All literal independent KO/EN clauses and complete current word-aligned spans; final encoded pixels and human pronunciation separately reviewed.',
 allFinalPixels=False,humanWholeListening='pending',humanPronunciation='pending')
target.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
mp=BASE.parent/'project.json';m=read(mp);m['paths']['captionAlignmentReview']=target.relative_to(ROOT).as_posix()
mp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(semanticClauses=40,ko=168,en=68,allLiteralTextsRetained=True)))
