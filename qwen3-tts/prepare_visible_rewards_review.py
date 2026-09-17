"""Export a narration-only listening copy and measured edit cues after alignment.

No music/source download, no TTS generation, no publication approval.
Raw synthesis is retained; each listening export version is immutable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'projects/visible-rewards'


def ffmpeg(arguments):
    result = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-nostdin', *arguments],
                            capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return result.stderr


def measure(path):
    log = ffmpeg(['-i', str(path), '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'])
    return json.loads(re.findall(r'\{[^{}]+\}', log)[-1])


def timecode(seconds):
    milliseconds = round(seconds * 1000)
    minutes, rest = divmod(milliseconds, 60000)
    seconds, millis = divmod(rest, 1000)
    return f'{minutes:02}:{seconds:02}.{millis:03}'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', type=int, default=1)
    parser.add_argument('--resume', action='store_true', help='Inspect existing intermediate exports without overwriting them')
    args = parser.parse_args()
    manifest_path = PROJECT / 'project.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['approvals']['voice'] == 'approved-A-balanced'
    output = ROOT / manifest['tts']['outputDir']
    stem = manifest['tts']['filenameStem']
    raw = ROOT / manifest['paths']['narration']
    script = json.loads((ROOT / manifest['paths']['script']).read_text(encoding='utf-8'))
    timing = json.loads((output / f'{stem}.timing.json').read_text(encoding='utf-8'))
    asr = json.loads((output / f'{stem}.asr-review.json').read_text(encoding='utf-8'))
    assert asr['complete'] and asr['sceneCount'] == len(script['scenes'])
    assert timing['alignment']['captionCount'] >= len(timing['entries'])
    for scene in asr['scenes']:
        chunk = output / 'chunks' / f"{scene['scene']}-scene.wav"
        assert hashlib.sha256(chunk.read_bytes()).hexdigest() == scene['audio_sha256']
        assert scene['acousticChecks']['endingHeuristicPassed']
    # Confirm identical bilingual timelines, not only matching cue counts.
    cue_pattern = r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$'
    captions = [re.findall(cue_pattern, (ROOT / manifest['paths'][key]).read_text(encoding='utf-8'), re.M)
                for key in ('captionsKo', 'captionsEn')]
    assert captions[0] == captions[1] and captions[0]
    stats = measure(raw)
    target = float(manifest['audio']['narrationTargetLufs'])
    origins = {scene['id']: next(e['start'] for e in timing['entries'] if e['scene_id'] == scene['id'])
               for scene in script['scenes']}
    scene_levels, level_filters = [], []
    # Match chapter loudness with a constant gain per chapter, retaining phrasing
    # inside it. Switch gains in the middle of existing inter-chapter silence.
    for i, scene in enumerate(script['scenes']):
        level = measure(output / 'chunks' / f"{scene['id']}-scene.wav")
        correction = target - float(level['input_i'])
        start = max(0, origins[scene['id']] - manifest['tts']['sceneGapSeconds'] / 2)
        end = (origins[script['scenes'][i+1]['id']] - manifest['tts']['sceneGapSeconds'] / 2
               if i+1 < len(script['scenes']) else timing['duration_seconds'] + 1)
        level_filters.append(f"volume={correction:.6f}dB:enable='gte(t,{start:.6f})*lt(t,{end:.6f})'")
        scene_levels.append({'scene':scene['id'], 'rawLufs':float(level['input_i']), 'staticGainDb':correction})
    gain = .27
    for attempt in range(1, 6):
        wav = output / f'{stem}-listening-v{args.version}-level{attempt}.wav'
        mp3 = wav.with_suffix('.mp3')
        if (wav.exists() or mp3.exists()) and not (args.resume and wav.exists() and mp3.exists()):
            raise FileExistsError('Use a new --version to preserve the existing review copy')
        filters = (','.join(level_filters) + f',aresample=192000,volume={gain:.6f}dB,'
                   'alimiter=limit=0.724436:level=false:attack=5:release=80:latency=true,aresample=48000')
        if not wav.exists():
            ffmpeg(['-n', '-i', str(raw), '-af', filters, '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(wav)])
            ffmpeg(['-n', '-i', str(wav), '-c:a', 'libmp3lame', '-b:a', '192k', str(mp3)])
        wav_stats, mp3_stats = measure(wav), measure(mp3)
        error = target - float(mp3_stats['input_i'])
        finish_gain = 0.0
        # Once the safety limiter has controlled peaks, use available headroom
        # for a tiny final constant trim rather than repeatedly limiting again.
        if abs(error) > .3 and max(float(s['input_tp']) for s in (wav_stats, mp3_stats)) + error <= -1.7:
            original = wav
            wav = wav.with_stem(wav.stem + '-matched')
            mp3 = wav.with_suffix('.mp3')
            if wav.exists() or mp3.exists():
                raise FileExistsError('Matched copy exists; use a fresh review version')
            finish_gain = error
            ffmpeg(['-n', '-i', str(original), '-af', f'volume={finish_gain:.6f}dB', '-c:a', 'pcm_s16le', str(wav)])
            ffmpeg(['-n', '-i', str(wav), '-c:a', 'libmp3lame', '-b:a', '192k', str(mp3)])
            wav_stats, mp3_stats = measure(wav), measure(mp3)
            error = target - float(mp3_stats['input_i'])
        print(f'Listening level {attempt}: {mp3_stats["input_i"]} LUFS, {mp3_stats["input_tp"]} dBTP', flush=True)
        if abs(error) <= .3:
            break
        gain += error
    if abs(error) > .3 or any(float(stat['input_tp']) > -1.5 for stat in (wav_stats, mp3_stats)):
        raise RuntimeError('Review exports need loudness/peak adjustment')
    # Match build_project_timing.py's 30fps snap / 60fps presentation grid.
    cuts = [round(origins[scene['id']] * 30) / 30 for scene in script['scenes']]
    cuts.append(round(timing['duration_seconds'] * 30) / 30)
    games = ['Stardew Valley'] * 4 + ['Vampire Survivors', 'Stardew Valley / Vampire Survivors',
                                    'Vampire Survivors', 'Stardew Valley']
    fields = ['scene', 'start', 'end', 'segment_type', 'visual', 'source', 'source_audio', 'bgm', 'status']
    with (PROJECT / 'planning/edit-cues.csv').open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for i, scene in enumerate(script['scenes']):
            begin, end = cuts[i:i+2]
            split = min(end, begin + manifest['editing']['exampleSeconds'])
            for a, b, kind, visual, source, sound in (
                    (begin, split, 'real-example-placeholder', games[i], '', 'planned-quiet-source-not-attached'),
                    (split, end, 'channel-explanation-storyboard', scene['title'], 'original-diagram-plan', 'off')):
                writer.writerow(dict(zip(fields, [scene['id'], timecode(a), timecode(b), kind,
                    visual, source, sound, manifest['approvals']['music'], 'narration-review-footage-pending'])))
    report = {'project':'visible-rewards', 'rawSha256':hashlib.sha256(raw.read_bytes()).hexdigest(),
              'rawLoudness':stats, 'listeningWav':str(wav.relative_to(ROOT)).replace('\\','/'),
              'listeningMp3':str(mp3.relative_to(ROOT)).replace('\\','/'), 'wavLoudness':wav_stats,
              'mp3Loudness':mp3_stats, 'gainDb':gain, 'finishGainDb':finish_gain, 'targetLufs':target,
              'sceneLevels':scene_levels,
              'processing':'Constant gain per chapter + oversampled safety limiter; no tempo or pitch processing',
              'durationSeconds':timing['duration_seconds'], 'pairedCaptionCount':len(captions[0]),
              'bgmIncluded':False, 'sourceAudioIncluded':False, 'humanFullListeningApproved':False}
    (output / f'{stem}-listening-v{args.version}.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    editor_audio = ROOT / 'motion-canvas/src/projects/visible-rewards/assets/narration-review.wav'
    shutil.copy2(wav, editor_audio)
    manifest['paths']['editorNarration'] = str(editor_audio.relative_to(ROOT)).replace('\\', '/')
    manifest['paths']['narrationListening'] = report['listeningMp3']
    manifest['status'] = 'narration-review'
    manifest['editing']['timingStatus'] = 'measured-narration-aligned-captions-footage-pending'
    manifest['publishReady'] = False
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
