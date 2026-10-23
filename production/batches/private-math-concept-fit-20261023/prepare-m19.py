from common import *
import shutil
P=R/'projects/game-math-mesh-uv';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';O.mkdir(parents=True,exist_ok=True);authorized('M19')
edits={'02':{
 '1':['타이니 글레이드에서 작은 건물을 만들고 지붕을 돌리는 장면입니다. 지붕의 바깥 윤곽과 표면에 반복되는 기와 선을 따로 보세요.','Tiny Glade shows a small building being created and its roof rotated. Separate the outer roof silhouette from the repeated tile lines on its surface.'],
 '2':['지붕을 돌리고 높이를 바꾸면 벽과 만나는 모양도 달라집니다. 모양을 정하는 표면과 그 위의 무늬를 같은 정보라고 생각하기 쉽습니다.','Rotating and raising the roof changes how it meets the wall. It is easy to confuse the surface that defines shape with the pattern on that surface.'],
 '3':['모형에서도 지붕의 외곽선과 면 안의 격자를 따로 표시하겠습니다. 외곽을 바꾸는 형태와 면 안에 보이는 선을 구분해 보세요.','Our model marks the roof silhouette separately from the interior grid. Distinguish changes to the outline from lines inside a face.']},
 '06':{
 '1':['스페이스 엔지니어스 투에서 우주선 부품을 배치하는 장면입니다. 빨강과 흰색 판의 이음선과, 우주선 바깥 윤곽을 나누어 보세요.','Space Engineers 2 shows spacecraft parts being placed. Separate the seams on the red and white panels from the craft silhouette.'],
 '2':['부품을 붙였다 떼면 전체 형태가 달라지고, 남아 있는 판에는 이음선이 보입니다. 바깥 테두리와 면 안의 선은 같은 정보가 아닙니다.','Attaching or removing a part changes the overall shape, while panel seams remain visible. The outer boundary and lines inside a face are different information.'],
 '3':['이 차이를 모형의 사각 판으로 옮겨 보겠습니다. 판의 테두리, 표면 무늬, 실제로 정의한 두 삼각형을 차례로 구분합니다.','Transfer that distinction to our rectangular model. Separate its boundary, surface pattern and the two explicitly defined triangles.'],
 '4':['게임의 이음선이 모두 삼각형 인덱스의 모서리라는 증거는 아닙니다. 무늬, 별도 표면이나 다른 표현일 수도 있습니다.','The game panel seams do not prove triangle-index edges. They could come from patterns, separate surfaces or other representations.'],
 '7':['모형에서 표면의 위치는 고정하고 방향 화살표만 바꾸어 보겠습니다. 이 비교를 바탕으로 면 법선과 정점 법선의 역할을 연결하겠습니다.','Keep the model surface fixed and change only its direction arrows. This comparison connects face normals with vertex normals.']},
 '07':{
 '1':['스페이스 엔지니어스 투의 우주선 옆면을 보겠습니다. 꺾인 바깥 윤곽과, 빨강과 흰색 면 안의 밝기를 따로 관찰해 보세요.','Look at the spacecraft side in Space Engineers 2. Separate its angular silhouette from brightness within the red and white faces.'],
 '2':['부품을 배치하며 관찰 방향이 바뀌어도 각진 가장자리는 남습니다. 화면에 각진 모양이 보인다고 모든 면의 법선 처리까지 알 수는 없습니다.','Angular edges remain as parts are placed and the viewpoint changes. Their appearance does not reveal how every face normal is handled.'],
 '3':['이 관계를 모형으로 옮겨 빛의 방향을 고정하겠습니다. 같은 빛을 받아도 위쪽 면과 옆쪽 면은 서로 다른 방향을 향합니다.','In our model, keep the light direction fixed. The top and side faces point in different directions under the same light.'],
 '5':['모형에서는 바깥 모양을 만드는 위치를 그대로 두고, 빛 계산에 쓰는 방향만 바꾸겠습니다. 두 입력의 역할을 따로 비교해 보세요.','Keep the model vertex positions fixed and change only the lighting directions. Compare these two inputs separately.']},
 '10':{'1':['타이니 글레이드의 성에서 평평한 벽과 뾰족한 지붕, 둥근 탑의 경계를 보세요. 서로 다른 표면이 만나는 곳의 형태를 비교하겠습니다.','Look at the boundaries between flat walls, pointed roofs and round towers in Tiny Glade. Compare the shape where different surfaces meet.']}}
visual=['11','15'];save(B/'m19-narration-edits.json',dict(edits=edits,visualOnlyScenes=visual,reason='Replace traversal/combat with roof editing and spacecraft assembly; retain only short wall-opening passages whose visible thickness directly demonstrates silhouette versus shading.'))
count=sum(map(len,edits.values()));total=sum(len(s['lines']) for s in read(P/'script/narration.ko.json')['scenes'])
src=P/'production/local/private-polish-v1/baseline-audio.m4a';dst=O/'baseline-audio.m4a'
if not dst.exists():shutil.copy2(src,dst)
assert sha(src)==sha(dst);save(H/'restoration.json',dict(source=rel(src),path=rel(dst),sha256=sha(dst),kind='Recovered original AAC; original PCM unavailable',oldMastersPreserved=True))
def adapt(s):return s.replace('M18','M19').replace('m18','m19').replace('game-math-projection-depth',P.name)
s=adapt((B/'prepare-m18-voice.py').read_text(encoding='utf8'));a=s.index('titles=');z=s.index('\njobs=[]',a);s=s[:a]+"titles={'02':'지붕의 윤곽과 표면 무늬','06':'판의 이음선과 삼각형 연결','07':'우주선의 형태와 면의 밝기','10':'벽·지붕·탑이 만나는 경계'}"+s[z:];(B/'prepare-m19-voice.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m18-audio.py').read_text(encoding='utf8')).replace('newTtsParagraphs=6',f'newTtsParagraphs={count}').replace('unchangedParagraphs=60',f'unchangedParagraphs={total-count}').replace('changed=6,unchanged=60',f'changed={count},unchanged={total-count}').replace("{'03':6,'06':5,'09':7.4}","{'02':5,'06':2.1,'07':4,'10':2.4,'11':5.4,'15':4}");(B/'assemble-m19-audio.py').write_text(s,encoding='utf8')
for name in ['asr','render','preflight']:(B/f'{name}-m19.py').write_text(adapt((B/f'{name}-m18.py').read_text(encoding='utf8')),encoding='utf8')
s=adapt((B/'captions-m18.py').read_text(encoding='utf8'));a=s.index('pairedEnglish=');z=s.index("\nfor s in T['scenes']:",a);s=s[:a]+'pairedEnglish={}'+s[z:];s=s.replace('sourceParagraphs=66',f'sourceParagraphs={total}');(B/'captions-m19.py').write_text(s,encoding='utf8')
save(H/'narration-text-review.json',dict(status='All original KO/EN paragraphs and thirteen replacement game paragraphs directly read',at=now(),changed=count,unchanged=total-count,total=total,orderPreserved=True,mathPreserved=['192 versus140 bytes; local44 bytes is a different scope','Full vertex attribute sharing and winding','Face normals versus shading normals and silhouette','Normalized sum(1,1,1) and degenerate/zero guards','Cube8positions24records; UV and normal seams','Triangle count bias(1,2,1), angle versus area weights'],actualListening=False))
print(count,'changed;',total-count,'preserved;',total,'paragraphs')
