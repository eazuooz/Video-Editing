"""Inventory only native-used fixed typography; never stage arbitrary PNGs."""
from pathlib import Path
import argparse,hashlib,json,re
from rasterize_unity_labels import key,FONT
H=Path(__file__).resolve().parent;R=H.parents[3];U=R/'unity/VideoEditing';M=R/'projects/kind-to-beginners/production/local/botw-v4'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix() if p.is_relative_to(R) else p.as_posix()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['preflight','render'],required=True);ap.add_argument('--revision',required=True);a=ap.parse_args()
 lookup={}
 for p in (M/'label-cache').glob('*-request.json'):
  x=read(p)
  for l in x['layouts']:
   for text in x['texts']:lookup[key(text,l['size'],l['width'],l['height'])]={'text':text,'fontSize':l['size'],'width':l['width'],'height':l['height']}
 used={}
 for p in (M/a.phase/a.revision).glob('*/'+a.phase+'-success.json'):
  x=read(p)
  for path in x['assets']:
   if '/design-d29-botw-v4/Generated/ReferenceImages/' in path:used.setdefault(path,[]).append({'cutId':x['cutId'],'scene':x['scene'],'receipt':rel(p)})
 rows=[]
 for path,uses in sorted(used.items()):
  image=U/path;src=read(Path(str(image)+'.source.json'));source=Path(src['source']);meta=Path(str(image)+'.meta')
  assert sha(source)==src['sha256']==sha(image)
  layout=lookup[source.stem];guid=re.search(r'^guid: (\w+)',meta.read_text('utf-8'),re.M).group(1)
  rows.append({'assetPath':rel(image),'sha256':sha(image),'metaPath':rel(meta),'metaSha256':sha(meta),'guid':guid,'sourceCache':rel(source),'sourceRecord':rel(Path(str(image)+'.source.json')),**layout,'runtimeColor':'White raster is tinted by the original Text.color at each Apply; semantic palette unchanged.','uses':uses,'purpose':'Exact readable scene label/state/heading; editable .unity references this texture.','minimumNeed':'This is a texture actually imported by a captured stage. Unused cache combinations are excluded. Final commit selection must intersect final saved-scene dependencies, not this provisional inventory.'})
 out=H/('label-assets-'+a.revision+'.json');doc={'schemaVersion':1,'revision':'botw-v4','capturePhase':a.phase,'captureVariant':a.revision,'status':'provisional-preflight-do-not-bulk-commit' if a.phase=='preflight' else 'final-native-used-texture-candidates','font':{'path':str(FONT),'sha256':sha(FONT),'family':'Malgun Gothic','style':'regular','fontBinaryNotRedistributed':True},'generator':{'path':rel(H/'rasterize_unity_labels.py'),'sha256':sha(H/'rasterize_unity_labels.py'),'regeneration':'The native stage writes exact text/layout request JSON, then runs this deterministic white-alpha rasterizer.'},'count':len(rows),'assets':rows,'excluded':'All source screenshots, movies, QA images and hypothetical unused label cache PNGs.'}
 out.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(str(out),len(rows))
if __name__=='__main__':main()
