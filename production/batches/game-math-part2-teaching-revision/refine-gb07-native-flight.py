"""Replace rejected sparse wing draft using exact native-frame landmarks."""
from pathlib import Path
import json,copy,hashlib
B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'gb07-landmarks.json';d=read(p)
archive=B/'before-dense/gb07-before-native-flight.json';archive.parent.mkdir(exist_ok=True)
if not archive.exists():write(archive,d)
points=[
(546,135,280,421,280),(546.2,132,273,418,254),(546.4,144,273,414,244),
(546.6,174,264,416,251),(546.8,235,251,416,243),(547,260,248,416,240),
(547.2,273,246,421,247),(547.4,265,238,409,268),(547.6,268,210,401,270),
(547.8,261,202,385,278),(548,253,194,401,282),(548.2,251,216,407,291),
(548.4,220,233,397,277),(548.6,250,275,400,248),(548.7,265,292,409,218),
(548.8,278,301,430,192),(548.9,294,308,436,162),(549,301,309,425,158),
(549.1,307,310,442,142),(549.2,318,312,462,144),(549.3,325,313,480,151),
(549.4,328,315,493,159),(549.5,334,311,487,171),(549.6,340,311,503,150),
(549.7,361,331,526,129),(549.8,362,333,515,168),(549.9,334,317,527,189),
(550,309,304,547,209),(550.2,260,239,518,265),(550.4,238,222,480,297),
(550.6,211,240,471,293),(550.8,208,253,461,258),(551,256,300,493,224),
(551.2,301,324,516,213),(551.4,310,324,511,205),(551.6,263,284,510,241),
(551.8,224,241,468,272),(552,223,211,429,309)]
d['keyframes']=[{'t':t,'left':[lx,ly],'right':[rx,ry]} for t,lx,ly,rx,ry in points]
d['trackingMethod']='Native-frame manual endpoints every0.2s; every0.1s during fast bank548.6–550; sparse draft rejected after real rendered7.76s drift'
d['nativeFrameTimestampCorrection']={'rule':'exact input frame selection; these new points already use native times; do not add fps-bin offsets'}
d['movingPixelApproval']=False;d['authoringPagesReviewed']=6
d['nativeEvidence']=['GB07-flight-start','GB07-fast-flight','GB07-flight-end'];write(p,d)
p=B/'quaternion-annotation-tracks.json';r=read(p);s=r['scenes']['GB07'];s.update(mathNotePosition=[20,80],wingLabelPosition=[30,157],movingPixelApproval=False)
s['compositionReason']='Real render7.76s showed the old reminder covering the upper wing. Move reminder above the main action at top left; fixed semantic label below it; the line itself remains anchored.'
write(p,r)
print('38 exact-time native wing anchors prepared; replacement render/moving review pending')
