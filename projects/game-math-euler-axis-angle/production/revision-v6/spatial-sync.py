"""Sync only actually saved V6 isolated scenes; adapt copied materials to URP.

The main project's settings, old scenes and old materials are never changed.
"""
from pathlib import Path
import hashlib,importlib.util,json,shutil,sys
ROOT=Path(__file__).resolve().parents[4]
P=ROOT/'projects/game-math-euler-axis-angle';LOCAL=P/'production/local/revision-v6'
OWN=ROOT/'unity/VideoEditing/Assets/VideoScenes/game-math-euler-axis-angle/revision-v6'
ISO=LOCAL/'unity-capture';SRC=ISO/'Assets/VideoScenes/game-math-euler-axis-angle/revision-v6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy_owned_yaml(source,destination,text=None):
    if text is None:
        try:text=source.read_text(encoding='utf8')
        except UnicodeDecodeError:
            shutil.copy2(source,destination);return
    destination.write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n',encoding='utf8')
def main():
    success=ISO/'m04-v6-scenes-saved.json'
    if not success.exists():raise RuntimeError('No actual V6 Editor scene-save marker; no saved-scene claim made.')
    helper=OWN.parent/'sync-baked-assets.py'
    sys.dont_write_bytecode=True
    spec=importlib.util.spec_from_file_location('m04_previous_material_conversion',helper);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    copied=[]
    for folder in ['Scenes','Shared']:
        folder_meta=Path(str(SRC/folder)+'.meta')
        if folder_meta.exists():copy_owned_yaml(folder_meta,Path(str(OWN/folder)+'.meta'))
        for p in (SRC/folder).rglob('*'):
            if not p.is_file():continue
            if p.suffix not in ['.unity','.asset','.mat','.meta']:continue
            dest=OWN/p.relative_to(SRC);dest.parent.mkdir(parents=True,exist_ok=True)
            if p.suffix=='.mat':copy_owned_yaml(p,dest,module.convert_material(p.read_text(encoding='utf8'))[0])
            else:copy_owned_yaml(p,dest)
            if p.suffix=='.unity':copied.append(dict(file=str(dest.relative_to(ROOT)).replace('\\','/'),sha256=sha(dest)))
    provenance=dict(schemaVersion=1,actualEditorSave=json.loads(success.read_text()),scenes=copied,canonicalMaterialPipeline='URP17.6 using existing installed shader GUIDs; copied V6 material files only',isolatedCapturePipeline='Built-in, unchanged isolated originals',mainProjectSettingsChanged=False,oldSceneAssetsChanged=False,mainUrpDirectPreviewPerformed=False)
    (P/'production/revision-v6/spatial-saved-scenes.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(savedScenes=len(copied),canonicalUrpDirectPreview=False)))
if __name__=='__main__':main()
