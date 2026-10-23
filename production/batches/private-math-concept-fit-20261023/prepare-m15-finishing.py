"""Compose only inspected light/material evidence, on the matching spoken clauses."""
from common import *
P=R/'projects/game-math-rendering-light';H=P/'production/concept-fit-v2';T=read(H/'timeline.json');slots={s['id']:s for s in T['scenes']}
authorized('M15')
SOURCES={
 'big':dict(path='shared/output/game-math-part2-full-series/sources/wzQLP0Z3zII.mp4',audioPath='shared/output/private-math-concept-fit-20261023/sources/m15-audio/wzQLP0Z3zII.m4a',url='https://www.youtube.com/watch?v=wzQLP0Z3zII',game='Big Walk',minimumHeight=1080),
 'sub':dict(path='shared/output/game-math-part2-full-series/sources/dYyWmhVuc3w.mp4',audioPath='shared/output/private-math-concept-fit-20261023/sources/m15-audio/dYyWmhVuc3w.m4a',url='https://www.youtube.com/watch?v=dYyWmhVuc3w',game='Subnautica 2',minimumHeight=1080)}
def shot(scene,source,start,seconds,title,meaning,model,line=1,track=None,track2=None):
 return dict(scene=scene,source=source,start=start,seconds=seconds,offset=slots[scene]['lineStarts'][line-1] if line>1 else 0,title=title,phases=[(0,seconds,meaning)],model=model,track=track or [],track2=track2 or [])
SHOTS={
 '02':shot('02','big',515.5,8,'노란 벽과 뒤쪽 캐릭터','가까운 벽이 겹친 부분을 가림','앞벽 / 뒤 물체',track=[(1.1,.51,.55,46),(1.5,.51,.55,46)],track2=[(3.5,.46,.45,48),(4.5,.47,.54,48),(5.5,.54,.45,48),(6.5,.22,.62,52),(7.4,.44,.5,48)]),
 '05-hole':shot('05','big',1621,1.5,'빈 구멍으로 보이는 배경','구멍에는 앞벽 표면이 없음','구멍 / 뒤의 나무',track=[(.05,.88,.59,45),(.5,.74,.58,45),(1,.68,.53,45)]),
 '05-glass':shot('05','big',1561,7,'반투명 상자의 표면과 내부','표면이 있어도 뒤 물체의 빛이 기여','반투명 표면 / 뒤 물체',line=3,track=[(.3,.50,.63,86),(1,.50,.63,86),(3,.49,.62,86),(5,.5,.63,86),(6.8,.5,.63,86)]),
 '08-entry':shot('08','sub',618.5,6,'입구 너머 벽과 수납장 비교','재질과 조명 조건이 함께 만든 명암','표면 색 / 빛의 조건'),
 '08-preview':shot('08','sub',742,4,'문틀 설치와 주변 벽','도구의 미리 보기와 설치 뒤 표면 구분','도구 표시 / 주변 벽 밝기',line=3,track=[(1.2,.3,.52,67),(2.2,.25,.52,67),(3.5,.25,.52,67)]),
 '11':shot('11','big',797,5,'빨간 표면 안의 밝고 어두운 부분','표시된 색과 빛의 스펙트럼은 다른 정보','픽셀 색 / RGB 표현'),
 '14':shot('14','sub',249,5.5,'전방 조명이 비추는 굽은 바위','법선 외에도 거리·가림·재질이 함께 변함','표면의 굴곡 / 각 위치의 법선',track=[(2,.49,.72,86),(3,.48,.72,86),(4,.5,.72,86)]),
 '17':shot('17','sub',764.5,13.5,'천장 조명 설치 전후 비교','미리 보기 → 조명 설치 → 밝아진 벽','빛을 내는 면 / 빛을 받는 벽',line=3,track=[(.2,.5,.49,93),(1,.5,.49,93),(2,.5,.49,93),(2.5,.5,.49,93)]),
 '19':shot('19','big',1945.5,5,'그늘에서도 보이는 바닥','한 방향이 가려져도 다른 빛은 남을 수 있음','가려진 방향 / 남은 방향'),
 '21':shot('21','big',1708,4,'앞뒤로 겹친 캐릭터','가시성은 앞면 선택 / 밝기는 그다음 계산','어느 표면 / 얼마나 밝은가',track=[(1,.46,.43,43),(2,.46,.43,43),(3,.45,.43,43)])}

def adapt(s):return s.replace('M14','M15').replace('m14','m15').replace('game-math-polygon-partition-v2',P.name)
s=adapt((B/'compose-m14.py').read_text(encoding='utf8'));a=s.index('SOURCES=');z=s.index('ENC=',a);s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[z:]
a=s.index("  prep='[0:v]");z=s.index("  print('Compose",a)
s=s[:a]+'''  selected=[(key,v) for key,v in SHOTS.items() if v['scene']==sid]
  assert abs(sum(v['seconds'] for key,v in selected)-slot['gameWindowSeconds'])<.001
  for key,shot in selected:
   assert shot['offset']+shot['seconds']<=slot['seconds']
  prep='[0:v]null[prepared];'
  if sid in ['02','05','08','11','14','17','19','21']:
   prep='[0:v]drawbox=x=0:y=875:w=1920:h=60:color=0x090D12:t=fill[prepared];'
  if selected:
   graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),split={len(selected)+1}[full]'+''.join(f'[m{i}]' for i in range(len(selected)))+';'
   current='full'
   for i,(key,shot) in enumerate(selected):
    src=SOURCES[shot['source']];annotations(key,shot);off=shot['offset'];sec=shot['seconds']
    args+=['-ss',shot['start'],'-t',sec,'-i',R/src['path']]
    graph+=f'[m{i}]crop=850:540:80:210,scale=620:394[small{i}];color=c=0x090D12:s=1920x1080:r=60:d={slot["seconds"]}[bg{i}];[{i+1}:v]fps=60,scale=1280:720:flags=lanczos,setsar=1,setpts=PTS+{off}/TB[game{i}];[bg{i}][game{i}]overlay=0:130:eof_action=pass[panel{i}];[panel{i}][small{i}]overlay=1300:240,ass={key}.guides.ass[split{i}];[{current}][split{i}]overlay=0:0:enable=\\'between(t,{off},{off+sec-1/60})\\'[out{i}];'
    current=f'out{i}'
   graph+=f'[{current}]setsar=1[v]'
  else:graph=f'[0:v]tpad=stop_mode=clone:stop_duration=0.05,trim=end_frame={n},setpts=N/(60*TB),setsar=1[v]'
  graph=prep+graph.replace('[0:v]','[prepared]')
'''+s[z:]
s=s.replace("'game + math' if sid in SHOTS","'game + math' if selected").replace('passthrough_ok=sid not in SHOTS','passthrough_ok=not selected').replace('game=SHOTS.get(sid)','game=[v for key,v in selected]').replace('len(records)==24','len(records)==22').replace('24 exact-frame','22 exact-frame');(B/'compose-m15.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m14.py').read_text(encoding='utf8')).replace('len(levels)==13','len(levels)==14').replace('Matched13','Matched14').replace("t['id']==sid","t['id']==s.get('scene',sid)").replace("['셰이프즈 투','기계','엘자','네 삼각형'","['BRDF','복사휘도','복사조도','입체각'");(B/'mix-m15.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m14.py').read_text(encoding='utf8')).replace('다각형 ② 빈 공간을 지키는 삼각형 분할','렌더링 ① 빛·재질·시선으로 픽셀 계산하기').replace('물 그리기·도형 가공·타일 배치와 영역 보존 모형 비교로','가림·반투명 표면·조명 설치를 대응하는 단면 모형과 함께 보여 주도록');(B/'assemble-m15.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m14.py').read_text(encoding='utf8'));a=s.index(" if s['gameWindowSeconds']:");z=s.index(' for tm in sorted',a)
s=s[:a]+''' for key,shot in __import__('runpy').run_path(str(B/'compose-m15.py'))['SHOTS'].items():
  if shot['scene']!=s['id']:continue
  offset=shot['offset'];times += [s['start']+offset+.2+i*.5 for i in range(math.floor(shot['seconds']*2))]+[s['start']+offset+shot['seconds']+.2]
'''+s[z:]
s=s.replace("['QG04','14','15','16','QG05','17','QG06','QB13','QG09','19','QG07','21']","['02','05','08','11','14','17','19','21','09','13','18','22']");(B/'qa-m15.py').write_text(s,encoding='utf8')
save(H/'scene-visual-plan.json',dict(sourceShots=SHOTS,renderer='14 unchanged approved mathematical clips retained; 8 independently editable Manim cross-section/color models continue the established math renderer. These are illustrations, not a measured Unity/Unreal implementation.',coordinateConvention='Own2D cross sections with x right/y up; annotated gameplay uses inspected screen coordinates only. Game normals, distances, RGB values and renderer algorithms are not measured.',changedParagraphs=14,unchangedParagraphs=109,sourceAudio='Video-only local downloads; original synchronized audio separately recovered from the same recording URLs. No extra BGM. Actual audio-content listening pending.',sourceSelectionEvidence=rel(H/'source-evidence.json'),sourceRecuts=['05-hole:1621–1622.5 only; remove subsequent jumping/camera drift','08-frame:742–746 construction action, not a sustained green preview'],speechVisualCues='All gameplay windows start on matching complete paragraph; 05 and08 use two distinct cuts,17 light installation starts at paragraph3. Narration continues through animation; no forced silence.',guides='Thick hollow screen guides name narrated targets, clear at cuts/occlusion; no fabricated telemetry',actualListening=False))
print('M15 finishing prepared;22 scenes,10 native cuts,14 math clips retained')
