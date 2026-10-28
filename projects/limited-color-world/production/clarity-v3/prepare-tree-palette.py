"""Losslessly expose the actual PSD merged pixels to Unity's PNG decoder.

No vendor/import setting is modified. The generated PNG stays local and can be
rebuilt from the user's owned asset library; only source/provenance enter Git.
"""
from pathlib import Path
import hashlib,json,datetime,re
from PIL import Image

R=Path(__file__).resolve().parents[4]
H=Path(__file__).resolve().parent
U=R/'unity/VideoEditing'
base=U/'Assets/ThirdParty/YamyamAssetLibrary/023-low-poly-stylized-tiny-forest/EmaceArt/Low Poly Tiny Forest'
source=base/'Textures/EA04_LPNP-Artefacts_Colorsheet_v1.psd'
material=base/'Materials/EA04_LPNP-Artefacts_Colorsheet_v1.mat'
prefab=base/'Prefabs/Trees/Bowl/EA04_Trees_Bowl_01a_PRE.prefab'
dest=R/'projects/limited-color-world/production/local/clarity-v3/derived-inputs/tree-source-psd-merged.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guid(p):return re.search(r'^guid: ([a-f0-9]+)$',Path(str(p)+'.meta').read_text('utf-8'),re.M).group(1)
def main():
    assert 'guid: '+guid(material) in prefab.read_text('utf-8'),'Tree prefab does not reference the recorded material'
    assert 'guid: '+guid(source) in material.read_text('utf-8'),'Material does not reference the recorded PSD'
    before={str(p.relative_to(R)):sha(p) for p in [source,Path(str(source)+'.meta'),material,Path(str(material)+'.meta')]}
    image=Image.open(source).convert('RGBA'); original=image.tobytes()
    assert image.size==(256,256),'Unexpected owned palette dimensions'
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():
        assert Image.open(dest).convert('RGBA').tobytes()==original,'Existing derived pixels differ; preserve and inspect'
    else:image.save(dest,format='PNG')
    decoded=Image.open(dest).convert('RGBA')
    assert decoded.size==image.size and decoded.tobytes()==original,'Lossless conversion failed'
    assert before=={str(p.relative_to(R)):sha(p) for p in [source,Path(str(source)+'.meta'),material,Path(str(material)+'.meta')]}
    sibling=source.with_suffix('.png')
    report={'status':'lossless-merged-pixel-match','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'prefabPath':prefab.relative_to(U).as_posix(),'prefabGuid':guid(prefab),'prefabSha256':sha(prefab),'prefabMaterialTextureLinksVerified':True,
        'productId':'023','materialPath':material.relative_to(U).as_posix(),'materialGuid':guid(material),'materialSha256':sha(material),
        'actualSourceTexture':source.relative_to(U).as_posix(),'sourceTextureGuid':guid(source),'sourceTextureSha256':sha(source),
        'sourceImportSettingsSha256':sha(Path(str(source)+'.meta')),'derivedPath':dest.relative_to(R).as_posix(),'derivedSha256':sha(dest),
        'dimensions':list(image.size),'rgbaSha256':hashlib.sha256(original).hexdigest(),'decodedRgbaIdentical':True,
        'siblingPngRejectedBecauseDifferentPixels':Image.open(sibling).convert('RGBA').tobytes()!=original,
        'vendorFilesUnchanged':True,'sourceHashesBeforeAndAfter':before,'creativeChangesInExtraction':False,
        'colorAdjustment':'Only the later stage remaps cyan/blue leaf texels in its private generated palette; source extraction itself is pixel-identical.',
        'generatedPngGitPolicy':'Local rebuild artifact; not registered as a new essential image.'}
    (H/'tree-palette-provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
