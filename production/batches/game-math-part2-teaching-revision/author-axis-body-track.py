"""Clear suffix after the rejected crash; hide equipment-transition occlusion."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
points=[(258,219,274,308),(300,218,340,288),(275,204,281,277),(273,206,257,282),(293,211,258,281),(320,221,293,279),(292,204,288,263),(317,214,338,272),(291,203,289,267),(287,216,307,270),(298,209,297,271),(294,206,291,264),(289,183,268,249),(302,165,293,230),(296,172,293,263),(276,194,295,255),(310,195,315,270),(329,200,352,250),(252,194,257,260),(358,120,341,183),(308,153,274,223),(288,175,270,249),(292,185,281,264),(290,192,297,255),(280,164,275,235),(279,167,268,238),(294,198,267,252),(315,165,288,238),(299,166,285,237),(289,168,291,235),(280,190,284,263)]
d={'id':'GA06','sourceId':'_dw9jjRpanA','sourceFile':'shared/output/game-math-part2-teaching-revision/sources/_dw9jjRpanA.mp4','interval':[302,317],'coordinatePixels':[800,450],'keyframes':[{'t':302+i*.5,'upper':[ux,uy],'lower':[lx,ly]} for i,(ux,uy,lx,ly) in enumerate(points)],'hideIntervals':[[311.2,312.3]],'meaning':'Visible back marker and lower torso/cape base in camera projection; no measured world axis. Hide oversized/partly occluded gear transition.','authoringPagesReviewed':4,'movingPixelApproval':False}
path=B/'ga06-landmarks.json';path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'quaternion-annotation-tracks.json';registry=json.loads(p.read_text(encoding='utf8'));registry['scenes']['GA06']={'landmarks':path.relative_to(ROOT).as_posix(),'revealAtLine':1,'showWheel':False,'showScreenReference':False,'movingPixelApproval':False};p.write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'quaternion-on-footage-math.json';labels=json.loads(p.read_text(encoding='utf8'))
for x in labels['labels']:
 if x['scene']=='GA06':x['line']=2
 if x['scene']=='GB01':x['line']=2
 if x['scene']=='GA04':x['geometry']='tracked torso and visible bicycle wheel contour; no invented ski direction'
labels['labels'] += [{'scene':'GA10','line':1,'text':'되돌리기 → 두 회전의 합성은?','geometry':'tracked torso direction versus traveled position'},{'scene':'GB07','line':1,'text':'두 끝 자세 → 중간 자세는?','geometry':'tracked wing tips after the equipment transition'}]
p.write_text(json.dumps(labels,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Axis observation track authored; current spoken color and final moving QA still required')
