"""Record PC v5 evidence and preserve all prior deliveries and upload boundaries."""
from pathlib import Path
import datetime,hashlib,json,shutil
root=Path(__file__).resolve().parents[3];project=root/'projects/ai-3d-lofi-gaming-room';local=project/'production/local/garden-v5'
now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
d=read(local/'delivery.json');build=read(local/'native-build.json');qa=read(local/'runtime-qa.json');native=read(local/'native-memo-qa.json')
assert d['videoFrames']==2880 and build['result']=='Succeeded' and build['errors']==0
assert qa['shaderSupported'] and qa['shaderErrors']==0 and qa['chairBackTop']<.90 and qa['maximumLengthError']<.0001
assert all(qa['memo'][x] for x in ['roundtrip','backup','recovered','atomic','noUserNoteWritten'])
assert native['autosavedExactUnicode'] and native['reopenedInNativeUI'] and native['hotkeysDidNotInterruptTyping']
assert (local/'native-memo-reopened.jpg').is_file()
previous=read(project/'production/hearth-v4-delivery.json')
for t in previous['textureInputs']:assert sha(root/t['path'])==t['sha256']
files=[{'path':p.relative_to(local/'windows').as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted((local/'windows').rglob('*')) if p.is_file()]
save(project/'production/garden-v5-delivery.json',{**d,'updatedAtKst':now,'reviewUrl':'http://127.0.0.1:9323/',
 'scene':'unity/LofiGamingRoomWeb/Assets/LofiRoom/Scenes/LofiGardenRoom.unity','nativeBuild':build,'nativeExecutable':str(local/'windows/YamyamLofiRoom.exe'),'nativePackageFiles':files,
 'textureInputs':previous['textureInputs'],'runtimeQA':qa,'nativeMemoQA':native,'sourceLicenses':'production/hearth-v4-asset-record.json',
 'visualReview':{'sampledSeconds':[2,14,22,30,35,44],'nativeMemoProof':'production/local/garden-v5/native-memo-reopened.jpg','humanApproval':False},
 'features':{'chair':'Back is 39.4 cm wide and 37.4 cm high, with its top at 85.2 cm. Seat and body/hand/foot contact targets are unchanged.','display':'iMac body and contents lowered 13 cm, with a shorter stand.','window':'Original procedural upright panorama, three layered pine silhouettes, moon/maria/stars, day/night palette. Not a downloaded photo or a complete 3D outdoor level.','motion':'Leaf shader wind .028 to .085, slow speed preserved. Existing constrained hair chain has stronger breeze, 12 cm displacement cap, 43-degree angle limit, length/head/shoulder constraints.','memo':'Multiline Korean memo, 0.7-second debounce, UTF-8 JSON at Application.persistentDataPath, backup and temp-file recovery, focus-loss/quit flushing, visible errors. Game shortcuts and world clicks suppressed while typing.','retained':'Licensed native walk/sit/read/stand, iMac, hearth, record player and original CC0 audio retained.'},
 'remaining':['User PC v5 review','Focus timer and remaining full-game polish','Remaining tool demonstrations and full production video','Final WebGL build/hosting explicitly deferred'],'youtubeUploaded':False,'publicWebDeployed':False,'webBuildDeferred':True})
manifest=read(project/'project.json');manifest.update(status='garden-v5-pc-review-ready',humanReview='v4-feedback-applied-v5-pending');manifest['paths']['sampleDelivery']='projects/ai-3d-lofi-gaming-room/production/garden-v5-delivery.json';save(project/'project.json',manifest)
cp=read(project/'production/checkpoint.json');cp.update(stage='garden-v5-pc-review-ready',sampleDelivery=manifest['paths']['sampleDelivery'],updatedAtKst=now,nextAction='Deliver PC v5 review. User may check chair visibility, window moon/forest, wind and locally persisted notes. Preserve deferred WebGL boundary.')
cp['completed']=[x for x in cp['completed'] if not x.startswith('PC v5:')]+['PC v5: smaller chair back and 13 cm lower display; seat/hand/foot targets preserved','PC v5: upright original forest/moon panorama with day/night and stronger constrained foliage/hair motion','PC v5: local UTF-8 memo auto-save, backup/recovery and native UI restart checked in isolated storage','PC v5: zero-error Windows build and 48-second FHD60 four-output review'];cp['pending']=['User PC v5 review','Focus timer and remaining full-game polish','Remaining tool demonstrations and full production video','Web build and hosting explicitly deferred'];save(project/'production/checkpoint.json',cp)
ledger=read(project/'production/review-ledger.json');ledger['checks']=[x for x in ledger['checks'] if x['id']!='garden-v5-pc-review'];ledger['checks'].append({'id':'garden-v5-pc-review','status':'visual-and-native-persistence-qa-complete','evidence':'production/garden-v5-delivery.json','masterSha256':d['outputs'][1]['sha256'],'humanReviewed':False,'webBuilt':False});save(project/'production/review-ledger.json',ledger)
plan=read(project/'planning/production-plan.json');plan.update(stage='garden-v5-pc-review-ready',sampleDelivery='production/garden-v5-delivery.json');plan['game']['engine']['sceneTarget']='Assets/LofiRoom/Scenes/LofiGardenRoom.unity';plan['authorization']['latestUserReplies']=cp['latestUserSteering'];plan['authorization']['immediatePriority']='PC v5 chair/monitor visibility, forest/moon, larger leaf/hair motion and locally autosaved memo. Web remains deferred.';save(project/'planning/production-plan.json',plan)
shutil.copyfile(project/'production/garden-v5-review.html',local/'index.html')
print(json.dumps({'status':manifest['status'],'masterSha256':d['outputs'][1]['sha256'],'nativeBytes':build['bytes']}))
