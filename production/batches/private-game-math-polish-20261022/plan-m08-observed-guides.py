"""Observed body/board directions only; no inferred game rotation data."""
from polish_common import *
e=Episode('M08');e.authorized();guides=[]
def direction(sid,role,keys):
 guides.append({'scene':sid,'role':role,'shape':'direction','leader':False,
 'label':'몸체 방향' if role=='body' else '보드의 긴 방향','labelPosition':[500 if role=='body' else 1310,115],
 'keyframes':[[r[0],*[v*4 for v in r[1:]]] for r in keys],
 'meaning':'Observed torso direction' if role=='body' else 'Observed visible board length',
 'coordinateFrame':'observed-screen-projection','worldAxisOrAngleMeasured':False,
 'tracking':'Manually traced source-frame torso/board endpoints; encoded intermediate preflight required.',
 'occlusion':'Guide clears outside its visible span and at source cuts; no hidden 3D axes reconstructed.'})
direction('IG03','body',[[1.5,212,160,223,123],[2,218,143,211,106],[2.5,254,168,253,126],[3,271,177,272,137],[3.5,232,137,250,101],[4,230,120,241,89],[4.5,236,141,242,108],[5,231,150,238,115]])
# These source15.5-19.5 endpoints are the same already observed frames as M07.
m07=read(Episode('M07').H/'observed-guides.json')
board=next(g for g in m07['guides'] if g['scene']=='IG01' and g['role']=='board')
direction('IG03','board',[[k[0]-6,*[v/4 for v in k[1:]]] for k in board['keyframes']])
direction('IG04','body',[[.5,209,98,205,51],[1,242,185,242,143],[1.5,221,183,250,172],[2,233,173,267,167],[2.5,245,117,254,91],[3,244,116,234,91],[3.5,243,126,229,101],[4,256,159,260,126],[4.5,223,188,240,161],[5,226,162,227,119]])
direction('IG04','board',[[.5,223,172,264,164],[1,220,239,235,213]])
direction('IG04','board',[[3,242,149,257,142],[3.5,233,163,242,156],[4,223,219,259,199]])
direction('IG11','body',[[0,226,91,253,33],[.5,263,186,262,143],[1,255,164,246,126],[1.5,260,186,249,143],[2,268,161,278,117],[2.5,252,203,280,161],[3,257,167,273,123],[3.5,247,186,256,145],[4,239,167,237,123]])
direction('IG11','board',[[0,191,153,225,139],[.5,247,229,260,205],[1,264,231,253,210],[1.5,247,225,271,226],[2,242,230,256,194],[2.5,213,250,244,219],[3,216,226,244,198],[3.5,225,242,240,218],[4,225,235,236,209]])
direction('IG05','body',[[0,218,145,224,106],[.5,235,116,246,78],[1,224,124,238,82],[1.5,255,155,269,111],[2,253,157,267,117],[2.5,262,153,280,112],[3,256,156,266,119],[3.5,257,152,265,112],[4,272,176,282,122]])
# The landing drops rapidly between the former 0.5s anchors. Trace observed
# board endpoints at 0.1s here instead of interpolating across the jump.
direction('IG05','board',[[11.8,186,164,244,164],[11.9,181,183,241,178],[12,193,207,244,213],[12.1,189,204,243,209],[12.2,184,202,241,205],[12.3,179,200,236,194],[12.4,177,201,236,194],[12.5,177,201,237,194],[12.6,187,207,229,187],[12.7,198,205,235,182],[12.8,211,207,246,182],[13.3,237,226,252,211],[13.8,234,216,268,229],[14.3,239,210,265,230],[14.8,253,226,277,224],[15.3,252,229,270,201],[15.8,241,229,263,229]])
direction('IG08','body',[[0,232,161,244,117],[.5,244,162,241,116],[1,242,168,236,126],[1.5,241,154,235,113],[2,224,194,249,151],[2.5,227,134,247,96],[2.75,236,122,240,80],[3,243,117,237,80],[3.25,239,124,237,84],[3.5,233,156,240,120],[4,230,173,236,130]])
direction('IG08','body',[[10.5,245,182,245,142],[11,244,182,243,142],[11.5,239,182,240,142],[12,236,184,236,146],[12.5,240,185,240,146],[13,240,185,240,146],[13.5,246,183,247,145]])
direction('IG09','body',[[0,242,173,252,126],[.5,232,192,238,146],[1,216,166,209,121],[1.5,220,187,223,145],[2,220,177,234,139],[2.5,218,184,233,143],[3,209,163,205,121],[3.5,196,178,192,137],[4,198,164,195,120]])
direction('IG09','board',[[8.5,221,218,238,192],[9,196,218,213,198],[9.5,194,226,209,199],[10,210,218,223,195],[10.5,237,214,256,245]])
direction('IG06','body',[[0,230,165,235,119],[.5,229,189,236,147],[1,222,163,227,117],[1.5,216,185,204,144],[2,201,160,199,115],[2.5,217,184,207,144],[3,229,163,233,119],[3.5,231,186,238,141],[4,240,164,249,121],[4.5,226,182,215,141],[5,215,156,207,113],[5.25,220,177,213,138],[5.5,224,174,209,132],[5.75,218,167,206,119],[6,215,160,208,113],[6.5,233,183,220,135],[7,235,160,229,116],[7.5,244,173,245,123],[8,241,171,239,120]])
direction('IG06','board',[[0,211,234,232,215],[.5,210,233,222,209],[1,203,236,223,206],[1.5,207,233,222,213],[2,211,235,227,218],[2.5,207,230,227,215],[3,209,234,228,211],[3.5,213,231,227,210],[4,209,232,244,204],[4.5,211,230,228,213],[5,210,230,227,205],[6,216,233,233,214],[6.5,230,232,247,214],[7,236,231,247,211],[7.5,249,228,273,225],[8,245,227,260,225]])
def region(sid,label,keys,pos):
 guides.append({'scene':sid,'role':'focus','shape':'ring','label':label,'labelPosition':pos,
 'keyframes':[[r[0],*[v*4 for v in r[1:]]] for r in keys],'meaning':label,
 'coordinateFrame':'editorial screen-space region, not measured axes','worldAxisOrAngleMeasured':False,
 'tracking':'Open region around observed target; inspect encoded current pixels before delivery.',
 'occlusion':'Clear at source cuts and outside the selected spoken observation.'})
region('17','몸통·날개의 기울기',[[3,220,158,55,26],[3.5,220,159,59,29],[4,225,166,61,34],[4.5,231,165,64,30],[5,237,162,64,30],[5.5,237,164,65,30],[6,240,164,65,29],[6.5,225,166,65,32],[7,206,171,65,36]],[1230,470])
region('20','차체 자세',[[0,240,181,65,55],[1,240,181,65,55],[2,240,181,65,55],[3,240,181,65,55],[4,241,179,65,55]],[1390,470])
region('20','앞쪽과 기울기 함께 보기',[[27,239,176,60,52],[28,239,176,60,52],[29,239,176,60,52],[30,237,178,62,53],[31,234,180,62,53]],[1350,430])
region('23','차체가 향하는 쪽',[[0,240,181,65,55],[.5,247,181,65,55],[1,253,181,65,55],[1.5,247,183,65,55],[2,244,185,65,55],[2.5,246,185,65,55],[3,244,188,65,55],[3.5,241,187,65,55],[4,232,183,65,55]],[1380,450])
region('23','같은 대상의 앞·위',[[29,250,178,75,55],[29.5,251,179,70,55],[30,247,180,69,55],[30.5,246,178,62,50],[31,246,178,62,50],[31.5,237,178,62,50],[32,241,178,62,50],[32.5,239,180,62,50],[33,239,177,62,50]],[1370,450])
region('23','다음 계산으로 연결',[[53,220,181,70,55],[53.5,226,181,67,55],[54,240,181,65,55],[54.5,246,181,65,55],[55,246,181,65,55]],[1370,450])
save(e.H/'observed-guides.json',{'version':1,'episode':e.id,'guides':guides,
 'captionClearanceScenes':[s['id'] for s in e.T['scenes'] if s['classification']=='actual'],
 'renderMapping':{'full':[1,0,0],'inset':[5/6,160,0]},
 'sourceCutMap':rel(e.H/'fhd-replacement-cuts.json'),'sourceCutMapSha256':sha(e.H/'fhd-replacement-cuts.json'),
 'sourceEvidence':rel(e.H/'guide-target-samples.json'),'status':'draft-anchors-await-current-pixel-preflight',
 'axisConvention':'Red/blue identify body/board only; no game world/local axes or measured angle inferred.','fullMasterApproval':False})
print(e.id,len(guides),'visible-span guides drafted; preflight required',flush=True)
