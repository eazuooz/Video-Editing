from pathlib import Path
import copy,hashlib,json
H=Path(__file__).resolve().parent;P=H.parents[2]/'projects/shorts-returnal-particle-tentacles'
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,t):assert not p.exists(),p;p.write_text(t,'utf8')
cp=P/'planning/caption-clauses-repair-v27.json';c=read(cp);a=next(x['clauses']for x in c['paragraphs']if x['id']=='p006');assert a[2][0]=='아티스트와 애니메이터는 공격을 알아보기 쉽게 동작 시간을 조절했습니다.'
a[2:3]=[['아티스트와 애니메이터는','Artists and animators'],['공격을 알아보기 쉽게 동작 시간을 조절했습니다.','adjusted motion timing so attacks were easy to read.']];out=P/'planning/caption-clauses-repair-v31.json';write(out,json.dumps(c,ensure_ascii=False,indent=2)+'\n')
plan=read(P/'planning/film-beats-v27.json');plan['semanticClauses']=pin(out)
for b in next(x['beats']for x in plan['paragraphs']if x['id']=='p006'):
 if b['firstClauseIndex']>=3:b['firstClauseIndex']+=1
pp=P/'planning/film-beats-v31.json';write(pp,json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
ct=read(H/'source-ordered-film-contracts-v27.json');row=next(x for x in ct['projects']if x['slug']==P.name);row['plan']=pin(pp);write(H/'source-ordered-film-contracts-v31.json',json.dumps(ct,ensure_ascii=False,indent=2)+'\n')
s=(H/'review-corrected-voice-captions-v27.py').read_text(encoding='utf8');old="caps=read(cp);pt=";assert s.count(old)==1;s=s.replace(old,"cp=P/'planning/caption-clauses-repair-v31.json'if P.name=='shorts-returnal-particle-tentacles'else cp;cv='v31'if P.name=='shorts-returnal-particle-tentacles'else cv;caps=read(cp);pt=");write(H/'review-corrected-voice-captions-v31.py',s)
s=(H/'bind-ready-film-inputs-v27.py').read_text(encoding='utf8').replace('source-ordered-film-contracts-v27.json','source-ordered-film-contracts-v31.json');write(H/'bind-ready-film-inputs-v31.py',s)
print(json.dumps(dict(captions=pin(out),plan=pin(pp),voicePcmChanged=False,captionEdgesRequireActualWholeWords=True)))
