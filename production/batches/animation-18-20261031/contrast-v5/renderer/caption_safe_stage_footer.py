"""Narrow lossless intermediate patch: remove the redundant stage footer only.

Preserves the original443-row manifest/media. The new manifest is adopted by
the parent only after every changed row has its own matching hashed receipt.
No audio, gameplay, captions, episode timing, GPU or platform work.
"""
from pathlib import Path
import argparse, ast, copy, hashlib, importlib.util, json, os, subprocess, sys, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
# Load this interpreter's compatible SciPy before the legacy renderer prepends
# its Python-version-specific dependency folder. No environment is modified.
from scipy.spatial.transform import Rotation
from scipy.ndimage import label

H = Path(__file__).resolve().parent
R = H.parents[4]
sys.path.insert(0, str(H))
import render_rows as rr
import complete_observation_results as observations
import a15_complete_repeats as fingers

BASE = H / 'caption-safe/integration-before.json'
DEST = Path('C:/Users/1/Videos/YamyamProduction/animation-contrast-v5-work/caption-safe')
NEW = H / 'integration-caption-safe.json'
ENC = ['-threads', '4', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '0',
       '-bf', '0', '-g', '120', '-sc_threshold', '0', '-pix_fmt', 'yuv420p',
       '-r', '60', '-video_track_timescale', '60000', '-color_primaries', 'bt709',
       '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart']


def read(p): return json.loads(Path(p).read_text('utf-8-sig'))


def sha(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()


def rel(p):
    p = Path(p).absolute()
    try: return p.relative_to(R).as_posix()
    except ValueError: return p.as_posix()


def save(p, value):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    t = p.with_suffix('.' + str(os.getpid()) + '.pending')
    t.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', 'utf8'); os.replace(t, p)


def extracted_state(mod):
    """Compile the exact nested state function, without calling execute/render."""
    source = Path(mod.__file__)
    tree = ast.parse(source.read_text('utf8'))
    candidates = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == 'state']
    assert len(candidates) == 1
    node = ast.Module(body=[candidates[0]], type_ignores=[])
    namespace = dict(vars(mod)); exec(compile(ast.fix_missing_locations(node), str(source), 'exec'), namespace)
    return namespace['state']


def ranges(indices):
    out = []
    for n in indices:
        if out and out[-1][1] == n: out[-1][1] += 1
        else: out.append([n, n + 1])
    return out


def plan():
    control = read(R / 'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
    assert control['renderAuthorized'] and control['fullLocalProductionAuthorized']
    base = read(BASE)
    assert len(base['episodes']) == 17 and sum(len(e['rows']) for e in base['episodes']) == 443
    override_ids = {r['id'] for r in read(H / 'observation-corrections.json')['rows']}
    finger_ids = {r['id'] for r in read(H / 'pacing-extension.json')['bodyOverrides']}
    obs, finger = extracted_state(observations), extracted_state(fingers)
    jobs = []
    for e in base['episodes']:
        assert e['id'] in control['episodes'] and e['id'] != 'A03'
        for row in e['rows']:
            if row['mode'] == 'native': continue
            if not (row.get('phaseModeAtTail') or e['id'] == 'A02' or row['id'] in override_ids): continue
            state = obs if row['id'] in override_ids else finger if row['id'] in finger_ids else rr.state
            frames = row['newFrames']
            actual = [i for i in range(frames) if state(e['id'], row, i)[1] == 'stages']
            if not actual: continue
            text = '같은 동작에서 판정 구간만 변경' if e['id'] == 'A16' and row['key'] == 'active' else '같은 시연의 서로 다른 실제 자세'
            font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', 30)
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((64, 880), text, font=font, anchor='lt')
            # Even coordinates preserve source YUV420 chroma alignment. The top
            # edge is below all frame indices (821px +32px glyphs).
            x, y = (bbox[0] - 4) // 2 * 2, (bbox[1] - 4) // 2 * 2
            right, bottom = ((bbox[2] + 5) // 2 * 2), ((bbox[3] + 5) // 2 * 2)
            assert y >= 870 and bottom < 930 and right < 1600
            src = R / row['output']; assert sha(src) == row['sha256']
            dst = DEST / e['id'] / (row['id'] + '.mp4')
            jobs.append({'episode': e['id'], 'id': row['id'], 'key': row['key'],
                'source': row['output'], 'sourceSha256': row['sha256'], 'output': rel(dst),
                'frames': frames, 'stageFrameRanges': ranges(actual), 'stageFrames': len(actual),
                'stateFunction': str(Path(observations.__file__ if row['id'] in override_ids else fingers.__file__ if row['id'] in finger_ids else rr.__file__).relative_to(R)).replace('\\', '/'),
                'cutOffset': row.get('cutOffset', 0), 'originalCutFrames': row.get('originalCutFrames'),
                'clearRectangleXYWH': [x, y, right - x, bottom - y], 'removedText': text,
                'protects': 'Frame indices at821, all stage panels/gizmos/headings, native/compare frames. This input is silent and captionless; final captions are burned later unchanged.'})
    return {'schemaVersion': 1, 'status': 'planned', 'originalManifest': rel(BASE),
        'originalManifestSha256': sha(BASE), 'oldIntegrationFileSha256': sha(H / 'integration-manifest.json'),
        'originalRows': 443, 'originalA15AddedFrames': 230, 'patchCodeSha256': sha(__file__),
        'stateCodeSha256': {rel(H / f): sha(H / f) for f in ['render_rows.py', 'complete_observation_results.py', 'a15_complete_repeats.py']},
        'futureCompositorSha256': sha(H / 'compose.py'), 'jobs': jobs,
        'oldMediaOverwritten': False, 'fullMastersChanged': False, 'platformChanged': False}


def probe(p):
    return read_json_output(['ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(p)])['streams']


def read_json_output(cmd):
    return json.loads(subprocess.check_output(cmd, creationflags=subprocess.CREATE_NO_WINDOW))


def decode_yuv(file, frame):
    seek = max(0, frame // 60 - 2); offset = frame - seek * 60
    data = subprocess.check_output(['ffmpeg', '-v', 'error', '-threads', '1', '-ss', str(seek), '-i', str(file),
        '-an', '-filter_threads', '1', '-vf', f'select=eq(n\\,{offset})', '-frames:v', '1',
        '-pix_fmt', 'yuv420p', '-f', 'rawvideo', '-'], creationflags=subprocess.CREATE_NO_WINDOW)
    assert len(data) == 1920 * 1080 * 3 // 2
    return data


def patch(job):
    source, output = R / job['source'], R / job['output']
    output.parent.mkdir(parents=True, exist_ok=True)
    x, y, w, h = job['clearRectangleXYWH']
    enable = '+'.join(f'between(n,{a},{b-1})' for a, b in job['stageFrameRanges'])
    vf = f"drawbox=x={x}:y={y}:w={w}:h={h}:color=0x080c0a:t=fill:enable='{enable}'"
    signature = {'sourceSha256': job['sourceSha256'], 'frames': job['frames'], 'filter': vf, 'encoder': ENC}
    receipt = output.with_suffix('.json'); previous = read(receipt) if receipt.exists() else {}
    if not (output.exists() and previous.get('signature') == signature and previous.get('sha256') == sha(output)):
        assert sha(source) == job['sourceSha256']
        temporary = output.with_suffix('.pending.mp4')
        with output.with_suffix('.log').open('wb') as log:
            subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-threads', '4', '-i', str(source),
                '-an', '-filter_threads', '1', '-vf', vf, '-frames:v', str(job['frames']), *ENC, str(temporary)],
                stdout=log, stderr=log, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        streams = probe(temporary)
        assert len(streams) == 1
        s = streams[0]
        assert (s['width'], s['height'], s['avg_frame_rate'], int(s['nb_frames'])) == (1920, 1080, '60/1', job['frames'])
        os.replace(temporary, output)
        previous = {'episode': job['episode'], 'rowId': job['id'], 'sha256': sha(output),
            'signature': signature, 'frames': job['frames'], 'silent': True,
            'stageFrameRanges': job['stageFrameRanges'], 'clearRectangleXYWH': job['clearRectangleXYWH'],
            'losslessIntermediate': True, 'humanReview': False}
        save(receipt, previous)
    return previous


def run(limit=0):
    spec = plan(); save(H / 'caption-safe/plan.json', spec)
    for index, job in enumerate(spec['jobs']):
        receipt = patch(job); job['sha256'] = receipt['sha256']; job['receipt'] = rel((R / job['output']).with_suffix('.json'))
        print(f"{index+1}/{len(spec['jobs'])} {job['episode']} {job['id']} {job['stageFrames']} stage frames", flush=True)
        if limit and index + 1 >= limit:
            save(H / 'caption-safe/progress.json', spec); return
    clone = copy.deepcopy(read(BASE)); patches = {j['id']: j for j in spec['jobs']}
    for e in clone['episodes']:
        for row in e['rows']:
            if row['id'] not in patches: continue
            j = patches[row['id']]
            row.update(output=j['output'], sha256=j['sha256'], captionSafePatch={
                'source': j['source'], 'sourceSha256': j['sourceSha256'], 'receipt': j['receipt'],
                'stageFrameRanges': j['stageFrameRanges'], 'clearRectangleXYWH': j['clearRectangleXYWH'],
                'reason': 'Remove redundant secondary sentence that overlapped the fixed final caption. Actual stage pose/frame labels retained.'})
    assert sum(len(e['rows']) for e in clone['episodes']) == 443
    assert sum(e['additionalFrames'] for e in clone['episodes']) == 230
    assert sha(H / 'integration-manifest.json') == spec['oldIntegrationFileSha256'], 'Parent adopted another integration while patching'
    clone['captionSafeRevision'] = {'baselineManifestSha256': sha(BASE), 'changedRows': len(patches),
        'changedStageFrames': sum(j['stageFrames'] for j in spec['jobs']), 'plan': rel(H / 'caption-safe/plan.json'),
        'old443FilesPreserved': True, 'audioAndTimingChanged': False, 'actualCaptionOverlayQa': 'pending'}
    clone['status'] = 'caption-safe-plates-complete-parent-adoption-pending'
    spec['status'] = 'all-caption-safe-plates-ready'; spec['newManifest'] = rel(NEW)
    save(H / 'caption-safe/plan.json', spec); save(NEW, clone)
    print(json.dumps({'ready': True, 'changedRows': len(patches), 'manifest': rel(NEW), 'sha256': sha(NEW)}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--render', action='store_true'); parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    if args.render: run(args.limit)
    else:
        p = plan(); save(H / 'caption-safe/plan.json', p)
        print(json.dumps({'jobs': len(p['jobs']), 'stageFrames': sum(j['stageFrames'] for j in p['jobs']),
            'perEpisode': {e: sum(j['episode'] == e for j in p['jobs']) for e in sorted({j['episode'] for j in p['jobs']})}}))
