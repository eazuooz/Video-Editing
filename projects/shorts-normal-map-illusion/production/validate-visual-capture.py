"""Check our captured shader trace and fixed assets before compositing."""
from pathlib import Path
import json,hashlib,math
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local';C=L/'capture-full-v1'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 timing=read(P/'production/visual-timing.json');data=read(C/'full-readback.json');frames=data['frames'];success=read(C/'success.json')
 assert len(frames)==timing['frames']==success['frames']
 assert len(list((C/'frames').glob('frame-*.png')))==len(frames)
 assert all(f['frame']==i and f['panelVertices']==4 and f['panelTriangles']==2 and f['spriteTriangles']==2 for i,f in enumerate(frames))
 probes=[f['probe'] for f in frames if not f['kind'].startswith('knight')];errors=[abs(p['gpuNDotL']-p['cpuCheckNDotL']) for p in probes]
 assert max(errors)<.004
 assert all(abs(sum(p['gpuShadingNormal'][k]**2 for k in ['x','y','z'])-1)<.01 for p in probes)
 ab=[f for f in frames if f['kind']=='wall-ab']
 assert len(list((C/'ab-off').glob('frame-*.png')))==len(ab)==len(list((C/'ab-on').glob('frame-*.png')))
 assert all(abs(f['offProbe']['gpuShadingNormal']['z']+1)<.0001 and abs(f['offProbe']['gpuShadingNormal']['x'])<.0001 for f in ab)
 old=read(L/'capture-preview-v2/execution.json');root=R/'unity/VideoEditing/Assets/VideoScenes/shorts-normal-map-illusion'
 frozen=[]
 for name in ['BrickNormal.png','KnightColour.png','KnightNormal.png']:
  file=root/'Generated'/name;key=str(file.relative_to(R)).replace('\\','/');baseline=next(x['sha256'] for x in old['sourceHashes'] if x['path']==key);assert sha(file)==baseline;frozen.append(dict(path=key,sha256=baseline))
 data['mode']='full';(L/'capture-data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
 report=dict(status='pass',frames=len(frames),fps=60,nativeSize=[1080,1080],nativeFrameFiles=len(frames),sameFrameABPairs=len(ab),gpuProbeSamples=len(probes),maxCPUvsGPUdotError=max(errors),meshVertices=4,meshTriangles=2,sourceKnightTriangles=data['knightSourceTriangles'],sourceImagesUnchanged=frozen,readback=str(C/'full-readback.json').replace('\\','/'),continuousFrames=True,fullMCStarted=False)
 (L/'visual-capture-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report))
if __name__=='__main__':main()
