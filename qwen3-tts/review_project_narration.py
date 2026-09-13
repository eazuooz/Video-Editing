"""Cache per-scene Whisper read-backs with word timestamps for local TTS QA.

This is evidence for review, not automatic approval of the speaker's delivery.
Use --watch while rendering; rerun without --watch after synthesis completes.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import time
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]


def normalize(text: str) -> str:
    text = text.lower().replace('ai', '에이아이').replace('api', '에이피아이')
    return re.sub(r'[^a-z0-9가-힣]', '', text)


def acoustic_evidence(wav: Path, config: dict) -> dict:
    samples, rate = sf.read(wav, dtype='float32', always_2d=True)
    mono = samples.mean(axis=1)
    rms = float(np.sqrt(np.mean(mono**2)))
    ratio = float(np.sqrt(np.mean(mono[-round(rate*.05):]**2))) / max(rms, 1e-12)
    envelope = np.convolve(np.abs(mono[-round(rate*.4):]), np.ones(round(rate*.005))/round(rate*.005), mode='same')
    peak = int(np.argmax(envelope))
    below = np.where(envelope[peak:] < envelope[peak]*.1)[0]
    decay = float(below[0]/rate*1000) if len(below) else None
    passed = ((ratio <= config['tailRatioThreshold'] and (decay is None or decay >= config['tailDecayMsThreshold']))
              or (ratio <= .025 and (decay is None or decay >= 35)))
    return {'duration':len(mono)/rate, 'sampleRate':rate, 'rms':rms,
            'tailRatio':ratio, 'decayMs':decay, 'endingHeuristicPassed':passed,
            'samplePeakDbfs':float(20*np.log10(max(np.max(np.abs(samples)),1e-12)))}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument('--project', required=True)
    p.add_argument('--device', choices=['cpu', 'cuda'], default='cuda')
    p.add_argument('--watch', action='store_true')
    p.add_argument('--scenes', default='', help='Only create/refresh these comma-separated scene caches; other valid caches are retained')
    args = p.parse_args()
    project = ROOT / 'projects' / args.project
    project.resolve().relative_to((ROOT / 'projects').resolve())
    manifest = json.loads((project / 'project.json').read_text(encoding='utf-8'))
    script = json.loads((ROOT / manifest['paths']['script']).read_text(encoding='utf-8'))
    selected = {value.strip().zfill(2) for value in args.scenes.split(',') if value.strip()}
    unknown = selected - {scene['id'] for scene in script['scenes']}
    if unknown:
        raise ValueError(f'Unknown scene IDs: {sorted(unknown)}')
    out = ROOT / manifest['tts']['outputDir']
    qa = out / 'asr'
    qa.mkdir(parents=True, exist_ok=True)
    transcriber = None
    deadline = time.monotonic() + 7200
    while True:
        complete = True
        summaries = []
        for scene in script['scenes']:
            wav = out / 'chunks' / f"{scene['id']}-scene.wav"
            if not wav.exists():
                complete = False
                continue
            digest = hashlib.sha256(wav.read_bytes()).hexdigest()
            cached = qa / f"{scene['id']}.json"
            result = json.loads(cached.read_text(encoding='utf-8')) if cached.exists() else {}
            if result.get('audio_sha256') != digest:
                if selected and scene['id'] not in selected:
                    complete = False
                    continue
                if transcriber is None:
                    import torch
                    from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
                    torch.set_num_threads(2)
                    device = 'cuda:0' if args.device == 'cuda' else 'cpu'
                    dtype = torch.float16 if args.device == 'cuda' else torch.float32
                    model_id = 'openai/whisper-large-v3-turbo'
                    model = AutoModelForSpeechSeq2Seq.from_pretrained(
                        model_id, dtype=dtype, low_cpu_mem_usage=True,
                        use_safetensors=True, attn_implementation='eager',
                    ).to(device)
                    processor = AutoProcessor.from_pretrained(model_id)
                    transcriber = pipeline('automatic-speech-recognition', model=model,
                        tokenizer=processor.tokenizer, feature_extractor=processor.feature_extractor,
                        dtype=dtype, device=device)
                print(f"Transcribing scene {scene['id']} on {args.device}", flush=True)
                raw = transcriber(str(wav), generate_kwargs={'language':'korean', 'task':'transcribe'},
                                  return_timestamps='word')
                result = {'scene':scene['id'], 'audio_sha256':digest, 'text':raw['text'], 'words':raw['chunks']}
                cached.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
            expected = ' '.join(scene['lines'])
            a, b = normalize(expected), normalize(result['text'])
            match = difflib.SequenceMatcher(None, a, b, autojunk=False)
            changes = [{'kind':tag, 'expected':a[i:j], 'recognized':b[k:l]}
                       for tag,i,j,k,l in match.get_opcodes() if tag != 'equal']
            summaries.append({'scene':scene['id'], 'audio_sha256':digest,
                              'similarity':match.ratio(), 'differences':changes,
                              'acousticChecks':acoustic_evidence(wav, manifest['tts']),
                              'expected':expected, 'recognized':result['text']})
        report = {'kind':'ASR evidence, human listening approval separate', 'complete':complete,
                  'sceneCount':len(summaries), 'scenes':summaries}
        (out / f"{manifest['tts']['filenameStem']}.asr-review.json").write_text(
            json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (out / f"{manifest['tts']['filenameStem']}.asr-review.txt").write_text(
            '\n\n'.join(f"[{s['scene']}] {s['recognized']}" for s in summaries)+'\n',encoding='utf-8')
        if complete:
            print('Read-back complete; inspect differences and voice quality.', flush=True)
            break
        if not args.watch:
            if selected:
                print(f'Selected scene caches reviewed; {len(summaries)}/{len(script["scenes"])} current caches available.', flush=True)
                break
            raise RuntimeError('Some scene WAVs are missing; render first or use --watch')
        if time.monotonic() > deadline:
            raise TimeoutError('Waiting for scene WAVs timed out')
        time.sleep(15)


if __name__ == '__main__':
    main()
