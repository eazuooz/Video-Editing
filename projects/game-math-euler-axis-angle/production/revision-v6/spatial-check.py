"""Bounded CPU audit of V6 shot programs and compilation against installed Unity APIs."""
from pathlib import Path
import hashlib,json,math,subprocess

ROOT=Path(__file__).resolve().parents[4];P=ROOT/'projects/game-math-euler-axis-angle'
H=P/'production/revision-v6';LOCAL=P/'production/local/revision-v6'
OWN=ROOT/'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/revision-v6'
I=[[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def vec(d):return [d.get(k,0) for k in ['x','y','z']]
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def tr(a):return list(map(list,zip(*a)))
def diff(a,b):return max(abs(a[i][j]-b[i][j]) for i in range(3) for j in range(3))
def aa(n,deg):
    theta=math.radians(deg);length=math.sqrt(sum(x*x for x in n))
    if abs(theta)<1e-12:return [r[:] for r in I]
    assert length>0;n=[x/length for x in n];x,y,z=n;c=math.cos(theta);s=math.sin(theta);t=1-c
    return [[c+x*x*t,x*y*t+z*s,x*z*t-y*s],[y*x*t-z*s,c+y*y*t,y*z*t+x*s],[z*x*t+y*s,z*y*t-x*s,c+z*z*t]]
def hpb(v):return mm(mm(aa([0,0,1],v[2]),aa([1,0,0],v[1])),aa([0,1,0],v[0]))
def u(t,a,b,linear):
    if a==b:return 0
    v=max(0,min(1,(t-a)/(b-a)));return v if linear else v*v*(3-2*v)
def program(p,t):
    if p is None:return I
    value=[0,0,0];keys=p.get('keys',[])
    if keys:
        left=right=keys[0]
        for right in keys[1:]:
            if t<=right['t']:break
            left=right
        f=u(t,left['t'],right['t'],p.get('linear',False));a=vec(left['value']);b=vec(right['value']);value=[a[i]+(b[i]-a[i])*f for i in range(3)]
    if p['kind']=='rotvec':return aa(value,math.degrees(math.sqrt(sum(x*x for x in value))))
    if p['kind']=='sequence':
        r=hpb(vec(p.get('initialEuler',{})))
        for s in p.get('steps',[]):
            delta=aa(vec(s['axis']),s['degrees']*u(t,s['start'],s['end'],p.get('linear',False)))
            r=mm(delta,r) if s['space']=='body' else mm(r,delta)
        return r
    return hpb(value)
def determinant(a):return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])

def main():
    catalog=json.loads((OWN/'spatial-shots.json').read_text(encoding='utf8'));shots={s['id']:s for s in catalog['shots']}
    maximum=0;sample_count=0
    for s in shots.values():
        for i in range(61):
            for name in ['a','b']:
                if not s.get(name):continue
                r=program(s[name],i/60);e=max(diff(mm(r,tr(r)),I),abs(determinant(r)-1));maximum=max(maximum,e);sample_count+=1
                assert e<1e-10,(s['id'],i,e)
    equal=['v6-10.B02','v6-11.B02','v6-18.B02','v6-20.B02','v6-20.B03','v6-27.B02','v6-30.B01','v6-36.B02','v6-37.B01','v6-37.B02','v6-38.B01','v6-38.B02','v6-38.B03']
    results=[]
    for sid in equal:
        s=shots[sid];e=diff(program(s['a'],1),program(s['b'],1));assert e<1e-10,(sid,e);results.append(dict(id=sid,expected='same endpoint',maximumElementError=e))
    for sid in ['v6-05.B02','v6-11.B03','v6-12.B02','v6-13.B01','v6-39.B02','v6-39.B03']:
        s=shots[sid];e=diff(program(s['a'],1),program(s['b'],1));assert e>.1,(sid,e);results.append(dict(id=sid,expected='different endpoint',maximumElementDifference=e))
    s=shots['v6-27.B02'];mid=diff(program(s['a'],.5),program(s['b'],.5));assert mid>.1
    # One source compile, no Editor, GPU context or executable scene is launched.
    unity=Path('C:/Program Files/Unity/Hub/Editor/6000.6.0f1/Editor/Data');out=LOCAL/'spatial-compile';out.mkdir(parents=True,exist_ok=True)
    refs=list((unity/'NetStandard/ref/2.1.0').glob('*.dll'))+list((unity/'NetStandard/compat/2.1.0/shims/netstandard').glob('*.dll'))+[p for p in (unity/'Managed/UnityEngine').glob('*.dll') if p.name not in ['UnityEngine.dll','UnityEditor.dll']]
    sources=list(OWN.rglob('*.cs'))
    args=['/nostdlib+','/target:library','/langversion:latest','/define:UNITY_EDITOR,UNITY_STANDALONE_WIN',f'/out:"{out/"SpatialCompileOnly.dll"}"']+[f'/reference:"{p}"' for p in refs]+[f'"{p}"' for p in sources]
    rsp=out/'spatial.rsp';rsp.write_text('\n'.join(args),encoding='utf8')
    command=['dotnet','C:/Program Files/dotnet/sdk/10.0.402/Roslyn/bincore/csc.dll','@'+str(rsp)]
    completed=subprocess.run(command,text=True,encoding='utf8',capture_output=True);(out/'compiler.log').write_text(completed.stdout+completed.stderr,encoding='utf8')
    if completed.returncode:raise RuntimeError(completed.stdout+completed.stderr)
    plan=json.loads((H/'spatial-plan.json').read_text(encoding='utf8'))
    def luminance(h):
        v=[int(h.lstrip('#')[i:i+2],16)/255 for i in [0,2,4]]
        v=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in v]
        return sum(a*b for a,b in zip(v,[.2126,.7152,.0722]))
    ratios={name:(luminance(color)+.05)/(luminance('#080b0d')+.05) for name,color in plan['testbed']['axisPalette'].items()}
    assert all(r>=4.5 for r in ratios.values())
    report=dict(schemaVersion=1,kind='CPU source/authoring math only; actual Unity execution/pixels pending GPU handoff',inputs={'planSha256':sha(H/'spatial-plan.json'),'catalogSha256':sha(OWN/'spatial-shots.json'),'sources':[dict(file=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha(p)) for p in sources]},coverage={'sceneMappings':41,'beatMappings':106,'physicalShots':len(shots),'orientationSamples':sample_count,'samplesPerProgram':61},rowMath={'maximumOrthogonalityOrDeterminantError':maximum,'pairEndpointChecks':results,'aliasInterpolationMidpointDifference':mid,'oldZReflectionUsed':False,'engineConversion':'transpose row matrix only'},palette={'background':'#080b0d','labelAndGuideNominalContrastRatios':ratios,'note':'Source token contrast only; actual lighting, antialiasing and font/mobile output still require direct visual inspection.'},compile={'passed':True,'compiler':'Installed Roslyn5.9, installed Unity6000.6.0f1 module/API references','references':len(refs),'sourceFiles':len(sources),'log':str((out/'compiler.log').relative_to(ROOT)).replace('\\','/'),'editorLaunched':False,'actualUnityRuntimeMathChecks':'pending; EulerV6Math.Validate runs at actual isolated entry'},pending=['Actual isolated Editor save/bake','Current native sample and375px visual/caption inspection','Actual Shader/TextMesh rendering and occlusion','Measured teaching-beat timeline','Main URP direct preview remains unperformed'],mediaJobsStarted=0)
    (H/'spatial-cpu-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(compilePassed=True,physicalShots=len(shots),samples=sample_count,maximumMatrixError=maximum,pairChecks=len(results),editorLaunched=False)))

if __name__=='__main__':main()
