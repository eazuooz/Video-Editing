"""Replace only the user-selected882native frames; preserve immutablev2inputs."""
from pathlib import Path
import argparse,copy,hashlib,json,math
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf8')
def dot(a,b):return sum(a[k]*b[k] for k in 'xyz')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('directory');ap.add_argument('--preview',action='store_true');a=ap.parse_args()
 baseline=read(L/'capture-data-v2.json');directory=L/a.directory;patch=read(directory/'full-readback.json');frames=patch['frames']
 assert len(baseline['frames'])==4928 and len(frames)==(10 if a.preview else 882)
 expected=[194,260,332,400,471,600,750,855,940,1075] if a.preview else list(range(194,1076))
 assert [f['frame'] for f in frames]==expected
 max_dot_error=0;minimum_projected_length=1e9
 for f in frames:
  assert f['gridRenderedNative'] and f['panelTriangles']==2 and f['panelVertices']==4
  assert len(f['normalGrid'])==63 and abs(f['gridArrowLength']-.58)<1e-5
  assert (directory/'frames'/f"frame-{f['frame']:05}.png").is_file()
  p=f['probe'];n=p['geometryNormal'];t=p['tangent'];b=p['bitangent']
  assert abs(dot(n,t))<1e-5 and abs(dot(n,b))<1e-5
  if f['frame']>=332:assert abs(f['wallYaw']-302)<1e-3
  for sample in f['normalGrid']:
   gpu=sample['gpuShadingNormal'];ts=sample['tangentSpaceNormal']
   reconstructed={k:t[k]*ts['x']+b[k]*ts['y']+n[k]*ts['z'] for k in 'xyz'}
   assert math.dist(list(gpu.values()),list(reconstructed.values()))<1e-4
   assert abs(dot(gpu,gpu)-1)<1e-4
   max_dot_error=max(max_dot_error,abs(sample['gpuNDotL']-sample['cpuCheckNDotL']))
   if f['normalStrength']==0:
    assert dot(n,gpu)>.99999 and len(f['rightAngleScreen'])==3
    if f['frame']>=332:
     start,end=sample['screenPoint'],sample['gridNormalScreenEnd']
     minimum_projected_length=min(minimum_projected_length,math.hypot(end['x']-start['x'],end['y']-start['y']))
  baseline['frames'][f['frame']]={**f,'nativeFrameDirectory':a.directory}
 assert max_dot_error<1e-4 and minimum_projected_length>90
 baseline.update(revision='normal-map-v3-spatial-normals',spatialPatch=dict(kind='preview-only' if a.preview else 'complete',directory=a.directory,frames=len(frames),firstFrame=194,endFrame=1076))
 baseline['gridSampling']='V3changedframes:63actualGPUrasterpixelnormals shown as depth-tested3Dshafts/cones; displaylength0.58worldunits. Other frames unchangedv2.'
 save(L/'capture-data-v3.json',baseline)
 report=dict(status='preview-verified' if a.preview else 'complete-verified',frames=len(frames),unchangedFrames=4928-len(frames),meshVertices=4,meshTriangles=2,representativePixels=63,actualTBNVerified=True,flatNormalsPerpendicular=True,minSettledProjectedArrowPixels=minimum_projected_length,maxNDotLError=max_dot_error,baselineSha256=hashlib.sha256((L/'capture-data-v2.json').read_bytes()).hexdigest(),patchReadbackSha256=hashlib.sha256((directory/'full-readback.json').read_bytes()).hexdigest(),patch=baseline['spatialPatch'])
 save(directory/'merge-verification.json',report);print(json.dumps(report))
if __name__=='__main__':main()
