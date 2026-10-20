"""Reviewed bilingual sentence/clause design; CPU text only, no media/model job."""
from pathlib import Path
import json,re,hashlib,importlib.util
from PIL import ImageFont
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent;O=P/'production/local/revision-v7-part1'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('approved_caption_geometry',P/'production/revision-v6/captions.py');geom=importlib.util.module_from_spec(spec);spec.loader.exec_module(geom)
SPLITS={
'v7-a01.L02.S01':(['이걸'],['how is']),
'v7-a01.L03.S01':(['비행기를','순서에 따라'],['then see why','can produce']),
'v7-a01.L04.S01':(['그 숫자를'],['and connect']),
'v7-a03.L02.S02':(['어느 쪽을'],['so we also']),
'v7-a03.L03.S01':(['알 버튼을','축을 가리키는'],['holding R','reveals an axis']),
'v7-a04.L02.S01':(['두 와이'],['so either']),
'v7-a04.L06.S02':(['방금'],['we use']),
'v7-a05.L05.S02':(['두 축을'],['so treating']),
'v7-a05.L06.S01':(['화면의 오른쪽과'],['screen right']),
'v7-a05.L06.S02':(['정확한 두 축의'],['our model']),
'v7-a06.L04.S02':(['뱅크는'],['so bank']),
'v7-a06.L05.S01':(['피치 이십 도,','뱅크 삼십 도를'],['pitch 20 degrees,','and bank 30 degrees']),
'v7-a06.L06.S03':(['같은 물체의'],['they are steps']),
'v7-a07.L01.S01':(['앞에서 쓴'],['our use']),
'v7-a08.L01.S01':(['뱅크가'],['bank then']),
'v7-a08.L03.S02':(['먼저 차체의'],['separately follow']),
'v7-a08.L06.S02':(['이제 그 모형의'],['we can now']),
'v7-a10.L05.S01':(['함께 보이는'],['This relationship is one reason']),
'v7-a10.L05.S02':(['움직이는 축과'],['the moving-axis']),
'v7-a10.L04.S01':(['고정 축에서'],['is the same as']),
'v7-a11.L02.S02':(['이어 고정된'],['then heading']),
'v7-a12.L02.S02':(['물체 와이는'],['but object Y']),
'v7-a12.L06.S02':(['계속 수직인'],['we can often']),
'v7-a13.L01.S01':(['현재 물체'],['rotation about']),
'v7-a13.L02.S02':(['완성된 현재'],['and adding rotation']),
'v7-a13.L04.S01':(['그다음 몸체의','마지막 진행'],['then the body’s','then its forward']),
'v7-a13.L05.S02':(['축의 기울기가','팽이 몸이'],['nutation,','and the top’s']),
'v7-a13.L06.S02':(['어느 이름을'],['so whatever']),
'v7-a14.L02.S01':(['다른 프로그램의'],['into another program’s']),
'v7-a14.L03.S01':(['같은 회전을'],['then recover']),
'v7-a14.L04.S02':(['같은 자세를'],['we move']),
'v7-a15.L01.S02':(['아래로 십 도','날개를 이십 도','말하면'],['pitching down','and banking','suggests']),
'v7-a15.L03.S01':(['피치 슬라이더'],['moving the pitch']),
'v7-a15.L05.S02':(['놓을 자리뿐'],['requires judging']),
'v7-a15.L06.S02':(['그 결과를'],['and adjust']),
'v7-a16.L01.S01':(['삼차원 회전에는'],['three independently']),
'v7-a16.L01.S03':(['아홉 칸의'],['using fewer']),
'v7-a16.L04.S01':(['저장할 값은','원래 있던'],['fewer distinct','but their original']),
'v7-a16.L05.S01':(['최종 자세의'],['does not mean']),
'v7-a16.L06.S02':(['그 숫자의'],['we must separately']),
'v7-a18.L03.S03':(['끝 모습과'],['we are distinguishing']),
'v7-a18.L06.S02':(['같은 모습을'],['we need a rule']),
'v7-a19.L01.S01':(['마이너스 백팔십','플러스 백팔십'],['greater than','and at most']),
'v7-a20.L01.S02':(['처음의 와이 축과'],['follow how']),
'v7-a20.L04.S02':(['헤딩 이십 도와'],['as heading']),
'v7-a21.L01.S01':(['피치가'],['we can set']),
'v7-a21.L05.S01':(['먼저 앞·위·옆을'],['already helped']),
'v7-a21.L06.S01':(['물 위로'],['ready to be']),
'v7-a21.L06.S02':(['쓸 수 있는'],['have come together']),
'v7-a21.L08.S02':(['한 축과'],['then examine'])
}
# Two clauses must retain the same semantic order, rather than split a translated
# predicate at an unrelated source boundary. These overrides are caption-only
# sentence translations preserving the already reviewed paragraph meaning.
EN_SENTENCE={
'v7-a10.L05.S01':'The yaw-pitch-roll and roll-pitch-yaw descriptions can both appear because of this relationship.',
'v7-a12.L06.S02':'Rather than turning the head about tilted object Y, we can often describe it as changing heading around a consistently vertical reference.',
'v7-a20.L01.S02':'As pitch increases, follow how the initial Y axis and the final bank’s Z axis approach the same line.'
}
# Entries are bound to the exact paragraph and offset below, never global
# substitutions in the narration or source-ASR data.
LEX=[('마리오 카트 에이트 디럭스','마리오 카트 8 디럭스'),('인트린식 로테이션','Intrinsic Rotation'),('엑스트린식 로테이션','Extrinsic Rotation'),('오리엔테이션','Orientation'),('알 버튼','R 버튼'),('엑스','X'),('와이','Y'),('제트','Z')]
NUMBERS={'칠백이십':720,'삼백육십':360,'백삼십오':135,'백팔십':180,'사십오':45,'팔십':80,'구십':90,'삼십':30,'이십':20,'십':10,'일':1,'영':0,'영 점 오':0.5,'이십 점 사':20.4}
def aliases(text):
 candidates=[]
 for spoken,display in LEX:
  for m in re.finditer(re.escape(spoken),text):candidates.append((m.start(),m.end(),spoken,display,'canonical symbol/name'))
 for words,value in NUMBERS.items():
  for prefix,sign in [('마이너스 ','−'),('플러스 ','+'),('양의 ','+'),('음의 ','−'),('','')]:
   pattern=r'(?<![가-힣])'+re.escape(prefix+words+' 도')
   for m in re.finditer(pattern,text):candidates.append((m.start(),m.end(),m[0],sign+str(value)+'°','canonical degree display; spoken number preserved'))
 selected=[]
 for a,b,spoken,display,meaning in sorted(candidates,key=lambda x:(-(x[1]-x[0]),x[0])):
  if any(a<d and b>c for c,d,*_ in selected):continue
  selected.append((a,b,spoken,display,meaning))
 return [dict(sourceStart=a,sourceEnd=b,spoken=s,display=d,meaning=m) for a,b,s,d,m in sorted(selected)]
def cut(text,markers):
 out=[];at=0
 for marker in markers:
  n=text.find(marker,at);assert n>at,(marker,text)
  out.append(text[at:n].strip());at=n
 out.append(text[at:].strip());assert ' '.join(out)==text
 return out
def main():
 ko_file=P/'script/revision-v7-two-part/part-01.ko.json';en_file=P/'script/revision-v7-two-part/part-01.en.json';ko,en=read(ko_file),read(en_file)
 font=ImageFont.truetype(str(geom.FONT),48);bold=ImageFont.truetype(str(geom.BOLD),48)
 rows=[];needs=[];aliases_by=[]
 for s,t in zip(ko['scenes'],en['scenes']):
  assert s['id']==t['id'] and len(s['lines'])==len(t['lines']);emphasized=set()
  for i,(kp,ep) in enumerate(zip(s['lines'],t['lines']),1):
   ks,es=geom.sentences(kp),geom.sentences(ep);assert len(ks)==len(es),(s['id'],i)
   spans=aliases(kp);aliases_by.append(dict(scene=s['id'],line=i,sourceText=kp,sourceTextSha256=hashlib.sha256(kp.encode()).hexdigest(),spans=spans));offset=0
   for j,(k,e) in enumerate(zip(ks,es),1):
    key=f'{s["id"]}.L{i:02d}.S{j:02d}'
    if key in EN_SENTENCE:assert e==EN_SENTENCE[key],('English rephrasing must be saved in the current full script',key)
    if key in SPLITS:
     km,em=SPLITS[key]
     # A sentence reordered as a whole is still bound to this same spoken
     # sentence; no extra source sentence or useful claim is removed.
     if key=='v7-a10.L05.S01':km=['함께 보이는'];em=['because of']
     kc,ec=cut(k,km),cut(e,em)
    else:kc,ec=[k],[e]
    assert len(kc)==len(ec)
    for n,(a,b) in enumerate(zip(kc,ec),1):
     pos=kp.index(a,offset);offset=pos+len(a);display,changes=geom.display_aliases(a,pos,spans)
     ke=ee=None
     for term,eng in geom.TERMS:
      ka,ea=display.find(term),b.lower().find(eng.lower())
      if ka>=0 and ea>=0 and term not in emphasized:
       ke=dict(start=ka,end=ka+len(term),role='focus');ee=dict(start=ea,end=ea+len(eng),role='focus');emphasized.add(term);break
     row=dict(id=f'{key}.C{n:02d}',scene=s['id'],line=i,sentence=j,clause=n,sourceKo=a,sourceEn=b,sourceKoOffset=pos,sourceKoEnd=pos+len(a),ko=display,en=b,emphasisKo=ke,emphasisEn=ee,displayAliasesKo=changes)
     try:row['koLines']=geom.wrap(display,font,bold,ke);row['enLines']=geom.wrap(b,font,bold,ee)
     except AssertionError:needs.append(dict(id=row['id'],ko=a,en=b,koWords=len(a.split()),enWords=len(b.split())))
     rows.append(row)
 for s,t in zip(ko['scenes'],en['scenes']):
  for i,(kp,ep) in enumerate(zip(s['lines'],t['lines']),1):
   selected=[x for x in rows if x['scene']==s['id'] and x['line']==i]
   assert ' '.join(x['sourceKo'] for x in selected)==kp,(s['id'],i,'KO reconstruction')
   assert ' '.join(x['sourceEn'] for x in selected)==ep,(s['id'],i,'EN reconstruction')
 assert len(aliases_by)==135
 report=dict(schemaVersion=1,part=1,policy='caption-clause-keyword-v1',inputs=dict(koSha256=sha(ko_file),enSha256=sha(en_file),designSha256=sha(Path(__file__)),approvedGeometrySha256=sha(P/'production/revision-v6/captions.py')),sceneCount=21,paragraphCount=135,cueCount=len(rows),cues=rows,aliases=aliases_by,layoutNeeds=needs,timing='pending measured new source ASR; no artificial gaps',sourceKoUnchanged=True,geometry='boxed-white-forest-v1; center960,970 /48px /2lines /1570px',translationReview='135 semantic paragraph translations; paired complete sentences with explicit condition/action/result splits; EN rephrasing remains in same sentence',newMediaCreated=False)
 (H/'caption-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'cues':len(rows),'paragraphs':135,'layoutNeeds':needs},ensure_ascii=False))
if __name__=='__main__':main()
