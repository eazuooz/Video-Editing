"""Manually observed 480x270 source endpoints, expanded to original FHD space."""
from polish_common import *
e=Episode('M07');e.authorized();guides=[]
def direction(sid,role,keys,why):
 guides.append({'scene':sid,'role':role,'shape':'direction','leader':False,
 'label':'몸체 방향' if role=='body' else '보드의 긴 방향',
 'labelPosition':[500 if role=='body' else 1310,115],
 'keyframes':[[row[0],*[round(v*4,2) for v in row[1:]]] for row in keys],
 'meaning':why,'coordinateFrame':'observed-screen-projection','worldAxisOrAngleMeasured':False,
 'tracking':'Manually traced visible hip-to-shoulder or board-endpoints at0.5s; direct moving preflight pending.',
 'occlusion':'Only traced visible spans are shown; outside listed spans the guide clears. No interpolation across source cuts.'})
direction('IG01','body',[
 [3,231,188,225,152],[3.5,231,180,239,150],[4,231,177,230,140],
 [4.5,229,181,226,144],[5,259,169,236,154]],'Identify the red torso direction before the board explanation.')
direction('IG01','board',[
 [7.5,243,186,270,169],[8,214,171,257,188],[8.5,235,224,248,197],
 [9,253,219,274,184],[9.5,221,165,241,144],[10,224,139,248,136],
 [10.5,215,190,241,191],[11,213,201,234,185],[11.5,208,216,233,195]],'Follow visible board length through departure and landing; hidden during the preceding airborne occlusion.')
direction('IG10','body',[
 [0,262,172,258,119],[.5,267,164,269,118],[1,251,196,270,154],
 [1.5,250,205,270,169],[2,249,161,271,130],[2.5,239,191,264,151],
 [3,238,177,258,133],[3.5,244,185,245,142],[4,238,187,245,143]],'Compare torso direction with the separate board during the grind.')
direction('IG10','board',[
 [0,253,226,277,224],[.5,252,229,270,201],[1,241,229,263,229],
 [1.5,246,232,268,231],[2,246,178,250,207],[2.5,231,218,251,210],
 [3,233,218,256,209],[3.5,231,229,254,222],[4,225,221,252,217]],'Visible board length, not a world axis or unit-length measurement.')
direction('IG10','board',[[6.5,206,177,267,227],[7,223,255,242,237],[7.5,224,231,235,204],[8,211,230,245,197]],'Reappear after the large close-up and follow landing/ground travel; hide while board leaves the frame.')
direction('IG02','body',[
 [0,232,181,239,133],[.5,226,178,234,137],[1,233,174,241,133],
 [1.5,232,177,234,140],[2,224,156,219,113],[2.5,218,189,232,171]],'Body direction and the board are independent observed screen properties.')
direction('IG02','board',[
 [0,204,228,222,206],[.5,205,230,220,207],[1,210,233,227,206],
 [1.5,220,236,237,219],[2,218,194,231,212]],'Board remains visible on approach; hide during folded-pose occlusion.')
# The later aerial board reaches the top edge and rotates too rapidly for the
# observed half-second anchors; omit that guide instead of guessing its path.
direction('IG07','body',[
 [0,231,190,224,146],[.5,232,203,217,167],[1,252,159,213,148],
 [1.5,233,138,213,155],[2,239,138,211,117],[2.5,237,173,234,123],
 [3,242,195,240,153]],'Red torso changes orientation and stands again in this first excerpt.')
direction('IG07','board',[[8.3,223,230,253,205],[8.8,220,235,241,212],[9.3,232,218,245,181]],'Show the board after the original source cut; clear before the inverted, obscured board.')
direction('IG07','board',[[10.8,261,158,290,133],[11.3,227,222,249,217],[11.8,229,218,245,203]],'Resume on visible board and landing; no inferred rotation through the hidden interval.')
def region(sid,label,role,keys,labelpos,shape='ring'):
 guides.append({'scene':sid,'label':label,'role':role,'shape':shape,
 'labelPosition':labelpos,'keyframes':[[k[0],*[v*4 for v in k[1:]]] for k in keys],
 'meaning':label,'coordinateFrame':'screen-space editorial region, not measured axes',
 'tracking':'Observed source frames; open boundary deliberately surrounds rather than segments the target',
 'occlusion':'Clear outside this short spoken observation and at each source cut.'})
region('02','차체','focus',[[3.8,240,188,66,58],[4,240,188,66,58],[6,237,188,67,59],[6.7,237,188,67,59]],[1400,550])
region('02','굽은 길','context',[[18,211,130,66,31],[20,242,131,66,31],[22,249,134,66,31]],[1410,340])
region('05','차체의 방향 변화','focus',[[0,241,180,65,53],[2,238,180,65,53],[4,237,180,65,53],[4.7,237,180,65,53]],[1390,510])
region('08','차체 앞쪽·위쪽 함께 보기','focus',[[24.8,239,179,62,53],[26,238,180,62,53],[28,237,179,62,53],[30,259,182,76,57],[32,247,179,66,55],[34,246,179,66,55],[34.9,241,180,65,55]],[1330,430])
region('08','새 발췌의 차체','focus',[[35.1,236,180,62,53],[37,236,181,62,53],[39,239,180,62,53],[40,241,180,62,53]],[1390,470])
region('11','이동 속도','context',[[19.1,443,222,33,40],[25.5,443,222,33,40]],[1400,630],shape='corners')
region('14','몸통·팔의 기울기','focus',[[5,199,116,61,33],[5.5,194,114,61,33],[6,191,115,61,33],[6.5,188,114,55,37],[7,204,113,46,38],[7.5,204,113,47,38],[8,203,114,48,40],[8.5,207,113,48,40],[9,205,111,50,42]],[1210,380])
region('14','기울어진 몸통','focus',[[37,212,132,45,43],[37.5,193,127,47,34],[38,196,126,47,34],[38.5,194,124,48,30],[39,191,126,47,34],[39.5,194,126,47,31],[40,181,132,55,45]],[1260,340])
region('14','다른 장비에서도 몸체 관찰','focus',[[51.2,174,154,50,56],[51.5,174,153,50,55],[52,180,152,50,55],[52.5,162,154,46,50],[53,161,153,52,51],[53.5,187,154,55,50],[54,202,155,55,50]],[1280,570])
save(e.H/'observed-guides.json',{
 'version':1,'episode':e.id,'guides':guides,
 'captionClearanceScenes':[s['id'] for s in e.T['scenes'] if s['classification']=='actual'],
 'renderMapping':{'full':[1,0,0],'inset':[5/6,160,0]},
 'sourceCutMap':rel(e.H/'fhd-replacement-cuts.json'),'sourceCutMapSha256':sha(e.H/'fhd-replacement-cuts.json'),
 'sourceEvidence':rel(e.H/'guide-target-samples.json'),
 'status':'draft-anchors-await-current-pixel-preflight',
 'axisConvention':'No X/Y/Z axes or positive-angle convention inferred. Red/blue identify torso and board only.',
 'fullMasterApproval':False})
print('M07',len(guides),'short visible-span guides drafted; preflight pending',flush=True)
