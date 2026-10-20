"""Copy only actually saved V7 editable sources/assets to the canonical project.

No Unity launch, editor interaction, ProjectSettings change, cache copy or Git.
Allowed destination ownership: revision-v7-part1/ and that folder's .meta only.
Main URP runtime is explicitly unverified; capture and serialized shader proof
are separate evidence, never a claim that a foreign editor was opened/tested.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re,shutil

H=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('v7_right_save_prepare',H/'right-prepare.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
ROOT,P,O,ISO=M.ROOT,M.P,M.O,M.ISO
REL=Path('Assets/VideoScenes/game-math-euler-axis-angle/revision-v7-part1')
STAGE=ISO/REL;DEST=ROOT/'unity/VideoEditing'/REL
ALLOWED={'.cs','.json','.asmdef','.unity','.asset','.mat','.meta'}
PATCH_REPLACE={}

def guid(meta):
    found=re.search(r'^guid: ([a-f0-9]{32})$',Path(meta).read_text(encoding='utf8'),re.M)
    assert found,meta;return found.group(1)

def copy_verified(src,dst,derived=None):
    # All resolved destinations remain in the exact newly owned asset folder.
    if dst!=DEST.with_suffix('.meta'):dst.resolve().relative_to(DEST.resolve())
    else:assert dst.resolve()==DEST.with_suffix('.meta').resolve()
    expected=M.sha(src)if derived is None else hashlib.sha256(derived).hexdigest()
    if dst.exists()and expected!=M.sha(dst):
        prior=PATCH_REPLACE.get(M.rel(dst));assert prior and prior['sha256']==M.sha(dst),'Existing nonidentical canonical asset preserved: '+str(dst)
        patch=M.read(O/'sail31-patch.json');assert patch['status']=='captured-and-merged'
        archive=ROOT/patch['preservedRecordDirectory']/'canonical'/dst.relative_to(DEST)
        archive.parent.mkdir(parents=True,exist_ok=True);assert not archive.exists();shutil.copy2(dst,archive)
        if derived is None:shutil.copy2(src,dst)
        else:dst.write_bytes(derived)
    elif dst.exists():assert expected==M.sha(dst),'Existing nonidentical canonical asset preserved: '+str(dst)
    else:
        dst.parent.mkdir(parents=True,exist_ok=True)
        if derived is None:shutil.copy2(src,dst)
        else:dst.write_bytes(derived)
    assert expected==M.sha(dst)
    return dict(file=M.rel(dst),sha256=M.sha(dst),bytes=dst.stat().st_size,sourceSha256=M.sha(src),byteIdentity=derived is None)

def material_color(text,name):
    match=re.search(r'^    - '+re.escape(name)+r': \{([^}]+)\}',text,re.M)
    return {k:float(v)for k,v in re.findall(r'([rgba]): ([^,}]+)',match.group(1))}if match else None

def audit_opaque(text):
    color=material_color(text,'_BaseColor')or material_color(text,'_Color');assert color
    emission=material_color(text,'_EmissionColor')or dict(r=0,g=0,b=0,a=0)
    # These owner-authored explanatory solids have no texture/alpha/emission
    # effects. Refuse an unexpected special material instead of losing a feature.
    assert abs(color['a']-1)<1e-6,'Unexpected transparency requires explicit adaptation.'
    assert all(abs(emission[k])<1e-6 for k in ['r','g','b']),'Unexpected emission requires explicit adaptation.'
    assert '_ALPHATEST_ON'not in text and '_ALPHABLEND_ON'not in text
    for mode in ['_Mode','_Surface']:
        value=re.search(r'^    - '+mode+r': ([^\n]+)',text,re.M)
        if value:assert float(value.group(1))==0
    return dict(baseColor=color,alpha=1,opaque=True,emissionRGBZero=True,textureDependentAppearance=False)

def run():
    approval=M.authorized();capture=M.read(O/'spatial-native/capture-receipt.json');assert not capture['sampleOnly']
    generated=M.read(M.PLAN)['generatedUnity'];receipt=M.read(ISO/'m04-v7-part1-scenes-saved.json')
    assert receipt['sceneCount']==25 and receipt['testbedSaved']and receipt['totalSceneFiles']==26
    assert receipt['editor']=='6000.6.0f1'and capture['success']['editor']==receipt['editor']
    assert capture['success']['pipeline']=='isolated built-in'
    assert capture['authorization']==approval
    for key in ['generatedRuntime','generatedBridge','catalog']:
        source=ROOT/generated[key];assert M.sha(source)==generated[key+'Sha256']
        stage=STAGE/source.relative_to(O/'prepared-unity');assert stage.exists()and M.sha(stage)==M.sha(source)
    scenes=sorted((STAGE/'Scenes').glob('*.unity'));assert len(scenes)==26
    catalog=M.read(STAGE/'spatial-shots.json');expected={s['sceneId']for s in catalog['shots']}|{'testbed'}
    assert {s.stem for s in scenes}==expected
    # All generated script/asset GUIDs must be present before copying a scene.
    for f in STAGE.rglob('*'):
        if f.is_file():assert f.suffix.lower()in ALLOWED,'Unexpected media/cache in saved asset scope: '+str(f)
        if f.is_file()and f.suffix!='.meta':assert Path(str(f)+'.meta').exists(),f
    shaderMeta={}
    for name in ['Lit','Unlit']:
        canonical=list((ROOT/'unity/VideoEditing/Library/PackageCache').glob('com.unity.render-pipelines.universal@*/Shaders/'+name+'.shader.meta'))
        canonical=[f for f in canonical if M.read(f.parents[1]/'package.json')['version']=='17.6.0']
        assert len(canonical)==1,(name,'canonical URP shader must exist in actual installed package')
        shaderMeta[name]={'file':M.rel(canonical[0]),'sha256':M.sha(canonical[0]),'guid':guid(canonical[0])}
    converter=DEST.parent/'sync-baked-assets.py'
    spec=importlib.util.spec_from_file_location('v7_reused_owned_material_converter',converter);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    helper.LIT=shaderMeta['Lit']['guid'];helper.UNLIT=shaderMeta['Unlit']['guid']
    materialProof=[];converted={}
    for f in sorted((STAGE/'Shared').glob('*.mat')):
        text=f.read_text(encoding='utf8');audit=audit_opaque(text);updated,shader=helper.convert_material(text)
        assert audit_opaque(updated)['baseColor']==audit['baseColor'],'Authored RGBA must survive pipeline adaptation.'
        converted[f]=updated.encode('utf8');dest=DEST/f.relative_to(STAGE)
        materialProof.append({'source':M.rel(f),'sourceSha256':M.sha(f),'sourceShaderDeclaration':re.search(r'm_Shader: ([^\n]+)',text).group(1),
            'file':M.rel(dest),'expectedCanonicalSha256':hashlib.sha256(converted[f]).hexdigest(),'shaderGuid':shader,
            'kind':next(k for k,v in shaderMeta.items()if v['guid']==shader),'appearanceAudit':audit,
            'derivedProperties':'Actual installed URP shader GUID; same RGBA; opaque blend/ZWrite; explicit double-sided Cull0; smoothness retained. Existing imported/vendor materials untouched.'})
    assert materialProof
    files=[]
    # The root folder GUID and every subasset GUID are copied unchanged. Main
    # project imports may observe new files, but no main editor API is invoked.
    files.append(copy_verified(STAGE.with_suffix('.meta'),DEST.with_suffix('.meta')))
    for f in sorted(STAGE.rglob('*')):
        if f.is_file():files.append(copy_verified(f,DEST/f.relative_to(STAGE),converted.get(f)))
    for row in materialProof:
        dest=ROOT/row['file'];text=dest.read_text(encoding='utf8')
        assert re.search(r'm_Shader: \{[^}]*guid: '+row['shaderGuid'],text)
        assert audit_opaque(text)['baseColor']==row['appearanceAudit']['baseColor']
        row['observedCanonicalSha256']=M.sha(dest);row['metaGuidPreserved']=guid(Path(str(dest)+'.meta'))==guid(Path(str(ROOT/row['source'])+'.meta'))
        assert row['metaGuidPreserved']
    sceneRows=[{'scene':M.rel(DEST/'Scenes'/f.name),'sha256':M.sha(f),'metaSha256':M.sha(Path(str(f)+'.meta')),'guid':guid(Path(str(f)+'.meta'))}for f in scenes]
    result={'schemaVersion':1,'part':1,'status':'actual25 script/motion scenes plus shared testbed saved, GUID/hash preserved, URP shader references verified; main runtime not executed',
        'authorization':approval,'captureReceipt':M.rel(O/'spatial-native/capture-receipt.json'),'captureReceiptSha256':M.sha(O/'spatial-native/capture-receipt.json'),
        'savedReceipt':M.rel(ISO/'m04-v7-part1-scenes-saved.json'),'savedReceiptSha256':M.sha(ISO/'m04-v7-part1-scenes-saved.json'),
        'editor':'6000.6.0f1','canonicalRenderPipelinePackage':'URP17.6.0','nativeCapturePipeline':'isolated built-in / linear / 2xMSAA /1920x1080/60',
        'runtimeShaderRouting':'UsesSrp checks current/default/quality pipeline and chooses URP Lit/Unlit vs Standard/UnlitColor; existing controlled geometry/math retained',
        'shaderPackages':shaderMeta,'savedMaterialProof':materialProof,'scenes':sceneRows,'files':files,
        'materialConverter':{'source':M.rel(converter),'sha256':M.sha(converter),'reuse':'existing V6/V2 pure owned-material conversion; main current shader GUIDs supplied; capture originals unchanged'},
        'scriptSceneCount':21,'supplementaryMotionSceneCount':4,'sharedTestbedCount':1,'mainEditorOpenedOrControlled':False,
        'newOwnedAssetFilesWrittenOnly':True,'existingMainAssetsModified':False,
        'mainSettingsChanged':False,'foreignProcessesChanged':False,'mainURPRuntimeExecuted':False,'vendorAssetsChanged':False,
        'nativePixelReview':'recorded separately in right preview/motion QA; shader serialization proof is not a main runtime test'}
    M.save(H/'right-saved-scenes.json',result)
    print(json.dumps({'savedScenes':26,'files':len(files),'canonical':M.rel(DEST),'proof':M.rel(H/'right-saved-scenes.json')}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--copy-verified',action='store_true');ap.add_argument('--replace-sail-patch',action='store_true');a=ap.parse_args()
    if a.replace_sail_patch:
        proof=M.read(H/'right-saved-scenes.json')
        allowed=['Editor/EulerV7RightCapture.cs','spatial-shots.json','Scenes/v7-a02-sail-raise.unity']
        PATCH_REPLACE.update({r['file']:r for r in proof['files']if r['file']in {M.rel(DEST/part)for part in allowed}})
        assert len(PATCH_REPLACE)==3
    if a.copy_verified:run()
    else:ap.print_help()
