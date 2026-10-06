"""Independent numeric checks for chapter9 corrections and worked examples.

This produces planning evidence, not final lecture/render approval.
"""
from pathlib import Path
import datetime, hashlib, itertools, json, math
import numpy as np
r=Path(__file__).resolve().parents[4]
out=Path(__file__).with_name('geometry-source-numeric-audit.json')
source=r/'tmp/game-math-part2-sources/3e10b1ffa61e81c0878ce2c8a397fd23.txt'
results=[]
def save(name, evidence): results.append({'name':name,'passed':True,'evidence':evidence})
def close(a,b): assert np.allclose(a,b,rtol=1e-10,atol=1e-10),(a,b)

# Independent membership checks of a translated circle need its linear terms.
for angle in np.linspace(0,2*math.pi,33):
    x,y=2+math.cos(angle),3+math.sin(angle)
    close(x*x+y*y-4*x-6*y+12,0)
save('translated-conic-linear-terms',{'center':[2,3],'radius':1,'equation':'x²+y²-4x-6y+12=0','boundarySamples':33})

# Equal-distance locus, rather than the original line through q and r.
q=np.array([0.,0.]);v=np.array([2.,0.]);n=v-q;d=n@((q+v)/2)
for y in [-3.,0.,2.,7.]:
    p=np.array([1.,y]);close(n@p,d);close(np.linalg.norm(p-q),np.linalg.norm(p-v))
save('perpendicular-bisector',{'q':q.tolist(),'r':v.tolist(),'normal':n.tolist(),'d':float(d),'locus':'x=1; original rotated-normal formula gives y=0'})

# The source's first two exercise lines; these slopes use actual endpoints.
o=np.array([5.,3.]);delta=np.array([-7.,5.]);m=delta[1]/delta[0];intercept=o[1]-m*o[0]
close(o+delta,[-2,8]);close(m,-5/7);close(intercept,46/7)
close(42/7,6)
save('ray-exercises',{'exercise1':{'slope':float(m),'intercept':float(intercept),'endpoint':(o+delta).tolist()},'exercise2':{'equation':'4x+7y=42','slope':-4/7,'intercept':6},'tHalfExample':[5,2.5],'parameterMeaning':'normalized segment fraction unless explicitly reparameterized'})

# Separately label the introductory fraction example, not the exercise endpoint.
exampleOrigin=np.array([2.,1.]);exampleDelta=np.array([6.,3.]);length=np.linalg.norm(exampleDelta)
close(exampleOrigin+.5*exampleDelta,[5,2.5]);close(exampleOrigin+exampleDelta,[8,4])
unit=exampleDelta/length;close(np.linalg.norm(unit),1)
close(exampleOrigin+.5*length*unit,[5,2.5])
save('fraction-versus-distance-intro-example',{'origin':exampleOrigin.tolist(),'delta':exampleDelta.tolist(),'tHalf':[5,2.5],'tOne':[8,4],'segmentLength':float(length),'unitDirection':unit.tolist(),'distanceToMidpoint':float(length/2),'fractionHasNoImplicitTimeOrLengthUnit':True})

# Exact proxy data for the planned sphere explanation; never inferred from a game.
sphereCenter=np.array([1.,2.,3.]);radius=2.
distances=[float((p-sphereCenter)@(p-sphereCenter)) for p in [sphereCenter,np.array([3.,2.,3.]),np.array([4.,2.,3.])]]
close(distances,[0,4,9])
close((4*math.pi*(2*radius)**2)/(4*math.pi*radius**2),4)
close(((4/3)*math.pi*(2*radius)**3)/((4/3)*math.pi*radius**3),8)
save('sphere-proxy-membership-and-radius-scaling',{'center':sphereCenter.tolist(),'radius':radius,'squaredDistances':distances,'boundaryRadiusSquared':4,'doubleRadiusSurfaceFactor':4,'doubleRadiusVolumeFactor':8,'dataIsExplicitMathematicalExampleNotMeasuredGameplay':True})

# Two separated slender boxes can nevertheless overlap in world AABB space.
u=np.array([math.sqrt(.5),math.sqrt(.5)]);n=np.array([-math.sqrt(.5),math.sqrt(.5)])
first=np.array([a*u+b*n for a,b in itertools.product([-3.,3.],[-.1,.1])]);second=first+n
lo=np.maximum(first.min(0),second.min(0));hi=np.minimum(first.max(0),second.max(0))
assert np.all(lo<hi)
assert (first@n).max()<(second@n).min()
save('broadphase-aabb-false-positive',{'firstVertices':first.tolist(),'secondVertices':second.tolist(),'aabbOverlapMin':lo.tolist(),'aabbOverlapMax':hi.tolist(),'separatingNormal':n.tolist(),'normalGap':float((second@n).min()-(first@n).max()),'shapesTouch':False})

# Compare tight bounds of points to enclosure of the source's entire box.
points=np.array([[7,11,-5],[2,3,8],[-3,3,1],[-5,-7,0],[6,3,4]],dtype=float)
low,high=points.min(0),points.max(0);close(low,[-5,-7,-5]);close(high,[7,11,8])
angle=math.pi/4;A=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1.]])
corners=np.array(list(itertools.product(*zip(low,high))))
actual=points@A.T;enclosed=corners@A.T
center=(low+high)/2;half=(high-low)/2
close(A@center-np.abs(A)@half,enclosed.min(0));close(A@center+np.abs(A)@half,enclosed.max(0))
assert np.all(actual.min(0)>=enclosed.min(0)-1e-10) and np.all(actual.max(0)<=enclosed.max(0)+1e-10)
save('aabb-source-exercise-and-conventions',{'min':low.tolist(),'max':high.tolist(),'center':center.tolist(),'size':(high-low).tolist(),'corners':corners.tolist(),'columnRotation45':A.tolist(),'rotatedPointsMin':actual.min(0).tolist(),'rotatedPointsMax':actual.max(0).tolist(),'rotatedBoxMin':enclosed.min(0).tolist(),'rotatedBoxMax':enclosed.max(0).tolist(),'sourceRoundedCoefficient':0.707,'calculationCoefficient':math.sqrt(0.5),'roundingDistinguished':True})

# Independent random affine tests against enumeration, including shear/reflection.
rng=np.random.default_rng(20261006);maxError=0.
for _ in range(1000):
    c=rng.normal(size=3);e=rng.uniform(.01,8,size=3);M=rng.normal(size=(3,3));t=rng.normal(size=3)
    verts=np.array(list(itertools.product(*zip(c-e,c+e))));mapped=verts@M.T+t
    first=M@c+t-np.abs(M)@e;last=M@c+t+np.abs(M)@e
    close(first,mapped.min(0));close(last,mapped.max(0));maxError=max(maxError,float(np.max(np.abs(first-mapped.min(0)))),float(np.max(np.abs(last-mapped.max(0)))))
save('affine-aabb-enclosure-independent-corner-reference',{'cases':1000,'maximumAbsoluteError':maxError,'scope':'Affine image of an input AABB, not generally the tight bounds of the enclosed original mesh'})

# Plane scaling must scale both n and d. Nonunit residual alone is not distance.
normal=np.array([0.,2.,0.]);offset=4.;p=np.array([4.,5.,-3.])
signed=(normal@p-offset)/np.linalg.norm(normal);close(signed,3)
projection=p-(normal@p-offset)/(normal@normal)*normal;close(projection,[4,2,-3]);close(normal@projection,offset)
save('signed-plane-distance-and-projection',{'normal':normal.tolist(),'d':offset,'point':p.tolist(),'residual':6,'signedDistance':float(signed),'closestPoint':projection.tolist()})

# A 3D barycentric solution requires a coplanar query; projection conceals errors.
tri=np.array([[0,0,0],[6,0,0],[0,4,0]],dtype=float);weights=np.array([.2,.3,.5]);p=weights@tri
close(p,[1.8,2,0]);close(weights.sum(),1)
query=np.array([1.8,2,7.]);normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);distance=(normal@(query-tri[0]))/np.linalg.norm(normal)
assert abs(distance)>1e-10
outside=np.array([-.2,.7,.5]);close(outside.sum(),1);assert outside.min()<0
save('barycentric-weights-and-off-plane-rejection',{'vertices':tri.tolist(),'weights':weights.tolist(),'point':p.tolist(),'offPlaneQuery':query.tolist(),'offPlaneDistance':float(distance),'outsideWeights':outside.tolist(),'outsidePoint':(outside@tri).tolist(),'largestProjectionCanMatchXYButNotZ':True})

# Analytic right triangle separates its three centers and corrects missing factor2.
tri=np.array([[0,0],[4,0],[0,3]],dtype=float);lengths=np.array([5.,3.,4.]);perimeter=lengths.sum();area=6.
centroid=tri.mean(0);incenter=lengths@tri/perimeter;circumcenter=np.array([2.,1.5])
close(centroid,[4/3,1]);close(incenter,[1,1]);close(2*area/perimeter,1)
close(np.linalg.norm(tri-circumcenter,axis=1),[2.5]*3)
obtuse=np.array([[0.,0.],[4.,0.],[1.,1.]]);matrix=2*(obtuse[1:]-obtuse[0]);rhs=np.sum(obtuse[1:]**2,axis=1)-obtuse[0]@obtuse[0];center=np.linalg.solve(matrix,rhs)
close(center,[2,-1]);close(np.linalg.norm(obtuse-center,axis=1),[math.sqrt(5)]*3)
save('triangle-centers-right-and-obtuse',{'rightTriangleVertices':tri.tolist(),'centroid':centroid.tolist(),'incenter':incenter.tolist(),'inradius':1.,'circumcenter':circumcenter.tolist(),'circumradius':2.5,'obtuseVertices':obtuse.tolist(),'obtuseCircumcenter':center.tolist(),'outsideByNegativeY':True})

# Signed area cancellation does not make an outside concave fan a valid partition.
polygon=np.array([[0.,0.],[4.,0.],[4.,1.],[1.,1.],[1.,4.],[0.,4.]])
polygonArea=abs(np.sum(polygon[:,0]*np.roll(polygon[:,1],-1)-polygon[:,1]*np.roll(polygon[:,0],-1)))/2
ordered=np.roll(polygon,-2,axis=0)
def cross2(a,b): return a[0]*b[1]-a[1]*b[0]
fan=[float(cross2(ordered[i]-ordered[0],ordered[i+1]-ordered[0])/2) for i in range(1,len(ordered)-1)]
close(sum(fan),polygonArea);assert sum(abs(a) for a in fan)>polygonArea
save('concave-fan-counterexample',{'vertices':polygon.tolist(),'anchorVertex':[4,1],'polygonArea':float(polygonArea),'signedFanAreas':fan,'absoluteFanAreaSum':sum(abs(a) for a in fan),'validPartition':False,'convexSevenVertexFanTriangleCount':5})

# Verify this particular ear-removal sequence independently of any renderer.
remaining=list(range(len(polygon)));triangles=[];earEvidence=[]
def inTriangle(p,a,b,c,strict=False):
    values=[cross2(b-a,p-a),cross2(c-b,p-b),cross2(a-c,p-c)]
    return min(values)>1e-10 if strict else min(values)>=-1e-10
for ear in [1,2,3]:
    index=remaining.index(ear);previous=remaining[index-1];following=remaining[(index+1)%len(remaining)]
    a,b,c=polygon[[previous,ear,following]]
    assert cross2(b-a,c-a)>0
    others=[v for v in remaining if v not in [previous,ear,following]]
    assert not any(inTriangle(polygon[v],a,b,c) for v in others)
    triangle=[previous,ear,following];triangles.append(triangle)
    earEvidence.append({'ear':ear,'triangle':triangle,'otherRemainingVertices':others,'containsOtherVertex':False})
    remaining.remove(ear)
triangles.append(remaining)
areas=[float(cross2(polygon[t[1]]-polygon[t[0]],polygon[t[2]]-polygon[t[0]])/2) for t in triangles]
assert len(triangles)==len(polygon)-2 and min(areas)>0;close(sum(areas),polygonArea)
samples=0
for x in np.linspace(.031,3.973,47):
    for y in np.linspace(.043,3.967,43):
        p=np.array([x,y]);expected=x<1 or y<1
        signs=[inTriangle(p,*polygon[t],strict=True) for t in triangles]
        # Omit samples on shared internal edges; the remaining points test coverage.
        boundary=any(any(abs(cross2(polygon[t[(j+1)%3]]-polygon[t[j]],p-polygon[t[j]]))<1e-10 for j in range(3)) for t in triangles)
        if boundary:continue
        assert sum(signs)==int(expected),(p,signs)
        samples+=1
save('concave-ear-sequence-specific-example',{'vertices':polygon.tolist(),'earChecks':earEvidence,'triangles':triangles,'positiveTriangleAreas':areas,'totalArea':sum(areas),'independentNonBoundaryCoverageSamples':samples,'scope':'Specific validated simple L-shaped polygon, not a general hole-handling implementation or a proof of arbitrary fans'})

record={'schemaVersion':1,'status':'passed-planning-numerics-only','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sourcePath':source.relative_to(r).as_posix(),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scriptSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':results,'notFinalProductionQA':True,'newNarrationOrMediaCreated':False}
out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':record['status'],'checks':len(results),'randomAffineCases':1000,'maxError':maxError,'path':out.relative_to(r).as_posix()}))
