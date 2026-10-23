from common import *
P=R/'projects/game-math-camera-projection';H=P/'production/concept-fit-v2';T=read(H/'timeline.json');slots={s['id']:s for s in T['scenes']};authorized('M17')
SOURCES={
 'portal':dict(path='shared/output/game-math-part2-full-series/sources/yFRbGppLaUI.mp4',audioPath='shared/output/private-math-concept-fit-20261023/sources/m17-audio/yFRbGppLaUI.mp4',url='https://www.youtube.com/watch?v=yFRbGppLaUI',game='Portal 2',minimumHeight=720,resolutionException='production/batches/private-game-math-polish-20261022/portal-original-resolution-exception.json'),
 'town':dict(path='shared/output/game-math-part2-full-series/sources/FRfnXAIbA-M.mp4',audioPath='shared/output/private-math-concept-fit-20261023/sources/m16-audio/FRfnXAIbA-M.mp4',url='https://www.youtube.com/watch?v=FRfnXAIbA-M',game='Townscaper',minimumHeight=1080),
 'tiny':dict(path='shared/output/private-math-concept-fit-20261023/sources/tiny-glade-official/release-date-trailer.mp4',url='https://pouncelight.games/tiny-glade/presskit',game='Tiny Glade',minimumHeight=1080)}
def shot(scene,source,start,seconds,title,meaning,model,line=1,track=None):
 return dict(scene=scene,source=source,start=start,seconds=seconds,offset=slots[scene]['lineStarts'][line-1] if line>1 else 0,title=title,phases=[(0,seconds,meaning)],model=model,track=track or [],track2=[])
SHOTS={
 '02':shot('02','portal',18,4,'기둥은 그대로 · 관찰 위치는 이동','기둥의 화면 위치와 뒤쪽 장치의 가림','고정 기둥 / 카메라 변경'),
 '05':shot('05','tiny',17,5,'같은 지붕의 모서리를 계속 추적','기존 지붕과 새 창문·굴뚝을 구분','기존 기준점 A / 새로 생긴 점'),
 '08':shot('08','town',532,6,'탑과 새 발판 · 관찰 방향 구분','구조 추가와 카메라 변화를 따로 보기','기존 탑 / 새 발판 / 관찰 방향'),
 '11-carry':shot('11','portal',36,3.5,'큐브를 방 안에서 이동','기둥을 기준으로 큐브 배치 비교','기둥 고정 / 큐브 이동'),
 '11-place':shot('11','portal',54,3.5,'큐브를 내려놓고 레이저 연결','세계 배치와 화면 위치를 구분','큐브 배치 / 관찰 위치',line=2),
 '14':shot('14','town',640.5,3,'앞 건물의 지붕 편집','새 지붕과 뒤쪽의 기존 면을 구분','구조 편집 / 앞뒤 가림',track=[(1.5,.30,.52,90),(2,.30,.52,90),(2.8,.30,.52,90)])}
# The chosen roof ridge is stable across these directly inspected frames.
SHOTS['05']['track']=[(1.5,.40,.43,42),(2,.40,.43,42),(2.5,.40,.43,42),(3,.40,.43,42),(3.5,.40,.43,42),(4,.40,.43,42)]
SHOTS['08']['track']=[(5,.535,.10,70),(5.5,.535,.10,70),(5.9,.535,.10,70)]
def adapt(s):return s.replace('M16','M17').replace('m16','m17').replace('game-math-camera-frustum',P.name)
s=adapt((B/'compose-m16.py').read_text(encoding='utf8'));a=s.index('SOURCES=');b=s.index('ENC=',a);s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[b:]
s=s.replace("['02','05','08','11','13','16','19','21']","['02','05','08','11','14']").replace('len(records)==22','len(records)==16').replace('22 exact-frame','16 exact-frame')
s=s.replace('only the own model uses right-handed column-vector coordinates','own spatial illustration uses a z-up pinhole projection; preserved numeric lesson explicitly uses row vectors / left-handed view +z / depth0..1')
(B/'compose-m17.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m16.py').read_text(encoding='utf8')).replace("'05.L02 지금'","'세계·좌표·클리핑'");(B/'mix-m17.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m16.py').read_text(encoding='utf8')).replace('카메라 ① 시야각·절두체·출력 창','렌더링 ③ 한 3D 점이 화면의 픽셀이 되는 과정').replace('건축 편집·시점 이동·두 플레이어 화면을 대응하는 투영 모형과 함께 비교하도록','지붕의 같은 점·큐브 배치·카메라 이동을 대응하는 좌표 모형과 함께 비교하도록');(B/'assemble-m17.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m16.py').read_text(encoding='utf8')).replace("['02','05','08','11','13','16','19','21','09','14','18','22']","['02','05','08','11','14','03','07','10','13','15','24']");(B/'qa-m17.py').write_text(s,encoding='utf8')
sources=[];old=read(R/'projects/game-math-camera-frustum/production/concept-fit-v2/source-evidence.json')['sources']
for key,s in SOURCES.items():
 meta=probe(R/s['path']);v=next(x for x in meta['streams'] if x['codec_type']=='video');assert v['height']>=s['minimumHeight'];audio=R/s.get('audioPath',s['path']);am=probe(audio);assert any(x['codec_type']=='audio' for x in am['streams'])
 r=dict(key=key,**s,sha256=sha(R/s['path']),width=v['width'],height=v['height'],fps=v['r_frame_rate'],audioSha256=sha(audio),audioStreams=[x['codec_name'] for x in am['streams'] if x['codec_type']=='audio'])
 if key=='portal':r.update(rights='Valve Video Policy educational/YouTube use; official pre-release gameplay, not current-retail implementation evidence.',rightsEvidence=rel(P/'sources/gameplay-cuts.json'),resolution='Explicit approved720p exception for M17 slots02/11; never represented as FHD source',metadataProof=rel(audio.with_suffix('.info.json')),credit='Portal 2 © Valve Corporation')
 else:r['inheritedRights']=next(x for x in old if x.get('game')==s['game'])
 sources.append(r)
e=dict(checkedAt=now(),sources=sources,coarseInspection='shared/output/private-math-concept-fit-20261023/candidates/m17/inspection.json',fineInspection='shared/output/private-math-concept-fit-20261023/candidates/m17/selected/inspection.json',directVisualReview='All89 coarse frames/8sheets and60 fine frames/5sheets inspected, plus actual-resolution roof/terrace/roof-edit frames. Source action viewed before changed narration.',nativePlayback=dict(tool='cua_repl local tab73',segments=[dict(start=a,end=b,rate=1) for a,b in [(18,22.137625),(17,22.243782),(532,538.116233),(36,39.721769),(54,57.64038),(638.5,643.535458)]],actualListening=False),sourceShots=SHOTS,reviewLimit='Game recordings establish visible geometry/view changes only, not hidden matrices/depth values.');save(H/'source-evidence.json',e)
plan=dict(checkedAt=now(),status='five-model-preflight-complete-occlusion14-correction-before-composition',sourceShots=SHOTS,sourceEvidence=rel(H/'source-evidence.json'),renderer='Manim existing mathematical stage reused for projected3D geometry and preserved row-vector calculations; no second-engine duplicate.',modelSource=rel(B/'m17-scenes.py'),modelPreflight='10 actual rendered frames/2sheets inspected; scene14 camera bearing corrected to -135 degrees so foreground/background houses overlap before raising the view.',changes='9 game-specific paragraphs regenerated;91 original paragraphs and11 mathematical clips retained. No unrelated walking/combat filler.',coordinateConvention='Own spatial picture uses z-up pinhole geometry. Numeric lesson retains explicit row-vector, LH +z, clip0..w, screen+y down. Neither is measured game telemetry.',annotations='Screen-space editorial marks on inspected roof/terrace regions only; cleared at source cuts. No fabricated distances or axes.',reuseReason='Same games reused only for distinct object editing, persistent landmarks or cube placement; no M16 interval repeated.',gameAudio='Same-source original audio, standard ducking, no added BGM',actualListening=False,humanReview='pending');save(H/'scene-visual-plan.json',plan)
print('M17 six native cuts and five edited mathematical models prepared')
