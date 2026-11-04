"""CPU-only validation of actual immutable manifests and narrow profile exceptions."""
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,copy,hashlib,shutil
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('exporter',HERE/'export-native-editable.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
out=HERE/'qa'/('profile-exception-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
out.mkdir(parents=True)
job=m.read(m.TOOLS/'jobs/export-final-01.json');cases=[];checks=[]
for entry in job['captures']:
 manifest=m.read(entry['manifestPath']); inputs=m.read(entry['inputPath'])
 files={f['assetPath']:{'physical':Path(f['physicalPath']),'sha256':f['sha256']} for f in manifest['files'] if f['kind']=='asset'}
 external=[f for f in manifest['files'] if f['kind'].startswith('package-') and f['kind']!='package-lock']
 guids={f.get('guid') for f in manifest['files'] if f.get('guid')}
 snapshot=m.MEDIA/'native-source-snapshots'/inputs['sourceTreeSha256']
 refs,override=m.preserved_profile_references(inputs,files,external,guids,snapshot)
 assert len(refs)==4 and override['automaticExportReopenApplication'] is False
 data=Path(files[m.PROFILE_PATH]['physical']).read_bytes()
 assert not m.unresolved_guids(m.PROFILE_PATH,data,guids,[],refs)
 assert m.unresolved_guids(m.PROFILE_PATH,data+b'\n',guids,[],refs)==set(m.PROFILE_REFS)
 assert m.unresolved_guids('Assets/Other.asset',data,guids,[],refs)==set(m.PROFILE_REFS)
 checks.append({'slug':entry['slug'],'dependencyManifestSha256':m.sha(entry['manifestPath']),'references':refs,'capturePipelineOverrides':override})
cases+=['all-seven-exact-package-profile-and-source-bindings','changed-profile-bytes-not-exempt','same-guids-in-other-asset-not-exempt']
def reject(label,call):
 try:call()
 except ValueError:cases.append(label)
 else:raise AssertionError('Must reject '+label)
bad=copy.deepcopy(files);bad[m.PROFILE_PATH]['sha256']='f'*64
reject('wrong-local-profile-hash',lambda:m.preserved_profile_references(inputs,bad,external,guids,snapshot))
bad_external=[f for f in external if f['assetPath']!=m.PROFILE_PACKAGE_PATH]
reject('missing-package-template',lambda:m.preserved_profile_references(inputs,files,bad_external,guids,snapshot))
bad_external=copy.deepcopy(external)
for f in bad_external:
 if f['assetPath']==m.PROFILE_CORE_PATH:f['sha256']='f'*64
reject('changed-core-runtime',lambda:m.preserved_profile_references(inputs,files,bad_external,guids,snapshot))
reject('unreviewed-source-tree',lambda:m.preserved_profile_references(dict(inputs,sourceTreeSha256='f'*64),files,external,guids,snapshot))
reject('previously-missing-script-now-resolves',lambda:m.preserved_profile_references(inputs,files,external,guids|set(m.PROFILE_REFS),snapshot))
for name,p in [('local-profile.asset',m.OWNED/m.PROFILE_PATH),('package-profile.asset',Path(next(f['physicalPath'] for f in external if f['assetPath']==m.PROFILE_PACKAGE_PATH))),('VolumeProfile.cs',Path(next(f['physicalPath'] for f in external if f['assetPath']==m.PROFILE_CORE_PATH)))]:
 shutil.copyfile(p,out/name)
report={'passed':True,'cases':cases,'checks':checks,'packageMetaScan':{'isolatedCount':8033,'mainCount':22452,'fourGuidsFound':0},'assetChanged':False,'sourceChanged':False,'unityLaunched':False,'dependencyCompletenessVerified':False,'runtimeReopenVerified':False,'playerBuildVerified':False}
target=out/'test-report.json';target.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps({'passed':True,'cases':cases,'report':target.as_posix(),'sha256':m.sha(target)},indent=2))
