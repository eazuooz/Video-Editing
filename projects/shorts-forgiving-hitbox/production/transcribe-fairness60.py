"""Cache one complete CPU ASR per fairness60 additions, voice or encoded mix.

Expected text is compared after recognition and is never supplied as a prompt.
This script does not run ASR merely by importing or compiling it.
"""
import os

os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'

from pathlib import Path
import argparse
import difflib
import hashlib
import json
import re
import subprocess

R = Path(__file__).resolve().parents[3]
P = Path(__file__).resolve().parents[1]
L = P / 'production/local/fairness-60s'
S = P / 'script/fairness-60s'
FF = Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')


def normalized(text):
    return re.sub(r'[^0-9a-z가-힣]', '', text.lower())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('role', choices=['additions', 'numbers', 'voice', 'mix'])
    role = parser.parse_args().role
    sources = {
        'additions': R / 'shared/output/narration/shorts-forgiving-hitbox/fairness60-additions-v1/fairness60-additions-v1.wav',
        'numbers': R / 'shared/output/narration/shorts-forgiving-hitbox/fairness60-code-numbers-v1/fairness60-code-numbers-v1.wav',
        'voice': L / 'narration-timeline.wav',
        'mix': L / 'final-mix.m4a',
    }
    source = sources[role]
    expected_path = S / (role+'.ko.txt' if role in ['additions','numbers'] else 'narration.ko.txt')
    expected = expected_path.read_text(encoding='utf8').strip()
    sha = hashlib.sha256(source.read_bytes()).hexdigest()
    out = L / f'asr-{role}-{sha[:12]}.json'
    if out.exists():
        print(str(out))
        return

    L.mkdir(parents=True, exist_ok=True)
    os.environ['PATH'] = str(FF.parent) + os.pathsep + os.environ.get('PATH', '')
    wav = L / f'asr-{role}-{sha[:12]}-16k.wav'
    if not wav.exists():
        subprocess.run([str(FF), '-v', 'error', '-n', '-i', str(source), '-ac', '1', '-ar', '16000', str(wav)], check=True)

    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

    torch.set_num_threads(3)
    dedicated = R / 'qwen3-tts/models/whisper-large-v3-turbo'
    model_id = str(dedicated) if (dedicated / 'config.json').exists() else 'openai/whisper-large-v3-turbo'
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, dtype=torch.float32, attn_implementation='eager', local_files_only=True,
    ).to('cpu')
    processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
    asr = pipeline(
        'automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu',
    )
    print('Transcribing complete fairness60 ' + role, flush=True)
    recognized = asr(
        str(wav), generate_kwargs={'language': 'korean', 'task': 'transcribe'},
        return_timestamps='word',
    )
    report = dict(
        role=role, revision='fairness-60s', input=source.relative_to(R).as_posix(),
        sha256=sha, fullInput=True, device='cpu', text=recognized['text'],
        chunks=recognized.get('chunks', []), expected=expected,
        expectedPath=expected_path.relative_to(R).as_posix(),
        expectedSha256=hashlib.sha256(expected_path.read_bytes()).hexdigest(),
        normalizedMatch=normalized(expected) == normalized(recognized['text']),
        similarity=difflib.SequenceMatcher(None, normalized(expected), normalized(recognized['text'])).ratio(),
        humanListening='pending',
    )
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'output': str(out), 'text': report['text'], 'similarity': report['similarity']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
