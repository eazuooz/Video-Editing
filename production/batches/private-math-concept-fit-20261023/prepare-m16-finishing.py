from common import *
P=R/'projects/game-math-camera-frustum';H=P/'production/concept-fit-v2';T=read(H/'timeline.json');slots={s['id']:s for s in T['scenes']};authorized('M16')
SOURCES={
 'split':dict(path='shared/output/game-math-part2-full-series/sources/8RZ1nPWzWtg.mp4',audioPath='shared/output/private-math-concept-fit-20261023/sources/m16-audio/8RZ1nPWzWtg.mp4',url='https://www.youtube.com/watch?v=8RZ1nPWzWtg',game='Split Fiction',minimumHeight=1080),
 'town':dict(path='shared/output/game-math-part2-full-series/sources/FRfnXAIbA-M.mp4',audioPath='shared/output/private-math-concept-fit-20261023/sources/m16-audio/FRfnXAIbA-M.mp4',url='https://www.youtube.com/watch?v=FRfnXAIbA-M',game='Townscaper',minimumHeight=1080),
 'tiny':dict(path='shared/output/private-math-concept-fit-20261023/sources/tiny-glade-official/release-date-trailer.mp4',url='https://pouncelight.games/tiny-glade/presskit',game='Tiny Glade',minimumHeight=1080)}
def shot(scene,source,start,seconds,title,meaning,model,line=1,track=None,track2=None):
 return dict(scene=scene,source=source,start=start,seconds=seconds,offset=slots[scene]['lineStarts'][line-1] if line>1 else 0,title=title,phases=[(0,seconds,meaning)],model=model,track=track or [],track2=track2 or [])
SHOTS={
 '02':shot('02','split',33,8,'두 플레이어의 서로 다른 화면','분할선 양쪽의 관찰 방향을 비교','관찰 방향 / 출력 영역'),
 '05':shot('05','tiny',12,4.5,'탑 앞의 건물을 직접 편집','지붕과 벽이 바뀜 → 물체의 형태 변경','물체 변화 / 시점 변화',track=[(2,.53,.59,95),(2.5,.49,.60,95),(3,.48,.60,95),(3.5,.47,.60,95),(4.3,.46,.60,95)]),
 '08':shot('08','town',409.7,4.3,'완성된 건물 주위로 시점 이동','낮은 시점 → 높은 시점 → 다른 면','같은 건물 / 다른 관찰 방향',track=[(3.3,.58,.38,70),(3.8,.58,.38,70),(4.2,.58,.38,70)]),
 '11':shot('11','split',294,7,'캐릭터 크기와 주변 공간','거리·방향·시야각을 따로 확인','크기를 만드는 조건 / 통제된 비교'),
 '13':shot('13','town',775.5,4.5,'같은 지붕을 넓게, 가까이 보기','같은 기준점을 남겨 확대 전후 비교','앞 지붕 A / 뒤 지붕 B',track=[(3.5,.20,.21,70),(4,.20,.21,70),(4.4,.20,.23,70)]),
 '16':shot('16','town',1450,4.5,'큰 문과 뒤쪽 지붕의 관계','건물 고정 · 가까워지고 방향이 바뀜','앞벽 A / 뒤 지붕 B',track=[(2.5,.72,.35,80),(3,.72,.35,80),(3.5,.72,.35,80),(4,.72,.35,80)]),
 '19':shot('19','tiny',53.25,5.25,'같은 성에서 주변 탑까지','카메라가 물러나며 보이는 범위 변화','관찰 위치 / 담을 범위'),
 '21-view':shot('21','town',1104,3,'물체 변화와 관찰 변화 구분','시점과 담는 범위를 먼저 비교','관찰 조건 변화'),
 '21-build':shot('21','town',1107,7,'블록 추가는 물체의 변화','새로 생긴 바닥과 기존 면 구분','물체 자체의 변화',line=2,track=[(2.5,.55,.58,100),(3,.55,.58,100),(3.5,.55,.58,100),(4,.55,.58,100),(4.5,.55,.58,100),(5,.55,.58,100),(5.5,.55,.58,100),(6,.55,.58,100)])}
def adapt(s):return s.replace('M15','M16').replace('m15','m16').replace('game-math-rendering-light',P.name)
s=adapt((B/'compose-m15.py').read_text(encoding='utf8'));a=s.index('SOURCES=');b=s.index('ENC=',a);s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[b:]
s=s.replace("['02','05','08','11','14','17','19','21']","['02','05','08','11','13','16','19','21']")
needle=" path=C/f'{sid}.guides.ass';"
s=s.replace(needle,""" if s['source']=='split':
  event(0,d,'{\\\\an7\\\\pos(640,130)\\\\p1\\\\bord3\\\\shad0\\\\1a&HFF&\\\\3c&HA2D380&}m 0 0 l 0 720',1)
  label(0,d,55,150,'왼쪽 카메라',28,'80D3A2');label(0,d,700,150,'오른쪽 카메라',28,'78B7FF')
"""+needle)
(B/'compose-m16.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m15.py').read_text(encoding='utf8')).replace('len(levels)==14','len(levels)==9').replace('Matched14','Matched9').replace("['BRDF','복사휘도','복사조도','입체각'","['타이니 글레이드','시야각','직교 투영','05.L02 지금'");(B/'mix-m16.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m15.py').read_text(encoding='utf8')).replace('렌더링 ① 빛·재질·시선으로 픽셀 계산하기','카메라 ① 시야각·절두체·출력 창').replace('가림·반투명 표면·조명 설치를 대응하는 단면 모형과 함께 보여 주도록','건축 편집·시점 이동·두 플레이어 화면을 대응하는 투영 모형과 함께 비교하도록');(B/'assemble-m16.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m15.py').read_text(encoding='utf8')).replace("['02','05','08','11','14','17','19','21','09','13','18','22']","['02','05','08','11','13','16','19','21','09','14','18','22']");(B/'qa-m16.py').write_text(s,encoding='utf8')
e=read(H/'source-evidence.json')
for source in e['sources']:
 if source['id'] not in ['8RZ1nPWzWtg','FRfnXAIbA-M']:continue
 ident=source['id'];info=R/f'shared/output/private-math-concept-fit-20261023/sources/m16-audio/{ident}.info.json';d=read(info)
 audio=R/f'shared/output/private-math-concept-fit-20261023/sources/m16-audio/{ident}.mp4';m=probe(audio);assert len([s for s in m['streams'] if s['codec_type']=='audio'])==1
 source.update(currentPermissionDescription=d['description'],currentPermissionProof=rel(info),currentPermissionProofSha256=sha(info),audioPath=rel(audio),audioSha256=sha(audio),audioSeconds=m['format']['duration'],audioFormat='YouTube offered234 HLS original audio; no other recording substituted',sourceAudioUsed=True)
 if ident=='8RZ1nPWzWtg':source.update(creditRequirement='Gameplay – @Candepril; placement not specified in current description, credit in our description bottom',requiredVisibleCredit=None)
save(H/'source-evidence.json',e)
plan=read(H/'scene-visual-plan.json');plan.update(status='model-preflight-complete-composition-next',sourceShots=SHOTS,modelImplementation='Manim mathematical pinhole-camera projection, real3D planar meshes with depth-sorted faces; own model geometry/camera independent variables, not game telemetry',modelSource=rel(B/'m16-scenes.py'),modelPreflight='16 actual rendered frames on2 sheets directly inspected: building faces, roof markers, right-hand swap16, caption-space clear. Final captions still pending.',sourceAudio='Synchronized audio separately recovered from the same Split Fiction/Townscaper source; Tiny Glade developer trailer original audio. No added BGM.',scene21Cue='Split native window:1104–1107 on paragraph1;1107–1114 on paragraph2 when narration names block additions.',actualListening=False);save(H/'scene-visual-plan.json',plan)
print('M16 nine native cuts,8 changed models,14 preserved mathematical clips prepared')
