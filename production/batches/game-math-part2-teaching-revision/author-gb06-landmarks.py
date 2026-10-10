"""Landmarks read directly from the 25 source-frame authoring pages."""
from pathlib import Path
import json
B=Path(__file__).parent
rows=[
 (618,276,169,280,241,300,300,316,371),
 (618.5,300,190,289,263,283,306,264,377),
 (619,300,190,289,263,283,306,264,377), # hidden by foliage, never rendered
 (619.5,329,194,280,270,235,300,194,350),
 (620,316,192,293,256,266,310,243,373),
 (620.5,339,210,335,270,331,341,344,394),
 (621,253,195,271,261,272,325,292,375),
 (621.5,306,194,280,264,273,308,252,359),
 (622,304,169,297,238,280,287,258,335),
 (622.5,274,198,269,266,273,304,260,350),
 (623,290,188,287,258,301,302,281,352),
 (623.5,300,180,292,240,285,300,265,353),
 (624,266,171,264,223,250,291,228,350),
 (624.5,288,184,271,243,262,306,235,355),
 (625,302,197,265,253,245,311,217,347),
 (625.5,272,204,227,269,202,300,172,328),
 (626,283,204,242,270,218,304,187,334),
 (626.5,275,205,232,265,202,300,170,333),
 (627,275,205,232,265,202,300,173,326),
 (627.5,283,196,245,251,214,289,184,321),
 (628,288,203,247,260,215,297,179,331),
 (628.5,294,219,256,272,215,312,181,336),
 (629,310,209,272,272,245,318,210,363),
 (629.5,303,197,298,265,283,329,261,383),
 (630,285,199,273,261,260,321,231,382),
]
d={'id':'GB06','sourceId':'4Odvp_TIeQU','sourceFile':'shared/output/game-math-part2-full-series/sources/4Odvp_TIeQU.mp4','interval':[616,642],'trackedInterval':[618,630],'coordinatePixels':[800,450],'meaning':'Visible back/waist direction and a visible fat rear-wheel contour, projected into the moving camera image. Screen reference is not measured world up; game quaternion/order is unknown.','colors':{'torso':'#ef5350','wheel':'#42a5f5','screenReference':'#26c6b8'},'hideIntervals':[[618.75,619.3]],'trackingMethod':'manually read half-second frames; foliage interval explicitly hidden; fast bank intermediates require moving-pixel correction','narrationTimed':False,'movingPixelApproval':False,'authoringPagesReviewed':3,'keyframes':[{'t':t,'upper':[ux,uy],'lower':[lx,ly],'wheel':[[ax,ay],[bx,by]]} for t,ux,uy,lx,ly,ax,ay,bx,by in rows]}
(B/'gb06-landmarks.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('25 GB06 landmarks authored; final tracking approval remains false')
