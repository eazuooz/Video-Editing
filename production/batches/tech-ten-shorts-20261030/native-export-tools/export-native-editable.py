"""Prepare a bounded read-only Unity inventory job, then preserve editable projects.

No Unity launch, GPU, Git, deletion, source mutation or archive compression.
prepare: exact seven successful full captures -> immutable export job JSON.
collect: actual AssetDatabase manifests -> local editable projects + text projection.
Run Unity separately only after all captures finish; see prepare's command output.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path('D:/Github/VideoEditing')
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/tech-ten-shorts-20261030')
OWNED = MEDIA / 'unity-capture'
TOOLS = MEDIA / 'native-export-tools'
CODE_PREFIX = 'Assets/VideoScenes/tech-ten-shorts-20261030/'
NATIVE = (
 'shorts-alyx-liquid-shader', 'shorts-batman-origins-snow-below-camera',
 'shorts-sea-of-thieves-water-masking', 'shorts-uncharted3-fixed-plane-scrolling-desert',
 'shorts-uncharted4-taut-rope-fallback', 'shorts-starcraft-worker-mineral-walk',
 'shorts-starcraft2-marine-random-firing-delay',
)
CODE_EXT = {'.cs', '.shader', '.hlsl', '.cginc', '.asmdef', '.asmref'}
TEXT_ASSETS = CODE_EXT | {'.unity', '.meta', '.mat', '.asset', '.prefab', '.anim', '.controller', '.overridecontroller'}
DEFINITION_ONLY_REUSE = {
 'shorts-sea-of-thieves-water-masking': 'definition-overlay-v3',
 'shorts-starcraft-worker-mineral-walk': 'definition-overlay-v2',
}
SETTINGS_PATH = 'ProjectSettings/EditorBuildSettings.asset'
SETTINGS_SHA = '746171162169ec7b3f70ac4a8c2fd7c3c94d982ff2cf1da6d10986fd56757a95'
SETTINGS_SOURCE_TREES = {
 'ae3b2fd85f8fad48b6e51fc20d5d673868c1aba8aaa5dad8fb81ac58e3f4a661',
 'f16754c26af604fd8a69414a83dcc5d5de968ba602d57e050bdef005a2401939',
}
SETTINGS_SCOPE = 'Only the seven receipt-bound Sample(seconds)/Camera.Render captures; not general Play Mode or player builds'
SETTINGS_REFS = {
 '99c9720ab356a0642a771bea13969a05': (
  'm_Scenes[0].guid (Assets/Scenes/SampleScene.unity)',
  '    guid: 99c9720ab356a0642a771bea13969a05'),
 '1b1c20d82303e4b5781c3ef50ac1449f': (
  'm_configObjects.com.unity.dt.app-ui',
  '    com.unity.dt.app-ui: {fileID: 11400000, guid: 1b1c20d82303e4b5781c3ef50ac1449f, type: 2}'),
 '052faaac586de48259a63d0c4782560b': (
  'm_configObjects.com.unity.input.settings.actions',
  '    com.unity.input.settings.actions: {fileID: -944628639613478452, guid: 052faaac586de48259a63d0c4782560b, type: 3}'),
}
PROFILE_PATH='Assets/Settings/DefaultVolumeProfile.asset'
PROFILE_PACKAGE_PATH='Packages/com.unity.render-pipelines.universal/Editor/Volume/DefaultVolumeProfile.asset'
PROFILE_SHA='6698bfacfad479acfd9766d00aba81ab52527d3b15c8b133d03ed7a2401499d6'
PROFILE_CORE_PATH='Packages/com.unity.render-pipelines.core/Runtime/Volume/VolumeProfile.cs'
PROFILE_CORE_SHA='d163fd2cd62551c27b536d112c4affd10d96fdaae463f9cb7fb1b35fee146fbb'
PROFILE_REFS={
 '60f3b30c03e6ba64d9a27dc9dba8f28d':('OutlineVolumeComponent','-7750755424749557576',78),
 '0fd9ee276a1023e439cf7a9c393195fa':('TestAnimationCurveVolumeComponent','-7274224791359825572',119),
 '5a00a63fdd6bd2a45ab1f2d869305ffd':('OasisFogVolumeComponent','-5139089513906902183',264),
 '74955a4b0b4243bc87231e8b59ed9140':('TestVolume','4251301726029935498',833),
}
BUILDER_SHAS={
 'ae3b2fd85f8fad48b6e51fc20d5d673868c1aba8aaa5dad8fb81ac58e3f4a661':'446f6cf96dc30fc3acd5e27c8400f58517c1b9da854246fce25e6af16903fb49',
 'f16754c26af604fd8a69414a83dcc5d5de968ba602d57e050bdef005a2401939':'6747816f4f82b83585c6b87bc1be812674e3b92ed67791bc11aa2fda0cf45977',
}

def preserved_profile_references(inputs, files, external, guids, snapshot):
 # These are pre-existing missing scripts in the package-shipped profile,
 # not dependencies lost by the copier. No asset is fixed or reserialized.
 f=files.get(PROFILE_PATH)
 if not f: return [], {}
 tree=inputs['sourceTreeSha256']; builder_sha=BUILDER_SHAS.get(tree)
 if not builder_sha or inputs['sourceCode'].get('Editor/TechTenBuilder.cs')!=builder_sha:
  raise ValueError('Unreviewed source for package-profile exception')
 builder=Path(snapshot)/'Editor/TechTenBuilder.cs'; verify(builder,builder_sha)
 override='GraphicsSettings.defaultRenderPipeline=null;QualitySettings.renderPipeline=null;'
 if override not in builder.read_text(encoding='utf-8-sig'):
  raise ValueError('Captured builtin-pipeline setup differs')
 if f['sha256']!=PROFILE_SHA or Path(f['physical']).resolve()!=(OWNED/PROFILE_PATH).resolve():
  raise ValueError('Local default profile differs from reviewed package template')
 verify(f['physical'],PROFILE_SHA); data=Path(f['physical']).read_bytes()
 matches={name:[v for v in external if v['assetPath']==name] for name in (PROFILE_PACKAGE_PATH,PROFILE_CORE_PATH)}
 if any(len(v)!=1 for v in matches.values()):raise ValueError('Missing unique package profile/runtime provenance')
 template=matches[PROFILE_PACKAGE_PATH][0]; core=matches[PROFILE_CORE_PATH][0]
 for entry,expected in ((template,PROFILE_SHA),(core,PROFILE_CORE_SHA)):
  if entry['kind']!='package-reference' or entry['sha256']!=expected:
   raise ValueError('Package profile/runtime provenance differs')
  inside(entry['physicalPath'],OWNED/'Library/PackageCache');verify(entry['physicalPath'],expected)
 if Path(template['physicalPath']).read_bytes()!=data:raise ValueError('Local/package profile bytes differ')
 if 'components.RemoveAll(x => x == null);' not in Path(core['physicalPath']).read_text(encoding='utf-8-sig'):
  raise ValueError('Package missing-component handling differs')
 if set(PROFILE_REFS)&guids:raise ValueError('Previously missing volume script now resolves; renew analysis')
 text=data.decode('utf-8-sig'); lines=text.splitlines(); refs=[]
 for guid,(component,subid,line_number) in PROFILE_REFS.items():
  line='  m_Script: {fileID: 11500000, guid: '+guid+', type: 3}'
  if lines[line_number-1]!=line or lines.count(line)!=1:raise ValueError('Volume script occurrence differs')
  block=re.search(r'^--- !u!114 &'+re.escape(subid)+r'\n(.*?)(?=^--- |\Z)',text,re.M|re.S)
  if not block or line not in block[1] or '\n  m_Name: '+component+'\n' not in block[1]:
   raise ValueError('Volume script component context differs')
  refs.append({'assetPath':PROFILE_PATH,'physicalPath':str(f['physical']),'assetSha256':PROFILE_SHA,
   'field':'m_Script','guid':guid,'componentName':component,'subAssetFileID':subid,'lineNumber':line_number,'serializedLine':line,
   'packageTemplate':{'assetPath':PROFILE_PACKAGE_PATH,'physicalPath':template['physicalPath'],'sha256':PROFILE_SHA},
   'packageRuntimeEvidence':{'assetPath':PROFILE_CORE_PATH,'physicalPath':core['physicalPath'],'sha256':PROFILE_CORE_SHA,'handling':'VolumeProfile.OnEnable removes null components for missing scripts'},
   'sourceTreeSha256':tree,'reason':'Unresolved script already present in byte-identical installed URP template. Captured builder selects builtin rendering; no Volume or URP additional-camera component occurs in the receipt scenes. Preserved defect, not a resolved dependency.',
   'dependencyCompletenessVerified':False,'runtimeReopenVerified':False,'playerBuildVerified':False})
 return refs,{'sourceTreeSha256':tree,'sourcePath':str(builder),'sourceSHA256':builder_sha,
  'setupCode':override,'defaultRenderPipeline':'null (builtin)','qualityRenderPipeline':'null (builtin)',
  'automaticExportReopenApplication':False,
  'instruction':'Apply these capture-time pipeline overrides before replaying the saved scene. Copied project defaults and a plain Play Mode start are not certified equivalent.'}

def validate_settings_exceptions(manifest, inputs, files):
 refs=manifest.get('unresolvedSettingsReferences', [])
 if not refs: return []
 if len(refs)!=3 or {r.get('guid') for r in refs}!=set(SETTINGS_REFS):
  raise ValueError('Only all three exact preserved settings references are recognized')
 if inputs['sourceTreeSha256'] not in SETTINGS_SOURCE_TREES:
  raise ValueError('Settings exception is not reviewed for this captured source')
 f=files.get(SETTINGS_PATH)
 if not f or f['sha256']!=SETTINGS_SHA or Path(f['physical']).resolve()!=(OWNED/SETTINGS_PATH).resolve():
  raise ValueError('Exception settings file binding differs')
 verify(f['physical'], SETTINGS_SHA)
 lines=Path(f['physical']).read_text(encoding='utf-8-sig').splitlines()
 for r in refs:
  key,line=SETTINGS_REFS[r['guid']]
  if (r.get('assetPath')!=SETTINGS_PATH or Path(r.get('physicalPath','')).resolve()!=(OWNED/SETTINGS_PATH).resolve()
      or r.get('settingsSha256')!=SETTINGS_SHA or r.get('key')!=key or r.get('serializedLine')!=line
      or lines.count(line)!=1 or not r.get('reason') or r.get('scope')!=SETTINGS_SCOPE
      or r.get('runtimeReopenVerified') is not False or r.get('playerBuildVerified') is not False):
   raise ValueError('Settings exception occurrence or limitation differs')
 for packages in ('Packages/manifest.json','Packages/packages-lock.json'):
  if 'com.unity.dt.app-ui' in read(OWNED/packages).get('dependencies',{}):
   raise ValueError('App UI package changed; renew capture-scoped analysis')
 return refs

def unresolved_guids(logical, data, known_guids, settings_exceptions, serialized_exceptions=()):
 if Path(logical).suffix.lower() not in {'.unity','.prefab','.mat','.asset','.controller','.anim'} or not data.startswith(b'%YAML'):
  return set()
 exceptions={r['guid'] for r in settings_exceptions} if logical==SETTINGS_PATH and hashlib.sha256(data).hexdigest()==SETTINGS_SHA else set()
 if logical==PROFILE_PATH and hashlib.sha256(data).hexdigest()==PROFILE_SHA:
  exceptions.update(r['guid'] for r in serialized_exceptions if r['assetPath']==PROFILE_PATH and r['assetSha256']==PROFILE_SHA)
 return {raw.decode() for raw in re.findall(rb'guid:\s*([0-9a-f]{32})',data)
         if not raw.startswith(b'0000000000000000') and raw.decode() not in known_guids and raw.decode() not in exceptions}

def read(path):
 return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def sha(path):
 h = hashlib.sha256()
 with Path(path).open('rb') as stream:
  for block in iter(lambda: stream.read(1024 * 1024), b''): h.update(block)
 return h.hexdigest()

def inside(path, root):
 path, root = Path(path), Path(root)
 path.resolve().relative_to(root.resolve())
 if path.resolve() == root.resolve(): raise ValueError('Expected child path')
 return path

def no_links(path, stop):
 path, stop = Path(path), Path(stop)
 inside(path, stop)
 for part in [path, *path.parents]:
  if part.is_symlink() or getattr(part, 'is_junction', lambda: False)():
   raise ValueError('Symlink/junction not copied: ' + str(part))
  if part == stop: break

def relative(text):
 p = PurePosixPath(text)
 if p.is_absolute() or '..' in p.parts or ':' in text or '\\' in text:
  raise ValueError('Unsafe logical asset path: ' + text)
 return p.as_posix()

def verify(path, expected):
 if not re.fullmatch('[a-f0-9]{64}', expected or '') or not Path(path).is_file() or sha(path) != expected:
  raise ValueError('Hash mismatch: ' + str(path))

def write_new(path, data):
 path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
 encoded = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8')
 if path.exists():
  if path.read_bytes() != encoded: raise ValueError('Preserve existing different file: ' + str(path))
 else:
  with path.open('xb') as stream: stream.write(encoded)

def verified_timing(slug, local, inputs):
 current_path = local / 'visual-timing.json'
 current = read(current_path); current_sha = sha(current_path)
 evidence = {'currentPath':current_path.as_posix(), 'currentSha256':current_sha,
  'capturedSha256':inputs['timingSha256']}
 if current_sha == inputs['timingSha256']:
  evidence.update(mode='exact-capture-timing', capturedPath=current_path.as_posix())
  return current, evidence
 # The two reviewed revisions changed only the compositor's definition card.
 # Native frames retain their original receipt; no general stale-timing bypass.
 if slug not in DEFINITION_ONLY_REUSE: raise ValueError('Unreviewed native timing change: '+slug)
 original_path = inside(local / 'finite-pipeline-v1/adoption-history' / DEFINITION_ONLY_REUSE[slug] / 'production/visual-timing.json', local)
 verify(original_path, inputs['timingSha256']); original = read(original_path)
 before = original['events'].pop('term-definition')
 after = current['events'].pop('term-definition')
 if original != current: raise ValueError('Native sections or non-definition event changed: '+slug)
 for event in (before,after):
  if set(event) != {'startFrame','endFrame','cueIds'} or not 0 <= event['startFrame'] < event['endFrame'] <= current['frames']:
   raise ValueError('Invalid bounded definition timing')
 if before == after: raise ValueError('Timing hash differs without reviewed definition change')
 current['events']['term-definition'] = after
 evidence.update(mode='reviewed-compositor-definition-only', capturedPath=original_path.as_posix(),
  onlyChangedField='events.term-definition', before=before, after=after,
  nativeSectionsActionsSourcesAndTimingInputsExactlyEqual=True)
 return current,evidence

def capture(slug):
 if slug not in NATIVE: raise ValueError('Unselected native slug')
 local = MEDIA / slug / 'local'
 receipt_path = local / 'unity-capture/native-receipt.json'
 input_path = local / 'unity-capture/input-receipt.json'
 receipt, inputs = read(receipt_path), read(input_path)
 if receipt.get('success') is not True or receipt.get('topic') != slug.removeprefix('shorts-'):
  raise ValueError('Native capture is incomplete: ' + slug)
 if receipt.get('voiceSha256') != inputs.get('voiceSha256') or not re.fullmatch('[a-f0-9]{64}', receipt.get('voiceSha256', '')):
  raise ValueError('Not a full voice-bound capture: ' + slug)
 timing, timing_evidence = verified_timing(slug, local, inputs)
 if timing['timingInputs']['voiceSha256'] != receipt['voiceSha256'] or timing['fps'] != 60:
  raise ValueError('Timing differs: ' + slug)
 code = inputs['sourceCode']
 digest = hashlib.sha256(json.dumps(code, sort_keys=True).encode()).hexdigest()
 if digest != inputs['sourceTreeSha256']: raise ValueError('Source tree digest differs')
 snapshot = MEDIA / 'native-source-snapshots' / digest
 for name, expected in code.items(): verify(inside(snapshot / relative(name), snapshot), expected)
 scenes = receipt.get('savedScenes', [])
 expected_prefix = CODE_PREFIX + 'Scenes/' + receipt['topic'] + '/source-' + digest[:12] + '/'
 if not scenes or len(scenes) != len(set(scenes)) or any(not s.startswith(expected_prefix) or not s.endswith('.unity') for s in scenes):
  raise ValueError('Scene version is not bound to captured source tree')
 expected_frame_count = sum(s['endFrame'] - s['startFrame'] for s in timing['sections'] if s['kind'] == 'unity')
 frame_count = 0; scene_artifacts = set()
 for item in receipt['artifacts']:
  path = Path(item['path'])
  if path.suffix.lower() == '.jpg':
   inside(path, local / 'unity-capture'); frame_count += 1
  elif path.suffix.lower() == '.unity':
   inside(path, OWNED / 'Assets')
   logical = path.relative_to(OWNED).as_posix()
   if logical not in scenes: raise ValueError('Unlisted scene artifact')
   scene_artifacts.add(logical)
  else: raise ValueError('Unexpected receipt artifact: ' + str(path))
  # Hash checking all existing captured frames is CPU-only and detects a stale
  # success receipt; no expensive encoding or source regeneration is performed.
  verify(path, item['sha256'])
  if path.stat().st_size != item['bytes']: raise ValueError('Artifact byte count differs')
 if frame_count != expected_frame_count or scene_artifacts != set(scenes):
  raise ValueError('Incomplete full capture frame/scene set')
 return receipt_path, input_path, receipt, inputs, snapshot

def prepare(job_path):
 job_path = inside(job_path, TOOLS / 'jobs')
 entries = []
 for slug in NATIVE:
  r, i, receipt, inputs, snapshot = capture(slug)
  digest = sha(r)
  _, timing_evidence = verified_timing(slug, MEDIA / slug / 'local', inputs)
  entries.append({'slug': slug, 'receiptPath': r.as_posix(), 'receiptSha256': digest,
   'inputPath': i.as_posix(), 'inputSha256': sha(i),
   'timingEvidence':timing_evidence,
   'manifestPath': (MEDIA / 'native-dependency-manifests' / job_path.stem / (slug + '-' + digest + '.json')).as_posix()})
 write_new(job_path, {'schemaVersion': 1, 'captures': entries})
 exe = read(ROOT / 'production/batches/tech-ten-shorts-20261030/gpu-authorization.json')['allowedExistingEditor']['executable']
 print(json.dumps({'job': str(job_path), 'helperInstallDestination': str(OWNED / 'Assets/Editor/TechTenArchive/TechTenDependencyManifest.cs'),
  'separateCommandNotExecuted': [exe, '-batchmode', '-nographics', '-projectPath', str(OWNED),
   '-executeMethod', 'Yamyam.TechTen.Archive.TechTenDependencyManifest.Run',
   '-techTenExportJob', str(job_path), '-logFile', str(job_path.with_suffix('.unity.log'))],
  'prerequisite': 'All native captures finished; owned project idle. Install helper only then. Do not target main Editor.'}, ensure_ascii=False, indent=2))

def eligible_text(logical, data):
 ext = Path(logical).suffix.lower()
 allowed = (logical.startswith(CODE_PREFIX) and ext in TEXT_ASSETS)
 allowed |= logical.startswith('Assets/') and ext == '.meta'
 allowed |= logical in {'Packages/manifest.json', 'Packages/packages-lock.json'}
 allowed |= logical.startswith('ProjectSettings/') and ext in {'.asset', '.txt'}
 allowed |= logical in {'Assets/ThirdParty/KayKitAdventurers/LICENSE.txt', 'Assets/ThirdParty/KayKitAdventurers/provenance.json'}
 if not allowed or b'\0' in data: return False
 try: data.decode('utf-8-sig')
 except UnicodeDecodeError: return False
 return True

def copy_exact(src, dst, expected):
 verify(src, expected)
 dst.parent.mkdir(parents=True, exist_ok=True)
 if dst.exists(): verify(dst, expected)
 else:
  with Path(src).open('rb') as reader, dst.open('xb') as writer: shutil.copyfileobj(reader, writer)
 verify(dst, expected); verify(src, expected)

def collect(job_path):
 job_path = inside(job_path, TOOLS / 'jobs'); job = read(job_path)
 if {x['slug'] for x in job['captures']} != set(NATIVE) or len(job['captures']) != 7:
  raise ValueError('Expected exactly seven selected native captures')
 outputs=[]
 for entry in job['captures']:
  slug = entry['slug']; rp, ip, receipt, inputs, snapshot = capture(slug)
  _, timing_evidence = verified_timing(slug, MEDIA / slug / 'local', inputs)
  if timing_evidence != entry['timingEvidence']: raise ValueError('Timing evidence changed after export preparation')
  verify(rp, entry['receiptSha256']); verify(ip, entry['inputSha256'])
  mp = inside(entry['manifestPath'], MEDIA / 'native-dependency-manifests'); manifest = read(mp)
  for key in ('slug', 'receiptSha256', 'inputSha256'):
   if manifest[key] != entry[key]: raise ValueError('Manifest receipt binding differs')
  if manifest['sourceTreeSha256'] != inputs['sourceTreeSha256'] or manifest['savedScenes'] != receipt['savedScenes'] or Path(manifest['project']).resolve() != OWNED.resolve():
   raise ValueError('Manifest source/scene binding differs')
  base = MEDIA / 'editable-native' / slug / entry['receiptSha256']
  full = base / 'project'; git = base / 'git-text-projection'
  files = {}; external=[]; code = inputs['sourceCode']; captured_keys = {CODE_PREFIX + relative(k): v for k,v in code.items()}
  for f in manifest['files']:
   logical = relative(f['assetPath'])
   if logical in files: raise ValueError('Duplicate manifest logical path')
   kind = f['kind']
   if kind == 'unity-built-in-reference': external.append(f); continue
   physical = Path(f['physicalPath']); verify(physical, f['sha256'])
   if physical.stat().st_size != f['bytes']: raise ValueError('Dependency size differs')
   if kind.startswith('package-') and kind != 'package-lock':
    # Registry package assets stay package-manager references, never copied as
    # Library cache or presented as redistributable project-owned files.
    external.append(f); continue
   no_links(physical, OWNED)
   if not logical.startswith(('Assets/', 'Packages/', 'ProjectSettings/')):
    raise ValueError('Unexpected project subtree')
   if physical.resolve() != (OWNED / logical).resolve(): raise ValueError('Physical/logical mismatch')
   is_code = Path(logical).suffix.lower() in CODE_EXT
   base_code = logical[:-5] if logical.endswith('.meta') else logical
   if (is_code or Path(base_code).suffix.lower() in CODE_EXT) and logical.startswith(CODE_PREFIX) and base_code not in captured_keys:
    continue  # Current code added after this capture is not part of this version.
   files[logical] = {'physical': physical, 'sha256': f['sha256'], 'guid': f.get('guid',''), 'kind': kind, 'binding': 'export-observed'}
  for logical, expected in captured_keys.items():
   src = snapshot / logical[len(CODE_PREFIX):]; verify(src, expected)
   if logical + '.meta' not in files: raise ValueError('Captured source .meta missing: '+logical)
   files[logical] = {'physical': src, 'sha256': expected, 'guid': files[logical + '.meta']['guid'], 'kind': 'captured-source', 'binding': 'input-receipt-sourceTreeSha256'}
  scene_hashes = {Path(a['path']).relative_to(OWNED).as_posix(): a['sha256'] for a in receipt['artifacts'] if a['path'].lower().endswith('.unity')}
  for logical, expected in scene_hashes.items():
   if logical not in files or files[logical]['sha256'] != expected: raise ValueError('Scene bytes differ from receipt')
   files[logical]['binding'] = 'native-receipt'
  guids = {f['guid'] for f in files.values() if f['guid']} | {f.get('guid') for f in external if f.get('guid')}
  settings_exceptions=validate_settings_exceptions(manifest, inputs, files)
  serialized_exceptions,pipeline_overrides=preserved_profile_references(inputs,files,external,guids,snapshot)
  if serialized_exceptions:
   for scene in scene_hashes:
    scene_text=Path(files[scene]['physical']).read_text(encoding='utf-8-sig')
    scripts=set(re.findall(r'm_Script:.*?guid: ([0-9a-f]{32})',scene_text))
    if scripts!={'4105a6e6acd6bf04895d8ff3ab832d4b'} or 'm_RenderPostProcessing:' in scene_text:
     raise ValueError('Receipt scene component set changed; renew volume-profile analysis')
  missing = set(); projection=[]; omitted=[]; records=[]
  for logical,f in files.items():
   src=f['physical']; data=src.read_bytes(); verify(src,f['sha256'])
   # Unity's builtin resources use reserved all-zero-prefix GUIDs. All other
   # serialized references must resolve to an inventoried asset/package GUID.
   missing.update(unresolved_guids(logical,data,guids,settings_exceptions,serialized_exceptions))
   copy_exact(src,full/logical,f['sha256'])
   record={'path':logical,'sha256':f['sha256'],'bytes':len(data),'guid':f['guid'],'binding':f['binding']}
   if eligible_text(logical,data): copy_exact(src,git/logical,f['sha256']); projection.append(record)
   else: omitted.append(record)
   records.append(record)
  if missing: raise ValueError('Unresolved serialized GUIDs; preserved partial export: '+','.join(sorted(missing)))
  # Receipt/snapshot provenance is copied separately, never into Assets or Git.
  copy_exact(rp,base/'evidence/native-receipt.json',sha(rp));copy_exact(ip,base/'evidence/input-receipt.json',sha(ip));copy_exact(mp,base/'evidence/dependency-manifest.json',sha(mp))
  # The saved scene holds editable objects; Sample(seconds) is driven by the
  # capture runner rather than Update(). Preserve the exact external timeline
  # as well, so section actions and elapsed offsets can be reconstructed.
  timing_files=[]
  for role,path_key,hash_key in [('captured','capturedPath','capturedSha256'),('current','currentPath','currentSha256')]:
   source=Path(timing_evidence[path_key]); target=base/'evidence'/('visual-timing-'+role+'.json')
   copy_exact(source,target,timing_evidence[hash_key])
   timing_files.append({'role':role,'path':target.as_posix(),'sha256':timing_evidence[hash_key]})
  record={'schemaVersion':1,'slug':slug,'success':True,'receiptSha256':entry['receiptSha256'],'dependencyManifestSha256':sha(mp),
   'sourceTreeSha256':inputs['sourceTreeSha256'],'timingEvidence':timing_evidence,'sceneBindings':[{'scene':s,'sceneSha256':scene_hashes[s],'sourceTreeSha256':inputs['sourceTreeSha256']} for s in receipt['savedScenes']],
   'editableProject':full.as_posix(),'gitTextProjection':git.as_posix(),'projectFiles':records,'gitTextAllowlist':projection,
   'localOnlyFiles':omitted,'externalPackageAndEngineReferences':external,
   'unresolvedSettingsReferences':settings_exceptions,
   'unresolvedSerializedReferences':serialized_exceptions,'dependencyCompletenessVerified':False,
   'preservedTimingFiles':timing_files,
   'playbackContract':{'automaticPlayModeAnimation':False,
    'capturePipelineOverrides':pipeline_overrides,
    'entryPoint':'Yamyam.TechTen.TechTenDemo.Sample(seconds)',
    'sectionSettings':['unityStage','actionKind','actionStartSeconds','actionResumeSeconds','elapsedOffsetSeconds'],
    'instructions':'Open the matching stage scene. Apply the captured section action settings and call Sample((globalFrame - section.startFrame)/60 + elapsedOffsetSeconds), equivalently Sample(sectionLocalFrame/60 + elapsedOffsetSeconds). The original capture runner is bounded to the owned capture project and is preserved unchanged; it is not a portable one-click render command.'},
   'currentProjectSettingsAreNotCaptureReceiptBound':True,'dependencyHashesObservedAtExport':True,
   'thirdPartyProvenance':'Assets/ThirdParty/KayKitAdventurers/provenance.json when referenced; preserve license and exact FBX/texture hashes. No new vendor binary Git exception.',
   'runtimeReopenVerified':False,'playerBuildVerified':False,'gpuOrUnityLaunchedByCopier':False,'gitActions':False}
  write_new(base/'editable-export.json',record)
  outputs.append({'slug':slug,'path':str(base/'editable-export.json'),'sha256':sha(base/'editable-export.json')})
 print(json.dumps({'exports':outputs,'count':len(outputs)},ensure_ascii=False,indent=2))

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('action',choices=['prepare','collect']);parser.add_argument('--job',type=Path,required=True)
 args=parser.parse_args()
 (prepare if args.action=='prepare' else collect)(args.job)

if __name__=='__main__': main()
