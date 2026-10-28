"""Author paired semantic caption units. No ASR, media job or guessed timestamps."""
from pathlib import Path
import json,re,hashlib
H=Path(__file__).resolve().parent
def read(name):return json.loads((H/name).read_text('utf-8-sig'))
def sentences(t):
 return [s.replace('Bros\u2024','Bros.') for s in re.split(r'(?<=[.?!]) +',t.replace('Bros.','Bros\u2024'))]
def after(t,anchors):
 out=[];pos=0
 for anchor in anchors:
  end=t.index(anchor,pos)+len(anchor);out.append(t[pos:end].strip());pos=end
 out.append(t[pos:].strip());assert all(out);return out
explicit={
 '04-p02':(['이제 두 조각의 구분은 나아졌습니다.','그런데 어두운 조각 뒤에 어두운 배경을 놓으면 어떨까요?','조각끼리는 달라도,','조각의 가장자리와 배경이 비슷해서 윤곽이 묻힙니다.'],['The two pieces are easier to distinguish now.','But place a dark background behind the darker piece:','although the pieces differ,','its edge can blend into its surroundings.']),
 '06-p02':(['컬러에서는 나무의 초록, 길의 갈색, 상자의 색이 달랐습니다.','흑백이 되면 이 색 이름으로는 구별할 수 없고','밝고 어두운 덩어리가 남습니다.','길과 주변 바닥이 비슷하게 밝으면 경계가 약해지고,'],['In color, the green trees, brown path and chest had distinct hues.','In grayscale those hue labels disappear,','leaving light and dark masses.','If the path and nearby ground have similar brightness, their boundary weakens.']),
 '06-p05':(['마리오 화면에서도 같은 질문을 던질 수 있습니다.','어디를 먼저 보게 할까요?'],['Ask the same question in Mario’s scene:','should the eye go first to the ground beneath the character, the next obstacle, or the distant scenery?']),
 '07-p01':(['정리하면 색각 시뮬레이션에서는 같은 종류를 구분할 수 있는지 확인하고,','흑백에서는 밝기와 경계, 시선의 우선순위를 확인합니다.','둘 중 하나가 다른 하나를 대신하지 않습니다.'],['Color-vision simulation checks whether matching types remain distinguishable.','Grayscale checks brightness, boundaries and the order of attention.','Neither replaces the other:']),
 '07-p02':(['익숙해서 지나쳤던 어색함이 드러나듯,','색을 잠깐 빼는 것도 화면을 새롭게 보는 방법입니다.'],['Flipping artwork can reveal awkward details hidden by familiarity.','Temporarily removing color is another way to see a scene afresh.'])
}
# The following authored boundaries match the same thought in both languages.
splits={
 ('01-p01',0):('뿌요뿌요 테트리스 2에서는,','In Puyo Puyo Tetris 2,'),
 ('01-p02',0):('다음 조각을 어디에 놓을지는,','Choosing where to place the next piece'),
 ('01-p02',2):('게임의 규칙은 같아도,','The rule stays the same,'),
 ('01-p03',0):('이번에는 같은 장면의 색을 바꿔 보면서,','We will change the colors in the same scene'),
 ('01-p03',1):('먼저 종류를 구별하는 단서를 보강하고,','First we will strengthen the clues that distinguish types,'),
 ('02-p01',0):('여기서는 원리를 보기 쉽게,','For a clear demonstration,'),
 ('02-p02',0):('이제 위치와 모양은 그대로 두고,','Now keep their positions and shapes unchanged'),
 ('02-p02',2):('조각이 없어진 것이 아니라,','The pieces have not disappeared;'),
 ('02-p03',2):('테마가 바뀌어 배경과 조각의 색이 달라지면,','When a theme changes the colors of the pieces and their surroundings,'),
 ('03-p01',1):('특정한 색각 조건을 가정했을 때,','It previews particular color-vision conditions'),
 ('03-p02',2):('한 화면만 통과했다고 끝내기보다,','Instead of stopping after one view looks acceptable,'),
 ('03-p04',0):('뿌요뿌요 테트리스 2에도 색 조정 기능이 추가되어,','Puyo Puyo Tetris 2 also added color-adjustment options,'),
 ('04-p01',1):('색의 차이가 작아도,','Even with a small color difference,'),
 ('04-p03',0):('배경을 한 단계 밝게 바꾸거나,','Making the background lighter'),
 ('04-p03',1):('조각을 무조건 더 밝게 만드는 대신,','Rather than making every piece brighter,'),
 ('04-p04',1):('한 종류에는 동그라미, 다른 종류에는 세모를 붙이고,','Give one type a circle, another a triangle,'),
 ('04-p04',3):('동그라미 세 개 옆에 동그라미 하나를 놓으면 네 개라는 관계를,','Three circles plus another circle make a group of four—'),
 ('04-p05',1):('색은 같은 종류를 빠르게 찾게 하고,','Color helps players find matching types quickly,'),
 ('05-p01',2):('색만 다른 두 점이 아니라,','They are not merely two colored spots:'),
 ('05-p03',1):('가까이에서는 윤곽과 표시가 대상을 확인해 주고,','Up close, outlines and symbols confirm the object,'),
 ('05-p03',2):('색, 모양, 행동의 결과가 같은 방향으로 안내할수록','When color, shape and action all point in the same direction,'),
 ('06-p01',0):('무엇인지 알게 했다면,','Once an object is recognizable,'),
 ('06-p01',1):('캐릭터 앞에는 걸어갈 길과 보물상자가 있고,','In our Unity scene, a path and a treasure chest lie in front of the character,'),
 ('06-p03',2):('다른 물체를 지우거나 카메라를 옮기지 않았는데도,','We have not removed objects or moved the camera,'),
 ('06-p04',3):('색을 없애는 것이 목적이 아니라,','The aim is not to remove color,'),
 ('08-p01',1):('그 옆에 명도, 모양, 무늬를 함께 준비하면','Supporting it with lightness, shape and pattern'),
 ('08-p01',2):('대상을 찾고, 배경과 구별하고,','Can players find the object, separate it from the background')
}
result=[]
ko,en=read('narration.ko.json'),read('narration.en.json')
for a,b in zip(ko['scenes'],en['scenes']):
 for line,(pid,k,e) in enumerate(zip(a['paragraphIds'],a['lines'],b['lines'])):
  if pid in explicit:ks=after(k,explicit[pid][0]);es=after(e,explicit[pid][1])
  else:ks,es=sentences(k),sentences(e)
  if len(ks)!=len(es):raise ValueError((pid,len(ks),len(es)))
  pairs=[]
  for j,(x,y) in enumerate(zip(ks,es)):
   if (pid,j) in splits:
    ax,ay=splits[pid,j];xs,ys=after(x,[ax]),after(y,[ay]);pairs.extend(zip(xs,ys))
   else:pairs.append((x,y))
  assert re.sub(r'\s','',k)==re.sub(r'\s','',' '.join(x for x,y in pairs)),pid
  assert re.sub(r'\s','',e)==re.sub(r'\s','',' '.join(y for x,y in pairs)),pid
  units=[{'ko':x,'en':y,'twoLineReason':'Keep the described '+{'01':'player decision and its visible clue','02':'controlled variable and its effect','03':'inspection condition and target','04':'contrast or symbol relationship','05':'recognizable object and action','06':'fixed-scene brightness relationship','07':'inspection question and criterion','08':'information-preserving conclusion'}[a['id']]+' together at the fixed48px size.'} for x,y in pairs]
  for u in units:
   for term,translation,role in [('색각 시뮬레이션','Color-vision simulation','term'),('명도 차이','lightness contrast','term'),('시각적 위계','visual hierarchy','term'),('밝고 어두운 덩어리','light and dark masses','result'),('네 개','four','result')]:
    if term in u['ko'] and translation in u['en']:
     u['emphasis']={lang:{'start':u[lang].index(word),'end':u[lang].index(word)+len(word),'role':role} for lang,word in [('ko',term),('en',translation)]};break
  result.append({'id':pid,'scene':a['id'],'line':line,'semanticPairingReviewed':True,'captionUnits':units})
root=H.parents[3]
inputs=[{'path':str((H/n).relative_to(root)).replace('\\','/'),'sha256':hashlib.sha256((H/n).read_bytes()).hexdigest(),'bytes':(H/n).stat().st_size} for n in ['narration.ko.json','narration.en.json','narration.spoken-ko.json']]
(H/'caption-units.json').write_text(json.dumps({'slug':'limited-color-world','revision':'clarity-v3','status':'paired-semantic-units-authored-timestamps-pending','scriptInputs':inputs,'paragraphs':{p['id']:p for p in result}},ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'paragraphs':len(result),'units':sum(len(p['captionUnits']) for p in result)}))
