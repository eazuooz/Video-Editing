"""Prepare exact current pair and QA workers without running a render."""
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2];REF=ROOT/'projects/presenting-game-scores/production'
out=BASE/'render-character-pair-v1.py';assert not out.exists();text=(REF/'render-reviewed-pair-v1.py').read_text('utf-8')
for a,b in [('presenting-game-scores','character-parameters'),('all31','all49'),('All31','All49'),('31-window','49-window'),("len(review['windows'])==31","len(review['windows'])==49"),('(168,68,[960,970])','(201,95,[960,970])'),('(19052,18332)','(23397,22677)'),('N=19052','N=23397'),("['node',","['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',")]:text=text.replace(a,b)
out.write_text(text,'utf-8')
out=BASE/'extract-character-final-qa-v1.py';assert not out.exists();text=(REF/'extract-encoded-caption-qa-v1.py').read_text('utf-8')
start=text.index("for chunk in cap['chunks']:");end=text.index("for placement in plan['voicePlacements']:",start)
text=text[:start]+'''for para in cap['paragraphs']:
 literal=[c for c in cap['ko']if (c['scene'],c['paragraph'])==(para['scene'],para['paragraph'])]
 assert literal
 for edge,t in [('onset',min(c['startSeconds']for c in literal)),('end',max(c['endSeconds']for c in literal))]:
  frame=math.ceil(t*60-1e-7)
  for offset in [-1,0,1]:add(frame+offset,f'complete-clause-{edge}:{para["scene"]}p{para["paragraph"]}')
'''+text[end:]
for a,b in [('presenting-game-scores','character-parameters'),('(168,68,19052)','(201,95,23397)'),('19052','23397'),('18452','22797'),('18451','22796'),('18512','22857'),('18752','23097'),('18992','23337'),('19051','23396'),('len(segments)==26','len(segments)==43'),('len(cues)==168','len(cues)==201'),('range(1,169)','range(1,202)'),("len(preflight['samples'])==651","len(preflight['samples'])==845"),('koCueCount=168,enCueCount=68,cutCount=24','koCueCount=201,enCueCount=95,cutCount=41'),('actualCutCount=12,explanationCutCount=12,completeClauseOnsets=40,logicalParagraphs=39,pcmPlacements=30','actualCutCount=24,explanationCutCount=17,completeClauseOnsets=37,logicalParagraphs=37,pcmPlacements=17'),('all651ApprovedInputAnchorsRetained','all845ApprovedInputAnchorsRetained'),('koCues=168,cuts=24,clauses=40','koCues=201,cuts=41,clauses=37')]:text=text.replace(a,b)
text=text.replace('1137,1138,','')
out.write_text(text,'utf-8');print('Prepared pair and encoded QA; gates unchanged/false')
