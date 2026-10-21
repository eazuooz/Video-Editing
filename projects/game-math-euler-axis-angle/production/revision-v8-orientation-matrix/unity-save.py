"""Copy only actually baked V8 editable assets; preserve all old projects/files."""
from pathlib import Path
import argparse,hashlib,importlib.util,re,shutil

sp=importlib.util.spec_from_file_location('v8_unity_prepare',Path(__file__).with_name('unity-prepare.py'))
M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
ROOT,H,O,ISO=M.ROOT,M.H,M.O,M.ISO
STAGE=ISO/M.ASSET;DEST=ROOT/'unity/VideoEditing'/M.ASSET

def guid(p):
    m=re.search(r'^guid: ([a-f0-9]{32})$',p.read_text(encoding='utf8'),re.M);assert m,p;return m.group(1)
def color(text):
    m=re.search(r'^    - _BaseColor: (\{[^}]+\})',text,re.M)or re.search(r'^    - _Color: (\{[^}]+\})',text,re.M)
    assert m;d={k:float(v)for k,v in re.findall(r'([rgba]): ([^,}]+)',m.group(1))};assert d['a']==1;return d
def copy(p,dest,data=None):
    if dest!=DEST.with_suffix('.meta'):dest.resolve().relative_to(DEST.resolve())
    value=p.read_bytes()if data is None else data;digest=hashlib.sha256(value).hexdigest()
    assert not dest.exists()or M.sha(dest)==digest,'Existing nonidentical canonical file preserved: '+str(dest)
    if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(value)
    assert M.sha(dest)==digest
    return dict(file=M.rel(dest),sha256=digest,source=M.rel(p),sourceSha256=M.sha(p),bytes=dest.stat().st_size,byteIdentity=data is None)

def run():
    approval=M.authorized();receipt=M.read(O/'native/capture-receipt.json')
    assert receipt['complete']and not receipt['sampleOnly']and receipt['approval']==approval
    saved=M.read(O/'native/scenes-saved.json');assert saved['scriptSceneCount']==13 and saved['totalSceneFiles']==14
    scenes=sorted((STAGE/'Scenes').glob('*.unity'));assert len(scenes)==14
    assert {p.stem for p in scenes}=={'testbed',*[f'm{i:02}'for i in range(1,14)]}
    job=M.read(O/'native/executed-job.json')
    for source,sha in job['immutableInputs'].items():assert M.sha(ROOT/source)==sha,'Changed capture binding: '+source
    for f in sorted((O/'prepared-unity').rglob('*')):
        if f.is_file():assert M.sha(STAGE/f.relative_to(O/'prepared-unity'))==M.sha(f)
    for f in STAGE.rglob('*'):
        if f.is_file():assert f.suffix in {'.cs','.json','.asmdef','.unity','.asset','.mat','.meta','.shader'},f
        if f.is_file()and f.suffix!='.meta':assert Path(str(f)+'.meta').is_file(),f
    shader={}
    for name in ['Lit','Unlit']:
        paths=list((ROOT/'unity/VideoEditing/Library/PackageCache').glob('com.unity.render-pipelines.universal@*/Shaders/'+name+'.shader.meta'))
        paths=[p for p in paths if M.read(p.parents[1]/'package.json')['version']=='17.6.0'];assert len(paths)==1,name
        shader[name]=dict(file=M.rel(paths[0]),sha256=M.sha(paths[0]),guid=guid(paths[0]))
    # Reuse a pure converter, never its historical copy/main entrypoint.
    converter=ROOT/'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/sync-baked-assets.py'
    sp=importlib.util.spec_from_file_location('v8_readonly_material_conversion',converter);c=importlib.util.module_from_spec(sp);sp.loader.exec_module(c)
    c.LIT=shader['Lit']['guid'];c.UNLIT=shader['Unlit']['guid']
    guideShaderGuid=guid(STAGE/'DiagramGuideOverlay.shader.meta')
    files=[];materials=[]
    for p in sorted(STAGE.rglob('*')):
        if not p.is_file():continue
        data=None
        if p.suffix=='.mat':
            old=p.read_text(encoding='utf8');originalColor=color(old)
            assert '_ALPHATEST_ON'not in old and '_ALPHABLEND_ON'not in old
            emission=re.search(r'^    - _EmissionColor: \{([^}]+)\}',old,re.M)
            if emission:assert all(float(v)==0 for k,v in re.findall(r'([rgb]): ([^,}]+)',emission.group(1)))
            if 'guid: '+guideShaderGuid in old:
                materials.append(dict(file=M.rel(DEST/p.relative_to(STAGE)),sourceSha256=M.sha(p),derivedSha256=M.sha(p),baseColor=originalColor,opaque=True,textureDependentAppearance=False,shaderGuid=guideShaderGuid,editorialProjectedGuide=True,depth='ZTestAlways/ZWriteOff',byteIdentity=True))
            else:
                new,used=c.convert_material(old);assert color(new)==originalColor
                assert used in {x['guid']for x in shader.values()}
                data=new.encode('utf8');materials.append(dict(file=M.rel(DEST/p.relative_to(STAGE)),sourceSha256=M.sha(p),derivedSha256=hashlib.sha256(data).hexdigest(),baseColor=originalColor,opaque=True,textureDependentAppearance=False,urpShaderGuid=used))
        files.append(copy(p,DEST/p.relative_to(STAGE),data))
    rootMeta=STAGE.with_suffix('.meta');assert rootMeta.is_file();files.append(copy(rootMeta,DEST.with_suffix('.meta')))
    for p in scenes:assert guid(Path(str(p)+'.meta'))==guid(Path(str(DEST/p.relative_to(STAGE))+'.meta'))
    report=dict(schemaVersion=1,revision='orientation-matrix-v8',approval=approval,complete=True,actualNativeBake=True,scriptSceneCount=13,testbedCount=1,totalSceneFiles=14,
        nativeCaptureReceipt=M.rel(O/'native/capture-receipt.json'),nativeCaptureReceiptSha256=M.sha(O/'native/capture-receipt.json'),sceneSaveReceipt=saved,
        files=files,materialCount=len(materials),materialDerivations=materials,installedCanonicalShaderSources=shader,
        sourceMaterialConversion=dict(file=M.rel(converter),sha256=M.sha(converter),scope='pure opaque converter reused read-only; main() never executed'),
        isolatedCapturePipeline='built-in; actual emitted native pixels and post-camera shader reports reviewed separately',
        canonicalPipeline='URP17.6 serialized shader compatibility with exact authored RGBA retained',canonicalMainRuntimeExecuted=False,
        canonicalMainRuntimeLimit='No main editor runtime, full-scene behaviour or artistic approval inferred from serialized shader/GUID proof. Editable scenes and native captures are distinct evidence.',
        foreignFilesOrProjectSettingsChanged=False,vendorOriginalsChanged=False)
    M.save(H/'unity-saved-scenes.json',report)
    print(dict(scenes=14,materials=len(materials),files=len(files),report=M.rel(H/'unity-saved-scenes.json')))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--copy-verified',action='store_true');a=ap.parse_args()
    if a.copy_verified:run()
    else:print('Prepared only. Actual complete bake/capture receipt required before copying canonical assets.')
