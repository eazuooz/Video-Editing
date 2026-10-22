"""Generate current captioned M11/M12 numeric states; never grant visual approval."""
import datetime
import math
import sys
from PIL import Image, ImageDraw, ImageFont
from polish_common import *

e = Episode(sys.argv[1])
assert e.id in ['M11','M12']
e.authorized()
out = e.O / 'planes-legibility-preflight'
out.mkdir(exist_ok=True)
lesson = read(R / 'production/batches/game-math-part2-full-series/lessons/game-math-planes-barycentric.json')
selected = set(sys.argv[2:])
records, tiles = [], []
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 16)
for slot in e.T['scenes']:
    sid = slot['id']
    if slot['classification'] != 'explanation' or (selected and sid not in selected):
        continue
    s = next(s for s in lesson['scenes'] if s['id'] == sid) if sid.isdigit() else {'mode':'supplement-final'}
    states = sorted({0, len(s['beats']) // 2, len(s['beats']) - 1}) if sid.isdigit() else [-1]
    for i in states:
        env = dict(os.environ, PYTHONUTF8='1', POLISH_SLUG=e.slug,
                   POLISH_TIMING_MAP=str(e.O / 'timing-map.json'),
                   MATH_RENDER_TIMING=str(e.P / 'production/timeline.json'),
                   REVISION_FINAL_TIMING='1', GEOMETRY_PREVIEW_SID=sid,
                   GEOMETRY_PREVIEW_STATE_COUNT=str(i + 1), OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='1')
        e.run([R/'manim/.venv/Scripts/python.exe', '-m', 'manim', '-s', '--resolution', '1920,1080',
               '--fps', '60', '--disable_caching', '--media_dir', out/'manim',
               B/'planes-legibility-preview.py', 'Preview'], 'interpolation-font-still.log', env=env)
        raw = next((out/'manim/images/planes-legibility-preview').glob('Preview_*.png'))
        t = slot['start'] + (min(slot['lineStarts'][i] + 1.5, slot['seconds'] - .1) if sid.isdigit() else slot['seconds']-.2)
        dst = out / f'{sid}-{i}.png'
        e.ff(['-i', raw, '-vf', f'setpts=PTS+{t}/TB,ass=captions.ko.ass', '-frames:v', '1', '-threads', '1', dst],
             'interpolation-font-caption.log', e.O)
        records.append({'scene': sid, 'mode': s['mode'], 'state': i, 'globalSeconds': t,
                        'image': rel(dst), 'imageSha256': sha(dst)})
        tile = Image.new('RGB', (375, 240), '#222222')
        tile.paste(Image.open(dst).convert('RGB').resize((375, 211), Image.Resampling.LANCZOS), (0, 29))
        ImageDraw.Draw(tile).text((5, 3), f'{e.id} {sid} {s["mode"]} #{i}', font=font, fill='white')
        tiles.append(tile)
    print(e.id, sid, 'font states generated', flush=True)
for i in range(0, len(tiles), 8):
    sheet = Image.new('RGB', (1500, 480), '#222222')
    for j, tile in enumerate(tiles[i:i+8]):
        sheet.paste(tile, (j % 4 * 375, j // 4 * 240))
    sheet.save(out / f'sheet-{i//8+1:02d}.jpg', quality=94)
code = [B/'planes-legibility-scenes.py', B/'planes-legibility-preview.py', B/'lesson-scenes.py',
        R/'manim/projects/game-math-part2-full-series/geometry.py',
        R/'manim/projects/game-math-part2-full-series/geometry_planes.py',
        R/'manim/projects/game-math-part2-full-series/lesson.py',
        R/'manim/projects/game-math-part2-teaching-revision/planes_additions.py']
save(e.H/'planes-legibility-preflight.json', {
    'status': 'await-direct-inspection', 'generatedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'sourceCode': {rel(p): sha(p) for p in code}, 'timelineSha256': sha(e.P/'production/timeline.json'),
    'samples': records, 'sheets': math.ceil(len(tiles)/8), 'selectedScenes': sorted(selected),
    'finalMovingReview': 'pending', 'readyForHumanReview': False,
    'changes': 'Header rule below subtitle; readable existing labels/formulas and min/max plane labels. Preserve original geometry, values, role colors, code execution outline, event timings and voice clock. Supplementary formula/label sizes enlarged in isolated geometry wrapper; encoded-source QA pending.',
    'gameplaySourceBlocker': 'unchanged; no full master authorized from unresolved non-FHD sources'})
