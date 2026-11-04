"""Preserve verified text-only scene sources for the seven completed native topics.

Default is read-only. --copy creates immutable, receipt-versioned project folders;
it never stages Git, touches Unity's active project, or copies binary assets.
"""
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('native_export', HERE / 'export-native-editable.py')
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)


def preserve(copy=False):
    plans = []
    # Validate every entry first. A missing export must not be called complete.
    for slug in export.NATIVE:
        receipt = export.MEDIA / slug / 'local/unity-capture/native-receipt.json'
        receipt_sha = export.sha(receipt)
        base = export.MEDIA / 'editable-native' / slug / receipt_sha
        manifest_path = base / 'editable-export.json'
        manifest = export.read(manifest_path)
        if manifest.get('slug') != slug or manifest.get('receiptSha256') != receipt_sha or manifest.get('success') is not True:
            raise ValueError('Export/receipt mismatch: ' + slug)
        projection = base / 'git-text-projection'
        if Path(manifest['gitTextProjection']).resolve() != projection.resolve():
            raise ValueError('Unexpected projection path')
        destination = export.ROOT / 'projects' / slug / 'native-editable' / receipt_sha
        files = []
        seen = set()
        for item in manifest['gitTextAllowlist']:
            logical = export.relative(item['path'])
            if logical in seen:
                raise ValueError('Duplicate projected file')
            seen.add(logical)
            source = export.inside(projection / logical, projection)
            export.no_links(source, projection)
            export.verify(source, item['sha256'])
            if source.stat().st_size != item['bytes'] or not export.eligible_text(logical, source.read_bytes()):
                raise ValueError('Non-text or changed projection: ' + logical)
            target = export.inside(destination / logical, destination)
            if target.exists():
                export.verify(target, item['sha256'])
            files.append((source, target, item['sha256']))
        scene_names = {item['scene'] for item in manifest['sceneBindings']}
        if not scene_names or not scene_names.issubset(seen):
            raise ValueError('An editable captured scene is missing')
        for item in manifest['preservedTimingFiles']:
            source = export.inside(item['path'], base)
            export.verify(source, item['sha256'])
            json.loads(source.read_text(encoding='utf-8-sig'))
            target = destination / 'evidence' / ('visual-timing-' + item['role'] + '.json')
            if item['role'] not in {'captured', 'current'}:
                raise ValueError('Unlisted timing role')
            files.append((source, target, item['sha256']))
        record = {
            'slug': slug, 'receiptSha256': receipt_sha,
            'sourceTreeSha256': manifest['sourceTreeSha256'],
            'exportManifest': str(manifest_path), 'exportManifestSha256': export.sha(manifest_path),
            'editableLocalProject': manifest['editableProject'],
            'trackedTextRoot': str(destination), 'sceneBindings': manifest['sceneBindings'],
            'textFiles': [{'path': str(t.relative_to(destination)).replace('\\', '/'), 'sha256': h} for _, t, h in files],
            'requiredLocalOnlyDependencies': manifest['localOnlyFiles'],
            'externalPackageAndEngineReferences': manifest['externalPackageAndEngineReferences'],
            'unresolvedSettingsReferences': manifest.get('unresolvedSettingsReferences', []),
            'unresolvedSerializedReferences': manifest.get('unresolvedSerializedReferences', []),
            'dependencyCompletenessVerified': False,
            'timingEvidence': manifest['timingEvidence'], 'playbackContract': manifest['playbackContract'],
            'runtimeReopenVerified': False, 'playerBuildVerified': False,
            'platformActions': False, 'gitStagingPerformed': False,
        }
        plans.append((destination, files, record))
    if copy:
        for destination, files, record in plans:
            for source, target, expected in files:
                export.copy_exact(source, target, expected)
            export.write_new(destination / 'scene-source-record.json', record)
    return {'copied': copy, 'count': len(plans), 'projects': [
        {'slug': r['slug'], 'destination': str(d), 'textFileCount': len(f),
         'sceneCount': len(r['sceneBindings']), 'receiptSha256': r['receiptSha256']}
        for d, f, r in plans]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--copy', action='store_true')
    print(json.dumps(preserve(parser.parse_args().copy), ensure_ascii=False, indent=2))
