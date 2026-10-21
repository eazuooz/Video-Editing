"""Independent row-matrix arithmetic and actual native-anchor audit, no renderer."""
from pathlib import Path
import argparse,importlib.util,json,math
import numpy as np

sp=importlib.util.spec_from_file_location('v8_unity_prepare',Path(__file__).with_name('unity-prepare.py'))
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
S=M.S;H,O,ROOT=M.H,M.O,M.ROOT

def ry(deg):
    c,s=math.cos(math.radians(deg)),math.sin(math.radians(deg))
    return np.array([[c,0,-s],[0,1,0],[s,0,c]])
def rx(deg):
    c,s=math.cos(math.radians(deg)),math.sin(math.radians(deg))
    return np.array([[1,0,0],[0,c,s],[0,-s,c]])
def rz(deg):
    c,s=math.cos(math.radians(deg)),math.sin(math.radians(deg))
    return np.array([[c,s,0],[-s,c,0],[0,0,1]])
BAD=np.array([[1.18,0,0],[.22,.95,0],[.05,0,1.08]])
NORMAL=BAD/np.linalg.norm(BAD,axis=1)[:,None]

def expected(shot,t):
    e=t*t*(3-2*t);d=shot['angleFrom']+(shot['angleTo']-shot['angleFrom'])*e;kind=shot['mode']
    if kind=='projection':return ry(shot['angleFrom']+(shot['angleTo']-shot['angleFrom'])*t)
    if kind in ['bank','intro-orientation']:return rz(d)
    if kind=='pitch':return rx(d)
    if kind=='scale':return np.diag([1+e,1,1])
    if kind=='shear':return np.array([[1,0,0],[.6*e,1,0],[0,0,1]])
    if kind=='reflection':return np.diag([1 if t<.5 else-1,1,1])
    if kind=='creep':return np.eye(3)*(1-e)+BAD*e
    if kind=='normalize':return BAD*(1-e)+NORMAL*e
    if kind=='orthonormalize':return NORMAL*(1-e)+np.eye(3)*e
    if kind=='complex':return rz(30)@rx(20)@ry(35)
    if kind in ['camera','direction','arm','intro-translate','humanoid']:return np.eye(3)
    return ry(d)

def independent_checks():
    checks=[]
    def add(name,actual,expected_value,tol=1e-9):
        a=np.asarray(actual);b=np.asarray(expected_value);error=float(np.max(np.abs(a-b)));assert error<=tol,(name,error)
        checks.append(dict(name=name,actual=a.tolist(),expected=b.tolist(),maximumError=error,passed=True))
    r=ry(90);v=np.array([1,0,2]);right=np.array([1,0,0])
    add('Y90 basis rows',r,[[0,0,-1],[0,1,0],[1,0,0]])
    add('same point object to upright',v@r,[2,0,-1]);add('same point inverse',np.array([2,0,-1])@r.T,v)
    add('m09 RIGHTunit first turn',right@r,[0,0,-1]);add('m09 RIGHTunit second turn',right@r@r,[-1,0,0])
    add('scale transpose is not inverse',np.diag([2,1,1])@np.diag([.5,1,1]),np.eye(3))
    add('cos60 signed projection',ry(60)[0,0],.5)
    add('normalized length only',np.linalg.norm(NORMAL,axis=1),[1,1,1])
    assert abs(float(NORMAL[0]@NORMAL[1]))>.2
    checks.append(dict(name='normalization alone does not restore right angle',actual=float(NORMAL[0]@NORMAL[1]),expected='nonzero',passed=True))
    q0=BAD[0]/np.linalg.norm(BAD[0]);q1=BAD[1]-(BAD[1]@q0)*q0;q1/=np.linalg.norm(q1);q2=BAD[2]-(BAD[2]@q0)*q0-(BAD[2]@q1)*q1;q2/=np.linalg.norm(q2);g=np.array([q0,q1,q2])
    add('example Gram-Schmidt gives identity',g,np.eye(3));add('repaired determinant',np.linalg.det(g),1)
    reflection=np.diag([-1,1,1]);add('reflection Gram remains identity',reflection@reflection.T,np.eye(3));add('reflection determinant',np.linalg.det(reflection),-1)
    add('storage matrix bytes per second',15*15*9*4,8100);add('storage three-value bytes per second',15*15*3*4,2700);add('30 second decimal byte difference',(8100-2700)*30,162000)
    return checks

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--anchors',type=Path);a=ap.parse_args();approval=M.authorized();checks=independent_checks()
    report=dict(schemaVersion=1,approval=approval,scriptSha256=M.APPROVED,independentArithmeticChecks=checks,arithmeticPassed=True,
        actualEngineRun=False,actualShaderCompilation=False,actualCapturePixelsReviewed=False,
        limits='CPU arithmetic checks do not approve shader compilation, saved runtime behaviour, camera content or actual audio/visual timing. Those require native captured output and final composition.',
        sources={M.rel(H/f):M.sha(H/f)for f in ['unity-runtime.cs.in','unity-geometry.cs.in','unity-specs.py','unity-capture.cs.in']})
    if a.anchors:
        errors=[];clipping=[];assets=[];count=0
        for shot in S.SHOTS:
            p=a.anchors/(shot['id']+'.anchors.ndjson')
            if not p.exists():continue
            rows=[json.loads(t)for t in p.read_text(encoding='utf8').splitlines()];maxerr=0.;allgram=0.
            for i,row in enumerate(rows):
                r=np.array(row['rowMatrix']).reshape(3,3);expected_r=expected(shot,row['t']);err=float(np.max(np.abs(r-expected_r)));maxerr=max(maxerr,err)
                if err>2e-5:errors.append(dict(shot=shot['id'],frame=i,kind='rowMatrix program disagreement',error=err))
                gram=r@r.T;recorded=np.array(row['rowGram']).reshape(3,3);gerr=float(np.max(np.abs(recorded-gram)));allgram=max(allgram,gerr)
                if gerr>3e-5:errors.append(dict(shot=shot['id'],frame=i,kind='Gram disagreement',error=gerr))
                xyz=lambda v:np.array([v[k]for k in ['x','y','z']])
                if np.max(np.abs(xyz(row['objectPoint'])@r-xyz(row['uprightPoint'])))>3e-5:errors.append(dict(shot=shot['id'],frame=i,kind='point coordinate disagreement'))
                anchors={v['name']:v for v in row['anchors']};scale=row['coordinateDrawingScale'];origin=xyz(row['offset'])
                if np.max(np.abs(origin+scale*xyz(row['uprightPoint'])-xyz(anchors['point']['world'])))>3e-5:errors.append(dict(shot=shot['id'],frame=i,kind='logical-to-drawn point disagreement'))
                if np.max(np.abs(xyz(anchors['weightedXEnd']['world'])-xyz(anchors['basisUnitX']['world'])))>3e-5:errors.append(dict(shot=shot['id'],frame=i,kind='one-unit weighted path does not end at unit-axis endpoint'))
                for axis,j in zip('XYZ',range(3)):
                    expected_end=origin+scale*r[j]
                    if np.max(np.abs(expected_end-xyz(anchors['basisUnit'+axis]['world'])))>3e-5:errors.append(dict(shot=shot['id'],frame=i,kind='unit-axis display scale inconsistency',axis=axis))
                if abs(np.linalg.det(r)-row['determinant'])>3e-5:errors.append(dict(shot=shot['id'],frame=i,kind='determinant disagreement'))
                if shot['mode']=='arm':
                    x=np.array(row['swordToHand']).reshape(3,3);y=np.array(row['handToArm']).reshape(3,3);z=np.array(row['swordToArm']).reshape(3,3)
                    if np.max(np.abs(x@y-z))>3e-5:errors.append(dict(shot=shot['id'],frame=i,kind='arm composition disagreement'))
                if shot['mode']=='humanoid':
                    refs=row['orientationReferences'];names={p['name']for p in refs}
                    if len(refs)!=15 or len(names)!=15:errors.append(dict(shot=shot['id'],frame=i,kind='not exactly15 distinct orientation references'))
                    for reference in refs:
                        if reference['parent']!='model_parent'and reference['parent']not in names:errors.append(dict(shot=shot['id'],frame=i,kind='missing reference parent',part=reference['name']))
                        m=np.array(reference['rowParentOrientation']).reshape(3,3)
                        if np.max(np.abs(m@m.T-np.eye(3)))>3e-5 or abs(np.linalg.det(m)-1)>3e-5:errors.append(dict(shot=shot['id'],frame=i,kind='invalid parent-relative orientation',part=reference['name']))
                b=row.get('modelPixelBounds',{});
                if (shot['plane']or shot['mode']in ['arm','humanoid']) and b and(b['x']<0 or b['y']<0 or b['z']>1000 or b['w']>700):clipping.append(dict(shot=shot['id'],frame=i,bounds=b))
                count+=1
            assets.append(dict(id=shot['id'],frames=len(rows),anchors=M.rel(p),sha256=M.sha(p),maxMatrixError=maxerr,maxGramError=allgram,logicalWorldPixelScaleChecked=True))
        assert not errors,errors[:20]
        report.update(actualEngineRun=True,actualAnchorFrameCount=count,actualAssets=assets,actualAnchorMathPassed=True,clippingFindings=clipping,actualAnchorDisagreements=errors)
        dest=a.anchors/'mathematical-validation.json'
    else:dest=O/'cpu-preflight.json'
    M.save(dest,report);print(json.dumps(dict(report=M.rel(dest),sha256=M.sha(dest),independentChecks=len(checks),actualEngineRun=report['actualEngineRun'],passed=True),ensure_ascii=False))

if __name__=='__main__':main()
