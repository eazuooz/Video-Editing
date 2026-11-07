"""Verify browser-downloaded Fab sources without starting editors or executing assets."""
import argparse
import collections
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import struct
import tarfile
import zipfile

HERE = Path(__file__).resolve().parent
RECORD = HERE / 'fab-assets-20261107.json'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def safe_target(root, name):
    rel = PurePosixPath(name.replace('\\', '/'))
    if rel.is_absolute() or '..' in rel.parts or ':' in name:
        raise ValueError(f'Unsafe archive path: {name}')
    target = (root / str(rel)).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Archive path escaped its target')
    return target


def fbx_probe(path):
    data = path.read_bytes()
    if not data.startswith(b'Kaydara FBX Binary  \x00\x1a\x00'):
        return {'binary': False, 'animationStackMarker': b'AnimationStack:' in data,
                'visualMotionVerified': False}
    version = struct.unpack_from('<I', data, 23)[0]
    fmt = '<QQQB' if version >= 7500 else '<IIIB'
    header = struct.calcsize(fmt)
    found = []
    counts = collections.Counter()

    def properties(at, count, end):
        values = []
        for _ in range(count):
            kind = chr(data[at]); at += 1
            if kind in 'YCFDIL':
                pf = {'Y':'h', 'C':'?', 'F':'f', 'D':'d', 'I':'i', 'L':'q'}[kind]
                values.append(struct.unpack_from('<' + pf, data, at)[0])
                at += struct.calcsize('<' + pf)
            elif kind in 'SR':
                size = struct.unpack_from('<I', data, at)[0]; at += 4
                if at + size > end:
                    raise ValueError('FBX property outside boundary')
                values.append(data[at:at+size].decode('utf-8', errors='replace') if kind == 'S' else None)
                at += size
            elif kind in 'fdilbc':
                _, _, compressed = struct.unpack_from('<III', data, at)
                at += 12 + compressed
                values.append(None)
            else:
                raise ValueError(f'Unknown FBX property {kind}')
            if at > end:
                raise ValueError('FBX property overflow')
        return values

    def walk(start, limit, depth=0):
        if depth > 100:
            raise ValueError('FBX depth limit')
        at = start
        while at + header <= limit:
            end, count, plen, nlen = struct.unpack_from(fmt, data, at)
            if end == 0:
                break
            if not at < end <= len(data) or end > limit or count > 100000:
                raise ValueError('Invalid FBX node boundary')
            name_at = at + header
            name = data[name_at:name_at+nlen].decode('ascii', errors='replace')
            prop_at = name_at + nlen
            child_at = prop_at + plen
            counts[name] += 1
            if name == 'AnimationStack':
                vals = properties(prop_at, count, child_at)
                found.append(str(vals[1]).replace('\x00\x01', '::') if len(vals)>1 else 'unnamed')
            if child_at < end:
                walk(child_at, end, depth+1)
            at = end

    walk(27, len(data))
    return {'binary': True, 'version': version, 'animationStacks': found,
            'animationCurveNodes': counts['AnimationCurve'],
            'visualMotionVerified': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--indices', nargs='+', type=int, help='Inspect only changed catalog items')
    args = parser.parse_args()
    record = json.loads(RECORD.read_text(encoding='utf-8-sig'))
    root = Path(record['storageRoot']).resolve()
    root.mkdir(parents=True, exist_ok=True)
    for item in record['items']:
        if args.indices is not None and item['index'] not in args.indices:
            continue
        for download in item['downloads']:
            source = Path(download['browserPath'])
            if not source.is_file():
                raise FileNotFoundError(source)
            folder = root / item['id']
            folder.mkdir(exist_ok=True)
            target = folder / source.name
            source_hash = digest(source)
            if target.exists() and digest(target) != source_hash:
                raise ValueError(f'Existing different source: {target}')
            if not target.exists():
                shutil.copy2(source, target)
            download.update(localPath=str(target), bytes=target.stat().st_size, sha256=source_hash)
            extracted = folder / 'source'
            extracted.mkdir(exist_ok=True)
            paths = []
            if zipfile.is_zipfile(target):
                with zipfile.ZipFile(target) as archive:
                    entries = archive.infolist()
                    if len(entries)>50000 or sum(e.file_size for e in entries)>5*1024**3:
                        raise ValueError('Archive exceeds inspection limits')
                    bad = archive.testzip()
                    if bad:
                        raise ValueError(f'CRC failed: {bad}')
                    download['archiveIntegrity'] = 'zip-crc-pass'
                    download['archiveEntries'] = len(entries)
                    download['archiveExtensions'] = dict(collections.Counter(Path(e.filename).suffix.lower() for e in entries if not e.is_dir()))
                    for entry in entries:
                        if entry.is_dir() or Path(entry.filename).suffix.lower() not in {'.fbx','.bvh'}:
                            continue
                        dest = safe_target(extracted, entry.filename)
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        if not dest.exists():
                            with archive.open(entry) as src, dest.open('xb') as dst:
                                shutil.copyfileobj(src, dst)
                        paths.append(dest)
            elif target.suffix.lower() == '.unitypackage':
                with tarfile.open(target, 'r:gz') as archive:
                    entries = archive.getmembers()
                    if len(entries)>50000 or sum(e.size for e in entries)>5*1024**3:
                        raise ValueError('Unity package exceeds limits')
                    members = {e.name:e for e in entries if e.isfile()}
                    download['archiveIntegrity'] = 'gzip-tar-read-pass'
                    for name, entry in members.items():
                        if not name.endswith('/pathname'):
                            continue
                        original = archive.extractfile(entry).read().decode('utf-8-sig').strip('\x00\r\n')
                        if Path(original).suffix.lower() not in {'.fbx','.bvh'}:
                            continue
                        asset = members.get(name.rsplit('/',1)[0]+'/asset')
                        if asset is None:
                            continue
                        dest = safe_target(extracted, original)
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        if not dest.exists():
                            with archive.extractfile(asset) as src, dest.open('xb') as dst:
                                shutil.copyfileobj(src, dst)
                        paths.append(dest)
            elif target.suffix.lower()=='.fbx':
                paths.append(target)
            else:
                download['inspectionNote'] = 'Source preserved; not executed or imported. Maya rig is not a playable UE animation package.'
            download['motionSources'] = []
            for path in paths:
                info = {'path':str(path), 'sha256':digest(path), 'bytes':path.stat().st_size}
                if path.suffix.lower()=='.fbx':
                    try:
                        info['fbx'] = fbx_probe(path)
                    except (ValueError, IndexError, struct.error) as exc:
                        info['fbx'] = {'probeError':str(exc), 'visualMotionVerified':False}
                download['motionSources'].append(info)
            print(json.dumps({'title':item['title'],'bytes':download['bytes'],'sources':len(paths),'path':str(target)}, ensure_ascii=False), flush=True)
    record['sourceInspection'] = {'method':'Local SHA256, ZIP CRC, bounded source-only extraction, FBX object-tree inspection; no downloaded code executed', 'visualPlaybackVerified':False, 'engineImportCompleted':False}
    RECORD.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
