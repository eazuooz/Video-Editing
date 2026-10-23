from common import *
P=R/'projects/game-math-normal-transform-uv';H=P/'production/concept-fit-v2';T=read(H/'timeline.json');slots={s['id']:s for s in T['scenes']};authorized('M20')
SOURCES={
 'tinyB':dict(path='shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/tiny-glade-256965562.mp4',url='https://pouncelight.games/tiny-glade/',game='Tiny Glade',minimumHeight=1080,sourceSilent=True),
 'se2':dict(path='shared/output/private-math-concept-fit-20261023/sources/se2-official/vs1.2.mp4',url='https://mirror.keenswh.com/PressKits/SE2%20Press%20Kit.zip',game='Space Engineers 2',minimumHeight=1080)}
def shot(scene,source,start,seconds,title,meaning,model):
 return dict(scene=scene,source=source,start=start,seconds=seconds,offset=0,title=title,phases=[(0,seconds,meaning)],model=model,track=[],track2=[])
SHOTS={
 '04':shot('04','se2',78.5,5,'부품의 모양은 그대로 · 색 변경','같은 부품의 모서리와 색을 나누어 보기','위치 고정 / 표면 속성'),
 '05':shot('05','tinyB',31,3,'건물 벽의 색 고르기','바깥 윤곽·창문 위치와 표면 색 구분','벽 윤곽 / 이미지 대응'),
 '08':shot('08','tinyB',41,6,'기존 초록 지붕에 붙은 기와','오른쪽 기존 지붕과 새 건물을 구분','표면 고정 / 관찰 방향'),
 '09':shot('09','se2',94,4.5,'손에 든 부품보다 바닥을 관찰','반복된 선·구멍이 내부 UV의 증거는 아님','화면 위치 / 표면 위치'),
 '12':shot('12','tinyB',52,4,'빛이 달라져도 남는 윤곽','큰 형태·면 방향·반복 무늬를 따로 점검','기하 / 법선 / UV')}
SHOTS['05']['track']=[(.2,.555,.36,72),(1,.555,.36,72),(2,.555,.36,72),(2.7,.555,.36,72)]
SHOTS['09']['track']=[(0,.10,.50,65),(.5,.10,.50,65),(1,.11,.47,65),(1.5,.12,.40,65),(2,.12,.40,65),(3,.12,.40,65),(4.3,.13,.42,65)]
def adapt(s):return s.replace('M19','M20').replace('m19','m20').replace('game-math-mesh-uv',P.name)
s=adapt((B/'compose-m19.py').read_text(encoding='utf8'));a=s.index('SOURCES=');b=s.index('ENC=',a);s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[b:];s=s.replace("['02','06','07','10','11','15']","['04','05','08','09','12']").replace('len(records)==16','len(records)==13').replace('16 exact-frame','13 exact-frame');(B/'compose-m20.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m19.py').read_text(encoding='utf8')).replace('len(levels)==13','len(levels)==18').replace('Matched13','Matched18').replace("['타이니 글레이드','시야각','직교 투영','세계·좌표·클리핑'","['타이니 글레이드','법선','역전치','UV·주소 모드'");(B/'mix-m20.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m19.py').read_text(encoding='utf8')).replace('렌더링 ⑤ 메시·인덱스·법선','렌더링 ⑥ 법선 변환과 UV').replace('지붕 편집·우주선 조립·벽 구멍을 대응하는 메시·법선 모형과 함께 비교하도록','부품 색 변경·벽 색 고르기·고정 지붕의 무늬를 법선·UV 설명 모형과 함께 비교하도록');(B/'assemble-m20.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m19.py').read_text(encoding='utf8')).replace("['02','06','07','10','11','15','04','05','08','09','12','13','14','16']","['02','03','04','05','06','07','08','09','10','11','12','13']");(B/'qa-m20.py').write_text(s,encoding='utf8')
s=adapt((B/'captions-m19.py').read_text(encoding='utf8')).replace('sourceParagraphs=97','sourceParagraphs=81').replace("[('클리핑','clipping'),('좌표','coordinates'),('시야각','field of view'),('출력 창','viewport'),('직교','orthographic'),('원근','perspective'),('줌','zoom')]","[('법선','normal'),('접선','tangent'),('역전치','inverse transpose'),('좌표','coordinates'),('UV','UV'),('보간','interpolation')]");(B/'captions-m20.py').write_text(s,encoding='utf8')
records=[]
rights={'tinyB':'projects/game-math-polygon-centers-v2/production/concept-fit-v2/source-evidence.json','se2':'projects/game-math-quaternion-foundations-v3/production/concept-fit-v2/source-evidence.json'}
for key,s in SOURCES.items():
 p=R/s['path'];meta=probe(p);v=next(x for x in meta['streams'] if x['codec_type']=='video');assert v['height']>=1080;aa=[x['codec_name'] for x in meta['streams'] if x['codec_type']=='audio'];assert aa or s.get('sourceSilent')
 records.append(dict(key=key,**s,sha256=sha(p),width=v['width'],height=v['height'],fps=v['r_frame_rate'],audioStreams=aa,inheritedRights=rights[key],rightsReceiptSha256=sha(R/rights[key])))
save(H/'source-evidence.json',dict(checkedAt=now(),sources=records,sourceShots=SHOTS,coarseInspection='shared/output/private-math-concept-fit-20261023/candidates/m19-m20/inspection.json',fineInspection='shared/output/private-math-concept-fit-20261023/candidates/m19-m20/selected/inspection.json',extraInspection='shared/output/private-math-concept-fit-20261023/candidates/m19-m20/extra/inspection.json',nativePlayback=rel(B/'m19-m20-source-playback.json'),directReview='128 coarse,96 selected and31 extra frames directly inspected. Native source intervals played at1x. Chosen actions show colour changes, persistent roof patterns, floor repetition and daylight changes, not generic traversal. Source appearance is never claimed to reveal UV or mesh data.',actualListening=False))
save(H/'scene-visual-plan.json',dict(checkedAt=now(),status='sources-inspected-model-preflight-pending',sourceShots=SHOTS,renderer='Reuse editable projected-geometry Manim mathematical stage, preserving every unchanged mathematical scene.',modelSource=rel(B/'m20-scenes.py'),changes='18 game-specific paragraphs replaced;63 original paragraphs retained.',guideMeaning='Surface outlines, labeled vertices, normal arrows, numbered UV checker and camera-only orbit are explicit own geometry. No recovered game telemetry.',coordinateConvention='Own z-up stage, perspective projection. Light calculation is a teaching Lambert example, not the game renderer.',noAddedBgm=True,actualListening=False,humanReview='pending'))
print('M20 finishing scripts and source plan prepared')
