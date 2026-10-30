"""Collect the exact saved A01 scene dependencies; no Git or media mutation."""
from pathlib import Path
import hashlib, json, re
from datetime import datetime, timezone

R=Path(__file__).resolve().parents[3]
H=R/'projects/animation-assigning/production/grid-v1'
U=R/'unity/VideoEditing'
SERIES=U/'Assets/VideoScenes/animation-series-v1'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(R).as_posix()
def read(p): return json.loads(p.read_text('utf-8-sig'))
def save(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf8')

def main():
    plan=read(H/'edit-plan.json'); queue=plan['nativeCaptureQueue']
    assert len(queue)==27 and not plan['pendingBeforeRender']['nativeCaptures']
    mapping={}
    for p in SERIES.rglob('*.meta'):
        m=re.search(r'^guid: ([a-f0-9]{32})$',p.read_text('utf8'),re.M)
        if m: mapping[m[1]]=p.with_suffix('')
    selected=set(); external=set(); scene_records=[]
    def visit(p):
        assert p.is_file(),p
        if p in selected:return
        selected.add(p)
        if p.suffix not in {'.png','.jpg'}:
            for guid in re.findall(r'guid: ([a-f0-9]{32})',p.read_text('utf8')):
                target=mapping.get(guid)
                if target and target.is_file():visit(target)
                elif guid!='00000000000000000000000000000000':external.add(guid)
    for q in queue:
        receipt=H.parent/'local/grid-v1/render'/q['revision']/q['mode']/'render-success.json'
        x=read(receipt);assert x['status']=='complete' and x['completed']==q['frames']
        scene=U/x['scene'];visit(scene)
        stamp=Path(str(scene)+'.capture-source.json');visit(stamp)
        scene_records.append({'cut':q['id'],'scene':rel(scene),'sha256':sha(scene),'captureReceipt':rel(receipt),'sourceFingerprint':x['compiledSourceFingerprint']})
    # Include importer identities and every necessary folder GUID, without other revisions.
    for p in list(selected):
        meta=Path(str(p)+'.meta')
        if meta.exists():selected.add(meta)
        for parent in p.parents:
            if parent==U/'Assets':break
            meta=Path(str(parent)+'.meta')
            if meta.exists():selected.add(meta)
    images=[p for p in sorted(selected) if p.suffix=='.png']
    assert images and all(p.is_relative_to(SERIES/'Generated/ReferenceImages') for p in images)
    now=datetime.now(timezone.utc).isoformat()
    entries=[{'path':rel(p),'purpose':'required-scene-asset','project':'animation-assigning',
      'reason':'Original Korean/English UI glyph texture referenced by an independently editable captured A01 Unity scene; generated from our own labels, not a source-video frame.',
      'sha256':sha(p),'reviewedAt':now} for p in images]
    manifest={'episode':'A01','scope':'exact27captured-scenes-and-owned-dependencies','scenes':scene_records,
      'files':[{'path':rel(p),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(selected)],
      'externalGuids':sorted(external),'externalGuidMeaning':'Existing Unity/URP/UI and licensed imported rig dependencies remain in their original shared assets; no duplication.',
      'generatedRasterCount':len(images),'createdAt':now}
    save(H/'saved-scene-source-manifest.json',manifest)
    spec={'scope':'animation-scene-source-assets','ownedPaths':[rel(p) for p in sorted(selected)]+[rel(H/'saved-scene-source-manifest.json')],
      'essentialImages':entries}
    save(Path(__file__).parent/'scene-source-commit-plan.json',spec)
    print(json.dumps({'scenes':len(scene_records),'files':len(selected),'labelTextures':len(images),'externalGuids':len(external)}))

if __name__=='__main__':main()
