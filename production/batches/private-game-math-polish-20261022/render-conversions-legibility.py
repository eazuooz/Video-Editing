"""Render M08 explanation-only replacements; blocked gameplay is never used."""
from polish_common import *

e = Episode('M08')
e.authorized()
preview = read(e.H/'conversions-legibility-preflight.json')
assert preview['status'] == 'passed-still-preflight'
assert not preview['selectedScenes'], 'Review every numeric scene first'
assert preview['timelineSha256'] == sha(e.P/'production/timeline.json')
for path, digest in preview['sourceCode'].items():
    assert sha(R/path) == digest
signature = hashlib.sha256(json.dumps(preview['sourceCode'], sort_keys=True).encode()).hexdigest() + preview['timelineSha256']
out = e.O/'conversions-legibility'
(out/'clips').mkdir(parents=True, exist_ok=True)
record = e.H/'conversions-legibility-render.json'
data = read(record) if record.exists() else {'scenes': {}}
data.update(sourceCode=preview['sourceCode'], timelineSha256=preview['timelineSha256'],
            visualQa='pending-encoded-source-review', readyForHumanReview=False,
            sourceScope='explanation-only; full master waits for gameplay FHD resolution decision')
env = dict(os.environ, PYTHONUTF8='1', POLISH_SLUG=e.slug,
           POLISH_TIMING_MAP=str(e.O/'timing-map.json'),
           MATH_RENDER_TIMING=str(e.P/'production/timeline.json'), REVISION_FINAL_TIMING='1',
           OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='1')
for slot in e.T['scenes']:
    if slot['classification'] != 'explanation':
        continue
    e.authorized()
    sid = slot['id']
    dst = out/f'clips/{sid}.mp4'
    old = data['scenes'].get(sid, {})
    if old.get('signature') == signature and dst.exists() and sha(dst) == old['sha256']:
        e.verify(dst, slot['frames'])
        continue
    raw = out/f'manim/videos/conversions-legibility-scenes/1080p60/Polish{sid}.mp4'
    e.run([R/'manim/.venv/Scripts/python.exe', '-m', 'manim', '--resolution', '1920,1080',
           '--fps', '60', '--disable_caching', '--media_dir', out/'manim',
           B/'conversions-legibility-scenes.py', 'Polish'+sid], f'conversions-legibility-{sid}.log', env=env)
    v = video(raw)
    assert (v['width'], v['height'], v['r_frame_rate']) == (1920, 1080, '60/1')
    difference = slot['frames'] - int(v['nb_frames'])
    assert abs(difference) <= 4, (sid, difference)
    e.ff(['-i', raw, '-vf', 'fps=60,tpad=stop_mode=clone:stop_duration=0.1,setsar=1',
          '-frames:v', slot['frames'], '-an', *ENC, dst], f'interpolation-normalize-{sid}.log')
    e.verify(dst, slot['frames'])
    e.ff(['-v', 'error', '-i', dst, '-f', 'null', '-'], f'interpolation-decode-{sid}.log')
    assert not (e.O/f'interpolation-decode-{sid}.log').read_text(encoding='utf8').strip()
    data['scenes'][sid] = {'signature': signature, 'path': rel(dst), 'sha256': sha(dst),
                          'rawPath': rel(raw), 'rawSha256': sha(raw), 'frames': slot['frames'],
                          'roundingFrameAdjustment': difference, 'fullDecode': True,
                          'reason': 'Original teaching events, values and clock; readable text/code and header-safe layout'}
    save(record, data)
    print('M08', sid, 'explanation replacement rendered; source visual QA pending', flush=True)
