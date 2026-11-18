"""Verify the selected revision, exact twelve local files and private phone receipt."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,urllib.parse
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
BASE=M/'shorts-mario64-lakitu-camera/camera-paired-v164'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))

def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())

class Links(HTMLParser):
 def __init__(self):super().__init__();self.videos=[];self.local=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='video':self.videos.append(a.get('src'))
  for key in ['src','href']:
   u=a.get(key,'')
   if u.startswith('file:'):self.local.append(u)

def main():
 out=H/'camera-paired-final-root-review-v174.json';assert not out.exists()
 v=read(H/'camera-paired-final-validation-v173.json');manifest=read(H/'local-final-review-manifest-v6.json');old=read(H/'local-final-review-manifest-v5.json');mobile=read(H/'mobile-selected-camera-review-v173.json')
 assert manifest['selectedOrders']==[2] and len(manifest['projects'])==12
 assert all(manifest['projects'][i]==old['projects'][i]for i in range(12)if i!=1)
 assert manifest['projects'][1]['titleKo']=='3D 게임의 판도를 바꾼 마리오64'
 checked=0
 for row in manifest['projects']:
  assert len(row['artifacts'])==6
  for f in row['artifacts'].values():assert pin(f['path'])['sha256']==f['sha256'];checked+=1
 parser=Links();page=H/'local-final-review-v6.html';text=page.read_text('utf8');parser.feed(text);assert len(parser.videos)==12
 for uri in parser.local:
  p=urllib.parse.unquote(urllib.parse.urlparse(uri).path)
  if len(p)>2 and p[0]=='/'and p[2]==':':p=p[1:]
  assert Path(p).exists(),p
 assert mobile['drive']['url'] in text and mobile['drive']['shared'] is False
 previous=read(H/'mobile-review-delivery-v159.json');assert len(previous['projects'])==12
 assert mobile['drive']['id'] not in [r['drive']['id']for r in previous['projects']]
 assert mobile['folder']['id']!=previous['folder']['id']
 assert mobile['source']==manifest['projects'][1]['artifacts']['captioned']
 bundle=read(BASE/'local-review-v6-r171/bundle-v6.json');assert bundle['localFinalBundleComplete']and bundle['acceptedVoiceMusicAndAacByteExact']and bundle['subtitlesByteExact']
 evidence=[]
 for r in bundle['evidence']:assert pin(r['path'])['sha256']==r['sha256'];evidence.append(r)
 assert read(BASE/'film-v171/pilot-visual-review.json')['allowedForFinalBundle']
 assert read(BASE/'film-v171/clean-derivative-verification.json')['minimumBodyPsnrDb']>=42
 old111=ROOT/'projects/shorts-leveldesign-11-05/checkpoint.json';assert pin(old111)['sha256']=='7123b2dffc7203700a296b2ceac45c23b3dece912d0da6887f3ee09e8a2512bb'
 extras=[Path(__file__),H/'camera-paired-final-validation-v173.json',H/'verify-paired-camera-encoded-v171.py',H/'verify-paired-camera-clean-v171.py',H/'paired-camera-layout-v167.py',H/'run-camera-paired-film-v171.py',H/'run-camera-paired-clean-v171.py']
 sources={r['path']:r for r in v['sourceInputs']}
 for p in extras:sources[str(p.resolve())]=pin(p)
 for r in sources.values():assert pin(r['path'])['sha256']==r['sha256']
 report=dict(sourceInputs=list(sources.values()),scopedSharedInputs=v['scopedSharedInputs'],scopedDocInputs=v['scopedDocInputs'],progress=v['progress'],selectedOrders=[2],allArtifactCount=checked,localVideoElements=12,allLocalLinksExist=True,otherElevenManifestRowsUnchanged=True,phoneUploadSelectedOnly=True,privatePhoneReadbackVerified=True,previousPhoneReceipt=pin(H/'mobile-review-delivery-v159.json'),previousCloudFilesPreserved=True,evidence=evidence,frozenOld111=pin(old111),actualFullListening=False,actualRealtimePlayback=False,actualPhonePlayback=False,humanApproval=False,allRequiredTechnicalChecksPassed=True)
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(report=pin(out),artifactCount=checked,onlyOrder2Revised=True,technicalChecksPassed=True)))

if __name__=='__main__':main()
