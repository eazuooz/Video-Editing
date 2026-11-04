"""Collect A02's 23 completed native scenes; never touch Unity, shared files or Git.

Default writes only the two A02 metadata outputs after every check passes.
--check performs the same read-only checks and prints the proposed counts.
No partial collection is written while any render or importer receipt is missing.
"""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import argparse, hashlib, json, math, re, subprocess, sys, time

sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent
R=H.parents[3]
U=R/'unity/VideoEditing'
L=H.parent/'local/grid-v1'
A=U/'Assets/VideoScenes/animation-exaggeration/grid-v1'
C=U/'Assets/VideoScenes/animation-series-v1'
B=R/'production/batches/animation-18-20261031'
EXPECTED_FINGERPRINT='eca5cfe8c2bc45c70d6d939bd085cb73eb0205c6e00803f378022af00802c66b'
SCOPE='A02-animation-scene-source-assets'
OUTPUT_MANIFEST=H/'saved-scene-source-manifest.json'
OUTPUT_SPEC=H/'scene-source-commit-plan.json'
GUID=re.compile(r'guid:\s*([a-f0-9]{32})')
IDENTITY=re.compile(r'^guid: ([a-f0-9]{32})$',re.M)
BUILTINS={'0'*32,'0000000000000000e000000000000000','0000000000000000f000000000000000'}
ACTOR_MODES={'normal-and-pause','size-amplitude','shoulder-control','paused-pose-context'}
# This pre-existing optional probe visualizer resource is absent from the installed
# package metadata. Preserve the frozen renderer bytes and report the unresolved
# environment fact; never describe it as restored or exempt another GUID/field.
KNOWN_EXTERNAL_DEBUG_REFERENCES=[{'path':'unity/VideoEditing/Assets/Settings/PC_Renderer.asset',
 'sha256':'3d0b01d8ded3327263b6690be128a3de58d17c514943ae42fe743a3e084a9c79',
 'field':field,'guid':identity,'fileId':file_id} for field,identity,file_id in (
 ('probeVolumeDebugShader','e5c6678ed2aaa91408dd3df699057aae',4800000),
 ('probeVolumeFragmentationDebugShader','03cfc4915c15d504a9ed85ecc404e607',4800000),
 ('probeVolumeOffsetDebugShader','53a11f4ebaebf4049b3638ef78dc9664',4800000),
 ('probeVolumeSamplingDebugShader','8f96cd657dc40064aa21efcc7e50a2e7',4800000),
 ('probeSamplingDebugMesh','57d7c4c16e2765b47a4d2069b311bffe',-3555484719484374845),
 ('probeSamplingDebugTexture','24ec0e140fb444a44ab96ee80844e18e',2800000),
 ('probeVolumeBlendStatesCS','b9a23f869c4fd45f19c5ada54dd82176',7200000))]
LEGACY_RESOURCE_EVIDENCE=[
 {'path':'unity/VideoEditing/Library/PackageCache/com.unity.render-pipelines.universal@8457e85b8184/Runtime/Deprecated.cs',
  'sha256':'4528f725dab168971d0e4703e4f3d3c5cc8c67c704e4432aa000e44d239d5cef'},
 {'path':'unity/VideoEditing/Library/PackageCache/com.unity.render-pipelines.core@2d66c71e606e/Runtime/Lighting/ProbeVolume/ProbeVolumeGlobalSettings.cs',
  'sha256':'27ff6a287c3b8e4c7d979cfcd5964ea2e94b341e6c32407d70396a6ff88d250f'}]
SHARED_SOURCE_NAMES=('AnimationLessonStage.cs','AnimationExaggerationStage.cs',
 'AnimationExaggerationBuildVersion.cs','Editor/AnimationGridCapture.cs',
 'Editor/AnimationExaggerationStageEditor.cs','animation-exaggeration-presentations.json','asset-map.json')

def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(R).as_posix()
def artifact(p):
    assert p.is_file() and p.resolve().is_relative_to(R.resolve()),str(p)
    return {'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size}
def check_artifact(item):
    p=R/item['path'];assert p.is_file() and sha(p)==item['sha256'],('Changed input',item['path'])
def meta_of(p):return Path(str(p)+'.meta')
def guid_of(p):
    m=IDENTITY.search(meta_of(p).read_text('utf-8-sig'));assert m,('Missing asset GUID',rel(p));return m[1]
def encoded(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def git_read(*args):
    env=__import__('os').environ.copy();env['GIT_OPTIONAL_LOCKS']='0'
    return subprocess.check_output(['git',*args],cwd=R,env=env)

def preserved_a01():
    manifest=R/'projects/animation-assigning/production/grid-v1/saved-scene-source-manifest.json'
    spec=B/'scene-source-commit-plan.json';m=read(manifest);s=read(spec)
    assert len(m['scenes'])==27 and m['generatedRasterCount']==78
    for item in m['files']:check_artifact(item)
    registry=read(R/'shared/git-essential-images.json')['entries']
    assert len(s['essentialImages'])==78
    for old in s['essentialImages']:
        assert [x for x in registry if x['path']==old['path']]==[old],('A01 essential row changed',old['path'])
    return {'manifest':artifact(manifest),'commitPlan':artifact(spec),'scenes':27,
            'files':len(m['files']),'labels':78,'allCurrentHashesAndRowsMatch':True}

def verify_freeze():
    p=H/'source-fingerprint.json';freeze=read(p)
    assert freeze['fingerprint']==EXPECTED_FINGERPRINT and freeze['episode']=='A02'
    assert freeze['stageClass']=='AnimationExaggerationStage' and not freeze['vendorBytesInTrackedSnapshot']
    calculated=hashlib.sha256(json.dumps(freeze['files'],sort_keys=True).encode('utf8')).hexdigest()
    assert calculated==EXPECTED_FINGERPRINT
    for item in freeze['files']:
        check_artifact(item)
        full=R/freeze['fullSnapshotRoot']/item['path'];assert full.is_file() and sha(full)==item['sha256']
        tracked=H/'source-snapshots'/EXPECTED_FINGERPRINT/item['path']
        if '/ThirdParty/' in item['path']:assert not tracked.exists(),('Vendor copy in tracked snapshot',rel(tracked))
        else:assert tracked.is_file() and sha(tracked)==item['sha256']
    version=(C/'AnimationExaggerationBuildVersion.cs').read_text('utf-8-sig')
    expected_version=('namespace Yamyam.AnimationSeries { public static class AnimationExaggerationBuildVersion '
      '{ public static string For(string stage) { return stage=="AnimationExaggerationStage"?"'
      +EXPECTED_FINGERPRINT+'":"unknown"; } } }\n')
    assert version==expected_version,'Derived A02 build-version source changed'
    ack=read(H/'compiled-ack.json')
    stages=[x for x in ack['stages'] if x['stageClass']=='AnimationExaggerationStage']
    assert len(stages)==1 and stages[0]['typeAvailable'] and stages[0]['fingerprint']==EXPECTED_FINGERPRINT
    return freeze,stages[0],ack

def scalar(scene,name):
    matches=re.findall(r'^  '+re.escape(name)+r': (.*)$',scene,re.M)
    assert len(matches)==1,('Ambiguous saved field',name)
    value=matches[0]
    return json.loads(value) if value.startswith('"') else value

def verify_runtime(queue,stage,ack):
    records=[];inputs=[];seeds=[]
    profiles=read(C/'animation-exaggeration-presentations.json')['presentations']
    byid={x['id']:x for x in profiles};assert len(byid)==len(profiles)==23
    assert set(byid)=={q['presentation'] for q in queue}
    for q in queue:
        folder=L/'render'/q['revision']/q['mode']
        paths={n:folder/n for n in ('render-success.json','request.json','scene-reopen-evidence.json','reopen-stage-diagnostic.json')}
        for p in paths.values():assert p.is_file(),('Final 23-scene runtime not complete',rel(p))
        receipt,request,reopen,diag=(read(paths[n]) for n in paths)
        scene=A/'RenderRevisions'/q['revision']/(q['mode']+'.unity')
        stamp_path=Path(str(scene)+'.capture-source.json')
        for p in (scene,meta_of(scene),stamp_path):
            assert p.is_file(),('Saved scene/import identity incomplete',rel(p))
        stamp=read(stamp_path)
        assert receipt['status']=='complete' and not receipt.get('error')
        assert receipt['completed']==receipt['frames']==q['frames']
        assert receipt['slug']==request['slug']==stamp['slug']=='animation-exaggeration'
        assert receipt['cutId']==request['cutId']==stamp['cutId']==q['mode']
        assert receipt['presentationId']==request['presentationId']==stamp['presentationId']==q['presentation']
        assert request['command']=='render' and request['frames']==stamp['frames']==q['frames']
        assert request['stageClass']==stamp['stageClass']=='AnimationExaggerationStage'
        assert receipt['scene']==reopen['scene']==scene.relative_to(U).as_posix()
        assert Path(receipt['output']).resolve()==folder.resolve()==Path(request['output']).resolve()
        assert receipt['compiledSourceFingerprint']==request['expectedFingerprint']==stamp['fingerprint']==EXPECTED_FINGERPRINT
        assert receipt['stageAssemblyMvid']==stage['assemblyMvid'] and receipt['unity']==ack['unityVersion']
        assert reopen['status']=='source-reconstruction-complete' and reopen['initialSceneClosed'] and reopen['savedSceneReopened']
        assert reopen['sourceReconstructionPerformed'] and not reopen['oldRuntimeCacheUsed'] and reopen['sourceFingerprint']==EXPECTED_FINGERPRINT
        assert reopen['maxBonePositionError']<=.001
        assert diag['reconstructedFromSavedProfile'] and diag['profileId']==q['presentation'] and diag['sourceFingerprint']==EXPECTED_FINGERPRINT
        assert diag['mode']==q['mode'] and diag['sourceKind']=='self-authored-explanation'
        assert diag['meshRendererCount']==diag['directMeshRendererCount']
        if q['mode'] in ACTOR_MODES:assert diag['createdPanelTextures']==2 and reopen['comparedBones']>0
        if q['mode']=='shape-overshoot':assert diag['generatedMeshCount']==2
        text=scene.read_text('utf-8-sig');profile_text=scalar(text,'profileSnapshotJson');frozen=json.loads(profile_text)
        assert scalar(text,'presentationId')==frozen['id']==q['presentation']
        assert scalar(text,'sourceCodeFingerprint')==EXPECTED_FINGERPRINT
        assert hashlib.sha256(profile_text.encode('utf8')).hexdigest()==reopen['profileJsonSha256']
        wanted=byid[q['presentation']]
        for key in ('id','episode','revision','mode'):assert frozen[key]==wanted[key]
        assert abs(frozen['duration']*60-q['frames'])<.001
        for key in ('freezeSeconds','actorYawDegrees'):
            if key in wanted:assert math.isclose(frozen[key],wanted[key],rel_tol=1e-6,abs_tol=1e-6)
        assert len(frozen['phases'])==len(wanted['phases'])
        for actual,expected in zip(frozen['phases'],wanted['phases']):
            for key in ('phase','start','end','motionStart','motionDuration','holdNativeAt','replayReason'):
                if key not in expected:continue
                if isinstance(expected[key],(int,float)):assert math.isclose(actual[key],expected[key],rel_tol=1e-6,abs_tol=1e-6)
                else:assert actual[key]==expected[key]
        movie=folder/'unity.mp4';assert movie.is_file() and movie.stat().st_size>0
        inputs.extend(artifact(p) for p in (*paths.values(),stamp_path))
        # SaveScene creates the real scene identity. Its subsequent File.WriteAllText
        # stamp is runtime bookkeeping, not loaded through AssetDatabase. Do not
        # manufacture an importer/meta or claim a GUID when it was never imported.
        stamp_meta=meta_of(stamp_path)
        if stamp_meta.exists():inputs.append(artifact(stamp_meta))
        seeds.extend((scene,stamp_path))
        for name in receipt['assets']+receipt['animations']:
            p=U/name;assert name.startswith('Assets/') and p.resolve().is_relative_to((U/'Assets').resolve())
            seeds.append(p)
        records.append({'cut':q['id'],'profile':q['presentation'],'mode':q['mode'],'frames':q['frames'],
          'scene':rel(scene),'sha256':sha(scene),'guid':guid_of(scene),'captureReceipt':artifact(paths['render-success.json']),
          'reopenReceipt':artifact(paths['scene-reopen-evidence.json']),'sourceFingerprint':EXPECTED_FINGERPRINT,
          'profileJsonSha256':reopen['profileJsonSha256'],'sourceReconstructionVerified':True,
          'captureStamp':artifact(stamp_path),'captureStampMeta':artifact(stamp_meta) if stamp_meta.exists() else None,
          'captureStampGuid':guid_of(stamp_path) if stamp_meta.exists() else None,
          'captureStampIdentity':'bookkeeping with existing meta/GUID; import execution not inferred' if stamp_meta.exists() else 'unimported file-backed bookkeeping; integrity bound by SHA256'})
    return records,inputs,seeds

def collect_dependencies(seeds,freeze):
    mapping=defaultdict(list)
    roots=[p for p in (U/'Assets',U/'Packages',U/'Library/PackageCache') if p.exists()]
    started=time.monotonic()
    # One bounded ripgrep pass avoids serial Python opens across the large local
    # vendor library. NUL separates filename from text, so drive-letter colons,
    # spaces and non-ASCII paths cannot corrupt the mapping. No stale cache.
    result=subprocess.run(['rg','--no-ignore','--hidden','--glob','*.meta','--no-heading',
      '--with-filename','--null','--crlf','--color','never','--threads','4',
      '^guid: [a-f0-9]{32}$',*[str(p) for p in roots]],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert result.returncode==0,('GUID index failed',result.stderr.decode('utf8','replace')[:2000])
    row_count=0
    for row in result.stdout.splitlines():
        name,separator,line=row.partition(b'\0');assert separator,('Malformed rg GUID row',row[:200])
        match=IDENTITY.fullmatch(line.decode('utf8').rstrip('\r'));assert match
        meta=Path(name.decode('utf8'));assert meta.suffix=='.meta'
        mapping[match[1]].append(meta.with_suffix(''));row_count+=1
    print(f'Indexed {row_count} metadata GUID rows with rg in {time.monotonic()-started:.1f}s',flush=True)
    explicit={C/x for x in SHARED_SOURCE_NAMES}
    seen=set();selected=set();external={};edges=[];builtins=[];unimported_bookkeeping={};external_unresolved=[]
    text_types={'.unity','.prefab','.mat','.asset','.controller','.overridecontroller','.anim','.json'}
    def visit(p,reason):
        p=Path(p);assert p.resolve().is_relative_to(U.resolve()) and p.is_file(),str(p)
        if p in seen:return
        seen.add(p);m=meta_of(p)
        if not m.is_file() and p.is_relative_to(A/'RenderRevisions') and p.name.endswith('.unity.capture-source.json'):
            assert not GUID.search(p.read_text('utf-8-sig')),'Unexpected GUID reference in unimported capture stamp'
            selected.add(p)
            unimported_bookkeeping[rel(p)]={'file':artifact(p),'meta':None,'guid':None,
              'classification':'file-backed-runtime-provenance','reason':'Written with File.WriteAllText after SaveScene; no importer identity exists. SHA256 and final runtime stamp fields were verified; no Unity import performed.'}
            return
        assert m.is_file(),('Missing importer meta',rel(p));identity=guid_of(p)
        path=rel(p)
        vendor='/ThirdParty/YamyamAssetLibrary/' in path
        package='/Library/PackageCache/' in path or '/Packages/' in path
        own=p.is_relative_to(A) or p in explicit
        row={'asset':artifact(p),'meta':artifact(m),'guid':identity,'reason':reason,
             'classification':'licensed-local-only' if vendor else 'installed-package-only' if package else 'owned' if own else 'existing-shared-asset'}
        if own:selected.update((p,m))
        else:external[path]=row
        # Exact installed packages are restored via the frozen lockfile, not vendored.
        if package:return
        texts=[m.read_text('utf-8-sig')]
        if p.suffix in text_types:
            try:texts.append(p.read_text('utf-8-sig'))
            except UnicodeError:pass
        for value in set(GUID.findall('\n'.join(texts))):
            if value==identity:continue
            if value in BUILTINS:builtins.append({'from':path,'guid':value});continue
            targets=list(dict.fromkeys(mapping.get(value,[])))
            matches=[x for x in KNOWN_EXTERNAL_DEBUG_REFERENCES if path==x['path'] and value==x['guid']]
            if not targets and matches:
                assert len(matches)==1;known=matches[0]
                assert sha(p)==known['sha256']
                field_pattern=r'^\s*'+known['field']+r': \{fileID: '+str(known['fileId'])+r', guid: '+known['guid']+r','
                assert re.search(field_pattern,p.read_text('utf-8-sig'),re.M)
                for evidence in LEGACY_RESOURCE_EVIDENCE:check_artifact(evidence)
                external_unresolved.append({**known,'resolved':False,'classification':'pre-existing-deprecated-frozen-external-resource',
                  'disposition':'Retain original unresolved reference and renderer hash. Installed URP Deprecated.cs marks this old ProbeVolumeResources field obsolete since2023.3; current resources are declared in ProbeVolumeDebugResources/ProbeVolumeRuntimeResources. This frozen external field is not an A02 scene-owned object or requested demonstration. The selected native render/reopen evidence does not certify probe features.',
                  'sourceAssetClosureExceptionOnly':True,'unityOrResourceRestored':False})
                continue
            assert len(targets)==1,('Unresolved/duplicate GUID',path,value,[rel(x) for x in targets])
            target=targets[0];edges.append({'from':path,'guid':value,'to':rel(target)});visit(target,'GUID reference')
        if p.suffix=='.png' and p.is_relative_to(A/'Generated/ReferenceImages'):
            provenance=Path(str(p)+'.source.json');r=read(provenance)
            source=Path(r['source']);assert source.resolve().is_relative_to((L/'label-cache').resolve())
            assert r['asset']==p.relative_to(U).as_posix() and r['sha256']==p.stem==sha(p)==sha(source)
            visit(provenance,'own-label provenance')
    for p in seeds:visit(p,'final-runtime dependency')
    for p in explicit:visit(p,'explicit source-backed reconstruction dependency')
    # Source fingerprints also bind dynamic paths and settings which have no YAML edge.
    for item in freeze['files']:
        p=R/item['path']
        if p.is_relative_to(U/'Assets') and p.suffix!='.meta':visit(p,'frozen source input')
    for p in list(selected):
        for parent in p.parents:
            if parent==U/'Assets':break
            m=meta_of(parent)
            if m.exists():selected.add(m)
    images=[p for p in selected if p.suffix=='.png']
    assert images and all(p.is_relative_to(A/'Generated/ReferenceImages') for p in images)
    assert not any('ThirdParty' in p.parts or 'Library' in p.parts for p in selected)
    return selected,external,edges,builtins,unimported_bookkeeping,sorted(external_unresolved,key=lambda x:(x['path'],x['field']))

def collect():
    plan=read(H/'edit-plan.json');queue=plan['nativeCaptureQueue']
    assert len(queue)==23 and len({q['presentation'] for q in queue})==23
    a01=preserved_a01();freeze,stage,ack=verify_freeze()
    scenes,verification,seeds=verify_runtime(queue,stage,ack)
    selected,external,edges,builtins,bookkeeping,external_unresolved=collect_dependencies(seeds,freeze)
    selected.update(R/x['path'] for x in freeze['files'] if (R/x['path']).parent==H)
    now=datetime.now(timezone.utc).isoformat()
    registry=read(R/'shared/git-essential-images.json')['entries'];entries=[]
    for p in sorted(selected):
        if p.suffix!='.png':continue
        item={'path':rel(p),'purpose':'required-scene-asset','project':'animation-exaggeration',
          'reason':'Own Korean/English UI glyph texture actually referenced by an independently editable captured A02 scene; generated from our labels, not a source-video frame.',
          'sha256':sha(p),'reviewedAt':now}
        prior=[x for x in registry if x['path']==item['path']]
        if prior:
            assert len(prior)==1
            for key in ('path','purpose','project','sha256'):assert prior[0][key]==item[key]
            item=prior[0]
        entries.append(item)
    verification.extend(artifact(p) for p in (H/'edit-plan.json',H/'source-fingerprint.json',H/'compiled-ack.json',C/'animation-exaggeration-presentations.json'))
    verification.extend(freeze['files'])
    verification.extend(r[k] for r in external.values() for k in ('asset','meta'))
    if external_unresolved:verification.extend(artifact(R/x['path']) for x in LEGACY_RESOURCE_EVIDENCE)
    verify_unique={x['path']:x for x in verification};verification=[verify_unique[k] for k in sorted(verify_unique)]
    identity={'fingerprint':EXPECTED_FINGERPRINT,'scenes':scenes,'files':[artifact(p) for p in sorted(selected)],'verification':verification,'a01':a01}
    signature=hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()
    if OUTPUT_MANIFEST.exists():
        old=read(OUTPUT_MANIFEST);assert old['inputSignature']==signature,'Preserve prior closure: input changed; use a new reviewed revision.'
        now=old['createdAt']
        for x in entries:
            matching=[e for e in old['essentialImages'] if e['path']==x['path']]
            assert len(matching)==1 and matching[0]['sha256']==x['sha256'];x.update(matching[0])
    manifest={'schemaVersion':1,'episode':'A02','scope':'exact23-final-scenes-and-resolved-source-dependencies','inputSignature':signature,
      'sourceFingerprint':EXPECTED_FINGERPRINT,'createdAt':now,'scenes':scenes,'files':identity['files'],
      'externalDependencies':[external[k] for k in sorted(external)],
      'guidEdges':sorted(edges,key=lambda x:(x['from'],x['guid'],x['to'])),
      'builtinReferences':sorted(builtins,key=lambda x:(x['from'],x['guid'])),
      'unimportedBookkeeping':[bookkeeping[k] for k in sorted(bookkeeping)],
      'selectedSourceUnresolvedGuids':[],'externalEnvironmentUnresolvedGuids':external_unresolved,
      'legacyExternalResourceEvidence':LEGACY_RESOURCE_EVIDENCE if external_unresolved else [],
      'unresolvedGuids':external_unresolved,'externalEnvironmentResourceCompleteness':not external_unresolved,
      'missingMetas':[],'vendorBytesSelectedForCommit':False,'generatedRasterCount':len(entries),
      'essentialImages':entries,'verificationInputs':verification,'a01Preservation':a01,
      'limits':['Runtime receipts and source bytes verified; this collector does not certify final picture quality or human review.',
                'Licensed local originals and installed package bytes remain external; a Git-only checkout does not redistribute the asset library.']}
    manifest_bytes=encoded(manifest)
    helpers=[H/'prepare_scene_sources.py',H/'commit_scene_sources.py']
    owned={rel(p):artifact(p) for p in selected}
    for p in helpers:owned[rel(p)]=artifact(p)
    owned[rel(OUTPUT_MANIFEST)]={'path':rel(OUTPUT_MANIFEST),'sha256':hashlib.sha256(manifest_bytes).hexdigest(),'bytes':len(manifest_bytes)}
    # Existing shared assets with identical HEAD bytes need no staging ownership.
    # They remain fully hash-bound in manifest.files; foreign staged changes stay foreign.
    for name in list(owned):
        if name.startswith('unity/') and not name.startswith(rel(A)+'/'):
            result=subprocess.run(['git','show','HEAD:'+name],cwd=R,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            if result.returncode==0 and hashlib.sha256(result.stdout).hexdigest()==owned[name]['sha256']:del owned[name]
    spec={'schemaVersion':1,'scope':SCOPE,'episode':'A02','expectedFinalSceneCount':23,'sourceFingerprint':EXPECTED_FINGERPRINT,
      'manifest':{'path':rel(OUTPUT_MANIFEST),'sha256':hashlib.sha256(manifest_bytes).hexdigest(),'bytes':len(manifest_bytes)},
      'ownedPaths':sorted([*owned,rel(OUTPUT_SPEC)]),'ownedFiles':[owned[k] for k in sorted(owned)],
      'essentialImages':entries,'verificationInputs':verification,'a01Preservation':a01,
      'runtimeComplete':True,'sourceRedistributionAllowed':False,'externalEnvironmentUnresolvedGuids':external_unresolved,
      'legacyExternalResourceEvidence':LEGACY_RESOURCE_EVIDENCE if external_unresolved else [],
      'sharedOverlayScope':'Only actually referenced A02 label entries and exact .gitignore exceptions; retain every A01 row and all unrelated bytes.'}
    if OUTPUT_SPEC.exists():
        prior=read(OUTPUT_SPEC)
        assert prior['manifest']==spec['manifest'] and prior['sourceFingerprint']==spec['sourceFingerprint']
        assert prior['essentialImages']==spec['essentialImages'] and prior['verificationInputs']==spec['verificationInputs']
        for item in prior['ownedFiles']:
            if item['path']!=rel(OUTPUT_MANIFEST):check_artifact(item)
        # A successful prior commit can make shared sources equal HEAD. Preserve
        # the original exact transaction spec instead of shrinking ownership.
        spec=prior
    return manifest,spec

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    manifest,spec=collect()
    # All checks finish before either A02 output is written. Shared files are never written.
    outputs={OUTPUT_MANIFEST:encoded(manifest),OUTPUT_SPEC:encoded(spec)}
    for p,raw in outputs.items():
        if p.exists():assert p.read_bytes()==raw,('Existing source metadata differs; preserve it',rel(p))
    if not args.check:
        for p,raw in outputs.items():
            if not p.exists():
                with p.open('xb') as f:f.write(raw)
    print(json.dumps({'status':'checked-no-writes' if args.check else 'A02-source-metadata-prepared','scenes':23,
      'sourceFingerprint':EXPECTED_FINGERPRINT,'files':len(manifest['files']),'labelTextures':manifest['generatedRasterCount'],
      'externalDependencies':len(manifest['externalDependencies']),'ownedPaths':len(spec['ownedPaths']),
      'unimportedBookkeeping':len(manifest['unimportedBookkeeping']),
      'selectedSourceUnresolvedGuids':len(manifest['selectedSourceUnresolvedGuids']),
      'externalEnvironmentUnresolvedGuids':manifest['externalEnvironmentUnresolvedGuids'],
      'gitOrSharedMutation':False,'manifest':rel(OUTPUT_MANIFEST),'spec':rel(OUTPUT_SPEC)},ensure_ascii=False))

if __name__=='__main__':main()
