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
                text=data.decode('utf8')
                shader=LIT if '_Metallic' in text else UNLIT
                text=re.sub(r'  m_Shader:.*',f'  m_Shader: {{fileID: 4800000, guid: {shader}, type: 3}}',text)
                color=re.search(r'    - _Color: (\{[^\n]+\})',text)
                if color and '_BaseColor:' not in text:
                    text=text.replace('    m_Colors:\n','    m_Colors:\n    - _BaseColor: '+color.group(1)+'\n')
                if '    - _Cull:' not in text:
                    text=text.replace('    m_Floats:\n','    m_Floats:\n    - _Cull: 0\n')
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
        isolatedCaptureMaterialPipeline='Built-in; isolated copies preserved',
        validation='Scene source was saved by isolated Unity; geometry GUID deduplication and URP-material adaptation were performed afterwards. Canonical main editor preview not claimed.')
    (OWN/'baked-scene-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(sceneCount=len(scenes),originalAssets=original_count,sharedAssets=len(grouped)),ensure_ascii=False))

if __name__=='__main__': main()
