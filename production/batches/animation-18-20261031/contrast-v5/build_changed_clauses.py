"""Author-selected semantic breaks; source strings are never rewritten."""
from pathlib import Path
import json,re,hashlib
H=next(p for p in Path(__file__).resolve().parents if p.name=='contrast-v5');S=H/'narration/source-verified-revisions.json'
s=json.loads(S.read_text('utf-8-sig'))
# Ordered end anchors, one list for each language. Sentence boundaries are also
# retained. Same-row cues share time; order differences are explicitly grouped.
BREAKS={
'A01:002':(['움직임에도'],['in Sifu']),
'A01:053':(['자연스러워도','두 캐릭터를 합쳤을 때'],['on its own,','brought together,']),
'A01:071':(['집고,'],['with its beak']),
'A02:028':(['같은 동작을'],['compares the same motion']),
'A04:002':(['훈련장에서는'],['training area,']),
'A04:039':(['도끼가 닿기 전에','바뀌었고,'],['Before the axe made contact,','changed first,']),
'A05:002':(['만들면서,'],['different directions,']),
'A05:012':(['화면에서는'],['Showtime!,']),
'A05:024':(['휘두를 때도','나누어 보면'],['guitar swing,','his arms and legs']),
'A05:025':(['자세라면'],['express emotion,']),
'A05:029':(['차이의 기타도'],['Chai’s guitar strike']),
'A05:040':(['목표로 뻗고','남아 있어서,'],['toward the target','in another direction,']),
'A06:041':(['내려왔는지,','힘을 실었는지,'],['came from,','body’s exertion,']),
'A07:035':(['가까운 얼굴과'],['a close face']),
'A07:045':(['큰 윤곽만으로,','작은 모델과 단순한 화면에서도'],['with her arms','emotion and action readable']),
'A08:003':(['바닥에 남아 있고,'],['planted front and back']),
'A08:018':(['상대를 향한 얼굴과'],['toward the opponent,']),
'A08:026':(['머리 위로 올라가면서'],['the ring overhead,']),
'A09:010':(['작게 보이는 것과,'],['in Slime Rancher 2']),
'A10:003':(['체력 막대를 가려도'],['Even with the health bar hidden,']),
'A10:053':(['다시 펴지며'],['then extend again']),
'A11:016':(['휘두를 때는'],['swings a weapon,']),
'A11:024':(['개발 발표에서도','키 프레임 사이를 자동으로 이어 주는','인터폴레이션 계산을 쓰지 않고'],['development presentation','automatically linking keyframes','through interpolation']),
'A11:040':(['망치를 내리치면,'],['after a hammer strike']),
'A11:062':(['몸을 앞으로 둔 뒤,'],['briefly leans forward,']),
'A12:001':(['동물의 숲에서','몸이 거의 그대로 있어도'],['In Animal Crossing,','Even with the body nearly still,']),
'A12:038':(['삼십삼 원정대의','시선을 내렸다 들고,'],['Expedition 33,','raises her gaze']),
'A13:009':(['터보의 디제이는'],['Turbo, Dee Jay']),
'A13:019':(['반대편에 섰을 때도'],['Even on the opposite side,']),
'A13:027':(['자세를 반전했을 때'],['When the pose is mirrored,']),
'A13:050':(['발의 윤곽이'],['the viewer needs to see']),
'A14:020':(['달려가는 에일로이와,'],['Aloy running from the campfire']),
'A14:043':(['같은 선수가 방향을 바꿀 때도','몸이 조금 기우는 순간과'],['In FC 25,','a slight body lean']),
'A14:059':(['무기의 방향을 읽을 수 있으면서도'],['the weapon direction remains readable']),
'A14:060':(['지켜야 할 자세와'],['choose the pose to preserve,']),
'A15:002':(['손가락 수가 같아도'],['Even with the same number of fingers,']),
'A15:033':(['검술 화면에서는'],['In Nintendo Switch Sports Chambara,']),
'A15:045':(['두 손을 모았다가,'],['bringing the hands together']),
'A17:001':(['주먹을 멀리 보내며'],['sends her gloves far away']),
'A17:014':(['손의 위치와'],['the position of the hand']),
'A17:024':(['얼굴 쪽으로 모을 때는'],['toward her face,']),
'A17:034':(['이런 모습을 옮겨 만들 때는'],['Recreating that appearance means checking']),
'A17:042':(['휘어진 팔을 만들려면,'],['curved arms like Helix’s,']),
'A18:001':(['몸통은 뒤에 남고,'],['the body remains behind,']),
}
def segments(text,anchors):
 cuts={len(text)}
 for m in re.finditer(r'(?<=[.!?])\s+',text):
  if text[:m.start()].endswith('Bros.'):continue
  cuts.add(m.start())
 pos=0
 for a in anchors:
  i=text.find(a,pos);assert i>=0,(a,text);pos=i+len(a);cuts.add(pos)
 out=[];pos=0
 for i in sorted(cuts):
  part=text[pos:i].strip()
  if part:out.append(part)
  pos=i
 assert ''.join(''.join(out).split())==''.join(text.split());return out
rows=[];flags=[]
for e in s['episodes']:
 for c in e['changes']+[x for x in s['existingApprovedChanges']if x['episode']==e['id']]:
  key=e['id']+':'+c['id'];kb,eb=BREAKS.get(key,([],[]));ko,en=segments(c['ko'],kb),segments(c['en'],eb)
  assert len(ko)==len(en),(key,ko,en)
  pairs=[{'ko':k,'en':v}for k,v in zip(ko,en)]
  for i,p in enumerate(pairs):
   if len(''.join(p['ko'].split()))>36 or len(p['en'])>85:flags.append({'key':key,'part':i,**p,'koChars':len(''.join(p['ko'].split())),'enChars':len(p['en'])})
  rows.append({'episode':e['id'],'sentenceId':c['id'],'parts':pairs,
   'adjacentCueGroup':key in ('A07:045','A11:024','A12:038','A14:043'),
   'note':'Adjacent English/Korean phrase order differs; read the linked sentence as a whole.'if key in ('A07:045','A11:024','A12:038','A14:043')else''})
out={'sourceRevisionsSha256':hashlib.sha256(S.read_bytes()).hexdigest(),'review':{'scope':'Model text semantic review only; not audio listening or word timing','originalNonspaceCharactersPreserved':True,'timingStatus':'pending waveform + later ASR review'},'scenes':rows,'lengthFlags':flags}
(H/'local/final-audio/caption-clauses.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf8')
print(len(rows),'passages',sum(len(r['parts'])for r in rows),'paired clauses');print(json.dumps(flags,ensure_ascii=False,indent=2))
