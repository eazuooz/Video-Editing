"""One current encoded-mix ASR on CPU, cached by the exact AAC input hash.

Root runs --review after verify-short.py. Existing source-ASR evidence is
reused only with the verified exact approved PCM excerpt. This file never
generates TTS or treats an ASR match as human listening/full text review.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import os
import re
import wave
from datetime import datetime, timezone
from pathlib import Path

_spec = importlib.util.spec_from_file_location('fov_renderer_for_asr', Path(__file__).with_name('render-short.py'))
renderer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(renderer)
ROOT, PROJECT, OUT = renderer.ROOT, renderer.PROJECT, renderer.OUT


def ensure(condition, message):
    if not condition:
        raise AssertionError(message)


def normalized(text):
    # Only punctuation/spacing/case normalization. Keep content disagreements,
    # numbers and homophones visible for direct full-context review.
    return re.sub(r'[^0-9a-z가-힣]+', '', text.lower())


def artifact(path):
    path = Path(path)
    return dict(path=renderer.rel(path), sha256=renderer.sha(path), bytes=path.stat().st_size)


def review():
    renderer.check_render_authorization()
    captioned = OUT/f'{PROJECT.name}.captioned.mp4'
    current_hash = renderer.sha(captioned)
    qa_dir = OUT/'qa'/current_hash[:16]
    integrity = renderer.read(qa_dir/'integrity.json')
    ensure(integrity['status'] == 'pass', 'Run current final-pair integrity QA first')
    ensure(integrity['files']['captioned']['file']['sha256'] == current_hash, 'Integrity report is stale')
    continuity = renderer.read(qa_dir/'audio-review.json')
    ensure(continuity['exactRetainedPcm'], 'Source PCM excerpt equivalence has not passed')
    decoded_info = integrity['files']['captioned']['fullDecode']['decodedAudio']
    decoded = ROOT/decoded_info['path']
    ensure(renderer.sha(decoded) == decoded_info['sha256'], 'Decoded audio changed after whole-output QA')
    mix = OUT/'final-mix.m4a'
    mix_hash = renderer.sha(mix)
    expected_path = PROJECT/'script/narration.ko.txt'
    expected = expected_path.read_text(encoding='utf-8-sig').strip()
    ensure(expected, 'Expected complete narration is empty')
    cache = OUT/'asr-cache'/mix_hash[:16]
    cache.mkdir(parents=True, exist_ok=True)
    result_path = cache/'result.json'
    if result_path.exists():
        result = renderer.read(result_path)
        ensure(result['mixSha256'] == mix_hash and result['device'] == 'cpu' and result['completeEncodedMix'], 'ASR cache does not match exact current mix')
        reused = True
    else:
        # This is a resample of the already decoded AAC PCM, not another video
        # or AAC integrity decode. It includes the full opening/tail silence.
        wav = cache/'encoded-audio-16k.wav'
        resample_receipt = cache/'resample.json'
        if wav.exists():
            previous = renderer.read(resample_receipt)
            ensure(previous['decodedInputSha256'] == decoded_info['sha256'] and previous['outputSha256'] == renderer.sha(wav), 'Partial ASR resample input differs')
        else:
            renderer.run([renderer.FFMPEG, '-v', 'error', '-n', '-i', str(decoded), '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', str(wav)])
            renderer.write(resample_receipt, dict(decodedInputSha256=decoded_info['sha256'], outputSha256=renderer.sha(wav)))
        with wave.open(str(wav), 'rb') as stream:
            ensure(stream.getframerate() == 16000 and stream.getnchannels() == 1 and stream.getnframes() == 480000, 'ASR input must be the entire30s mono16k mix')
        started = cache/'started.json'
        ensure(not started.exists(), 'An earlier current-mix ASR attempt has no result. Inspect it instead of silently repeating it.')
        os.environ['PATH'] = str(Path(renderer.FFMPEG).parent)+os.pathsep+os.environ.get('PATH', '')
        import torch
        from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
        torch.set_num_threads(4)
        model_path = ROOT/'qwen3-tts/models/whisper-large-v3-turbo'
        model_id = str(model_path) if (model_path/'config.json').is_file() else 'openai/whisper-large-v3-turbo'
        # The previously successful production uses the existing Hugging Face
        # cache when no dedicated project model folder exists. Both branches
        # prohibit network downloads; a missing cache is an explicit failure.
        model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id, dtype=torch.float32,
            attn_implementation='eager', local_files_only=True).to('cpu')
        processor = AutoProcessor.from_pretrained(model_id, local_files_only=True)
        asr = pipeline('automatic-speech-recognition', model=model, tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor, dtype=torch.float32, device='cpu')
        renderer.write(started, dict(startedAt=datetime.now(timezone.utc).isoformat(), mixSha256=mix_hash,
            decodedInputSha256=decoded_info['sha256'], device='cpu', status='in-progress-no-duplicate-automatic-attempt'))
        recognized = asr(str(wav), generate_kwargs={'language': 'korean', 'task': 'transcribe'}, return_timestamps='word')
        result = dict(schemaVersion=1, mixSha256=mix_hash, decodedInputSha256=decoded_info['sha256'],
            input16k=artifact(wav), device='cpu', model='installed-whisper-large-v3-turbo', completeEncodedMix=True,
            expectedTranscriptPromptUsed=False, recognized=recognized['text'], words=recognized['chunks'],
            completedAt=datetime.now(timezone.utc).isoformat(), newTtsJobs=0)
        renderer.write(result_path, result)
        reused = False
    recognized = result['recognized']
    ensure(recognized.strip(), 'Current whole-mix ASR returned no text')
    wanted, heard = normalized(expected), normalized(recognized)
    matcher = difflib.SequenceMatcher(None, wanted, heard)
    differences = [dict(kind=kind, expected=wanted[a:b], recognized=heard[c:d])
                   for kind, a, b, c, d in matcher.get_opcodes() if kind != 'equal']
    source_map = renderer.read(PROJECT/'script/raw-source-map.json')['narration']
    report = dict(schemaVersion=1, captionedSha256=current_hash, mixSha256=mix_hash,
        expectedText=expected, expectedTextFile=artifact(expected_path), recognized=recognized, words=result['words'],
        punctuationSpacingNormalizedSimilarity=matcher.ratio(), fullTextDifferences=differences,
        scope='Entire current30second encoded mix, including silent2.8second opening and.48second tail',
        device='cpu', expectedTranscriptPromptUsed=False, asrResult=artifact(result_path), asrResultReused=reused,
        rawSourceAsrReuse=dict(exactRetainedPcmVerified=True, sourceInterval=[81.26, 107.98],
            sourceSha256=source_map['sha256'], existingWordEvidence=artifact(ROOT/source_map['wordEvidence'])),
        directWholeTextReviewed=False, directWholeTextReview='pending-compare-the-complete-recognized-text',
        sourceLevelContinuity=artifact(qa_dir/'audio-review.json'),
        humanWholeListeningAndPronunciation='pending-user-final-review', newTtsJobs=0,
        asrPassIsNotHumanListening=True, endingHeuristicUsed=False)
    renderer.write(qa_dir/'final-mix-asr.json', report)
    renderer.write(OUT/'final-mix-asr.json', report)
    print(recognized)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--asr', '--review', dest='review', action='store_true', help='Root-only one-current-mix CPU ASR after current integrity QA')
    args = parser.parse_args()
    if not args.review:
        parser.error('--review required; importing starts no work')
    review()


if __name__ == '__main__':
    main()
