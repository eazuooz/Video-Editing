from common import *
import shutil
P=R/'projects/game-math-projection-depth';H=P/'production/concept-fit-v2';O=P/'production/local/concept-fit-v2';O.mkdir(parents=True,exist_ok=True);authorized('M18')
edits={'03':{
 '1':['타운스케이퍼에서 앞쪽 발판에 작은 건물이 생기는 모습을 보겠습니다. 새 지붕과 벽이 뒤쪽 난간의 일부를 가리며 앞뒤 관계가 달라집니다.','Watch a small building appear on the front platform in Townscaper. Its roof and wall cover parts of the railing behind, changing the visible overlap.'],
 '3':['이 관계를 모형으로 옮겨 관찰 높이만 바꿔보겠습니다. 높은 시점에서는 안쪽 바닥이 드러나고, 낮은 시점에서는 앞 지붕과 뒤 벽이 겹쳐 보입니다.','In our model, change only the viewing height. A higher view reveals the inner floor, while a lower view overlaps the front roof and rear wall.']},
 '06':{
 '1':['타이니 글레이드의 기울어진 지붕 무늬와 그 아래 창문을 함께 보세요. 반복되는 무늬가 화면 전체를 덮는 띠가 아니라 건물의 지붕에 붙어 있습니다.','Look at the slanted roof pattern and the windows below in Tiny Glade. The repeated pattern belongs to the roof rather than a stripe across the screen.'],
 '2':['모형에서는 무늬가 붙은 면을 기울여 보겠습니다. 화면에서 무늬의 간격만 단순히 나누면, 실제 표면에서 같은 비율로 떨어진 지점을 올바르게 찾을 수 없습니다.','Tilt the patterned surface in our model. Simply dividing visible spacing does not correctly recover equal fractions along the actual surface.']},
 '09':{
 '1':['마지막으로 타운스케이퍼의 높은 테라스와 가장자리의 작은 나무를 살펴보겠습니다. 시점이 돌아가도 같은 테라스의 모서리를 계속 찾아보세요.','Finally, follow the high terrace and its small edge trees in Townscaper. Keep identifying the same terrace corner as the viewpoint rotates.'],
 '2':['모형에서 그 모서리가 보이지 않으면 먼저 다른 건물 뒤로 가렸는지 확인합니다. 비슷하게 생긴 다른 테라스를 같은 점으로 착각하지 않는 것도 중요합니다.','If the corner disappears in our model, check whether another building hides it. Do not mistake a similar terrace elsewhere for the same point.']}}
save(B/'m18-narration-edits.json',dict(edits=edits,visualOnlyScenes=[],reason='Directly matched platform construction, roof pattern and terrace orbit; preserve all depth/w/interpolation calculations and explanation order.'))
count=sum(map(len,edits.values()));total=sum(len(s['lines']) for s in read(P/'script/narration.ko.json')['scenes'])
src=P/'production/local/private-polish-v1/baseline-audio.m4a';dst=O/'baseline-audio.m4a'
if not dst.exists():shutil.copy2(src,dst)
assert sha(src)==sha(dst);save(H/'restoration.json',dict(source=rel(src),path=rel(dst),sha256=sha(dst),kind='Recovered original AAC; original PCM unavailable',oldMastersPreserved=True))
def adapt(s):return s.replace('M17','M18').replace('m17','m18').replace('game-math-camera-projection',P.name)
s=adapt((B/'prepare-m17-voice.py').read_text(encoding='utf8'));a=s.index('titles=');z=s.index('\njobs=[]',a);s=s[:a]+"titles={'03':'앞 건물이 뒤 난간을 가리는 이유','06':'지붕에 붙은 무늬와 원근 보간','09':'같은 테라스의 기준점을 따라가기'}"+s[z:];(B/'prepare-m18-voice.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m17-audio.py').read_text(encoding='utf8')).replace('newTtsParagraphs=9',f'newTtsParagraphs={count}').replace('unchangedParagraphs=91',f'unchangedParagraphs={total-count}').replace('changed=9,unchanged=91',f'changed={count},unchanged={total-count}').replace("{'02':4,'05':5,'08':6,'11':7,'14':3}","{'03':6,'06':5,'09':7.4}");(B/'assemble-m18-audio.py').write_text(s,encoding='utf8')
for name in ['asr','render','preflight']:(B/f'{name}-m18.py').write_text(adapt((B/f'{name}-m17.py').read_text(encoding='utf8')),encoding='utf8')
# m18 will import the established architecture through m16, not m17.
p=B/'render-m18.py';p.write_text(p.read_text(encoding='utf8').replace("sha(B/'m16-scenes.py')","sha(B/'m16-scenes.py')"),encoding='utf8')
s=adapt((B/'captions-m17.py').read_text(encoding='utf8'));a=s.index('pairedEnglish=');z=s.index("\nfor s in T['scenes']:",a);s=s[:a]+'pairedEnglish={}'+s[z:];s=s.replace('sourceParagraphs=100',f'sourceParagraphs={total}');(B/'captions-m18.py').write_text(s,encoding='utf8')
save(H/'narration-text-review.json',dict(status='Every original KO/EN paragraph and six replacements directly read',at=now(),changed=count,unchanged=total-count,total=total,orderPreserved=True,mathPreserved=['Depth1.1−1.1/z: z2→.55,z4→.825,z6→.9167; orthographic(z−1)/10','w1/4,u0/1: screen midpoint numerator.125 denominator.625 givesu.2','Positive homogeneous scale cancels after divide; not every internal operation equivalent','Vertex→clip→divide→viewport; bounds/occlusion/LOD distinct','Camera move(3,1,1) produces(600,175);viewport origin0 yields(600,125);fullFHD(1440,300)'],actualListening=False))
print(count,'changed;',total-count,'preserved;',total,'paragraphs')
