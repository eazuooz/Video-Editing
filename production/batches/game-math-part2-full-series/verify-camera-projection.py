"""Independent CPU arithmetic for the complete narrated coordinate chain.

No renderer imports. A pending spoken correction blocks the final pass.
"""
from pathlib import Path
import argparse, json, math, hashlib, datetime, sys

B = Path(__file__).parent
R = B.parents[2]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--episode', choices=['game-math-camera-projection', 'game-math-projection-depth'], default='game-math-camera-projection')
args = parser.parse_args()
L = B / f'lessons/{args.episode}.json'
draft = json.loads(L.read_text(encoding='utf8'))
episode_draft = draft
episode_path = L
chapter_blueprint = draft.get('episodeRefinement', {}).get('chapterBlueprint')
if chapter_blueprint:
    L = R / chapter_blueprint
    draft = json.loads(L.read_text(encoding='utf8'))
    original = {s['id']: s for s in draft['scenes']}
    for scene in episode_draft['scenes']:
        source_id = scene.get('preparedSourceScene') if args.episode == 'game-math-projection-depth' else (scene['id'] if scene['id'] not in ['01','24'] else None)
        if source_id:
            assert scene['ko'] == original[source_id]['ko'] and scene['en'] == original[source_id]['en'], 'Current episode math lines differ from preserved chapter blueprint'
scenes = {s['id']: s for s in draft['scenes']}
checks, failures = [], []

def check(name, actual, expected, tol=1e-10):
    if isinstance(actual, (list, tuple)):
        ok = len(actual) == len(expected) and all(abs(a-b) <= tol for a,b in zip(actual,expected))
    elif isinstance(actual, bool):
        ok = actual == expected
    else:
        ok = abs(actual-expected) <= tol
    row = dict(claim=name, calculated=actual, expected=expected, tolerance=tol, passed=ok)
    checks.append(row)
    if not ok: failures.append(name)

def rowmul(p, m): return [sum(p[i]*m[i][j] for i in range(4)) for j in range(4)]
def matmul(a,b): return [rowmul(row,b) for row in a]
def trans(x,y,z): return [[1,0,0,0],[0,1,0,0],[0,0,1,0],[x,y,z,1]]
def project(x,y,z, negative_one=False):
    aa,bb = (1.2,-2.2) if negative_one else (1.1,-1.1)
    return [x,(16/9)*y,aa*z+bb,z]
def ndc(p): return [v/p[3] for v in p[:3]]
def viewport(p, origin=(100,50), size=(800,450)):
    return [origin[0]+(p[0]+1)*size[0]/2, origin[1]+(1-p[1])*size[1]/2]
def inside(p, negative_one=False):
    x,y,z,w=p
    return -w<=x<=w and -w<=y<=w and (-w if negative_one else 0)<=z<=w

local=[1,0,0,1]; M=trans(3,2,5); V=trans(-2,-1,-1)
P=[[1,0,0,0],[0,16/9,0,0],[0,0,1.1,1],[0,0,-1.1,0]]
world=rowmul(local,M); view=rowmul(world,V); clip=rowmul(view,P)
check('Model local point to world',world,[4,2,5,1])
check('Direction w0 is unaffected by translation',rowmul([1,0,0,0],M),[1,0,0,0])
check('World point to camera-relative view',view,[2,1,4,1])
check('Camera position becomes view origin',rowmul([2,1,1,1],V),[0,0,0,1])
check('Camera world and view transformations are inverse',rowmul(rowmul([3,4,5,1],trans(2,1,1)),V),[3,4,5,1])
check('Combined row-vector MVP equals staged chain',rowmul(local,matmul(matmul(M,V),P)),clip)
check('Projection matrix copies view z to w',clip,[2,16/9,3.3,4])
check('Horizontal ninety-degree zoom',1/math.tan(math.pi/4),1)
check('Square pixels require matched physical axis scales',800/2*1,450/2*(16/9))
check('Main NDC',ndc(clip),[.5,4/9,.825])
check('Main continuous screen point',viewport(ndc(clip)),[700,175])
check('Viewport center',viewport([0,0,0]),[500,275])
check('Point horizontal offset from viewport center',700-500,200)
check('Top-left viewport corner',viewport([-1,1,0]),[100,50])
check('Bottom-right exclusive geometric boundary',viewport([1,-1,1]),[900,500])
check('Main homogeneous halfspace acceptance',inside(clip),True)
for name,p,expected in [
 ('Left rejection',[-5,0,2,4],False),('Right rejection',[5,0,2,4],False),
 ('Bottom rejection',[0,-5,2,4],False),('Top rejection',[0,5,2,4],False),
 ('Near rejection',[0,0,-.1,4],False),('Far rejection',[0,0,4.1,4],False),
 ('Negative w rejection',[0,0,0,-1],False),('Boundary acceptance',[4,-4,4,4],True)]:
 check(name,inside(p),expected)
for z,depth,orthodepth in [(1,0,0),(2,.55,.1),(4,.825,.3),(6,11/12,.5),(11,1,1)]:
 check(f'Perspective depth at view z{z}',ndc(project(0,0,z))[2],depth)
 check(f'Orthographic depth at view z{z}',(z-1)/10,orthodepth)
check('Near distance change differs from far distance change',(.825-.55)>(11/12-.825),True)
check('View midpoint6 is not perspective depth midpoint',abs(ndc(project(0,0,6))[2]-.5)>.4,True)
check('Orthographic midpoint6', (6-1)/10,.5)
for z,expected in [(1,-1),(4,.65),(11,1)]:
 check(f'Alternate negative-one depth at z{z}',ndc(project(0,0,z,True))[2],expected)
 check(f'Alternate range converts to main depth at z{z}',(ndc(project(0,0,z,True))[2]+1)/2,ndc(project(0,0,z))[2])
check('Alternate clip z4',project(2,1,4,True),[2,16/9,2.6,4])
rh=[[1,0,0,0],[0,16/9,0,0],[0,0,-1.2,-2.2],[0,0,-1,0]]
v_rh=[2,1,-4,1]
column_result=[sum(rh[i][j]*v_rh[j] for j in range(4)) for i in range(4)]
check('RH column negative-z representation gives same clip',column_result,[2,16/9,2.6,4])
check('LH transpose alone is insufficient for negative-z input',abs(rowmul(v_rh,[[1,0,0,0],[0,16/9,0,0],[0,0,1.2,1],[0,0,-2.2,0]])[3]-4)>1,True)
for z,expected in [(1,-1),(6,0),(11,1)]:check(f'Alternate orthographic z{z}',2*(z-1)/10-1,expected)
A=[0,-.6,.5]; near_intersections=[]
for name,Bv in [('B',[-1,.5,2]),('C',[1,.5,2])]:
 t=(1-Bv[2])/(A[2]-Bv[2]); q=[Bv[k]+t*(A[k]-Bv[k]) for k in range(3)]
 check(f'Near edge {name} toward A parameter',t,2/3)
 check(f'Near {name} intersection',q,[-1/3 if name=='B' else 1/3,-7/30,1])
 check(f'Near {name} new clip z and w',project(*q)[2:],[0,1])
 near_intersections.append(q)
check('Reverse edge parameter A toward B', (1-.5)/(2-.5),1/3)
check('Clipped polygon retains two original vertices plus two intersections',2+len(near_intersections),4)
a=[0,0,1];b=[4,0,4];t=.2; spatial=[a[k]+t*(b[k]-a[k]) for k in range(3)]
check('Defined view-edge endpoints project to screen x0 and1',[a[0]/a[2],b[0]/b[2]],[0,1])
check('Spatial edge20 percent projects to screen50 percent',spatial[0]/spatial[2],.5)
num=.5*0/1+.5*1/4;den=.5/1+.5/4
check('Perspective-correct interpolation numerator',num,1/8)
check('Perspective-correct interpolation denominator',den,5/8)
check('Perspective-correct attribute at screen midpoint',num/den,.2)
check('Naive attribute midpoint is a different result',(.5*0+.5*1)!=num/den,True)
check('Barycentric example constant attribute preserved',sum(w*7/z for w,z in zip([.2,.3,.5],[1,2,4]))/sum(w/z for w,z in zip([.2,.3,.5],[1,2,4])),7)
check('Positive homogeneous scaling preserves NDC',ndc([2*v for v in clip]),ndc(clip))
check('Positive homogeneous scaling preserves clip acceptance',inside([2*v for v in clip]),inside(clip))
check('Plane distance scaling doubles ray intersection',2*.5,1)
check('Plane bounds scaling preserves normalized horizontal fraction',1/4,.5/2)
newview=rowmul(world,trans(-3,-1,-1));newndc=ndc(rowmul(newview,P))
check('Changed camera view',newview,[1,1,4,1])
check('Changed camera NDC',newndc,[.25,4/9,.825])
check('Changed camera final screen point',viewport(newndc),[600,175])
check('Original point with zero-origin small viewport',viewport(ndc(clip),(0,0)),[600,125])
check('Original point with full viewport',viewport(ndc(clip),(0,0),(1920,1080)),[1440,300])
O=[[.25,0,0,0],[0,4/9,0,0],[0,0,.1,0],[0,0,-.1,1]]
one=rowmul([0,0,1,1],O);eleven=rowmul([0,0,11,1],O)
check('Orthographic near and far share constant w',[one[3],eleven[3]],[1,1])
check('Orthographic near and far retain different clip depths',[one[2],eleven[2]],[0,1])
script_audit=[]
for name,sid,index,token in [
 ('Correct near edge direction','12',2,'이에서 영 점 오'),
 ('Correct near edge formula','12',2,'t=(2−1)/(2−0.5)=2/3'),
 ('Main screen pair','15',6,'가로 칠백, 세로 백칠십오'),
 ('Camera exercise pair','22',3,'육백, 세로는 백칠십오'),
 ('Zero-origin original point pair','22',4,'육백, 백이십오'),
 ('Full viewport original point pair','22',5,'천사백사십, 삼백'),
 ('Correct small-w reciprocal','12',6,'커지는 것은 일 나누기 더블유')]:
 field='formulas' if 'formula' in name else 'ko'
 text=scenes[sid][field][index];ok=token in text
 script_audit.append(dict(claim=name,scene=sid,paragraph=index+1,field=field,expected=token,current=text,passed=ok))
 if not ok:failures.append(name)
contract_correct='A(0,−.6,.5)' in draft['contract']['nearTriangle'] and 'from B/C toward A' in draft['contract']['nearTriangle']
if not contract_correct:failures.append('Near triangle contract needs corrected directed edge')
record=dict(status='passed' if not failures else 'blocked-pending-script-correction',checkCount=len(checks),
 checks=checks,scriptAudit=script_audit,failures=failures,lessonSha256=hashlib.sha256(L.read_bytes()).hexdigest(),
 checkedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
 conventions=draft['contract']['coordinates'],
 scope='Independent arithmetic and full narrated-value checks; no game engine implementation inferred. Current audio meaning, final animated pixels and every caption remain separately reviewed.',
 humanListening='pending',audioCorrectionReview='pending-current-replacement-raw-review',
 chapterBlueprint=chapter_blueprint,currentEpisodeLesson=episode_path.relative_to(R).as_posix(),
 currentEpisodeLessonSha256=hashlib.sha256(episode_path.read_bytes()).hexdigest(),
 episodeScope='All75 independent calculations verify the complete preserved chapter; current episode source paragraphs match exactly. Current episode audio,overview,closure and final pixels are separate delivery gates.')
target=B/('preflight/projection-depth-math.json' if args.episode == 'game-math-projection-depth' else 'preflight/camera-projection-math.json')
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(record['status'],len(checks),'independent numerical checks;',len(failures),'pending issues')
if failures:print('\n'.join(failures));sys.exit(2)
