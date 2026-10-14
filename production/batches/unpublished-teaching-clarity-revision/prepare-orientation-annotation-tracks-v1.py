"""Authored image observation anchors; no engine/world-space measurement."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'projects/game-math-orientation-matrices/revision-teaching-clarity-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Coordinates authored after directly reading each corresponding native image.
# Thumbnail points are multiplied by three into the unchanged1920x1080 source.
pts={
'05':[(333,180),(337,180),(337,183),(338,183),(348,184),(354,184),(362,188),(366,188),(344,184),(357,180),(360,184),(359,183),(351,184),(344,181),(340,183),(337,186),(333,183),(333,181),(326,188),(320,184),(313,189),(304,186),(310,187),(316,186),(322,187)],
'08':[(324,164),(323,170),(315,160),(307,180),(293,188),(290,204),(294,202),(294,198),(290,192),(293,184),(293,180),(286,180),(285,176),(295,176),(310,182),(331,180),(351,173),(355,174),(304,180),(271,184),(246,186),(242,188),(251,191),(270,192),(270,188)],
'11':[(337,180),(345,181),(355,184),(356,184),(351,190),(352,193),(350,198),(344,197),(345,195),(348,196),(353,194),(351,188),(351,175),(350,163),(350,178),(352,188),(350,190),(344,198),(331,193),(316,188),(311,188),(305,190),(305,191),(301,186),(299,183)],
'14':[(303,175),(307,181),(323,182),(334,181),(336,174),(342,174),(348,186),(350,198),(341,193),(326,190),(309,174),(309,181),(304,181),(313,185),(338,194),(358,189),(358,184),(348,172),(346,172),(335,165),(321,169),(312,178),(298,185),(299,202),(302,214)],
'17':[(316,180),(321,183),(343,182),(360,176),(381,182),(400,179),(401,190),(389,189),(366,193),(357,195),(342,199),(333,202),(329,196),(328,194),(329,186),(333,203),(334,201),(319,206),(307,207),(299,207),(297,195),(297,190),(303,184),(300,182),(296,177)],
'20':[(327,173),(328,181),(319,170),(310,180),(287,181),(277,179),(273,178),(279,174),(275,180),(272,179),(275,174),(286,184),(303,169),(309,178),(283,188),(257,184),(233,184),(257,194),(284,217),(303,222),(309,213),(319,201),(316,193),(316,190),(312,185)],
'23':[(303,172),(319,141),(360,177),(403,185),(400,189),(389,187),(354,190),(338,200),(327,220),(312,224),(308,246),(306,230),(304,211),(308,201),(311,184),(312,183),(318,186),(320,205),(323,207),(322,216),(323,233),(323,219),(314,211),(332,197),(350,212)]}
hidden={'11':[[60,121],[180,210]],'14':[[150,225]],'20':[[300,360]],'23':[[90,180]]}
titles={'05':'몸의 기울기와 화면의 위를 구분','08':'몸 기준의 방향을 바깥 기준으로 읽기','11':'같은 물체도 기준을 바꾸면 다르게 보임','14':'화면의 크기 변화는 축 길이 변화가 아님','17':'매끄러운 화면만으로 행렬을 검사할 수 없음','20':'화면의 왼쪽과 몸 기준 왼쪽은 다름','23':'관찰한 움직임을 세 축의 모형으로 연결'}
target=R/'annotation-observation-keyframes-v1.json'
assert not target.exists(),'Preserve existing authored tracks'
manifest=read(R/'annotation-anchor-native-v1/manifest.json')
review=read(R/'annotation-anchor-direct-review-v1.json')
assert review['all175ListedSourceSamplesDirectlyRead'] and review['all35BoardsDirectlyRead']
out=[]
for w in manifest['windows']:
    sid=w['scene'];samples=[s for s in manifest['samples'] if s['scene']==sid]
    samples.sort(key=lambda s:s['sourceFrame'])
    assert len(samples)==len(pts[sid])==25
    frames=[]
    for s,(x,y) in zip(samples,pts[sid]):
        assert sha(ROOT/s['path'])==s['sha256']
        frames.append(dict(frame=s['sourceFrame']-w['startNativeFrame'],x=x*3,y=y*3,inspectedImage=s['path'],inspectedImageSha256=s['sha256']))
    out.append(dict(scene=sid,title=titles[sid],startNativeFrame=w['startNativeFrame'],endNativeFrameExclusive=w['endNativeFrameExclusive'],keyframes=frames,hiddenLocalFrameRanges=hidden.get(sid,[])))
target.write_text(json.dumps(dict(preparedAt=datetime.now(timezone.utc).isoformat(),source=manifest['source'],sourceSha256=manifest['sourceSha256'],windows=out,method='Authored torso image observation points with piecewise linear interpolation; hide uncertain/occluded intervals and red displacement when either endpoint is hidden.',screenOnly=True,physicalCentroid=False,gameWorldAxesRecovered=False,annotationPointApproval=False,continuousMovingApproval=False,narrationTimed=False,finalCueApproval=False),ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(preparedWindows=len(out),authoredAnchors=sum(len(x['keyframes']) for x in out),encodedReviewApproved=False)))
