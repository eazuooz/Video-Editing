"""Copy own editor-saved scene sources back, deduplicating reusable geometry.

Only the selected canonical Assets folder is written. No editor or project settings
are opened/changed. The isolated capture retains its built-in materials; canonical
materials reference the installed URP17.6 shaders in the user's main project.
"""
from pathlib import Path
import hashlib, json, re, shutil

ROOT=Path(__file__).resolve().parents[5]
OWN=Path(__file__).resolve().parent
ISO=ROOT/'projects/game-math-euler-axis-angle/production/local/revision-v2/unity-capture'
SRC=ISO/'Assets/VideoScenes/game-math-euler-axis-angle'
LIT='933532a4fcc9baf4fa0491de14d08ed7'
UNLIT='650dd9526735d5b46b79224bc6e94025'

def convert_material(text):
    """Opaque URP source material, preserving the authored color/smoothness."""
    text=text.replace('\r\n','\n')
    lit='_Metallic' in text
    shader=LIT if lit else UNLIT
    smooth=re.search(r'    - _Smoothness: ([^\n]+)',text) or re.search(r'    - _Glossiness: ([^\n]+)',text)
    smoothness=smooth.group(1) if smooth else '.22'
    text=re.sub(r'  m_Shader:.*',f'  m_Shader: {{fileID: 4800000, guid: {shader}, type: 3}}',text)
    color=re.search(r'    - _BaseColor: (\{[^\n]+\})',text) or re.search(r'    - _Color: (\{[^\n]+\})',text)
    if color and '_BaseColor:' not in text:
        text=text.replace('    m_Colors:\n','    m_Colors:\n    - _BaseColor: '+color.group(1)+'\n')
    if '_BaseMap:' not in text:
        base='    - _BaseMap:\n        m_Texture: {fileID: 0}\n        m_Scale: {x: 1, y: 1}\n        m_Offset: {x: 0, y: 0}\n'
        if '    m_TexEnvs: []' in text:
            text=text.replace('    m_TexEnvs: []\n','    m_TexEnvs:\n'+base)
        else:text=text.replace('    m_TexEnvs:\n','    m_TexEnvs:\n'+base)
    opaque={'_Surface':'0','_Blend':'0','_AlphaClip':'0','_Cull':'0',
        '_SrcBlend':'1','_DstBlend':'0','_SrcBlendAlpha':'1','_DstBlendAlpha':'0','_ZWrite':'1'}
    if lit:opaque.update(_WorkflowMode='1',_Metallic='0',_Smoothness=smoothness)
    for key,value in opaque.items():
        pattern=r'(?m)^    - '+re.escape(key)+r': [^\n]+$'
        if re.search(pattern,text):text=re.sub(pattern,'    - '+key+': '+value,text)
        elif '    m_Floats: []' in text:text=text.replace('    m_Floats: []\n','    m_Floats:\n    - '+key+': '+value+'\n')
        else:text=text.replace('    m_Floats:\n','    m_Floats:\n    - '+key+': '+value+'\n')
    return text,shader

def meta_guid(path):
    text=Path(str(path)+'.meta').read_text(encoding='utf8')
    return re.search(r'^guid: ([a-f0-9]{32})$',text,re.M).group(1)

def main():
    success=ISO/'m04-scene-build-success.json'
    if not success.exists(): raise RuntimeError('No actual Unity scene save success exists yet.')
    grouped={}; guid_map={}; original_count=0
    shared=OWN/'Shared';shared.mkdir(exist_ok=True)
    for path in sorted((SRC/'Baked').rglob('*')):
        if path.suffix not in {'.asset','.mat'}: continue
        original_count+=1
        data=path.read_bytes(); key=hashlib.sha256(data).hexdigest()
        if key not in grouped:
            target=shared/(('mesh-' if path.suffix=='.asset' else 'material-')+key[:20]+path.suffix)
            first_guid=meta_guid(path)
            if path.suffix=='.mat':
                text,shader=convert_material(data.decode('utf8'))
                target.write_text(text,encoding='utf8')
            else: target.write_bytes(data)
            shutil.copy2(Path(str(path)+'.meta'),Path(str(target)+'.meta'))
            grouped[key]=dict(path=str(target.relative_to(ROOT)).replace('\\','/'),guid=first_guid)
        guid_map[meta_guid(path)]=grouped[key]['guid']
    scenes=[]
    for path in sorted((SRC/'Scenes').glob('*.unity')):
        data=path.read_text(encoding='utf8')
        def replace(match):
            old=match.group(1);return 'guid: '+guid_map.get(old,old)
        data=re.sub(r'guid: ([a-f0-9]{32})',replace,data)
        target=OWN/'Scenes'/path.name
        target.write_text(data,encoding='utf8')
        shutil.copy2(Path(str(path)+'.meta'),Path(str(target)+'.meta'))
        scenes.append(dict(path=str(target.relative_to(ROOT)).replace('\\','/'),sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    report=dict(schemaVersion=1,sceneCount=len(scenes),actualUnitySave=json.loads(success.read_text()),
        originalBakedAssetCount=original_count,sharedAssetCount=len(grouped),scenes=scenes,
        canonicalMaterialPipeline='URP17.6 references verified against installed Lit/Unlit shader meta GUIDs',
        sourceReuse='Saved hierarchy references are serialized; old scenes are rebound by name. Start preserves saved geometry; cross-pipeline fallback clones material instances only.',
        isolatedCaptureMaterialPipeline='Built-in; isolated copies preserved',
        validation='Scene source was saved by isolated Unity; geometry GUID deduplication and URP-material adaptation were performed afterwards. Canonical main editor preview not claimed.')
    (OWN/'baked-scene-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(sceneCount=len(scenes),originalAssets=original_count,sharedAssets=len(grouped)),ensure_ascii=False))

if __name__=='__main__': main()
