"""CPU-only tests for the exact preserved capture-settings exception."""
from pathlib import Path
from datetime import datetime, timezone
import importlib.util, json, copy, hashlib
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('exporter',HERE/'export-native-editable.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
base=HERE/'qa'/('settings-exception-fixture-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
m.OWNED=base/'owned';m.OWNED.mkdir(parents=True)
data=b'''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1045 &1
EditorBuildSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_Scenes:
  - enabled: 1
    path: Assets/Scenes/SampleScene.unity
    guid: 99c9720ab356a0642a771bea13969a05
  m_configObjects:
    com.unity.dt.app-ui: {fileID: 11400000, guid: 1b1c20d82303e4b5781c3ef50ac1449f, type: 2}
    com.unity.input.settings.actions: {fileID: -944628639613478452, guid: 052faaac586de48259a63d0c4782560b, type: 3}
'''
assert hashlib.sha256(data).hexdigest()==m.SETTINGS_SHA
settings=m.OWNED/m.SETTINGS_PATH;settings.parent.mkdir();settings.write_bytes(data)
(m.OWNED/'Packages').mkdir()
for name in ['manifest.json','packages-lock.json']:(m.OWNED/'Packages'/name).write_text('{"dependencies":{}}')
files={m.SETTINGS_PATH:{'physical':settings,'sha256':m.SETTINGS_SHA}}
inputs={'sourceTreeSha256':sorted(m.SETTINGS_SOURCE_TREES)[0]}
refs=[{'assetPath':m.SETTINGS_PATH,'physicalPath':str(settings),'settingsSha256':m.SETTINGS_SHA,'guid':guid,
 'key':key,'serializedLine':line,'reason':'Test fixture: capture-only, not player build','scope':m.SETTINGS_SCOPE,
 'runtimeReopenVerified':False,'playerBuildVerified':False} for guid,(key,line) in m.SETTINGS_REFS.items()]
manifest={'unresolvedSettingsReferences':refs}
assert m.validate_settings_exceptions(manifest,inputs,files)==refs
assert not m.unresolved_guids(m.SETTINGS_PATH,data,set(),refs)
def reject(label,call):
 try:call()
 except ValueError:cases.append(label)
 else:raise AssertionError('Must reject '+label)
cases=['exact-three-pinned-settings-accepted']
for field,value in [('key','other.key'),('serializedLine','wrong line'),('settingsSha256','b'*64),('physicalPath',str(m.OWNED/'other.asset')),('scope','unbounded'),('playerBuildVerified',True),('runtimeReopenVerified',True)]:
 bad=copy.deepcopy(manifest);bad['unresolvedSettingsReferences'][0][field]=value
 reject('altered-'+field,lambda bad=bad:m.validate_settings_exceptions(bad,inputs,files))
for badrefs in [refs[:2],refs+[refs[0]],refs[:2]+[dict(refs[2],guid='f'*32)]]:
 reject('incorrect-reference-set',lambda badrefs=badrefs:m.validate_settings_exceptions({'unresolvedSettingsReferences':badrefs},inputs,files))
reject('unreviewed-source-tree',lambda:m.validate_settings_exceptions(manifest,{'sourceTreeSha256':'f'*64},files))
settings.write_bytes(data+b'\n')
reject('altered-settings-bytes',lambda:m.validate_settings_exceptions(manifest,inputs,files))
assert m.unresolved_guids(m.SETTINGS_PATH,data+b'\n',set(),refs)==set(m.SETTINGS_REFS)
settings.write_bytes(data)
(m.OWNED/'Packages/manifest.json').write_text('{"dependencies":{"com.unity.dt.app-ui":"1.3.6"}}')
reject('new-app-ui-package',lambda:m.validate_settings_exceptions(manifest,inputs,files))
(m.OWNED/'Packages/manifest.json').write_text('{"dependencies":{}}')
for path in ['Assets/Scenes/Capture.unity','Assets/Materials/Render.mat','ProjectSettings/GraphicsSettings.asset']:
 assert m.unresolved_guids(path,data,set(),refs)==set(m.SETTINGS_REFS),path
 cases.append('no-exemption-outside-exact-file:'+path)
unknown=b'%YAML 1.1\n  asset: {guid: ffffffffffffffffffffffffffffffff}\n'
assert m.unresolved_guids(m.SETTINGS_PATH,unknown,set(),refs)=={'f'*32}
cases.append('unknown-guid-rejected')
report={'passed':True,'cases':cases,'fixtureRoot':base.as_posix(),'liveProjectChanged':False,'unityLaunched':False,'runtimeValidityClaimed':False}
(base/'test-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report,indent=2))
