"""Import only the two authorized completed Tripo ZIP exports; preserve originals."""
from pathlib import Path
import argparse,hashlib,json,zipfile
from PIL import Image
H=Path(__file__).resolve().parent;R=H.parents[2];A=R/'unity/LofiGamingRoomWeb/Assets/LofiRoom/TripoRattanV11'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--sofa',required=True);parser.add_argument('--table',required=True);args=parser.parse_args();records=[]
for key,asset,path in [('sofa','d46fe0fb-34f2-49bd-8c7d-4306ddc36076',args.sofa),('table','7aa66d34-e775-436b-b831-18a7b5c315ff',args.table)]:
 source=Path(path).resolve();assert source.is_file() and source.suffix.lower()=='.zip',source
 out=(A/key).resolve();assert out.is_relative_to(A.resolve());out.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(source) as archive:
  fbx=[n for n in archive.namelist() if n.lower().endswith('.fbx')];assert len(fbx)==1,fbx
  selected={'Model.fbx':fbx[0]}
  for target,term in [('BaseColor','basecolor'),('Normal','normal'),('Metallic','metallic'),('Roughness','roughness')]:
   found=[n for n in archive.namelist() if n.lower().endswith('_'+term+'.png')]
   if target in ('BaseColor','Normal'):assert len(found)==1,(target,found)
   if found:selected[target+'.png']=found[0]
  files=[]
  for target,member in selected.items():
   data=archive.read(member);destination=out/target
   if destination.exists():assert hashlib.sha256(data).hexdigest()==sha(destination),'Preserve a different existing input'
   else:destination.write_bytes(data)
   record={'path':destination.relative_to(R).as_posix(),'sourceMember':member,'sha256':sha(destination),'bytes':len(data)}
   if destination.suffix=='.png':record['dimensions']=list(Image.open(destination).size)
   files.append(record)
 record={'asset':key,'tripoAssetId':asset,'providerModel':'H3.1','generationCredits':55,'retopologyCredits':35,'targetTriangles':20000 if key=='sofa' else 10000,'observedTriangles':22066 if key=='sofa' else 9375,'export':'FBX / Mixamo axes preset / 4K current texture','archive':str(source),'archiveSha256':sha(source),'sourcePreserved':True,'files':files}
 records.append(record)
(H/'rattan-v11-import.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n','utf-8');print('Imported the two real Tripo furniture exports')
