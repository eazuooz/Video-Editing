from common import *
P=R/'projects/game-math-projection-depth';H=P/'production/concept-fit-v2';T=read(H/'timeline.json');slots={s['id']:s for s in T['scenes']};authorized('M18')
SOURCES={
 'town':dict(path='shared/output/game-math-part2-full-series/sources/FRfnXAIbA-M.mp4',audioPath='shared/output/private-math-concept-fit-20261023/sources/m16-audio/FRfnXAIbA-M.mp4',url='https://www.youtube.com/watch?v=FRfnXAIbA-M',game='Townscaper',minimumHeight=1080),
 'tinyB':dict(path='shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/tiny-glade-256965562.mp4',url='https://store.steampowered.com/app/2198150/Tiny_Glade/',game='Tiny Glade',minimumHeight=1080,sourceSilent=True)}
def shot(scene,source,start,seconds,title,meaning,model,line=1,track=None):
 return dict(scene=scene,source=source,start=start,seconds=seconds,offset=slots[scene]['lineStarts'][line-1] if line>1 else 0,title=title,phases=[(0,seconds,meaning)],model=model,track=track or [],track2=[])
SHOTS={
 '03':shot('03','town',1205,6,'새 건물이 뒤 난간을 가림','새 지붕·벽과 기존 난간 구분','가까운 지붕 / 뒤의 면'),
 '06':shot('06','tinyB',13.5,5,'기울어진 지붕에 붙은 무늬','면의 경계와 반복 무늬를 함께 보기','표면 격자 / 원근 보간'),
 '09-view':shot('09','town',1507.2,2.4,'같은 테라스의 모서리 찾기','나무와 모서리를 함께 기준으로 보기','같은 기준점 / 관찰 방향'),
 '09-build':shot('09','town',1492,5,'새 벽과 지붕이 생기는 순간','시점 변화와 구조 편집은 다른 조건','새 블록 / 기존 기준점',line=3)}
def adapt(s):return s.replace('M17','M18').replace('m17','m18').replace('game-math-camera-projection',P.name)
s=adapt((B/'compose-m17.py').read_text(encoding='utf8'));a=s.index('SOURCES=');b=s.index('ENC=',a);s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[b:];s=s.replace("['02','05','08','11','14']","['03','06','09']").replace('len(records)==16','len(records)==10').replace('16 exact-frame','10 exact-frame');(B/'compose-m18.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m17.py').read_text(encoding='utf8')).replace('len(levels)==9','len(levels)==6').replace('Matched9','Matched6');(B/'mix-m18.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m17.py').read_text(encoding='utf8')).replace('렌더링 ③ 한 3D 점이 화면의 픽셀이 되는 과정','렌더링 ④ 깊이와 원근 보간').replace('지붕의 같은 점·큐브 배치·카메라 이동을 대응하는 좌표 모형과 함께 비교하도록','앞뒤 가림·지붕 무늬·테라스 기준점을 대응하는 깊이·원근 모형과 함께 비교하도록');(B/'assemble-m18.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m17.py').read_text(encoding='utf8')).replace("['02','05','08','11','14','03','07','10','13','15','24']","['03','06','09','02','04','05','07','08','10']");(B/'qa-m18.py').write_text(s,encoding='utf8')
old=read(R/'projects/game-math-camera-projection/production/concept-fit-v2/source-evidence.json')['sources'];sources=[]
for key,s in SOURCES.items():
 meta=probe(R/s['path']);v=next(x for x in meta['streams'] if x['codec_type']=='video');assert v['height']>=1080;audio=R/s.get('audioPath',s['path']);am=probe(audio)
 r=dict(key=key,**s,sha256=sha(R/s['path']),width=v['width'],height=v['height'],fps=v['r_frame_rate'],audioSha256=sha(audio),audioStreams=[x['codec_name'] for x in am['streams'] if x['codec_type']=='audio'])
 if key=='town':r['inheritedRights']=next(x for x in old if x['key']=='town')
 else:
  assert not r['audioStreams'];r.update(rightsEvidence='projects/game-math-polygon-centers-v2/production/concept-fit-v2/source-evidence.json',rights='Pounce Light official Steam developer trailer/presskit; source has no audio stream, retain native silence.',credit='Tiny Glade © Pounce Light')
 sources.append(r)
e=dict(checkedAt=now(),sources=sources,coarseInspection='shared/output/private-math-concept-fit-20261023/candidates/m18/inspection.json',fineInspection='shared/output/private-math-concept-fit-20261023/candidates/m18/selected/inspection.json',directVisualReview='63 coarse frames/6sheets and46 fine frames/4sheets directly inspected. TinyB static roof selected without falsely claiming a camera orbit; Town orbit trimmed before roof editing.',nativePlayback=dict(tool='cua_repl local tab75',segments=[dict(start=a,end=b,rate=1) for a,b in [(1205,1211.112528),(13.5,18.551205),(1506,1511.076739),(1492,1497.080663)]],actualListening=False),sourceShots=SHOTS,reviewLimit='Rendered game pixels establish geometry/pattern/view observations, not internal depth or shader values.');save(H/'source-evidence.json',e)
save(H/'scene-visual-plan.json',dict(checkedAt=now(),status='source-review-complete-model-preflight-pending',sourceShots=SHOTS,sourceEvidence=rel(H/'source-evidence.json'),renderer='Manim mathematical stage reused for projected3D surface tiles and same-point camera geometry; no duplicate engine scene.',modelSource=rel(B/'m18-scenes.py'),changes='6 game-specific paragraphs;60 unchanged paragraphs and7 original mathematical clips preserved.',coordinateConvention='Own model z-up pinhole geometry, not game coordinates; numerical lesson retains declared row-vector LH+z depth0..1 convention.',annotations='Named screen-space editorial guides; no fabricated telemetry; all overlays clear at source cuts.',reuseReason='Townscaper selected for different object construction and persistent terrace landmark; no exact M16/M17 intervals repeated. TinyB13.5–18.5 differs from M13 intervals.',gameAudio='Town original sound with normal ducking; TinyB verified native silent source; no added BGM',actualListening=False,humanReview='pending'))
print('M18 four inspected windows prepared')
