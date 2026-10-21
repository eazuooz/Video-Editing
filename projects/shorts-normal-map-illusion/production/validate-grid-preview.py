"""Check measured representative pixels; no render/GPU or old-media mutation."""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw
P=Path(__file__).resolve().parents[1];L=P/'production/local';C=L/'capture-preview-grid-v2-grid-rgb'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def vec(v):return [v[k] for k in 'xyz']
def dist(a,b):return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def main():
 d=read(C/'preview-readback.json');frames={x['id']:x for x in d['frames']};off=frames['grid-off'];on=frames['grid-on']
 assert len(d['frames'])==8 and off['cameraPosition']==on['cameraPosition'] and off['lightDirection']==on['lightDirection']
 gridframes=[f for f in d['frames'] if f.get('normalGrid')]
 errors=[];unit=[];tbn=[];rgb=[]
 for f in gridframes:
  assert f['gridColumns']==9 and f['gridRows']==7 and len(f['normalGrid'])==63
  assert len({(p['sampleColumn'],p['sampleRow']) for p in f['normalGrid']})==63
  for p in f['normalGrid']:
   n=vec(p['gpuShadingNormal']);ts=vec(p['tangentSpaceNormal']);e=vec(p['encodedRGB']);T=vec(p['tangent']);B=vec(p['bitangent']);N=vec(p['geometryNormal'])
   unit.append(abs(sum(x*x for x in n)-1));errors.append(abs(p['gpuNDotL']-p['cpuCheckNDotL']))
   tbn.append(dist(n,[T[i]*ts[0]+B[i]*ts[1]+N[i]*ts[2] for i in range(3)]));rgb.append(dist(ts,[v*2-1 for v in e]))
   assert 0<=p['uv']['x']<=1 and 0<=p['uv']['y']<=1
   assert 0<=p['screenPoint']['x']<1080 and 0<=p['screenPoint']['y']<1080
 assert max(errors)<.004 and max(unit)<.01 and max(tbn)<.0001 and max(rgb)<.0001
 assert all(dist(vec(a['worldPoint']),vec(b['worldPoint']))<.00001 for a,b in zip(off['normalGrid'],on['normalGrid']))
 assert all(dist(vec(p['gpuShadingNormal']),vec(p['geometryNormal']))<.00001 for p in off['normalGrid'])
 unique=len({tuple(round(v,3) for v in vec(p['gpuShadingNormal'])) for p in on['normalGrid']});assert unique>1
 result=dict(status='pass',grid=[9,7],samplesPerFrame=63,sampledGridFrames=len(gridframes),gridGPUSamples=63*len(gridframes),offUniqueDirectionCount=1,onUniqueDirectionCount=unique,sameGeometryCameraLightBetweenOffOn=True,maxCPUvsGPUDotError=max(errors),maxNormalLengthSquaredError=max(unit),maxTBNReconstructionError=max(tbn),maxEncodeDecodeError=max(rgb),shaderPassesPerGridFrame=1,description='Representative raster pixels only; world endpoints come from real shader vectors and camera projection. Display length is not physical pixel displacement.',newScenes=d['savedScenes'],frozenPNGHashes=read(C/'execution.json')['frozenPngsUnchanged'])
 (L/'grid-rgb-preview-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 visual=L/'grid-rgb-source-preview-v2';sheet=Image.new('RGB',(1875,693),'#171717');draw=ImageDraw.Draw(sheet)
 for i,name in enumerate(['grid-off','grid-on','signed','encoding','neutral']):
  im=Image.open(visual/(name+'.png')).convert('RGB').resize((375,667),Image.Resampling.LANCZOS);im.save(visual/(name+'-375.png'));sheet.paste(im,(i*375,26));draw.text((i*375+8,7),name,fill='white')
 sheet.save(visual/'mobile-contact.jpg',quality=95)
 print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
