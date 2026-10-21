"""Generate current captioned M07 numeric states; never grant visual approval."""
import datetime
import math
import sys
from PIL import Image, ImageDraw, ImageFont
from polish_common import *

e = Episode('M07')
e.authorized()
out = e.O / 'interpolation-legibility-preflight'
out.mkdir(exist_ok=True)
lesson = read(R / 'production/batches/game-math-part2-full-series/lessons/game-math-rotation-interpolation.json')
selected = set(sys.argv[1:])
records, tiles = [], []
font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 16)
for slot in e.T['scenes']:
    sid = slot['id']
    if slot['classification'] != 'explanation' or not sid.isdigit() or (selected and sid not in selected):
        continue
    s = next(s for s in lesson['scenes'] if s['id'] == sid)
    for i in sorted({0, len(s['beats']) // 2, len(s['beats']) - 1}):
        env = dict(os.environ, PYTHONUTF8='1', POLISH_SLUG=e.slug,
                   POLISH_TIMING_MAP=str(e.O / 'timing-map.json'),
                   MATH_RENDER_TIMING=str(e.P / 'production/timeline.json'),
                   REVISION_FINAL_TIMING='1', INTERPOLATION_PREVIEW_SID=sid,
                   INTERPOLATION_PREVIEW_STATE_COUNT=str(i + 1), OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='1')
        e.run([R/'manim/.venv/Scripts/python.exe', '-m', 'manim', '-s', '--resolution', '1920,1080',
               '--fps', '60', '--disable_caching', '--media_dir', out/'manim',
               B/'interpolation-legibility-preview.py', 'Preview'], 'interpolation-font-still.log', env=env)
        raw = next((out/'manim/images/interpolation-legibility-preview').glob('Preview_*.png'))
        t = slot['start'] + min(slot['lineStarts'][i] + 1.5, slot['seconds'] - .1)
        dst = out / f'{sid}-{i}.png'
        e.ff(['-i', raw, '-vf', f'setpts=PTS+{t}/TB,ass=captions.ko.ass', '-frames:v', '1', '-threads', '1', dst],
             'interpolation-font-caption.log', e.O)
        records.append({'scene': sid, 'mode': s['mode'], 'state': i, 'globalSeconds': t,
                        'image': rel(dst), 'imageSha256': sha(dst)})
        tile = Image.new('RGB', (375, 240), '#222222')
        tile.paste(Image.open(dst).convert('RGB').resize((375, 211), Image.Resampling.LANCZOS), (0, 29))
        ImageDraw.Draw(tile).text((5, 3), f'M07 {sid} {s["mode"]} #{i}', font=font, fill='white')
        tiles.append(tile)
    print('M07', sid, 'font states generated', flush=True)
for i in range(0, len(tiles), 8):
    sheet = Image.new('RGB', (1500, 480), '#222222')
    for j, tile in enumerate(tiles[i:i+8]):
        sheet.paste(tile, (j % 4 * 375, j // 4 * 240))
    sheet.save(out / f'sheet-{i//8+1:02d}.jpg', quality=94)
code = [B/'interpolation-legibility-scenes.py', B/'interpolation-legibility-preview.py', B/'lesson-scenes.py',
        B/'quaternion-scenes.py', R/'manim/projects/game-math-part2-full-series/interpolation.py',
        R/'manim/projects/game-math-part2-full-series/lesson.py',
        R/'manim/projects/game-math-part2-teaching-revision/interpolation_additions.py']
save(e.H/'interpolation-legibility-preflight.json', {
    'status': 'await-direct-inspection', 'generatedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'sourceCode': {rel(p): sha(p) for p in code}, 'timelineSha256': sha(e.P/'production/timeline.json'),
    'samples': records, 'sheets': math.ceil(len(tiles)/8), 'selectedScenes': sorted(selected),
    'finalMovingReview': 'pending', 'readyForHumanReview': False,
    'changes': 'Header rule below subtitle; larger existing secondary labels/formulas; 24pt code with compact leading, separate checked_unit note and restrained active-line pulse. Original text, math, scene events and voice clock retained. Supplementary formula/label size enlarged in isolated wrapper; separate moving QA required.',
    'gameplaySourceBlocker': 'unchanged; no full master authorized from unresolved non-FHD sources'})
