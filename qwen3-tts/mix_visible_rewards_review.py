"""Approved Wanderlust + A narration review. Actual gameplay audio is pending."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path

from prepare_visible_rewards_review import ffmpeg, measure

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/visible-rewards'


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=nw=1:nk=1', str(path)], text=True).strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', type=int, default=1)
    args = parser.parse_args()
    manifest_path = PROJECT / 'project.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    music = manifest['audio']['backgroundMusic']
    assert music['approvalStatus'] == 'approved' and music['title'] == 'Wanderlust'
    assert music['licenseStatus'].startswith('verified-official')
    assert manifest['approvals']['voice'] == 'approved-A-balanced'
    source = ROOT / music['file']
    narration = ROOT / manifest['paths']['editorNarration']
    total, music_duration = duration(narration), duration(source)
    source_stats = measure(source)
    gain = manifest['audio']['bgmTargetLufs'] - float(source_stats['input_i'])
    crossfade = float(manifest['audio']['bgmLoopCrossfadeSeconds'])
    count = max(1, math.ceil((total - crossfade) / (music_duration - crossfade)))
    output = ROOT / manifest['tts']['outputDir']
    base = output / f'visible-rewards-narration-wanderlust-review-v{args.version}'
    wav, mp3, m4a = (base.with_suffix(ext) for ext in ('.wav', '.mp3', '.m4a'))
    bgm = base.with_name(base.name + '-bgm-only.wav')
    if any(p.exists() for p in (wav, mp3, m4a, bgm)):
        raise FileExistsError('Use a new --version to retain previous review output')
    inputs = ['-n', '-i', str(narration)]
    for _ in range(count):
        inputs += ['-i', str(source)]
    # Equal-power mono-to-stereo duplication keeps narration integrated loudness.
    filters = ['[0:a]aformat=sample_rates=48000:channel_layouts=mono,'
               'pan=stereo|c0=0.70710678*c0|c1=0.70710678*c0,asplit=2[n][side]']
    for i in range(count):
        filters.append(f'[{i+1}:a]aresample=48000,volume={gain:.6f}dB[m{i}]')
    previous = 'm0'
    for i in range(1, count):
        filters.append(f'[{previous}][m{i}]acrossfade=d={crossfade}:c1=tri:c2=tri[j{i}]')
        previous = f'j{i}'
    filters.append(f'[{previous}]atrim=duration={total:.9f},asetpts=PTS-STARTPTS,'
                   f'afade=t=in:st=0:d=0.45,afade=t=out:st={total-.45:.9f}:d=0.45,asplit=2[b][background]')
    filters.append(f'[b][side]sidechaincompress=threshold={manifest["audio"]["duckingThreshold"]}:'
                   f'ratio={manifest["audio"]["duckingRatio"]}:attack=15:release=280:makeup=1[ducked]')
    filters.append('[n][ducked]amix=inputs=2:normalize=0:duration=first,'
                   'aresample=192000,alimiter=limit=0.75:level=false:latency=true:attack=5:release=80,'
                   'aresample=48000[mix]')
    ffmpeg(inputs + ['-filter_complex', ';'.join(filters), '-map', '[mix]', '-c:a', 'pcm_s16le', str(wav),
                     '-map', '[background]', '-c:a', 'pcm_s16le', str(bgm)])
    ffmpeg(['-n', '-i', str(wav), '-c:a', 'libmp3lame', '-b:a', '192k', str(mp3)])
    ffmpeg(['-n', '-i', str(wav), '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(m4a)])
    stats = {name:measure(path) for name,path in [('wav',wav),('mp3',mp3),('m4a',m4a),('bgm',bgm)]}
    if any(float(stats[name]['input_tp']) > -1.5 for name in ('wav','mp3','m4a')):
        raise RuntimeError('Review peak too high; retain exports and adjust before editor connection')
    if any(abs(duration(path) - total) > .08 for path in (wav,mp3,m4a,bgm)):
        raise RuntimeError('Review audio duration mismatch')
    # Verify every chapter has music, including explanation and eventual footage areas.
    import numpy as np
    import soundfile as sf
    background, rate = sf.read(bgm, dtype='float32', always_2d=True)
    timing = json.loads((output / f'{manifest["tts"]["filenameStem"]}.timing.json').read_text(encoding='utf-8'))
    windows = []
    seen = set()
    for entry in timing['entries']:
        if entry['scene_id'] in seen:
            continue
        seen.add(entry['scene_id'])
        for offset in (3, manifest['editing']['exampleSeconds'] + 3):
            start = entry['start'] + offset
            data = background[round(start*rate):round((start+2)*rate)]
            rms = float(np.sqrt(np.mean(data**2)))
            if rms < 1e-6:
                raise RuntimeError(f'Unexpected absent music near {start}')
            windows.append({'scene':entry['scene_id'], 'start':start, 'rmsDbfs':20*math.log10(rms)})
    editor = ROOT / 'motion-canvas/src/projects/visible-rewards/assets/audio-review.wav'
    shutil.copy2(wav, editor)
    report = {'kind':'Narration + approved BGM review; gameplay audio NOT included',
              'durationSeconds':total,'music':music,'musicSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'sourceMusicLoudness':source_stats,'musicGainDb':gain,'crossfadeSeconds':crossfade,
              'loopCount':count,'loudness':stats,'musicWindows':windows,
              'sourceAudioIncluded':False,'humanFullListeningApproved':False}
    base.with_suffix('.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    manifest['paths']['audioReview'] = str(mp3.relative_to(ROOT)).replace('\\','/')
    manifest['paths']['editorAudioReview'] = str(editor.relative_to(ROOT)).replace('\\','/')
    manifest['audio']['mixStatus'] = 'review-narration-bgm-only-gameplay-pending'
    manifest['status'] = 'audio-review-footage-pending'
    manifest['publishReady'] = False
    cue_path = PROJECT / 'planning/edit-cues.csv'
    with cue_path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        fields, rows = reader.fieldnames, list(reader)
    for row in rows:
        row['bgm'] = 'Wanderlust-approved-continuous'
        row['status'] = 'narration-bgm-review-footage-pending'
    with cue_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'review':str(mp3),'editor':str(editor),'seconds':total,'loudness':stats,
                      'nonSilentMusicWindows':len(windows)},ensure_ascii=False,indent=2),flush=True)


if __name__ == '__main__':
    main()
