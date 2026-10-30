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
 timing_path = local / 'visual-timing.json'
 verify(timing_path, inputs['timingSha256'])
 timing = read(timing_path)
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
  entries.append({'slug': slug, 'receiptPath': r.as_posix(), 'receiptSha256': digest,
   'inputPath': i.as_posix(), 'inputSha256': sha(i),
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
  missing = set(); projection=[]; omitted=[]; records=[]
  for logical,f in files.items():
   src=f['physical']; data=src.read_bytes(); verify(src,f['sha256'])
   # Unity's builtin resources use reserved all-zero-prefix GUIDs. All other
   # serialized references must resolve to an inventoried asset/package GUID.
   if Path(logical).suffix.lower() in {'.unity','.prefab','.mat','.asset','.controller','.anim'} and data.startswith(b'%YAML'):
    for raw in re.findall(rb'guid:\s*([0-9a-f]{32})',data):
     guid=raw.decode()
     if not guid.startswith('0000000000000000') and guid not in guids: missing.add(guid)
   copy_exact(src,full/logical,f['sha256'])
   record={'path':logical,'sha256':f['sha256'],'bytes':len(data),'guid':f['guid'],'binding':f['binding']}
   if eligible_text(logical,data): copy_exact(src,git/logical,f['sha256']); projection.append(record)
   else: omitted.append(record)
   records.append(record)
  if missing: raise ValueError('Unresolved serialized GUIDs; preserved partial export: '+','.join(sorted(missing)))
  # Receipt/snapshot provenance is copied separately, never into Assets or Git.
  copy_exact(rp,base/'evidence/native-receipt.json',sha(rp));copy_exact(ip,base/'evidence/input-receipt.json',sha(ip));copy_exact(mp,base/'evidence/dependency-manifest.json',sha(mp))
  record={'schemaVersion':1,'slug':slug,'success':True,'receiptSha256':entry['receiptSha256'],'dependencyManifestSha256':sha(mp),
   'sourceTreeSha256':inputs['sourceTreeSha256'],'sceneBindings':[{'scene':s,'sceneSha256':scene_hashes[s],'sourceTreeSha256':inputs['sourceTreeSha256']} for s in receipt['savedScenes']],
   'editableProject':full.as_posix(),'gitTextProjection':git.as_posix(),'projectFiles':records,'gitTextAllowlist':projection,
   'localOnlyFiles':omitted,'externalPackageAndEngineReferences':external,
   'currentProjectSettingsAreNotCaptureReceiptBound':True,'dependencyHashesObservedAtExport':True,
   'thirdPartyProvenance':'Assets/ThirdParty/KayKitAdventurers/provenance.json when referenced; preserve license and exact FBX/texture hashes. No new vendor binary Git exception.',
   'runtimeReopenVerified':False,'gpuOrUnityLaunchedByCopier':False,'gitActions':False}
  write_new(base/'editable-export.json',record)
  outputs.append({'slug':slug,'path':str(base/'editable-export.json'),'sha256':sha(base/'editable-export.json')})
 print(json.dumps({'exports':outputs,'count':len(outputs)},ensure_ascii=False,indent=2))

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('action',choices=['prepare','collect']);parser.add_argument('--job',type=Path,required=True)
 args=parser.parse_args()
 (prepare if args.action=='prepare' else collect)(args.job)

if __name__=='__main__': main()
