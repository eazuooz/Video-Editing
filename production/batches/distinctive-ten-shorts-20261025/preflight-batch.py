"""Check script/caption identity and genuine mobile caption fit before TTS."""
from pathlib import Path
from PIL import ImageFont
import json,ast,re
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',60)
source=R/'projects/shorts-d2r-renderer-logic-separation/production/time-captions.py'
func=next(n for n in ast.parse(source.read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='wrap')
ns={};exec(compile(ast.Module(body=[func],type_ignores=[]),str(source),'exec'),ns)
norm=lambda x:re.sub(r'[^0-9a-z가-힣]','',x.lower())
report=[]
for row in read(B/'batch.json')['projects']:
 p=R/'projects'/row['slug'];doc=read(p/'script/narration.spoken.ko.json');clauses=read(p/'script/clauses.json')['clauses'];lines=[x for s in doc['scenes'] for x in s['lines']];errors=[]
 for i,line in enumerate(lines):
  actual=' '.join(c['spoken'] for c in clauses if c['lineIndex']==i)
  if norm(actual)!=norm(line):errors.append(dict(kind='spoken-mismatch',paragraph=i))
 for c in clauses:
  for lang in ['ko','en']:
   try:ns['wrap'](c[lang],font)
   except RuntimeError as error:errors.append(dict(kind='caption-layout',id=c['id'],language=lang,text=c[lang],error=str(error)))
 report.append(dict(slug=row['slug'],paragraphs=len(lines),clauses=len(clauses),errors=errors,status='pass' if not errors else 'needs-edit'))
(B/'preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for row in report:
 print(row['slug'],row['status'],len(row['errors']))
 for error in row['errors']:print(json.dumps(error,ensure_ascii=False))
