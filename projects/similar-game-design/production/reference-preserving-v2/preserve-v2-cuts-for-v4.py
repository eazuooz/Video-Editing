"""Root-run preservation helper. Default is read-only; --apply copies backups.

Preserves eight old cut MP4s/receipts (plus existing marks ASS) under the exact
C-backed edit/previous-cuts-v2 directory. The pixel-identical cut028 MP4 stays
put; its OLD receipt is also preserved before a documented timeline-only rebind.
No source, master, PCM, caption, render, encode, ASR or Git operation is started.
"""
from pathlib import Path
import argparse
import copy
import json
import shutil
import audio_pipeline as audio
import video_pipeline as video

HERE=Path(__file__).resolve().parent


def pixel_contract(cut):
    value=copy.deepcopy(cut)
    value.pop('startFrame',None);value.pop('endFrame',None)
    guide=value.get('editorialGuideAss')
    if guide:
        guide.pop('cutBindingSha256',None)
        for event in guide['events']:
            event.pop('globalStart',None);event.pop('globalEnd',None)
    return value


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply',action='store_true',help='Copy/hash-check selected old files and rebind World receipt only after backup')
    args=parser.parse_args()
    base_path=HERE/'edit-plan-final.json';v4_path=HERE/'edit-plan-final-v4.json'
    base=audio.read(base_path);new=audio.read(v4_path)
    if new['visualPatchV4']['basePlan']['sha256']!=audio.sha(base_path):
        raise ValueError('Base plan changed after v4 preparation')
    assert audio.audio_plan_contract(base)==audio.audio_plan_contract(new)
    old={c['id']:c for c in base['cuts']};current={c['id']:c for c in new['cuts']}
    ids=new['visualPatchV4']['pixelChangedBodyCutIds']
    if len(ids)!=8 or new['outputStem']!='similar-game-design-v4':
        raise ValueError('Expected exact root-selected eight-cut v4 scope')
    out=audio.current_local_output(new['outputDir'])
    archive=audio.current_local_output(out/'previous-cuts-v2')
    manifest_file=archive/'preservation.json'
    existing=audio.read(manifest_file) if manifest_file.exists() else None
    files=[]
    if existing:
        if existing['basePlanSha256']!=audio.sha(base_path) or existing['v4PlanSha256']!=audio.sha(v4_path):
            raise ValueError('Preserve a different existing backup; no overwrite')
        for item in existing['files']:
            if audio.sha(archive/item['name'])!=item['sha256']:
                raise ValueError('Existing backup hash changed')
        files=existing['files']
    else:
        for cid in ids:
            receipt=audio.read(out/(cid+'-render.json'))
            file=out/(cid+'.mp4')
            if receipt['signature']['cut']!=old[cid] or receipt['outputSha256']!=audio.sha(file):
                raise ValueError('Current cut is no longer the original v2 rendered definition: '+cid)
            for name in [cid+'.mp4',cid+'-render.json',cid+'-marks.ass']:
                source=out/name
                if source.exists():
                    files.append({'name':name,'sha256':audio.sha(source),'bytes':source.stat().st_size})
        files.append({'name':'cut028-render.json','sha256':audio.sha(out/'cut028-render.json'),
                      'bytes':(out/'cut028-render.json').stat().st_size})
    if pixel_contract(old['cut028'])!=pixel_contract(current['cut028']):
        raise ValueError('World cut has a pixel-affecting change; timeline-only receipt reuse forbidden')
    world_file=out/'cut028.mp4';world_receipt_file=out/'cut028-render.json'
    world_receipt=audio.read(world_receipt_file)
    if world_receipt['outputSha256']!=audio.sha(world_file):
        raise ValueError('World source cut file changed')
    if world_receipt['signature']['cut'] not in [old['cut028'],current['cut028']]:
        raise ValueError('Unexpected World receipt definition')
    if args.apply:
        archive.mkdir(parents=True,exist_ok=True)
        if not existing:
            for item in files:
                source,target=out/item['name'],archive/item['name']
                if target.exists():
                    if audio.sha(target)!=item['sha256']:
                        raise ValueError('Refuse to overwrite an incompatible backup: '+item['name'])
                else:
                    with source.open('rb') as src,target.open('xb') as dst:
                        shutil.copyfileobj(src,dst,4*1024*1024)
                    shutil.copystat(source,target)
                if audio.sha(target)!=item['sha256']:
                    raise ValueError('Backup copy hash mismatch')
            audio.save(manifest_file,{'basePlanSha256':audio.sha(base_path),'v4PlanSha256':audio.sha(v4_path),
                'files':files,'pixelChangedCutIds':ids,'worldTimelineOnlyReceiptPreserved':True,
                'sourceFilesMovedOrDeleted':False})
        if world_receipt['signature']['cut']!=current['cut028']:
            original_receipt_sha=audio.sha(world_receipt_file)
            _ass,guide=video.editorial_guide_ass(current['cut028'],new)
            world_receipt['signature']['cut']=copy.deepcopy(current['cut028'])
            world_receipt['signature']['editorialGuideAss']=guide
            world_receipt['timelineOnlyRebind']={'originalReceiptSha256':original_receipt_sha,
                'preservedAt':audio.relative(archive/'cut028-render.json'),
                'oldOutputFrames':[old['cut028']['startFrame'],old['cut028']['endFrame']],
                'newOutputFrames':[current['cut028']['startFrame'],current['cut028']['endFrame']],
                'sourceSeconds':[46,49.2],'frames':192,'pixelContractIdentical':True,
                'outputMp4Sha256':audio.sha(world_file),'rerendered':False,
                'reason':'Only output placement/guide absolute-clock binding changed; native pixels, relative guide ASS, source, marks and viewport are identical.'}
            audio.save(world_receipt_file,world_receipt)
    print(json.dumps({'mode':'applied-preservation-and-timeline-rebind' if args.apply else 'read-only-preview-no-copy',
        'archive':audio.relative(archive),'files':len(files),'backupBytes':sum(f['bytes'] for f in files),
        'selectedPixelCutIds':ids,'worldCutMp4ReusedWithoutCopyOrRender':True,
        'baseMasterFilesPreserved':True,'noRenderAsrOrAudioJob':True},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
