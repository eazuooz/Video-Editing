"""One targeted independent CPU pass for explicitly flagged current complete contexts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from audio_revision import P, R, L, VOICE, REVISION, read, guard


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ranges', required=True,
                        help='JSON current-voice-hash with id/range/reason for each ambiguous complete context.')
    args = parser.parse_args()
    guard()
    request = read(args.ranges)
    digest = sha(VOICE)
    whole = L / f'asr-voice-{digest[:12]}.json'
    original = read(whole)
    assert request['voiceSha256'] == digest == original['sha256']
    assert original['fullInput'] and original['rawRecognitionUnmodified']
    output = L / 'asr-context-current.json'
    assert not output.exists(), 'Reuse the one current context pass; do not repeat unchanged ASR.'
    ranges = request['contexts']
    assert ranges and len({x['id'] for x in ranges}) == len(ranges)
    for item in ranges:
        assert item['reason'] and len(item['range']) == 2
        start, end = map(float, item['range'])
        assert 0 <= start < end <= original['inputDurationSeconds']
        assert item['completeContext'] is True
    binary = Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/'
                  'Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
    os.environ['PATH'] = str(binary) + os.pathsep + os.environ['PATH']
    for key in ['HF_HUB_OFFLINE', 'TRANSFORMERS_OFFLINE']:
        os.environ[key] = '1'
    for key in ['OMP_NUM_THREADS', 'MKL_NUM_THREADS']:
        os.environ[key] = '3'
    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
    torch.set_num_threads(3)
    torch.set_num_interop_threads(1)
    directory = R / 'qwen3-tts/models/whisper-large-v3-turbo'
    model_id = str(directory) if (directory / 'config.json').exists() else 'openai/whisper-large-v3-turbo'
    started = time.monotonic()
    model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, dtype=torch.float32,
             attn_implementation='eager', local_files_only=True).to('cpu')
    processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
    recognize = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
             feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
    results = []
    for item in ranges:
        clip = L / f"asr-context-{item['id']}.wav"
        start, end = item['range']
        assert not clip.exists(), 'Preserve an existing partial context conversion for inspection.'
        subprocess.run([str(binary / 'ffmpeg.exe'), '-v', 'error', '-n', '-ss', str(start),
                        '-i', str(VOICE), '-t', str(end - start), '-ar', '16000', '-ac', '1',
                        '-c:a', 'pcm_s16le', str(clip)], check=True)
        result = recognize(str(clip), generate_kwargs={'language': 'korean', 'task': 'transcribe',
                           'num_beams': 3}, return_timestamps='word')
        results.append({**item, 'clip': clip.relative_to(R).as_posix(), 'clipSha256': sha(clip),
                        'text': result['text'], 'chunks': result['chunks']})
        print(json.dumps({'id': item['id'], 'text': result['text']}, ensure_ascii=False), flush=True)
    assert sha(VOICE) == digest
    report = {'revision': REVISION, 'voiceSha256': digest, 'wholeAsrSha256': sha(whole),
              'rangesRequestSha256': sha(args.ranges), 'expectedTextPromptUsed': False,
              'fullAsrRepeated': False, 'rawRecognitionUnmodified': True,
              'device': 'cpu', 'cpuThreads': 3, 'decoding': 'beam3 versus original greedy',
              'contexts': results, 'elapsedSeconds': round(time.monotonic() - started, 3),
              'humanListening': 'pending'}
    with output.open('x', encoding='utf8') as handle:
        handle.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
