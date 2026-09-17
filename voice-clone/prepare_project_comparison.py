"""Inspect endings and loudness-match a generated comparison take for listening."""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]


def run_ffmpeg(args: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-nostdin', *args],
                            text=True, capture_output=True, encoding='utf-8', errors='replace')
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return result


def measure(path: Path) -> dict:
    result = run_ffmpeg(['-i', str(path), '-af', 'loudnorm=I=-16:TP=-2:LRA=11:print_format=json', '-f', 'null', '-'])
    return json.loads(re.findall(r'\{[^{}]+\}', result.stderr)[-1])


def ending_quality(wav: np.ndarray, sr: int) -> dict:
    rms = lambda x: float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0
    ratio = rms(wav[-max(1, int(sr * .05)):]) / max(rms(wav), 1e-10)
    tail = np.abs(wav[-int(sr * .4):])
    size = max(1, int(sr * .005))
    smooth = np.convolve(tail, np.ones(size) / size, mode='same')
    peak = int(np.argmax(smooth))
    below = np.where(smooth[peak:] < smooth[peak] * .1)[0]
    decay = float(below[0] / sr * 1000) if len(below) else math.inf
    passed = (ratio <= .07 and decay >= 70) or (ratio <= .025 and decay >= 35)
    return {'tailRatio': ratio, 'tailDecayMs': decay if math.isfinite(decay) else None,
            'tailDecayUnbounded': not math.isfinite(decay), 'automaticEndingCheckPassed': passed,
            'humanListeningRequired': True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('take_report', type=Path)
    parser.add_argument('--inspect-only', action='store_true')
    parser.add_argument('--target-lufs', type=float, default=-18.5)
    parser.add_argument('--export-version', type=int, default=3)
    args = parser.parse_args()
    report_path = args.take_report.resolve()
    report_path.relative_to(ROOT)
    report = json.loads(report_path.read_text(encoding='utf-8'))
    raw = (ROOT / report['wav']).resolve()
    raw.relative_to(ROOT)
    wav, sr = sf.read(raw, dtype='float32')
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    checks = ending_quality(wav, sr)
    stats = measure(raw)
    quality = {'raw': str(raw), 'ending': checks, 'inputLoudness': stats,
               'asrReview': str(report_path.with_suffix('.asr.txt'))}
    quality_path = report_path.with_suffix('.quality.json')
    quality_path.write_text(json.dumps(quality, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(quality, ensure_ascii=False), flush=True)
    if args.inspect_only:
        return
    if not checks['automaticEndingCheckPassed']:
        raise RuntimeError('Possible cut-off ending: regenerate before loudness processing; raw take preserved')
    # Match the decoded listening MP3, not merely the normalizer's requested value.
    # Use static gain plus a safety peak limiter; do not ride every phrase's volume.
    # Each attempt starts from RAW and gets its own name, preserving previous exports.
    gain = args.target_lufs - float(stats['input_i']) + .27
    for attempt in range(1, 6):
        suffix = f'-listening-v{args.export_version}-level{attempt}'
        output = raw.with_name(raw.name.replace('-raw.wav', suffix + '.wav'))
        mp3 = output.with_suffix('.mp3')
        if output.exists() or mp3.exists():
            raise FileExistsError('Listening export already exists; increment --export-version')
        norm = (f'aresample=192000,volume={gain:.6f}dB,'
                'alimiter=limit=0.724436:level=false:attack=5:release=80:latency=true,'
                'aresample=48000')
        run_ffmpeg(['-n', '-i', str(raw), '-af', norm, '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(output)])
        run_ffmpeg(['-n', '-i', str(output), '-c:a', 'libmp3lame', '-b:a', '192k', str(mp3)])
        measured_wav, measured_mp3 = measure(output), measure(mp3)
        error = args.target_lufs - float(measured_mp3['input_i'])
        if abs(error) <= .3:
            break
        gain += error
    quality.update({'listeningWav': str(output), 'listeningMp3': str(mp3),
                    'listeningLoudness': measured_wav, 'mp3Loudness': measured_mp3,
                    'speedProcessing': False, 'pitchProcessing': False,
                    'previewTargetLufs': args.target_lufs, 'gainDb': gain,
                    'processing': 'Static gain + oversampled peak limiter; raw take retained'})
    quality_path.write_text(json.dumps(quality, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    if abs(float(measured_mp3['input_i']) - args.target_lufs) > .3 or any(
            float(m['input_tp']) > -1.5 for m in (measured_wav, measured_mp3)):
        raise RuntimeError('Export created but loudness/peak requires review; do not mark ready')
    print(json.dumps({'listeningWav': str(output), 'listeningMp3': str(mp3),
                      'lufs': measured_mp3['input_i'], 'truePeak': measured_mp3['input_tp']}), flush=True)


if __name__ == '__main__':
    main()
