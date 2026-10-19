"""Remove editorial credit strips; retain the exact approved intro/audio/timing."""
from pathlib import Path
import argparse, hashlib, json, math, shutil, subprocess
from PIL import Image, ImageDraw

P = Path(__file__).resolve().parents[2]
R = P.parents[1]
L = P / 'production/local/credits-v3'
V2 = P / 'production/local/intro-v2'
BIN = Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
FF, FP = str(BIN / 'ffmpeg.exe'), str(BIN / 'ffprobe.exe')

def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
def run(args):
    proc = subprocess.run(args, capture_output=True)
    if proc.returncode: raise RuntimeError(proc.stderr.decode(errors='replace')[-5000:])
    return proc.stdout
def guard():
    s = read(R / 'shared/publishing/video-production-control.json')['shortsRecurringAuthorization']
    assert s['selectedShort'] == P.name and s['latestSelection']['selectedRevision'] == 'zombie-quiet-credits-v3'
    assert sha(V2 / 'captioned.mp4') == 'b91f1fce674b6e2426e1a111d8ba1aa45db8e10999fb421871fd711816a61644'

def pair():
    guard(); L.mkdir(parents=True, exist_ok=True)
    body = R / 'shared/output/motion-canvas/shorts-zombie-quiet-director-body-credits-v3.mp4'
    intro = R / 'shared/output/motion-canvas/shorts-zombie-quiet-director-intro-v2.mp4'
    body_cc = L / 'body-captioned.mp4'
    ass = str((P / 'production/local/captions.ko.ass').relative_to(R)).replace('\\', '/')
    run([FF, '-v', 'warning', '-n', '-i', str(body), '-vf', 'ass=' + ass,
         '-an', '-c:v', 'libx264', '-preset', 'fast', '-crf', '18', '-pix_fmt', 'yuv420p', str(body_cc)])
    for name, first, second in [('clean', intro, body), ('captioned', V2 / 'intro-captioned.mp4', body_cc)]:
        concat = L / (name + '-concat.txt')
        concat.write_text("file '" + first.as_posix() + "'\nfile '" + second.as_posix() + "'\n", encoding='utf8')
        visual = L / (name + '-visual.mp4')
        run([FF, '-v', 'warning', '-n', '-f', 'concat', '-safe', '0', '-i', str(concat),
             '-map', '0:v:0', '-an', '-c:v', 'copy', str(visual)])
        run([FF, '-v', 'warning', '-n', '-i', str(visual), '-i', str(V2 / 'final-mix.m4a'),
             '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', str(L / (name + '.mp4'))])
    for lang in ['ko', 'en']: shutil.copyfile(V2 / f'captions.{lang}.srt', L / f'captions.{lang}.srt')
    save(L / 'pair-build.json', {'revision': 'zombie-quiet-credits-v3', 'introFramesReused': 277,
         'bodyFrames': 2652, 'totalFrames': 2929, 'audioRemixed': False,
         'audioSourceSha256': sha(V2 / 'final-mix.m4a'), 'cleanSha256': sha(L / 'clean.mp4'),
         'captionedSha256': sha(L / 'captioned.mp4')})

def aac(path):
    return hashlib.sha256(run([FF, '-v', 'error', '-i', str(path), '-map', '0:a:0',
        '-c', 'copy', '-f', 'adts', 'pipe:1'])).hexdigest()
def intro_hashes(path):
    data = run([FF, '-v', 'error', '-i', str(path), '-map', '0:v:0', '-an', '-frames:v', '277', '-f', 'framemd5', '-']).decode()
    return [s.split(',')[-1].strip() for s in data.splitlines() if s and not s.startswith('#')]

def integrity():
    guard(); reports = []
    baseline_audio = aac(V2 / 'captioned.mp4')
    for name in ['clean', 'captioned']:
        f = L / f'{name}.mp4'
        run([FF, '-v', 'error', '-xerror', '-i', str(f), '-f', 'null', '-'])
        probe = json.loads(run([FP, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(f)]))
        v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        assert (v['width'], v['height'], v['r_frame_rate'], int(v['nb_frames'])) == (1080, 1920, '60/1', 2929)
        frames = json.loads(run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries',
            'frame=best_effort_timestamp_time', '-of', 'json', str(f)]))['frames']
        assert len(frames) == 2929 and all(abs(float(s['best_effort_timestamp_time']) - i/60) < 2e-6 for i, s in enumerate(frames))
        assert aac(f) == baseline_audio
        assert intro_hashes(f) == intro_hashes(V2 / f'{name}.mp4')
        reports.append({'name': name, 'sha256': sha(f), 'bytes': f.stat().st_size,
            'decoded': True, 'regular60FpsPts': True, 'frames': 2929,
            'intro277DecodedFramesIdentical': True, 'aacIdenticalToApprovedV2': True})
    for lang in ['ko', 'en']: assert sha(L / f'captions.{lang}.srt') == sha(V2 / f'captions.{lang}.srt')
    save(L / 'integrity.json', {'status': 'pass', 'outputs': reports,
        'approvedAACHash': baseline_audio, 'captionsAndTimingIdentical': True,
        'audioEvidenceReused': 'production/intro-v2/review.json; exact AAC retained, no ASR/remix repeated'})

def qa():
    guard(); folder = L / 'qa'; folder.mkdir(exist_ok=True)
    cues = read(P / 'script/captions.json')['cues']
    timing = read(P / 'production/intro-v2/timing.json')
    times = sorted(set(round(t, 3) for t in [*((c['start'] + c['end'])/2 for c in cues),
        *(max(0, s['start'] - .035) for s in timing['sections']),
        *(s['start'] + .1 for s in timing['sections']), 29.0, 30.8, 42.5, 44.5, 47.9]))
    rows = []
    for i, t in enumerate(times):
        f = folder / f'frame-{i:03}.png'
        if not f.exists(): run([FF, '-v', 'error', '-n', '-ss', str(t), '-i', str(L / 'captioned.mp4'), '-frames:v', '1', str(f)])
        rows.append({'seconds': t, 'path': str(f.relative_to(R)).replace('\\', '/')})
    for start in range(0, len(rows), 12):
        subset = rows[start:start+12]
        sheet = Image.new('RGB', (375*4, 700*math.ceil(len(subset)/4)), '#242424')
        draw = ImageDraw.Draw(sheet)
        for j, row in enumerate(subset):
            im = Image.open(R / row['path']).convert('RGB'); im.thumbnail((375, 666))
            x, y = j%4*375, j//4*700
            sheet.paste(im, (x, y)); draw.text((x+5, y+674), str(row['seconds'])+'s', fill='white')
        sheet.save(folder / f'sheet-{start//12+1:02}.jpg', quality=93)
    save(folder / 'index.json', {'captionMidpoints': len(cues), 'rows': rows,
        'scope': 'All28captioncues and everycut; changedgameheaders/credit-removal regions and cat clarity; moving review separately required'})
    (L / 'playback.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><title>좀비 쇼츠 출처 띠 제거 v3 검수</title><style>body{margin:0;background:#151515;color:white;font:16px sans-serif}h1{font-size:18px}main{display:flex;align-items:flex-start;gap:24px;padding:16px}video{width:375px;height:666.67px;background:black}a{color:#ffe07a}</style><main><section><h1>v3 · 1080×1920 / 60fps · 전체 48.82초</h1><video controls preload="auto" src="captioned.mp4"></video><p>화면 출처 띠 제거 · 고양이 가림 수정</p></section><section><h1>네이티브 원본</h1><a href="captioned.mp4">1080p 전체 자막영상</a><p>기존 음성·BGM·자막·인트로 유지</p></section></main></html>''', encoding='utf8')
    print(json.dumps({'sampleFrames': len(times), 'captionCues': len(cues), 'sheets': math.ceil(len(times)/12)}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('command', choices=['pair', 'integrity', 'qa'])
    globals()[parser.parse_args().command]()
