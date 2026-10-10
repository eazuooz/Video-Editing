"""Single CPU2/GPU0 native-PTS preflight for two unadopted opening candidates."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[3]
batch = root / 'production/batches/unpublished-teaching-clarity-revision'
out = root / 'shared/assets/presenting-game-scores/raw/motion-opening-native-v4'
state_path = batch / 'motion-opening-native-execution-v4.json'
assert not state_path.exists(), 'Read existing execution and outputs before starting another job'
audit = json.loads((batch / 'motion-script-audit-v1.json').read_text('utf-8'))
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()
for relative, expected in audit['inputSha256'].items():
    assert sha(root / relative) == expected, relative
source = root / 'shared/assets/game-footage/motion-sickness-games/PF5L_2g9UVQ.mp4'
assert sha(source) == 'd2fff989d106762f66971c6e85172f79ce0bb6782c75f318d348447e11161612'
ps = ['powershell', '-NoProfile', '-Command',
      "@{processors=@(Get-CimInstance Win32_Processor | Select-Object LoadPercentage); processes=@(Get-CimInstance Win32_Process | Where-Object {$_.Name -match 'python|ffmpeg|node' -and $_.CommandLine -match 'gpu-handoff|render-voice|resume_with_preview|inspect-motion-opening-native|assemble-lines-ready-scenes'} | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine)} | ConvertTo-Json -Depth 5"]
resources = json.loads(subprocess.check_output(ps, text=True, encoding='utf-8-sig'))
assert max(p['LoadPercentage'] for p in resources['processors']) < 85, 'Wait for sufficient CPU headroom'
gpu = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.free,utilization.gpu', '--format=csv,noheader,nounits'], text=True).strip()
own = [p for p in resources['processes'] if 'inspect-motion-opening-native-v4.py' in (p.get('CommandLine') or '') and p['ProcessId'] != os.getpid()]
assert not own, 'Existing own native inspection must not be duplicated'
assert not out.exists(), 'Preserve existing native samples'
out.mkdir(parents=True)
state = {'schemaVersion': 4, 'pid': os.getpid(), 'startedAt': datetime.now(timezone.utc).isoformat(),
         'command': sys.argv, 'cwd': str(root), 'threads': 2, 'gpuUse': False,
         'resourcesBefore': resources, 'gpuBefore': gpu, 'status': 'running',
         'outerExitCode': None, 'sourceAdoptionApproved': False,
         'allFinalPixelsApproved': False, 'researchManipulations': 0,
         'recoveryReason': 'ffprobe stopped before one delayed final frame at the exclusive end; pad decoder read range and reuse 412 already verified selected PTS. No VFR inference.',
         'failedHistory': 'production/batches/unpublished-teaching-clarity-revision/motion-opening-native-execution-v3.json',
         'baselineChanged': False, 'output': str(out.relative_to(root)).replace('\\', '/')}
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
ffdir = Path('C:/ProgramData/HP/LCDDisplayHelper/bin')
windows = [{'id': 'roundabout-tail', 'firstFrame': 13447, 'endExclusiveFrame': 13860},
           {'id': 'tower-unused', 'firstFrame': 16614, 'endExclusiveFrame': 17340}]
baseline = json.loads((root / 'projects/motion-sickness-games/production/final-v1/plan.json').read_text('utf-8'))
baseline_cuts = baseline['cuts'] if 'cuts' in baseline else [c for scene in baseline['scenes'] for c in scene.get('cuts', [])]
records = []
try:
    for window in windows:
        first, end = window['firstFrame'], window['endExclusiveFrame']
        for cut in baseline_cuts:
            source_id = cut.get('sourceId', cut.get('idSource'))
            if source_id != 'PF5L_2g9UVQ':
                continue
            start_s = cut.get('sourceIn', cut.get('sourceStart', cut.get('inSeconds', cut.get('start'))))
            end_s = cut.get('sourceOut', cut.get('sourceEnd', cut.get('outSeconds', cut.get('end'))))
            if start_s is None or end_s is None:
                raise ValueError('Read exact baseline cut schema before adopting a range')
            a, b = round(float(start_s) * 60), round(float(end_s) * 60)
            assert end <= a or first >= b, f"Opening range reuses baseline {cut}"
        folder = out / window['id']
        folder.mkdir()
        probe_cmd = [str(ffdir / 'ffprobe.exe'), '-v', 'error', '-threads', '2',
                     '-read_intervals', f'{first / 60:.9f}%{end / 60 + 0.5:.9f}', '-select_streams', 'v:0',
                     '-show_frames', '-show_entries', 'frame=pts,best_effort_timestamp,pkt_duration', '-of', 'json', str(source)]
        reused_probe = root / 'shared/assets/presenting-game-scores/raw/motion-opening-native-v3/roundabout-tail/native-frames.json'
        reused_frames = []
        if window['id'] == 'roundabout-tail':
            reused_frames = json.loads(reused_probe.read_text('utf-8'))['frames']
            assert len([f for f in reused_frames if first * 256 <= int(f['pts']) < end * 256]) == 412
            probe_cmd[probe_cmd.index('-read_intervals') + 1] = f'{(end - 2) / 60:.9f}%{end / 60 + 0.5:.9f}'
        probe = subprocess.run(probe_cmd, capture_output=True, text=True, encoding='utf-8')
        (folder / 'probe-command.json').write_text(json.dumps(probe_cmd), encoding='utf-8')
        (folder / 'supplemental-native-frames.json').write_text(probe.stdout, encoding='utf-8')
        (folder / 'probe.stderr.log').write_text(probe.stderr, encoding='utf-8')
        assert probe.returncode == 0 and not probe.stderr.strip(), 'Native frame probe failed'
        combined = {int(f['pts']): f for f in reused_frames + json.loads(probe.stdout)['frames']}
        observed = [combined[pts] for pts in sorted(combined) if first * 256 <= pts < end * 256]
        (folder / 'native-frames.json').write_text(json.dumps({'frames': observed, 'reusedV3Frames': len(reused_frames),
            'reusedProbe': str(reused_probe.relative_to(root)) if reused_frames else None}), encoding='utf-8')
        assert [int(f['pts']) for f in observed] == list(range(first * 256, end * 256, 256)), 'Native PTS coverage mismatch'
        samples = sorted(set([first, first + 1, end - 2, end - 1] + list(range(first, end, 30))))
        filter_text = '+'.join(f'eq(pts,{n * 256})' for n in samples)
        cmd = [str(ffdir / 'ffmpeg.exe'), '-hide_banner', '-nostdin', '-threads', '2',
               '-ss', f'{first / 60 - 0.5:.9f}', '-copyts', '-i', str(source), '-an',
               '-filter_threads', '2', '-vf', f"select='{filter_text}',showinfo", '-fps_mode', 'passthrough',
               '-frames:v', str(len(samples)), str(folder / 'frame-%03d.png')]
        extraction = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        (folder / 'extract.stderr.log').write_text(extraction.stderr, encoding='utf-8')
        (folder / 'extract-command.json').write_text(json.dumps(cmd), encoding='utf-8')
        assert extraction.returncode == 0, 'Native sample extraction failed'
        pts = [int(value) for value in re.findall(r'Parsed_showinfo[^\n]*\bn:\s*\d+\s+pts:\s*(-?\d+)', extraction.stderr)]
        assert pts == [n * 256 for n in samples], 'Every sampled absolute PTS must match the expected source frame'
        images = sorted(folder.glob('frame-*.png'))
        assert len(images) == len(samples)
        font = ImageFont.truetype('C:/Windows/Fonts/consola.ttf', 18)
        sample_records = []
        boards = []
        for i, (frame, path) in enumerate(zip(samples, images)):
            sample_records.append({'sourceFrame': frame, 'pts': frame * 256, 'seconds': frame / 60,
                                   'path': str(path.relative_to(root)).replace('\\', '/'), 'sha256': sha(path)})
        for start in range(0, len(images), 6):
            board = Image.new('RGB', (1440, 1296), '#111111')
            draw = ImageDraw.Draw(board)
            for j, image_path in enumerate(images[start:start + 6]):
                with Image.open(image_path) as image:
                    image = image.convert('RGB').resize((720, 405))
                    x, y = (j % 2) * 720, (j // 2) * 432
                    board.paste(image, (x, y + 27))
                    draw.text((x + 8, y + 3), f"{window['id']} f{samples[start+j]} / pts{samples[start+j]*256}", fill='white', font=font)
            board_path = folder / f'board-{start // 6 + 1:02d}.jpg'
            board.save(board_path, quality=94)
            boards.append({'path': str(board_path.relative_to(root)).replace('\\', '/'), 'sha256': sha(board_path)})
        records.append({**window, 'frames': end - first, 'seconds': (end - first) / 60,
                        'nativeTimeBase': '1/15360', 'nativePtsStep': 256,
                        'probeExitCode': probe.returncode, 'extractionExitCode': extraction.returncode,
                        'allFramePtsVerified': True, 'samples': sample_records, 'boards': boards,
                        'sourceAdoptionApproved': False, 'directPixelReviewApproved': False})
    state.update(status='native-pts-and-samples-completed-awaiting-direct-review',
                 completedAt=datetime.now(timezone.utc).isoformat(), outerExitCode=0,
                 windows=records, sampleCount=sum(len(w['samples']) for w in records),
                 boardCount=sum(len(w['boards']) for w in records),
                 protectedInputSha256=audit['inputSha256'], sourceSha256=sha(source))
    for relative, expected in audit['inputSha256'].items():
        assert sha(root / relative) == expected
except Exception as error:
    state.update(status='failed-preserve-native-evidence', outerExitCode=1, error=str(error),
                 completedAt=datetime.now(timezone.utc).isoformat())
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    raise
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: state[k] for k in ['status', 'pid', 'outerExitCode', 'sampleCount', 'boardCount']}))
