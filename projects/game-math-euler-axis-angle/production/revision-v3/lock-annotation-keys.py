"""Adopt inspected tracking and replace drift with source-frame manual paths."""
from pathlib import Path
import json,copy,hashlib
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';O=P/'production/local/revision-v3';FILE=P/'sources/annotation-plan-v3.json'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=read(FILE);windows={w['id']:w for w in p['windows']};media=read(P/'sources/media-revision-v3.json')
sources={s['id']:s for s in media['sources']}
for w in windows.values():
 f=O/'tracking'/(w['id']+'.json')
 if not f.exists():continue
 t=read(f);w['keyframes']=t['keyframes'];w['trackingReceiptSha256']=sha(f)
 w['sourceSha256']=sources[w['sourceId']]['downloadedSha256']
 w['sourcePixelReview']='All half-second tracking contact frames inspected; incorrect drift removed or replaced below; moving composite remains pending'
 for k in w['keyframes']:
  # A guide surrounds the whole body rather than the texture patch used by CSRT.
  k['ellipseRadius']=[v+12 for v in k['ellipseRadius']]
  if w['sourceId']=='_wH_-1saHnw':k['ellipseRadius']=[v+15 for v in k['ellipseRadius']]
def trim(id,start,end):
 w=windows[id];w['sourceIn']=start;w['sourceOutExclusive']=end
 keys=[k for k in w['keyframes'] if start<=k['sourceTime']<end];assert len(keys)>1
 keys.append({**keys[-1],'sourceTime':end-1/60});w['keyframes']=keys
# Remove impact/occluded/tracker-loss intervals rather than fabricate motion.
trim('02-glide',27,30.35);trim('05-kart',111,119.9)
trim('17-jump',1331,1333.75);trim('20-raftlog',990,994.25)
trim('20-platform',264,267.25);trim('20-raft',1014,1019.8)
# A short source-defined visible point trace is added below after the raft enters water.
windows['20-raft'].pop('screenTrace',None)

def manual_box(id,rows,label=None):
 w=windows[id];w['sourceIn']=rows[0][0];w['sourceOutExclusive']=rows[-1][0]+1/60;w['shape']='brackets'
 if label:w['label']=label
 w['keyframes']=[]
 for t,x,y,width,height in rows:
  w['keyframes'].append(dict(sourceTime=t,visible=True,center=[(x+width/2)*3,(y+height/2)*3],ellipseRadius=[(width/2+8)*3,(height/2+8)*3]))
 w['tracking']='manual source-frame keyframes replacing drifting CSRT';w.pop('trackingReceiptSha256',None)

manual_box('08-hook',[(240.5,286,20,104,136),(241,281,28,102,126),(241.5,290,43,92,176),(242,290,44,92,179),(242.5,285,35,95,183),(243,286,40,93,178),(243.4,285,40,94,178)])
windows['08-hook']['color']='focus';windows['08-hook']['labelPosition']=[74,450]
manual_box('20-log',[(401,175,130,118,35),(401.5,190,133,111,38),(402,177,150,113,35),(402.5,177,145,120,35),(403,183,148,130,40),(403.5,164,144,120,37),(404,157,142,131,42)],'통나무의 위치 이동')
# 20-log coordinates above were observed on480px tracking tiles.
for k in windows['20-log']['keyframes']:
 k['center']=[v*4/3 for v in k['center']];k['ellipseRadius']=[v*4/3 for v in k['ellipseRadius']]

def line(id,scene,sid,rows,label,color='reference',position=None):
 w=windows.get(id,dict(id=id,scene=scene,sourceId=sid,meaning='Visible source surface/direction guide; not a world axis or measured telemetry'))
 w.update(sourceIn=rows[0][0],sourceOutExclusive=rows[-1][0]+1/60,shape='polyline',label=label,color=color,sourceSha256=sources[sid]['downloadedSha256'],tracking='manually traced actual source pixels at the listed frame times',sourcePixelReview='Exact listed source frames inspected; current moving composite pending')
 w['keyframes']=[dict(sourceTime=t,visible=True,points=[[x*3,y*3] for x,y in pts]) for t,pts in rows]
 if position:w['labelPosition']=position
 windows[id]=w

line('08-logs','08','YNQ20CKbY8U',[
 (418.5,[(84,193),(240,201),(410,201),(587,193)]),
 (419,[(81,185),(240,194),(410,195),(570,190)]),
 (419.5,[(84,177),(240,190),(410,190),(566,183)]),
 (420,[(91,173),(240,182),(410,183),(566,177)]),
 (420.5,[(145,158),(290,170),(455,177),(620,180)]),
 (421,[(141,130),(300,145),(450,151),(620,156)])], '통나무를 길게 잇는 방향',position=[74,300])

# Mast direction follows the actual rigid pole. The cyan Ultrahand tether is
# deliberately excluded: it is not the object's physical rotation axis.
line('20-mast','20','YNQ20CKbY8U',[
 (1000,[(305,160),(379,238),(452,316)]),
 (1000.5,[(306,167),(378,244),(450,322)]),
 (1001,[(320,137),(322,205),(325,282)]),
 (1001.5,[(308,80),(319,124),(323,194)]),
 (1002,[(291,29),(291,63),(292,110)]),
 (1002.5,[(306,61),(306,105),(307,151)]),
 (1003,[(314,43),(315,86),(316,127)]),
 (1003.5,[(311,30),(308,80),(305,123)]),
 (1004,[(318,35),(317,93),(315,135)]),
 (1004.5,[(330,40),(329,110),(331,170)]),
 (1005,[(345,30),(347,105),(346,182)]),
 (1005.5,[(333,49),(332,120),(332,188)]),
 (1006,[(331,48),(331,124),(331,190)]),
 (1006.5,[(331,48),(331,124),(331,190)])], '돛대의 긴 방향 · 자세 변화',position=[74,350])

line('05-road','05','dbA2StfJhqw',[
 (115,[(375,283),(363,218),(352,157),(329,100)]),
 (115.5,[(440,283),(386,222),(340,153),(310,84)]),
 (116,[(450,283),(421,207),(397,147),(387,90)]),
 (116.5,[(463,283),(447,227),(432,180),(423,151)]),
 (117,[(507,283),(455,220),(411,173),(377,137)]),
 (117.5,[(441,283),(411,216),(375,151),(327,97)]),
 (118,[(123,283),(194,221),(247,165),(271,123)]),
 (118.5,[(222,283),(291,215),(333,151),(337,103)]),
 (119,[(357,283),(382,214),(372,154),(343,108)]),
 (119.5,[(356,283),(366,226),(350,169),(321,112)])], '도로의 가장자리',position=[74,292])
line('11-road','11','dbA2StfJhqw',[
 (244,[(30,310),(185,248),(280,206),(346,143)]),
 (244.5,[(72,312),(188,249),(248,181),(277,109)]),
 (245,[(92,312),(173,239),(214,165),(240,109)]),
 (245.5,[(40,311),(134,242),(217,177),(296,139)]),
 (246,[(50,305),(166,256),(274,194),(363,149)]),
 (246.5,[(20,242),(107,212),(188,184),(248,151)]),
 (247,[(28,301),(113,248),(197,199),(268,163)])], '도로의 경계 · 화면에서의 관찰',position=[74,292])
line('23-road','23','dbA2StfJhqw',[
 (379.5,[(28,119),(182,138),(368,164),(546,203)]),
 (380,[(25,108),(191,127),(367,157),(547,188)]),
 (380.5,[(25,54),(202,95),(368,133),(546,185)]),
 (381,[(25,42),(195,93),(369,143),(546,187)]),
 (381.5,[(25,96),(193,123),(369,147),(546,181)]),
 (382,[(25,130),(195,127),(369,138),(546,168)]),
 (382.5,[(30,253),(194,189),(371,135),(546,205)]),
 (383,[(25,216),(191,151),(366,87),(546,42)])], '파란 선: 도로 가장자리',position=[74,300])
trace=dict(id='20-screen-trace',scene='20',sourceId='YNQ20CKbY8U',sourceIn=1026,sourceOutExclusive=1034+1/60,
 label='돛대 중앙 · 화면 좌표의 자취',labelPosition=[74,230],meaning='Past-only approximate visible mast-center image trajectory; camera-dependent, not measured world distance',color='result',shape='ellipse',screenTrace=True,
 sourceSha256=sources['YNQ20CKbY8U']['downloadedSha256'],tracking='Manual actual-source mast-midpoint samples',sourcePixelReview='Each listed source frame inspected; moving composite pending')
trace['keyframes']=[dict(sourceTime=t,visible=True,center=[x*3,y*3],ellipseRadius=[13,13]) for t,x,y in [(1026,376,213),(1027,320,219),(1028,364,220),(1029,357,233),(1030,357,236),(1031,353,239),(1032,351,249),(1033,351,251),(1034,351,254)]]
windows[trace['id']]=trace
p['windows']=list(windows.values());p['labelPosition']=[74,230]
p['status']='manual-corrections-awaiting-composite-review';p['tracking']='Inspected CSRT keys for bodies; manually traced object/road keys; no detector overlay or measured world values'
FILE.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Prepared',len(windows),'annotation windows; lock only after current preview.')
