"""One independent CPU ASR of the selected complete ambiguous voice context.

Preserves raw recognition and relative word timestamps without an expected-text
prompt. This is not a full-voice or final-mix ASR and does not replace listening.
"""
from pathlib import Path
import importlib.util
import json
import os
import subprocess
import time
import wave

P = Path(__file__).resolve().parents[1]
R = P.parents[1]
L = P / 'production/local'
START = 23.4
END = 40.5
EXPECTED_SOURCE_SHA_PREFIX = '7411ff6ab07e'


def main():
    spec = importlib.util.spec_from_file_location('zombie_transcribe_helpers', P / 'production/transcribe.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    project = helper.read(P / 'project.json')
    source = helper.repository_path(project['paths'].get('voiceNarration', helper.DEFAULT_VOICE))
    digest = helper.sha(source)
    if not digest.startswith(EXPECTED_SOURCE_SHA_PREFIX):
        raise RuntimeError('Selected source hash differs from the authorized voice context.')
    output = L / 'voice-contexts.json'
    wav = L / 'voice-contexts-23p4-40p5.wav'
    partial = L / 'voice-contexts.partial.json'
    if output.exists():
        prior = helper.read(output)
        if prior.get('sourceSha256') != digest or prior.get('sourceRange') != [START, END]:
            raise RuntimeError('Existing context cache belongs to a different input or interval.')
        print(json.dumps({'cached': True, 'output': helper.relative(output)}, ensure_ascii=False))
        return
    pre_asr_failures = []
    if partial.exists():
        prior = helper.read(partial)
        if prior.get('status') != 'failed-before-asr' or prior.get('sourceSha256') != digest:
            raise RuntimeError('A prior incomplete context run exists; inspect it before retrying.')
        pre_asr_failures = prior.get('preAsrFailures', [])

    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['OMP_NUM_THREADS'] = '3'
    os.environ['MKL_NUM_THREADS'] = '3'
    ffmpeg = helper.ffmpeg_path()
    os.environ['PATH'] = str(ffmpeg.parent) + os.pathsep + os.environ.get('PATH', '')
    if not wav.exists():
        subprocess.run([
            str(ffmpeg), '-v', 'error', '-n', '-ss', str(START), '-i', str(source),
            '-t', str(END - START), '-ac', '1', '-ar', '16000',
            '-c:a', 'pcm_s16le', str(wav),
        ], check=True)
    with wave.open(str(wav), 'rb') as audio:
        if audio.getnchannels() != 1 or audio.getframerate() != 16000:
            raise RuntimeError('Context must be16k mono PCM.')
        measured = audio.getnframes() / audio.getframerate()
    if abs(measured - (END - START)) > 1 / 16000:
        raise RuntimeError('Extracted context duration differs from selected interval.')
    partial.write_text(json.dumps({
        'status': 'running', 'sourceSha256': digest,
        'sourceRange': [START, END], 'device': 'cpu', 'cpuThreads': 3,
    }, indent=2) + '\n', encoding='utf8')

    import torch
    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

    torch.set_num_threads(3)
    torch.set_num_interop_threads(1)
    model_path = R / 'qwen3-tts/models/whisper-large-v3-turbo'
    model_id = str(model_path) if (model_path / 'config.json').exists() else 'openai/whisper-large-v3-turbo'
    started = time.monotonic()
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, dtype=torch.float32, attn_implementation='eager',
        local_files_only=True,
    ).to('cpu')
    processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
    recognize = pipeline(
        'automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor, dtype=torch.float32,
        device='cpu',
    )
    print('Transcribing one independent complete context23.4–40.5s on CPU,3threads', flush=True)
    raw = recognize(
        str(wav), generate_kwargs={'language': 'korean', 'task': 'transcribe'},
        return_timestamps='word',
    )
    if not raw.get('text') or not raw.get('chunks'):
        raise RuntimeError('Context returned no usable recognition or timestamps.')
    if helper.sha(source) != digest:
        raise RuntimeError('Source voice changed during context recognition.')
    absolute_chunks = [
        dict(text=chunk['text'], timestamp=[
            None if stamp is None else round(stamp + START, 5)
            for stamp in chunk['timestamp']
        ]) for chunk in raw['chunks']
    ]
    report = dict(
        schemaVersion=1, purpose='independent-complete-context-for-ambiguous-pronunciation',
        source=helper.relative(source), sourceSha256=digest, sourceRange=[START, END],
        fullVoiceInput=False, completeContext=True,
        contextAudio=helper.relative(wav), contextAudioSha256=helper.sha(wav),
        contextDurationSeconds=measured, model=model_id,
        device='cpu', cpuThreads=3, expectedTextPromptUsed=False,
        rawRecognitionUnmodified=True, text=raw['text'], chunks=raw['chunks'],
        rawRecognition=raw, absoluteSourceChunks=absolute_chunks,
        elapsedSeconds=round(time.monotonic() - started, 3),
        humanListening='pending', pronunciationVerdict='pending-human-listening',
        preAsrFailures=pre_asr_failures,
    )
    partial.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    partial.replace(output)
    print(json.dumps({'output': helper.relative(output), 'text': raw['text'], 'humanListening': 'pending'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
