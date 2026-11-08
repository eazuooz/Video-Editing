from pathlib import Path
import json,sys,datetime,subprocess
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];L=H/'local';L.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(R/'production/batches/design-25-30-review-actions-20261029'))
from scoped_json import patch,load
inventory=json.loads((B/'review-20261108/inventory.json').read_text('utf-8'));ids=[r['id'] for r in inventory]
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
scope={'selectedAt':now,'status':'planning-and-narrated-diagram-production','episodes':ids,'userInstruction':'설명 시연 전에 PPT 같은 관계도를 그려 설명하는 구간을 각 영상에 추가; AI2D 영상은 병렬로 계속','scope':'Exactly A01–A18 add narrated topic-specific relationship maps before explanatory demonstrations. Preserve existing useful narration, native-speed repeats, gameplay, branding/outro and previous deliveries. Repair directly related missing visual relationships identified in current audit.','baselineManifest':'production/batches/animation-18-20261031/pacing-v3/review-manifest.json','fullLocalProductionAuthorized':True,'ttsAuthorized':True,'tts':'Additions only; same approved own-voice Qwen1.7B used in latest additive revisions. Preserve existing voices/PCM.','renderAuthorized':True,'parallelDelegationAuthorized':True,'costlyGpuJobs':'Serialized with AI2D through current lease; no simultaneous model loading or foreign process termination','youtubeAuthorized':False,'schedulingAuthorized':False,'deletionAuthorized':False,'driveAuthorized':False,'humanFinalReviewRequired':True,'checkpoint':'production/batches/animation-18-20261031/relations-v4/checkpoint.json'}
control=R/'shared/publishing/video-production-control.json';raw=control.read_bytes();j=load(raw);j['animationRelationsRevision20261108']=scope
# Preserve unrelated JSON bytes by inserting a top-level key with the existing scoped helper.
if 'animationRelationsRevision20261108' in load(raw):raw=patch(raw,['animationRelationsRevision20261108'],scope)
else:
 at=raw.rfind(b'}');assert at>=0
 body=raw[:at].rstrip();separator=b'' if body.endswith(b'{') else b','
 raw=body+separator+b'\n  "animationRelationsRevision20261108": '+json.dumps(scope,ensure_ascii=False,indent=2).encode('utf-8')+b'\n'+raw[at:]
assert load(raw)['animationRelationsRevision20261108']==scope
control.write_bytes(raw)
(H/'scope.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n','utf-8')
(H/'checkpoint.json').write_text(json.dumps({'stage':'planning','completed':['Full18 source/script audit','144 encoded frame observations','Scope recorded'],'remaining':['18 relationship scripts','Narrated diagrams and insertions','Current audio/text/visual QA','Four outputs and integrated local review'],'platformChanges':False,'updatedAt':now},ensure_ascii=False,indent=2)+'\n','utf-8')
physical=Path('C:/Users/1/Videos/YamyamCoding/VideoEditing/animation-relations-v4');physical.mkdir(parents=True,exist_ok=True)
layout=[]
for ep in inventory:
 logical=R/'projects'/ep['slug']/'production/local/relations-v4';target=physical/ep['slug']
 assert str(logical.absolute()).startswith(str(R.absolute())) and str(target.absolute()).startswith(str(physical.absolute()))
 if logical.exists():
  assert logical.resolve()==target.resolve(),('Foreign existing revision directory',logical)
 else:
  target.mkdir(exist_ok=True);logical.parent.mkdir(parents=True,exist_ok=True)
  quote=lambda p:"'"+str(p).replace("'","''")+"'"
  subprocess.run(['powershell','-NoProfile','-Command','New-Item -ItemType Junction -Path '+quote(logical)+' -Target '+quote(target)+' | Out-Null'],check=True)
  assert logical.resolve()==target.resolve()
 layout.append({'id':ep['id'],'logical':str(logical),'physical':str(target),'previousMastersMoved':False})
(H/'storage-layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Authorized18 relationship revisions; new media directories onC; old masters untouched')
