from common import *
import shutil
P=R/'projects/game-math-camera-projection';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';O.mkdir(parents=True,exist_ok=True);authorized('M17')
edits={'02':{},'05':{
'1':['타이니 글레이드에서 앞쪽 집의 지붕 모서리를 기준점으로 골라 보세요. 창문과 굴뚝을 더해도 처음 고른 지붕 모서리와 새로 생긴 점은 서로 다릅니다.','Choose a roof corner on the foreground house in Tiny Glade. Adding a window or chimney creates new points; they are not the original roof landmark.'],
'2':['같은 점의 좌표 변환을 비교하려면 처음 고른 기준점을 계속 따라가야 합니다. 새 굴뚝의 끝으로 바꿔 잡으면 비교 대상부터 달라집니다.','To compare coordinate transforms of one point, keep following the original landmark. Switching to the new chimney tip changes the point being compared.'],
'3':['이제 같은 집을 단순한 모형으로 옮겨 시점만 돌려보겠습니다. 건물은 그대로인데 지붕 모서리의 화면 위치가 달라집니다.','Now move the same idea into our simplified house model and orbit only the camera. The building stays fixed, but the roof corner changes screen position.']},
'08':{'1':['타운스케이퍼의 높은 탑과 아래 테라스를 함께 보겠습니다. 아래에는 새 발판이 붙고, 시점이 낮아지면서 같은 탑에서 보이는 면도 달라집니다.','Watch the tall tower and lower terrace in Townscaper. A platform is added below; lowering the viewpoint also changes which faces of the same tower are visible.']},
'11':{'5':['모형에서는 큐브를 옮기는 조작과 카메라를 옮기는 조작을 따로 해보겠습니다. 화면 위치가 달라졌다는 결과만 같고, 바꾼 조건은 서로 다릅니다.','In our model, move the cube and move the camera separately. Both change its screen position, but they change different inputs.']},
'14':{
'1':['타운스케이퍼에서 앞쪽 테라스의 지붕을 편집하는 모습입니다. 새로 생긴 지붕과 뒤쪽의 높은 건물을 함께 보세요.','This Townscaper view edits the roof over the front terrace. Watch the new roof and the taller building behind it.'],
'2':['이 관계를 모형으로 옮겨 시점만 돌리면, 뒤 건물의 일부가 앞쪽 지붕 뒤로 숨습니다. 이런 가림은 화면 바깥으로 나가서 잘린 것과 다릅니다.','In our model of this relationship, orbiting the camera hides part of the rear building behind the front roof. That differs from crossing the screen boundary.'],
'3':['모형의 시점을 더 높이면 앞 지붕 뒤의 부분이 다시 드러납니다. 보이지 않는 이유를 하나로 뭉뚱그리면 오류를 찾기 어렵습니다.','Raising our model camera reveals the part hidden behind the front roof. Treating all invisibility as one problem makes debugging difficult.'],
'5':['게임 장면은 건물의 형태를 편집하는 예이고, 이어 본 모형은 시점에 따른 가림의 예입니다. 가까운 평면 때문에 구멍이 생겼다는 관찰과 구분합니다.','The game demonstrates geometry editing; our following model demonstrates viewpoint-dependent occlusion. Neither observation establishes a hole caused by the near plane.']}}
save(B/'m17-narration-edits.json',dict(edits=edits,visualOnlyScenes=[],reason='Preserve every mathematical explanation and its order; revise only game-specific descriptions after direct inspection. Remove unrelated extended laser gameplay; shorter native cuts with continuous corresponding model.'))
count=sum(map(len,edits.values()));total=sum(len(s['lines']) for s in read(P/'script/narration.ko.json')['scenes'])
src=P/'production/local/private-polish-v1/baseline-audio.m4a';dst=O/'baseline-audio.m4a'
if not dst.exists():shutil.copy2(src,dst)
assert sha(src)==sha(dst);save(H/'restoration.json',dict(source=rel(src),path=rel(dst),sha256=sha(dst),kind='Recovered original AAC; original PCM unavailable',oldMastersPreserved=True))
def adapt(s):return s.replace('M16','M17').replace('m16','m17').replace('game-math-camera-frustum',P.name)
s=adapt((B/'prepare-m16-voice.py').read_text(encoding='utf8'));a=s.index('titles=');z=s.index('\njobs=[]',a)
titles={'02':'고정된 기둥과 움직이는 관찰 위치','05':'기존 지붕의 점과 새로 생긴 점','08':'같은 탑과 바뀌는 발판·관찰 방향','11':'큐브 배치와 카메라를 따로 바꾸기','14':'새 지붕과 가림을 구분하기'}
(B/'prepare-m17-voice.py').write_text(s[:a]+'titles='+repr(titles)+s[z:],encoding='utf8')
s=adapt((B/'assemble-m16-audio.py').read_text(encoding='utf8')).replace('newTtsParagraphs=9',f'newTtsParagraphs={count}').replace('unchangedParagraphs=125',f'unchangedParagraphs={total-count}').replace('changed=9,unchanged=125',f'changed={count},unchanged={total-count}').replace("{'02':8,'05':4.5,'08':4.3,'11':7,'13':4.5,'16':4.5,'19':5.25,'21':10}","{'02':4,'05':5,'08':6,'11':7,'14':3}")
(B/'assemble-m17-audio.py').write_text(s,encoding='utf8')
for name in ['asr','render','preflight']:(B/f'{name}-m17.py').write_text(adapt((B/f'{name}-m16.py').read_text(encoding='utf8')),encoding='utf8')
s=adapt((B/'captions-m16.py').read_text(encoding='utf8'));a=s.index('pairedEnglish=');z=s.index("\nfor s in T['scenes']:",a);s=s[:a]+'pairedEnglish={}'+s[z:];s=s.replace('sourceParagraphs=134',f'sourceParagraphs={total}');(B/'captions-m17.py').write_text(s,encoding='utf8')
save(H/'narration-text-review.json',dict(status='All original KO/EN paragraphs and nine replacements directly read',at=now(),changed=count,unchanged=total-count,total=total,orderPreserved=True,mathematics=['Row vectors; LH +z; clip z0..w; top-left screen','local(1,0,0)→world(4,2,5)→view(2,1,4)','view inverse, orthonormal transpose limit','w prepared before divide','near1/far11 gives A1.1 B-1.1;clip(2,16/9,3.3,4)','six clipping bounds; near triangle edge t2/3;intersections±1/3','alternate depth .65 maps to .825','viewport(100,50,800,450)→(700,175);continuous coordinate not rounded pixel'],actualListening=False))
print(count,'changed;',total-count,'preserved;',total,'paragraphs')
