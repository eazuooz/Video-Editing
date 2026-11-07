"""Read native Unreal assets in an isolated worker; never modify vendor content."""
from pathlib import Path
from collections import Counter
import json, traceback
import unreal as u

HERE = Path(__file__).resolve().parent
LOCAL = HERE.parent / 'local/real-clips-v2'
project = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir())).resolve()
assert project == (LOCAL / 'unreal-worker').resolve()
roots = json.loads((LOCAL / 'scan-roots.json').read_text('utf-8'))
registry = u.AssetRegistryHelpers.get_asset_registry()
registry.scan_paths_synchronous(['/Game'], force_rescan=True)
rows = []
errors = []
try:
    for root in roots:
        for data in registry.get_assets_by_path('/Game/' + root, recursive=True):
            cls = str(data.asset_class_path.asset_name)
            if cls not in ('AnimSequence', 'SkeletalMesh', 'Skeleton', 'AnimMontage', 'PoseAsset'):
                continue
            row = {'path': str(data.package_name), 'class': cls, 'root': root}
            if cls in ('AnimSequence', 'SkeletalMesh') and root != 'Characters':
                try:
                    obj = data.get_asset()
                    row['skeleton'] = obj.get_editor_property('skeleton').get_path_name()
                    if cls == 'AnimSequence':
                        row['seconds'] = obj.get_play_length()
                        row['frames'] = u.AnimationLibrary.get_num_frames(obj)
                    else:
                        row['materials'] = [str(m.material_slot_name) for m in obj.materials]
                except Exception as exc:
                    row['inspectionError'] = str(exc)
                    errors.append({'path': row['path'], 'error': str(exc)})
            rows.append(row)
    result = {'engine': u.SystemLibrary.get_engine_version(), 'roots': roots,
              'assets': rows, 'counts': dict(Counter(x['class'] for x in rows)),
              'errors': errors, 'vendorAssetsModified': False}
    (LOCAL / 'asset-registry.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf-8')
    u.log('REAL_CLIP_INVENTORY_OK ' + str(result['counts']))
except Exception:
    (LOCAL / 'inventory-error.txt').write_text(traceback.format_exc(), 'utf-8')
    raise
