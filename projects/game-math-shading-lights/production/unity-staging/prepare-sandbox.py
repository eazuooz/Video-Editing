"""Prepare an isolated M21 Unity project. Never launch Unity or alter the shared project.

Usage: python prepare-sandbox.py --destination LocalUnity-v1
Owned asset payloads remain local and are excluded from Git. The manifest records
the exact source hashes and sandbox-only Read/Write import changes.
"""
from __future__ import annotations
import argparse, hashlib, json, re, shutil
from pathlib import Path
from datetime import datetime, timezone

STAGING=Path(__file__).resolve().parent
REPO=STAGING.parents[3]
SOURCE=REPO/'unity/VideoEditing'
LIBRARY=SOURCE/'Assets/ThirdParty/YamyamAssetLibrary/002-analog-memory-80s-90s-crt-vhs-rooms-godot-unity-blend'
GUID=re.compile(r'guid:\s*([0-9a-f]{32})')
PREFABS=['EAThe80_Lamp_Red_01a_PRE.prefab','EAThe80_Robot_Toy_01a_PRE.prefab']
CODE=sorted(p.name for p in STAGING.glob('LightLab*.cs') if p.name!='LightLabBuildVersion.cs')+sorted(p.name for p in STAGING.glob('*.shader'))

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--destination',required=True);args=ap.parse_args()
    dest=(STAGING/args.destination).resolve()
    if dest.parent!=STAGING or not dest.name.startswith('LocalUnity-'):
        raise ValueError('Destination must be a new LocalUnity-* child of the staging folder')
    if dest.exists():raise FileExistsError('An existing sandbox is preserved; choose a new revision')
    index={}
    for meta in LIBRARY.rglob('*.meta'):
        match=GUID.search(meta.read_text(encoding='utf-8-sig',errors='ignore'))
        if match:index[match.group(1)]=Path(str(meta)[:-5])
    pending=[]
    for name in PREFABS:
        matches=list(LIBRARY.rglob(name))
        if len(matches)!=1:raise ValueError(f'Expected one owned prefab: {name}')
        pending.extend(matches)
    selected=set();unresolved=set()
    while pending:
        src=pending.pop()
        if src in selected:continue
        if not src.is_file():raise FileNotFoundError(src)
        selected.add(src)
        metadata=Path(str(src)+'.meta').read_bytes()
        payload=src.read_bytes() if src.suffix.lower() in {'.prefab','.mat','.asset','.controller','.anim'} else b''
        for guid in GUID.findall((payload+b'\n'+metadata).decode('utf-8',errors='ignore')):
            if guid in index and index[guid].is_file():pending.append(index[guid])
            elif not guid.startswith('0000000000000000'):unresolved.add(guid)
    # Resolve package identities for provenance; package payloads are obtained via UPM.
    package_guids={}
    for package in (SOURCE/'Library/PackageCache').glob('com.unity.render-pipelines.*'):
        for meta in package.rglob('*.meta'):
            text=meta.read_text(encoding='utf-8-sig',errors='ignore');match=GUID.search(text)
            if match and match.group(1) in unresolved:package_guids[match.group(1)]=str(meta.relative_to(SOURCE))
    dest.mkdir(parents=True)
    records=[]
    for src in sorted(selected):
        for source_file in (src,Path(str(src)+'.meta')):
            relative=source_file.relative_to(SOURCE);out=dest/relative;out.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source_file,out);change=None
            if source_file.name.lower().endswith('.fbx.meta'):
                contents=out.read_text(encoding='utf-8-sig');new=re.sub(r'(isReadable:\s*)0\b',r'\g<1>1',contents)
                if new!=contents:out.write_text(new,encoding='utf-8');change='Read/Write enabled only in isolated copy for exact triangle-centre comparison'
            records.append({'path':relative.as_posix(),'sourceSha256':sha(source_file),'sandboxSha256':sha(out),'change':change,'bytes':source_file.stat().st_size})
    root=dest/'Assets/VideoScenes/game-math-shading-lights';(root/'Editor').mkdir(parents=True)
    fingerprint=hashlib.sha256(b''.join(name.encode()+b'\0'+(STAGING/name).read_bytes()+b'\0' for name in CODE)).hexdigest()
    for name in CODE:shutil.copy2(STAGING/name,root/('Editor' if name=='LightLabCapture.cs' else '')/name)
    (root/'LightLabBuildVersion.cs').write_text('namespace Yamyam.GameMath.LightLab { public static class LightLabBuildVersion { public const string Value="'+fingerprint+'"; } }\n',encoding='utf-8')
    (dest/'Packages').mkdir();(dest/'ProjectSettings').mkdir()
    (dest/'Packages/manifest.json').write_text(json.dumps({'dependencies':{'com.unity.render-pipelines.universal':'17.6.0','com.unity.ugui':'2.6.0','com.unity.modules.imageconversion':'1.0.0','com.unity.modules.physics':'1.0.0','com.unity.modules.ui':'1.0.0','com.unity.modules.uielements':'1.0.0'}},indent=2)+'\n',encoding='utf-8')
    shutil.copy2(SOURCE/'ProjectSettings/ProjectVersion.txt',dest/'ProjectSettings/ProjectVersion.txt')
    marker={'preparedUtc':datetime.now(timezone.utc).isoformat(),'sharedProjectUnchanged':True,'neverLaunchFromThisScript':True,'source':str(SOURCE),'project':str(dest),'fingerprint':fingerprint,'editor':'6000.6.0f1','urp':'17.6.0','ownedAssets':records,'packageGuids':package_guids,'unresolvedGuids':sorted(unresolved-set(package_guids)),'vendorMaterialsOverriddenOnInstancesOnly':True,'font':'Local OS Malgun Gothic; no font file copied'}
    (dest/'M21_SANDBOX.json').write_text(json.dumps(marker,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (STAGING/'sandbox-preparation.json').write_text(json.dumps({'status':'prepared-not-launched','sandbox':str(dest),'fingerprint':fingerprint,'fileCount':len(records),'sourceBytes':sum(x['bytes'] for x in records),'manifest':str(dest/'M21_SANDBOX.json'),'unresolvedGuids':marker['unresolvedGuids']},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'sandbox':str(dest),'fingerprint':fingerprint,'files':len(records),'bytes':sum(x['bytes'] for x in records),'unresolvedGuids':marker['unresolvedGuids']},ensure_ascii=False))
if __name__=='__main__':main()
