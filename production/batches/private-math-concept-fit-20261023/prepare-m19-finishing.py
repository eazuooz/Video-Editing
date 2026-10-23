from common import *
P=R/'projects/game-math-mesh-uv';H=P/'production/concept-fit-v2';T=read(H/'timeline.json');slots={s['id']:s for s in T['scenes']};authorized('M19')
SOURCES={
 'tinyB':dict(path='shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/tiny-glade-256965562.mp4',url='https://store.steampowered.com/app/2198150/Tiny_Glade/',game='Tiny Glade',minimumHeight=1080,sourceSilent=True),
 'launch':dict(path='shared/output/private-math-concept-fit-20261023/sources/se2-official/launch.mp4',url='https://store.steampowered.com/app/1133870/Space_Engineers_2/',game='Space Engineers 2',minimumHeight=1080),
 'big':dict(path='shared/output/game-math-part2-full-series/sources/wzQLP0Z3zII.mp4',audioPath='shared/output/private-math-concept-fit-20261023/sources/m15-audio/wzQLP0Z3zII.m4a',url='https://www.youtube.com/watch?v=wzQLP0Z3zII',game='Big Walk',minimumHeight=1080)}
def shot(scene,source,start,seconds,title,meaning,model,line=1):
 return dict(scene=scene,source=source,start=start,seconds=seconds,offset=slots[scene]['lineStarts'][line-1],title=title,phases=[(0,seconds,meaning)],model=model,track=[],track2=[])
SHOTS={
 '02':shot('02','tinyB',34,5,'지붕을 돌리고 높이를 바꾸기','바깥 윤곽과 기와 선을 따로 보기','윤곽선 / 표면 무늬'),
 '06':shot('06','launch',56.5,2.1,'우주선 부품을 붙이고 떼기','판의 이음선은 내부 삼각형의 증거가 아님','판의 테두리 / 명시한 삼각형'),
 '07':shot('07','launch',46.7,4,'각진 우주선의 형태와 밝기','바깥 모양과 면 안의 밝기를 구분','고정 위치 / 별도 법선'),
 '10':shot('10','tinyB',28,2.4,'평평한 벽·지붕·둥근 탑','서로 다른 면이 만나는 경계','평면 / 곡면'),
 '11-front':shot('11','big',600,2,'벽의 평평한 면과 둥근 구멍','실루엣과 표면의 밝기는 다른 단서','구멍의 외곽 / 면의 방향'),
 '11-depth':shot('11','big',603.4,3.4,'구멍 안쪽의 두께','움직임은 빈 공간의 두께를 드러내는 데만 사용','앞면 / 뒷면 / 안쪽 면',line=3),
 '15':shot('15','big',666,4,'같은 구멍을 다시 점검','밝기를 바꾸어도 실제 구멍의 윤곽은 남음','기하 위치 / 셰이딩 방향')}
def adapt(s):return s.replace('M18','M19').replace('m18','m19').replace('game-math-projection-depth',P.name)
s=adapt((B/'compose-m18.py').read_text(encoding='utf8'));a=s.index('SOURCES=');b=s.index('ENC=',a);s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[b:];s=s.replace("['03','06','09']","['02','06','07','10','11','15']").replace('len(records)==10','len(records)==16').replace('10 exact-frame','16 exact-frame');(B/'compose-m19.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m18.py').read_text(encoding='utf8')).replace('len(levels)==6','len(levels)==13').replace('Matched6','Matched13');(B/'mix-m19.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m18.py').read_text(encoding='utf8')).replace('렌더링 ④ 깊이와 원근 보간','렌더링 ⑤ 메시·인덱스·법선').replace('앞뒤 가림·지붕 무늬·테라스 기준점을 대응하는 깊이·원근 모형과 함께 비교하도록','지붕 편집·우주선 조립·벽 구멍을 대응하는 메시·법선 모형과 함께 비교하도록');(B/'assemble-m19.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m18.py').read_text(encoding='utf8')).replace("['03','06','09','02','04','05','07','08','10']","['02','06','07','10','11','15','04','05','08','09','12','13','14','16']");(B/'qa-m19.py').write_text(s,encoding='utf8')
records=[]
rights={'tinyB':'projects/game-math-polygon-centers-v2/production/concept-fit-v2/source-evidence.json','launch':'projects/game-math-quaternion-calculations-v3/production/concept-fit-v2/source-evidence.json','big':'projects/game-math-rendering-light/production/concept-fit-v2/source-evidence.json'}
for key,s in SOURCES.items():
 p=R/s['path'];v=next(x for x in probe(p)['streams'] if x['codec_type']=='video');assert v['height']>=1080;audio=R/s.get('audioPath',s['path']);aa=[x['codec_name'] for x in probe(audio)['streams'] if x['codec_type']=='audio'];assert aa or s.get('sourceSilent')
 records.append(dict(key=key,**s,sha256=sha(p),width=v['width'],height=v['height'],fps=v['r_frame_rate'],audioSha256=sha(audio),audioStreams=aa,inheritedRights=rights[key],rightsReceiptSha256=sha(R/rights[key])))
save(H/'source-evidence.json',dict(checkedAt=now(),sources=records,sourceShots=SHOTS,coarseInspection='shared/output/private-math-concept-fit-20261023/candidates/m19-m20/inspection.json',fineInspection='shared/output/private-math-concept-fit-20261023/candidates/m19-m20/selected/inspection.json',directReview='All128 coarse frames/11sheets and96 selected frames/8sheets directly inspected. M19 retained short wall-hole windows only for visible thickness; walking/combat windows replaced. Final M19-15 extra window playback pending.',actualListening=False))
save(H/'scene-visual-plan.json',dict(checkedAt=now(),status='sources-inspected-model-preflight-pending',sourceShots=SHOTS,renderer='Existing editable Manim projected-geometry stage; reuse all unchanged math clips.',modelSource=rel(B/'m19-scenes.py'),changes='13 game-specific paragraphs regenerated;84 original paragraphs and10 mathematical clips retained.',gameRoles={'Tiny Glade':'Building/roof manipulation and adjoining surface shapes','Space Engineers 2':'Spacecraft component assembly and silhouette/panel distinction','Big Walk':'Only the wall opening and thickness; return deliberately in the recap with a different question'},guideMeaning='Model outlines/topology/face-normal/vertex-normal arrows are explicit instructional geometry, never recovered game data.',coordinateConvention='Own stage z-up, pinhole view. Surface directions shown with labeled role colours; no game telemetry.',noAddedBgm=True,actualListening=False,humanReview='pending'))
save(H/'resource-choice.json',dict(checkedAt=now(),choice='Same Qwen1.7B/ref on CPU; four threads',reason='GPU memory remains occupied by other applications; preserve those processes and avoid a GPU OOM.',qualityChange='No voice/model/text change',actualListening=False))
print('M19 finishing plan prepared')
