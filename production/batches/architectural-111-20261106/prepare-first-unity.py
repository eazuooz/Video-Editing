"""Stage only our first experiment and three licensed asset inputs. Does not launch Unity."""
from pathlib import Path
import hashlib,json,shutil,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106')
DEST=MEDIA/'unity-capture'
SOURCE=ROOT/'unity/VideoEditing/Assets/ThirdParty/KayKitAdventurers'

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    provenance=json.loads((SOURCE/'provenance.json').read_text(encoding='utf8'))
    records=[]
    for spec in provenance['files']:
        path=SOURCE/spec['path'];assert sha(path)==spec['sha256']
        for original in [path,Path(str(path)+'.meta')]:
            if original.exists():
                target=DEST/'Assets/ThirdParty/KayKitAdventurers'/original.name
                target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,target)
                records.append(dict(source=original.relative_to(ROOT).as_posix(),target=target.relative_to(DEST).as_posix(),sha256=sha(target)))
    source=HERE/'unity-source';target=DEST/'Assets/VideoScenes/architectural-111-20261106'
    shutil.copytree(source,target,dirs_exist_ok=True)
    for path in source.rglob('*'):
        if path.is_file():records.append(dict(source=path.relative_to(ROOT).as_posix(),target=(target/path.relative_to(source)).relative_to(DEST).as_posix(),sha256=sha(path)))
    packages=DEST/'Packages';packages.mkdir(exist_ok=True)
    (packages/'manifest.json').write_text(json.dumps({'dependencies':{'com.unity.modules.physics':'1.0.0','com.unity.modules.animation':'1.0.0','com.unity.modules.imgui':'1.0.0','com.unity.modules.jsonserialize':'1.0.0','com.unity.modules.imageconversion':'1.0.0'}},indent=2)+'\n')
    settings=DEST/'ProjectSettings';settings.mkdir(exist_ok=True)
    (settings/'ProjectVersion.txt').write_text('m_EditorVersion: 6000.6.0f1\n')
    evidence=dict(project=DEST.as_posix(),editorVersion='6000.6.0f1',renderPipeline='Built-in Standard; original testbed',
        intendedScenes=['Assets/VideoScenes/architectural-111-20261106/03-02/02-narrow.unity','Assets/VideoScenes/architectural-111-20261106/03-02/04-wide.unity'],
        actualSceneFilesSaved=False,sourceStageComplete=True,unityLaunched=False,artifactKind='implementation-prepared-not-captured',
        claim='Change only tunnel width; same cart, collision capsule, speed and cameras. Dimensions are original illustrative values, not TF2 measurements.',
        licence=provenance,files=records)
    (HERE/'first-unity-preparation.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(stagedFiles=len(records),unityLaunched=False,source=DEST.as_posix())))

if __name__=='__main__':main()
