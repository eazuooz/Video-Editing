"""CPU fixtures only; every fake project/output is beneath qa/fixture-<timestamp>."""
import contextlib
import hashlib
import importlib.util
import io
import json
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('exporter',HERE/'export-native-editable.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=HERE/'qa'/('fixture-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
m.ROOT=base/'repo';m.MEDIA=base/'media';m.OWNED=m.MEDIA/'unity-capture';m.TOOLS=m.MEDIA/'native-export-tools'

def put(p,content):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content if isinstance(content,bytes) else content.encode('utf8'));return p
def save(p,value):return put(p,json.dumps(value,sort_keys=True))
def h(data):return hashlib.sha256(data).hexdigest()
def item(logical,kind='asset',guid=''):
 p=m.OWNED/logical
 return {'assetPath':logical,'physicalPath':str(p),'kind':kind,'guid':guid,'sha256':m.sha(p),'bytes':p.stat().st_size}

captured=b'// exact source captured at v1\n'; current=b'// different later source v2\n'
code={'Demo.cs':h(captured)};tree=h(json.dumps(code,sort_keys=True).encode())
put(m.MEDIA/'native-source-snapshots'/tree/'Demo.cs',captured)
codepath=m.CODE_PREFIX+'Demo.cs';put(m.OWNED/codepath,current)
put(m.OWNED/(codepath+'.meta'),'fileFormatVersion: 2\nguid: 11111111111111111111111111111111\n')
put(m.OWNED/'Packages/manifest.json','{"dependencies":{}}')
put(m.OWNED/'Packages/packages-lock.json','{"dependencies":{}}')
put(m.OWNED/'ProjectSettings/ProjectVersion.txt','m_EditorVersion: 6000.6.0f1\n')
tex='Assets/ThirdParty/KayKitAdventurers/knight_texture.png'
put(m.OWNED/tex,b'\x89PNG\r\n\x00test-only-not-real-image')
put(m.OWNED/(tex+'.meta'),'fileFormatVersion: 2\nguid: 22222222222222222222222222222222\n')
put(m.OWNED/'Assets/ThirdParty/KayKitAdventurers/LICENSE.txt','Test fixture license, not a real grant')
put(m.OWNED/'Assets/ThirdParty/KayKitAdventurers/provenance.json','{"testFixture":true}')
save(m.ROOT/'production/batches/tech-ten-shorts-20261030/gpu-authorization.json',{'allowedExistingEditor':{'executable':'not-launched.exe'}})
scenes={}
for slug in m.NATIVE:
 topic=slug.removeprefix('shorts-');local=m.MEDIA/slug/'local';scene=m.CODE_PREFIX+'Scenes/'+topic+'/source-'+tree[:12]+'/0-Baseline.unity';scenes[slug]=scene
 put(m.OWNED/scene,'%YAML 1.1\nm_Script: {fileID: 11500000, guid: 11111111111111111111111111111111, type: 3}\nm_Texture: {fileID: 2800000, guid: 22222222222222222222222222222222, type: 3}\n')
 put(m.OWNED/(scene+'.meta'),'fileFormatVersion: 2\nguid: '+h(slug.encode())[:32]+'\n')
 frame=put(local/'unity-capture/game/00000.jpg',b'fixture-frame')
 timing=save(local/'visual-timing.json',{'fps':60,'timingInputs':{'voiceSha256':'a'*64},'sections':[{'kind':'unity','startFrame':0,'endFrame':1}]})
 save(local/'unity-capture/input-receipt.json',{'voiceSha256':'a'*64,'timingSha256':m.sha(timing),'sourceCode':code,'sourceTreeSha256':tree})
 save(local/'unity-capture/native-receipt.json',{'success':True,'topic':topic,'voiceSha256':'a'*64,'savedScenes':[scene],'artifacts':[{'path':str(frame),'sha256':m.sha(frame),'bytes':frame.stat().st_size},{'path':str(m.OWNED/scene),'sha256':m.sha(m.OWNED/scene),'bytes':(m.OWNED/scene).stat().st_size}]})
job=m.TOOLS/'jobs/test-export.json'
with contextlib.redirect_stdout(io.StringIO()):m.prepare(job)
for e in m.read(job)['captures']:
 scene=scenes[e['slug']]
 files=[item(codepath,guid='1'*32),item(codepath+'.meta','meta','1'*32),item(scene,guid=h(e['slug'].encode())[:32]),item(scene+'.meta','meta',h(e['slug'].encode())[:32]),item(tex,guid='2'*32),item(tex+'.meta','meta','2'*32),item('Assets/ThirdParty/KayKitAdventurers/LICENSE.txt'),item('Assets/ThirdParty/KayKitAdventurers/provenance.json'),item('Packages/manifest.json','package-lock'),item('Packages/packages-lock.json','package-lock'),item('ProjectSettings/ProjectVersion.txt','project-settings')]
 save(Path(e['manifestPath']),{'slug':e['slug'],'project':str(m.OWNED),'receiptSha256':e['receiptSha256'],'inputSha256':e['inputSha256'],'sourceTreeSha256':tree,'savedScenes':[scene],'files':files})
with contextlib.redirect_stdout(io.StringIO()):m.collect(job)
for e in m.read(job)['captures']:
 output=m.MEDIA/'editable-native'/e['slug']/e['receiptSha256']
 assert (output/'project'/codepath).read_bytes()==captured
 assert (output/'git-text-projection'/codepath).read_bytes()==captured
 assert (output/'project'/tex).exists()
 assert not (output/'git-text-projection'/tex).exists()
 assert (output/'git-text-projection'/(tex+'.meta')).exists()
 report=m.read(output/'editable-export.json')
 assert report['sceneBindings'][0]['sourceTreeSha256']==tree and report['runtimeReopenVerified'] is False
assert (m.OWNED/codepath).read_bytes()==current
with contextlib.redirect_stdout(io.StringIO()):m.collect(job)  # exact idempotent reuse
for unsafe in ['../escape','C:/outside','Assets\\escape','/absolute']:
 try:m.relative(unsafe)
 except ValueError:pass
 else:raise AssertionError('Path escape accepted')
first=m.read(job)['captures'][0]
frame=m.MEDIA/first['slug']/'local/unity-capture/game/00000.jpg';original=frame.read_bytes();frame.write_bytes(b'altered')
try:m.capture(first['slug'])
except ValueError:pass
else:raise AssertionError('Altered successful artifact accepted')
frame.write_bytes(original)
print(json.dumps({'passed':True,'cases':['all-seven-successful-receipt-gate','exact-captured-source-restored-not-current-code','scene-sourceTree-binding','local-binary-preserved-git-excluded','meta-preserved','idempotent-copy','path-traversal-rejected','altered-receipt-artifact-rejected'],'fixtureRoot':str(base),'liveProjectMutated':False,'unityLaunched':False},indent=2))
