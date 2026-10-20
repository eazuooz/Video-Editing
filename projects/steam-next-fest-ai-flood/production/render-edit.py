"""Render recording cuts at native speed, composite the full-length Motion Canvas
overlay sequence, then encode the clean/captioned pair with original brand/member."""
from pathlib import Path
import json, subprocess, hashlib, shutil, sys
R = Path(__file__).resolve().parents[3]; P = R / 'projects/steam-next-fest-ai-flood'; O = P / 'production/local/edit'
OVERLAY = R / 'shared/output/motion-canvas/steam-next-fest-ai-flood-overlay'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd, name):
    with (O / (name + '.log')).open('w', encoding='utf8') as f: r = subprocess.run(cmd, cwd=R, stdout=f, stderr=subprocess.STDOUT)
    if r.returncode: raise RuntimeError((O / (name + '.log')).read_text(encoding='utf8', errors='replace')[-2500:])
def frames(p):
    v = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height,r_frame_rate,nb_frames', '-of', 'json', str(p)]))['streams'][0]
    assert (v['width'], v['height'], v['r_frame_rate']) == (1920, 1080, '60/1'), v
    return int(v['nb_frames'])
enc = ['-c:v', 'libx264', '-threads', '6', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-video_track_timescale', '60000']
plan = read(O / 'edit-plan.json'); assert plan['timing'] == 'measured-and-asr-aligned'
stage = sys.argv[1] if len(sys.argv) > 1 else 'cuts'
if stage == 'cuts':
    for c in plan['cuts']:
        src = R / c['sourceFile']; out = O / (c['id'] + '.mp4'); receipt = O / (c['id'] + '.json')
        vf = 'fps=60,setsar=1'
        if c['holdFrames'] > 0: vf += f",tpad=stop_mode=clone:stop_duration={c['holdFrames'] / 60}"
        sig = {'sourceSha256': sha(src), 'frames': c['frames'], 'sourceStart': c['sourceStart'], 'filter': vf, 'codec': enc}
        if not (out.exists() and receipt.exists() and read(receipt) == sig):
            run(['ffmpeg', '-hide_banner', '-y', '-loglevel', 'warning', '-ss', str(c['sourceStart']), '-i', str(src), '-an', '-vf', vf, '-frames:v', str(c['frames']), *enc, str(out)], c['id'])
            receipt.write_text(json.dumps(sig, indent=2) + '\n')
        assert frames(out) == c['frames']; print('Rendered', c['id'], flush=True)
    (O / 'body-concat.txt').write_text('\n'.join("file '" + (O / (c['id'] + '.mp4')).as_posix() + "'" for c in plan['cuts']) + '\n', encoding='utf8')
    run(['ffmpeg', '-hide_banner', '-y', '-loglevel', 'warning', '-f', 'concat', '-safe', '0', '-i', str(O / 'body-concat.txt'), '-vf', 'settb=expr=1/60,setpts=N,setsar=1', '-r', '60', '-fps_mode', 'cfr', *enc, str(O / 'body-footage.mp4')], 'body-concat')
    assert frames(O / 'body-footage.mp4') == plan['bodyFrames']
elif stage == 'overlay':
    pngs = sorted(OVERLAY.glob('*.png')); assert len(pngs) >= plan['bodyFrames'], (len(pngs), plan['bodyFrames'])
    first = pngs[0].name; digits = len(first.split('.')[0].split('_')[-1]) if '_' in first else len(first.split('.')[0])
    pattern = str(OVERLAY / (first.rsplit('_', 1)[0] + '_%0' + str(digits) + 'd.png')) if '_' in first else str(OVERLAY / ('%0' + str(digits) + 'd.png'))
    start = int(first.split('.')[0].split('_')[-1])
    run(['ffmpeg', '-hide_banner', '-y', '-loglevel', 'warning', '-i', str(O / 'body-footage.mp4'), '-framerate', '60', '-start_number', str(start), '-i', pattern, '-filter_complex', '[1:v]format=rgba[ov];[0:v][ov]overlay=0:0:format=auto:shortest=1,format=yuv420p[v]', '-map', '[v]', '-frames:v', str(plan['bodyFrames']), '-r', '60', '-fps_mode', 'cfr', *enc, str(O / 'body-overlaid.mp4')], 'body-overlay')
    assert frames(O / 'body-overlaid.mp4') == plan['bodyFrames']
    for name, count in [('branding', 120), ('membership', 600)]:
        src = R / 'projects/game-reward-planning/production/local/reference-preserving-v2/edit' / (name + '.mp4'); assert frames(src) == count; shutil.copy2(src, O / (name + '.mp4'))
    (O / 'concat.txt').write_text('\n'.join("file '" + p.as_posix() + "'" for p in [O / 'branding.mp4', O / 'body-overlaid.mp4', O / 'membership.mp4']) + '\n', encoding='utf8')
elif stage in ('pair', 'audio'):
    mix = O / 'final-mix.wav'; aac = O / 'final-mix.m4a'; sig = sha(mix); receipt = O / 'aac-source.json'
    if not (aac.exists() and receipt.exists() and read(receipt).get('sha256') == sig):
        run(['ffmpeg', '-hide_banner', '-y', '-i', str(mix), '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', str(aac)], 'audio-encode'); receipt.write_text(json.dumps({'sha256': sig}) + '\n')
    if stage == 'audio':
        for kind in ['clean', 'captioned']:
            old = O / f'steam-next-fest-{kind}.mp4'; new = O / f'steam-next-fest-{kind}.audio-updated.mp4'
            run(['ffmpeg', '-v', 'error', '-y', '-i', str(old), '-i', str(aac), '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-t', str(plan['totalFrames'] / 60), '-movflags', '+faststart', str(new)], 'audio-remux-' + kind)
            assert frames(new) == plan['totalFrames']; new.replace(old)
        raise SystemExit(0)
    graph = '[0:v]settb=expr=1/60,setpts=N,setsar=1,split=2[clean][capin];[capin]ass=' + (O / 'captions.ko.ass').relative_to(R).as_posix() + '[captioned]'
    args = ['ffmpeg', '-hide_banner', '-y', '-reinit_filter', '0', '-f', 'concat', '-safe', '0', '-i', str(O / 'concat.txt'), '-i', str(aac), '-filter_complex', graph]
    for kind in ['clean', 'captioned']: args += ['-map', f'[{kind}]', '-map', '1:a', '-frames:v', str(plan['totalFrames']), '-t', str(plan['totalFrames'] / 60), '-r', '60', '-fps_mode', 'cfr', '-enc_time_base', '1:60', *enc, '-c:a', 'copy', '-movflags', '+faststart', str(O / f'steam-next-fest-{kind}.mp4')]
    run(args, 'pair-encode')
    for kind in ['clean', 'captioned']: assert frames(O / f'steam-next-fest-{kind}.mp4') == plan['totalFrames']
else: raise ValueError(stage)
