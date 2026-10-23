from common import *
P=R/'projects/game-math-triangle-addresses-v2';H=P/'production/concept-fit-v2'
N=len(read(H/'timeline.json')['scenes'])
SOURCES={'townscaper':dict(path='shared/output/private-math-concept-fit-20261023/sources/townscaper-official/announcement.mp4',url='https://rawfury.com/games/townscaper/',game='Townscaper',minimumHeight=1080)}
SHOTS={
 '11':dict(source='townscaper',start=14,seconds=4.15,title='지붕과 벽이 만들어지는 모습',phases=[(0,1.25,'A · B · C: 지붕에서 고른 설명용 기준점'),(1.25,4.15,'모양이 바뀌면 기준도 다시 확인')],model='세 기준점 / 삼각형 안의 위치',track=[],track2=[],points=[(.25,[(740,400),(1145,235),(815,493)]),(.5,[(742,390),(1155,230),(821,490)]),(.75,[(818,360),(1210,207),(890,458)]),(1,[(892,371),(1283,211),(964,468)]),(1.25,[(777,390),(1180,226),(850,489)])]),
 '21':dict(source='townscaper',start=49.5,seconds=2,title='서로 다른 지붕과 벽의 색',phases=[(0,2,'지붕 · 벽: 표면의 위치와 속성 구분')],model='위치의 가중치 / 그 자리의 속성',track=[],track2=[],contours=[[(.05,[(630,250),(820,250)]),(1.6,[(630,250),(820,250)])],[(.05,[(750,465),(880,465)]),(1.6,[(750,465),(880,465)])]])}
def adapt(s):return s.replace('M11','M12').replace('m11','m12').replace('game-math-plane-distances-v2',P.name)
s=adapt((B/'compose-m11.py').read_text(encoding='utf8'));a=s.index('SOURCES={');z=s.index('ENC=',a);s=s[:a]+'SOURCES='+repr(SOURCES)+'\nSHOTS='+repr(SHOTS)+'\n'+s[z:]
s=s.replace('len(records)==19',f'len(records)=={N}').replace('19 exact-frame',f'{N} exact-frame')
insertion=r'''
 # Reference labels follow three directly inspected roof corners and clear before reshaping.
 for (a,pts),(b,nxt) in zip(s.get('points',[]),s.get('points',[])[1:]):
  for i,(p,q) in enumerate(zip(pts,nxt)):
   x=p[0]*2/3;y=130+p[1]*2/3;xx=q[0]*2/3;yy=130+q[1]*2/3
   event(a,b,'{\\an5\\move('+f'{x:.1f},{y:.1f},{xx:.1f},{yy:.1f}'+')\\fs33\\bord3\\1c&H73D7FF&}'+chr(65+i))
'''
# The generated Python needs two backslashes to encode one literal ASS backslash.
s=s.replace(" path=C/f'{sid}.guides.ass'",insertion+" path=C/f'{sid}.guides.ass'")
(B/'compose-m12.py').write_text(s,encoding='utf8')
s=adapt((B/'mix-m11.py').read_text(encoding='utf8')).replace('len(levels)==17','len(levels)==16').replace('Matched17','Matched16').replace("['폴리 브리지 쓰리','법선'","['타운스케이퍼','무게중심 좌표','보간'")
(B/'mix-m12.py').write_text(s,encoding='utf8')
s=adapt((B/'assemble-m11.py').read_text(encoding='utf8')).replace('평면과 삼각형 ① 표면까지의 거리','평면과 삼각형 ② 삼각형 안의 주소').replace('다리 표면·기울기·삼각형 조립과 계산용 평면 비교로','건물의 기준점·표면 색과 삼각형 좌표 모형 비교로');(B/'assemble-m12.py').write_text(s,encoding='utf8')
s=adapt((B/'qa-m11.py').read_text(encoding='utf8')).replace("['02','PG01','03','PG02','05','06','08','PG03','09','PF02']","['11','PG04','12','13','14','15','17','18','19','PG07','21','22']");(B/'qa-m12.py').write_text(s,encoding='utf8')
save(H/'scene-visual-plan.json',dict(sourceShots=SHOTS,renderer=f'Preserve {N-8} original mathematical clips. Eight independently editable Manim classes reuse original math renderer with explicit orthographic projection.',coordinateConvention='Own RH columns; XY triangle A0,0,0 B6,0,0 C0,4,0 and Z depth. Game labels are screen-space references, not extracted engine coordinates.',models=dict(reference='Three selected roof reference points motivate independently defined triangle, without treating roof curvature as a planar engine triangle.',weights='Same triangle and point translate together, with unchanged weights; outside weight is negative.',depth='Orthographic front view overlaps different depths; oblique view reveals separation. Coplanarity and finite membership remain separate.',degenerate='Height4 to.22; a fixed delta y=.05 produces delta wC=.05/h.',attributes='Linear RGB is interpolated using current weights, then converted to sRGB for display. Game appearance is not proof of this internal implementation.'),unchangedParagraphs=82,changedSourceDependentParagraphs=16,sourceReuseReason='Two distinct short construction/appearance operations. Repetitive traversal replaced by the same editable triangle model.',preflight='pending actual render',actualVisualQa='pending',actualListening=False))
e=read(H/'source-evidence.json');e['sources'][0]['selected'][1].update(start=49.5,end=51.5);e['sources'][0]['cutCorrection']='49.4 still showed preceding shot; begin at directly inspected49.5 facade frame.';save(H/'source-evidence.json',e)
for n in ['compose','mix','assemble','qa']:compile((B/f'{n}-m12.py').read_text(encoding='utf8'),n,'exec')
print('M12 finishing prepared',N,'scenes')
