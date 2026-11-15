"""Prepare bilingual semantic clauses; no voice timestamps inferred."""
from pathlib import Path
import json,re,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def norm(s):return re.sub(r'[^가-힣a-zA-Z0-9]','',s)
def main():
 summary=[]
 for row in read(HERE/'bounded-semantic-corrections-source-review-v6.json')['projects']:
  P=ROOT/'projects'/row['slug'];locked=P/'planning/narration-repair-v6.json';n=read(locked);old=read(P/'planning/narration-sentence-v2.json');cp=P/'planning/caption-clauses-sentence-v2.json';caps=read(cp);unit_clauses={}
  for para in old['paragraphs']:
   cs=next(x['clauses']for x in caps['paragraphs']if x['id']==para['id']);bounds={0:0};at=0
   for i,c in enumerate(cs):at+=len(norm(c[0]));bounds[at]=i+1
   at=0
   for u in [x for x in old['units']if x['paragraph']==para['id']]:
    start=at;at+=len(norm(u['ko']));assert start in bounds and at in bounds,(P.name,u['id'],'Existing clause crosses a natural sentence');unit_clauses[u['id']]=cs[bounds[start]:bounds[at]]
  extra={}
  if 'journey'in P.name:
   extra={'r0011':'The dunes in this game sparkle as you move.','r0071':'The team adjusted the distribution of directions to retain grain in smaller textures.','r0111':'Intended sparkle and unstable flickering are different.','r0121':'The team changed how the glints are calculated.','r0122':'They used a different relationship instead of the light–view halfway direction.','r0123':'It is the relationship between the surface and the view.'}
  out=[]
  for para in n['paragraphs']:
   clauses=[]
   for u in [x for x in n['units']if x['paragraph']==para['id']]:
    if u['id']in n['newEnglish']:pairs=[[u['ko'],n['newEnglish'][u['id']]]]
    elif u['id']in extra:pairs=[[u['ko'],extra[u['id']]]]
    else:pairs=unit_clauses[u['id']]
    clauses.extend([[ko,en.replace('individual3D','individual 3D')]for ko,en in pairs])
   assert norm(''.join(c[0]for c in clauses))==norm(para['ko']);out.append(dict(id=para['id'],clauses=clauses))
  target=P/'planning/caption-clauses-repair-v6.json';assert not target.exists();target.write_text(json.dumps(dict(schemaVersion=1,source=pin(locked),previousUntimedClauses=pin(cp),paragraphs=out,actualSpeechTimesAssigned=False,wordInterpolation=False,englishUsesSameMeaningClauseInterval=True),ensure_ascii=False,indent=2)+'\n','utf8');summary.append(dict(slug=P.name,clauses=sum(len(p['clauses'])for p in out),source=pin(target)))
 print(json.dumps(summary))
if __name__=='__main__':main()
