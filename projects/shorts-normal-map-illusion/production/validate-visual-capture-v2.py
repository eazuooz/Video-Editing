"""Validate v2 native capture,63pixel traces and frozen assets before MC."""
from pathlib import Path
import argparse,json,hashlib,math
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local'
REVISION='normal-map-v2-grid-rgb-deadcells'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def vector(v):return[v[k]for k in 'xyz']
def distance(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--capture',default='capture-full-v2-grid-rgb-deadcells-v1');a=ap.parse_args();C=L/a.capture
 timing=read(P/'production/visual-timing.json');assert timing['revision']==REVISION
 data=read(C/'full-readback.json');frames=data['frames'];success=read(C/'success.json');assert len(frames)==timing['frames']==success['frames']
 native=[f for f in frames if f['kind']!='game'];games=[f for f in frames if f['kind']=='game']
 assert len(list((C/'frames').glob('frame-*.png')))==len(native)
 assert all(f['frame']==i for i,f in enumerate(frames))
 assert all(f.get('nativeCaptured') and f['panelVertices']==4 and f['panelTriangles']==2 and f['spriteTriangles']==2 for f in native)
 assert all(not f.get('nativeCaptured') for f in games)
 assert all((L/'native-gameplay-v2/deadCells'/('frame-%05d.png'%i)).exists()for i in range(len(games)))
 probes=[f['probe']for f in native if not f['kind'].startswith('knight')];errors=[abs(p['gpuNDotL']-p['cpuCheckNDotL'])for p in probes]
 assert max(errors)<.004
 gridframes=[f for f in native if f['kind']in['wall-normals','wall-flatnormals']];griderrors=[];tbnerrors=[];rgberrors=[]
 for f in gridframes:
  assert len(f['normalGrid'])==63 and f['gridColumns']==9 and f['gridRows']==7
  assert len({(p['sampleColumn'],p['sampleRow'])for p in f['normalGrid']})==63
  for p in f['normalGrid']:
   n=vector(p['gpuShadingNormal']);ts=vector(p['tangentSpaceNormal']);T=vector(f['probe']['tangent']);B=vector(f['probe']['bitangent']);N=vector(f['probe']['geometryNormal']);rgb=vector(p['encodedRGB'])
   assert abs(sum(x*x for x in n)-1)<.01
   griderrors.append(abs(p['gpuNDotL']-p['cpuCheckNDotL']));tbnerrors.append(distance(n,[T[i]*ts[0]+B[i]*ts[1]+N[i]*ts[2]for i in range(3)]));rgberrors.append(distance(ts,[v*2-1 for v in rgb]))
 assert max(griderrors)<.004 and max(tbnerrors)<.0001 and max(rgberrors)<.0001
 off=[f for f in gridframes if f['normalStrength']==0];assert off and all(distance(vector(p['gpuShadingNormal']),vector(f['probe']['geometryNormal']))<.0001 for f in off for p in f['normalGrid'])
 changing=[f for f in gridframes if f['id']=='pixel-normal'];assert changing and changing[0]['normalStrength']<.01 and changing[-1]['normalStrength']>.99 and all(a['normalStrength']<=b['normalStrength']for a,b in zip(changing,changing[1:]))
 ab=[f for f in native if f['kind']=='wall-ab'];assert len(list((C/'ab-off').glob('frame-*.png')))==len(ab)==len(list((C/'ab-on').glob('frame-*.png')))
 assert all(abs(f['offProbe']['gpuShadingNormal']['z']+1)<.0001 for f in ab)
 signed=data['spriteSignedProbe'];assert data['spriteNegativeZPixels']>0 and signed['spriteTangentNormal']['z']<0 and signed['gpuShadingNormal']['z']>0 and distance(vector(signed['gpuShadingNormal']),vector(signed['expectedWorldNormal']))<.006
 expected=read(L/'capture-preview-grid-v2-grid-rgb/execution.json')['frozenPngsUnchanged'];owned=R/'unity/VideoEditing/Assets/VideoScenes'/P.name
 assert all(sha(owned/'Generated'/name)==value for name,value in expected.items())
 data.update(mode='full',revision=REVISION,captureDirectory=a.capture,previewDirectory='capture-preview-grid-v2-grid-rgb');(L/'capture-data-v2.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')
 report=dict(status='pass',revision=REVISION,frames=len(frames),nativeFrameFiles=len(native),nativeGameFrames=len(games),nativeGameSeconds=len(games)/60,fps=60,nativeSize=[1080,1080],sameFrameABPairs=len(ab),gpuProbeSamples=len(probes),representativeGridSize=[9,7],gridFrames=len(gridframes),gridSamples=len(gridframes)*63,maxCPUvsGPUdotError=max(errors+griderrors),maxTBNReconstructionError=max(tbnerrors),maxLogicalRGBEncodeDecodeError=max(rgberrors),normalStrengthTransition=[changing[0]['normalStrength'],changing[-1]['normalStrength']],frozenSourcePNGs=expected,sourceKnightTriangles=data['knightSourceTriangles'],readback=str(C.relative_to(R))+'/full-readback.json',continuousNativeFrames=True,fullMCStarted=False,percentageMeaning='GPU max(NdotL,0) diffuse direction factor, ambient/albedo excluded; not total screen luminance.',gridMeaning='Representative samples, not every pixel; projected true normal directions with readable display length.')
 (L/'visual-capture-validation-v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
if __name__=='__main__':main()
