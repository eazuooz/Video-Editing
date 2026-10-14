"""CPU source/math preparation; no future video, render or TTS is started."""
from pathlib import Path
import json, hashlib, math
from datetime import datetime, timezone
import numpy as np
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent.parent
checks=[]
def check(name,evidence):checks.append(dict(name=name,passed=True,evidence=evidence))
def close(a,b):np.testing.assert_allclose(a,b,atol=1e-10,rtol=1e-10)
hx=1/math.tan(math.radians(60)/2)
views=[]
for display_aspect, pixel_aspect, half_aspect in [(4/3,1,2/3),(16/9,4/3,8/9)]:
    close((640/480)*pixel_aspect,display_aspect)
    close((320/480)*pixel_aspect,half_aspect)
    vy=half_aspect*hx;vfov=math.degrees(2*math.atan(1/vy))
    close(hx/math.tan(math.radians(vfov)/2)**-1,1/half_aspect)
    views.append(dict(displayAspect=display_aspect,pixelWidthToHeight=pixel_aspect,
        physicalHalfViewportAspect=half_aspect,horizontalFovDegrees=60,horizontalZoom=hx,
        verticalZoom=vy,verticalFovDegrees=vfov))
check('Wii-resolution-is-not-physical-aspect',dict(assumption='Source historical640x480 frame fills the stated TV; no overscan/crop/letterboxing.',views=views))
n,f=1.,256.;vy=views[0]['verticalZoom']
gl=np.array([[hx,0,0,0],[0,vy,0,0],[0,0,-(f+n)/(f-n),-2*f*n/(f-n)],[0,0,-1,0.]])
dx=np.array([[hx,0,0,0],[0,vy,0,0],[0,0,f/(f-n),-f*n/(f-n)],[0,0,1,0.]])
for z,target in [(-n,-1),(-f,1)]:
    clip=gl@np.array([0,0,z,1.]);close(clip[2]/clip[3],target)
for z,target in [(n,0),(f,1)]:
    clip=dx@np.array([0,0,z,1.]);close(clip[2]/clip[3],target)
corner=np.array([n/hx,n/vy,-n,1.]);close((gl@corner)[:2]/(gl@corner)[3],[1,1])
corner[2]=n;close((dx@corner)[:2]/(dx@corner)[3],[1,1])
check('explicit-projection-conventions-and-depth-boundaries',dict(contract='Column vectors; chosen standard OpenGL RH negative forward/NDCz[-1,1], chosen D3D LH positive forward/NDCz[0,1]. APIs do not mandate world handedness.',near=n,far=f,openGLMatrix=gl.tolist(),direct3DMatrix=dx.tolist(),clearDepthComparison='Clear1 with LESS does not accept exactly1; compare state and mapped depth are separate.'))
p=np.array([2.,1,3,1]);M=np.array([[2.,0,0,4],[0,1,0,5],[0,0,1,6],[0,0,0,1.]])
close(p@M.T,M@p)
check('row-source-to-column-course-transposition',dict(rowExpression='mul(p,Mrow)',columnExpression='Mcolumn @ p',relation='Mrow=Mcolumn.T',separateFrom='Row/column matrix memory packing. HistoricalSM2 semantics and shader profiles are not modernSV semantics.'))
normal=np.array([1.,0,1]);normal/=np.linalg.norm(normal)
rot=np.array([[0.,0,1],[0,1,0],[-1,0,0]])
T=np.eye(4);T[:3,:3]=rot;T[:3,3]=[3,4,5]
close((T@np.r_[normal,0])[:3],rot@normal)
q=np.r_[rot@normal,1];assert not np.isclose(np.linalg.norm(q[:3]/np.linalg.norm(q)),1)
check('direction-w0-and-normalize3-before-w1',dict(directionW=0,translationEffect='none',incorrectNormalize4NormalLength=float(np.linalg.norm(q[:3]/np.linalg.norm(q))),generalTransform='Use inverse transpose for invertible nonuniform linear transform, then nonzero normalize. Source uniform/orthogonal examples are restricted.'))
inputs=[[-1.,0,0],[.267,-.535,.805],[0,0,1],[0,.857,.514]]
encoding=[]
for N in inputs:
    raw=(np.array(N)+1)*127.5;encoded=np.floor(raw+.5).clip(0,255).astype(int)
    decoded=2*encoded/255-1
    encoding.append(dict(sourceNormal=N,roundHalfUpRGB=encoded.tolist(),rawDecoded=decoded.tolist(),decodeLength=float(np.linalg.norm(decoded))))
assert encoding[0]['roundHalfUpRGB']==[0,128,128] and encoding[2]['roundHalfUpRGB']==[128,128,255]
check('specified-eight-bit-encoding-and-quantization',dict(formula='RGB=round-half-up(clamp((N+1)*127.5,0,255)); decode2RGB/255-1 then nonzero normalization.',sourceRoundedInputsNotSilentlyRenormalized=True,results=encoding))
cases=[([128,255,128],[.408,-.408,-.816],[.707,.707,0],1),([106,155,250],[0,1,0],[1,0,0],-1),([128,218,218],[1,0,0],[0,.447,-.894],1),([233,58,145],[.154,-.617,.772],[.986,.046,-.161],-1)]
results=[]
for rgb,ns,ts,h in cases:
    N=np.array(ns,dtype=float);N/=np.linalg.norm(N)
    originalT=np.array(ts,dtype=float);T=originalT-N*np.dot(N,originalT);T/=np.linalg.norm(T)
    bit=h*np.cross(N,T);basis=np.column_stack([T,bit,N]);close(basis.T@basis,np.eye(3))
    close(np.linalg.det(basis),h)
    decoded=2*np.array(rgb,dtype=float)/255-1;nt=decoded/np.linalg.norm(decoded);model=basis@nt
    close(np.linalg.norm(model),1)
    results.append(dict(rgb=rgb,sourceRoundedNormal=ns,sourceRoundedTangent=ts,handedness=h,bitangent=bit.tolist(),tangentUnitNormal=nt.tolist(),modelUnitNormal=model.tolist(),sourceDotError=float(np.dot(np.array(ns),originalT))))
check('four-TBN-exercises-with-declared-rounding-repair',dict(method='Nonzero normalizedN; Gram-SchmidtT; B=handedness*cross(N,T); unit decoded tangent normal; modelTBN @ nt. Rounded source bases are repaired explicitly, not claimed exact.',cases=results))
ids=['3e10b1ffa61e81d48a95fb2cf0a41b56','3e10b1ffa61e81e7aac4e718a255f15c','3e10b1ffa61e81c49172fdebf83ba3c2','3e10b1ffa61e8152b52de62f22610495']
sources=[]
for page_id in ids:
    path=R/f'tmp/game-math-part2-sources/current-20261009-{page_id}.txt'
    text=path.read_text(encoding='utf8');assert text.rstrip().endswith('</page>')
    sources.append(dict(id=page_id,path=path.relative_to(R).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),characters=len(text),wholeFetchedTextDirectlyRead=True))
record=dict(status='future-full-source-and-independent-math-preparation',atUtc=datetime.now(timezone.utc).isoformat(),target='game-math-pipeline-shaders',sources=sources,checks=checks,newProjectCreated=False,ttsStarted=False,officialDuplicateDecision='pending',historicalCodeCompileStatus='not compiled; source examples must be scoped to originalshader-profile or adapted and actually validated later.',unverifiedFigureMatches='Exercise4/5 external figures not inspected; do not invent correspondence answers.',independentPrimaryDocumentation=[
 'https://learn.microsoft.com/en-us/windows/win32/direct3d11/d3d10-graphics-programming-guide-rasterizer-stage-rules',
 'https://learn.microsoft.com/en-us/windows/win32/direct3d11/d3d10-graphics-programming-guide-output-merger-stage',
 'https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-semantics',
 'https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-mul',
 'https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-normalize',
 'https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-packing-rules'],clarifications=[
 'Conceptual pipeline order is not a guarantee of physicalexecution order; earlydepth depends on the shader and state.',
 'Clipz, interpolated/mappedz/w, depthrange, clearvalue and comparisonfunction are distinct.',
 'Historical fixedalpha-test state is replaced by shaderdiscard in modernDirect3D; transparentdepth writes require explicitpolicy.',
 'Pixel/sample coverage and top-leftshared-edge rules do not mean universalonepixelpertriangle or globallyuniquepixel.',
 'Clipped polygons can contain duplicate/degenerate vertices; count uniquevalidvertices explicitly.',
 'Frontface/winding configuration is independent of worldhandedness and may change under reflection; camera-relative normaldot is not universally normal.z.',
 'Source25/33instructions, MAX_BONES40, manualunrolling and AoS/SoA claims are historical examples, not measured2026performance.',
 'Legacy POSITION/COLOR/uniform/sampler2D/tex2D source must be named historical; modern SV_Position/SV_Target/inputformats require explicitadaptation.',
 'float3+float can share a16byteconstantbuffer slot; matrixpacking is distinct from row/columnmul convention.',
 'Source normalw0 comment contains a translationtypo; float4 normalization afterw1 yields a nonunitxyz normal.',
 'Source Gouraud light-direction temporary requires float3, not scalarfloat; byte4 is not a promised built-inmodernHLSL inputtype.',
 'Bone transform arrays, not allmeshvertices, are shaderconstant inputs in the skinningexample.',
 'TBN transpose equals inverse only for an orthonormalbasis; mirrored handedness, GS, singularcases and nonuniformmetric require explicitcare.',
 'Normal decoding/filtering/quantization requires nonzero normalization; zero lightdistance or zero halfvector requires a guard.',
 'Gouraudvertex-color representation cannot recover per-pixelnormal detail by itself; do not turn this into a universalhardware prohibition.',
 'HistoricalPS2DMA, scanout and doublebuffer examples remain explicitlyhistorical; no universalcurrentengineCPU/GPU percentage.',
 'SourcePhar spelling and historicalfreePDF statements need author/currentavailability verification before recommendedpurchase or downloadlinks.'
 ])
target=B/'preflight/pipeline-shaders-source-capture.json'
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(len(checks),'CPU independent checks passed; futurevideo production remains pending.')
