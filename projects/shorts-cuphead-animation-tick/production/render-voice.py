"""Prepare the selected Cuphead voice only after user games/editors exit.

--check performs read-only input validation, not GPU/device/model inspection.
The approved choice is GPU talker with CPU codec; --cpu is deliberately refused.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import time

from audio_revision import (
    P, R, L, VOICE, REVISION, AUTH_ID, guard, read, sha,
    assert_media_junction, gpu_lease, assert_owned_lease,
)


def save(path, document):
    assert_media_junction()
    path = Path(path)
    if not path.resolve().is_relative_to(L.resolve()):
        raise RuntimeError('Audio output must stay within this Cuphead C: audio directory.')
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.writing')
    with temporary.open('x', encoding='utf8') as stream:
        stream.write(json.dumps(document, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Read-only input guard; start no work.')
    parser.add_argument('--cpu', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.cpu:
        parser.error('CPU voice generation is disabled: wait for user game exit, then use the approved GPU path.')
    guard()
    manifest = read(P / 'production/tts-manifest.json')
    document = read(R / manifest['paths']['script'])
    jobs = [(scene['id'], index, text) for scene in document['scenes']
            for index, text in enumerate(scene['lines'], 1)]
    if args.check:
        print(json.dumps({'slug': P.name, 'revision': REVISION, 'inputGuard': 'passed',
                          'paragraphs': len(jobs), 'cpuFallbackAllowed': False,
                          'modelLoaded': False, 'gpuWorkStarted': False}, ensure_ascii=False))
        return
    if VOICE.exists():
        # Validate and reuse an exact completed assembly without loading a model.
        spec = importlib.util.spec_from_file_location('cuphead_assembly', P / 'production/assemble-paragraphs.py')
        assembly = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(assembly)
        assembly.main()
        return
    identity = {
        'revision': REVISION, 'authorizationId': AUTH_ID,
        'scriptSha256': sha(R / manifest['paths']['script']),
        'manifestSha256': sha(P / 'production/tts-manifest.json'),
        'voiceReferenceSha256': sha(R / manifest['tts']['reference']),
        'voiceReferenceTextSha256': sha(R / manifest['tts']['referenceText']),
    }
    receipt_path = L / 'reuse-takes.json'
    receipts = read(receipt_path) if receipt_path.exists() else {'inputLocks': identity, 'takes': {}}
    if receipts.get('inputLocks') != identity or not isinstance(receipts.get('takes'), dict):
        raise RuntimeError('Raw takes belong to different locked inputs; preserve them for review/versioning.')
    record = dict(identity, project=P.name, state='waiting-for-owned-gpu-lease',
                  allocatorCapMiB=4352, takes=[], foreignProcessesPaused=[])
    with gpu_lease('cuphead-approved-qwen-paragraph-voice') as lease:
        record.update(token=lease['token'], coordinator=lease['coordinator'],
                      resourceSnapshotBefore=lease['resourceSnapshotBefore'], startedAt=time.time())
        L.mkdir(parents=True, exist_ok=True)
        try:
            os.environ['HF_HUB_OFFLINE'] = '1'
            os.environ['TRANSFORMERS_OFFLINE'] = '1'
            os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'
            # Deliberately lazy imports; --check/import/--cpu cannot load a model.
            import torch
            import numpy as np
            import soundfile as sf
            from qwen_tts import Qwen3TTSModel

            assert_owned_lease(lease)
            torch.set_num_threads(3)
            torch.set_num_interop_threads(2)
            if not torch.cuda.is_available():
                raise RuntimeError('Approved GPU unavailable; preserve inputs and wait, with no CPU fallback.')
            torch.cuda.set_per_process_memory_fraction(
                4352 * 1048576 / torch.cuda.get_device_properties(0).total_memory)
            record.update(state='gpu-talker-cpu-codec', device='cuda:0')
            model = Qwen3TTSModel.from_pretrained(
                str(R / manifest['tts']['model']), device_map='cpu',
                dtype=torch.bfloat16, local_files_only=True,
            )
            assert_owned_lease(lease)
            model.model.talker.to('cuda:0')
            model.model.speaker_encoder.to('cuda:0')
            model.device = torch.device('cuda:0')
            model.model.speech_tokenizer.model.to(device='cpu', dtype=torch.float32)
            model.model.speech_tokenizer.device = torch.device('cpu')
            prompt = model.create_voice_clone_prompt(
                ref_audio=str(R / manifest['tts']['reference']),
                ref_text=(R / manifest['tts']['referenceText']).read_text(encoding='utf8').strip(),
                x_vector_only_mode=False,
            )
            out = VOICE.parent / 'chunks'
            out.mkdir(parents=True, exist_ok=True)
            for scene_id, index, text in jobs:
                assert_owned_lease(lease)
                path = out / f'{scene_id}-{index:02}.wav'
                if path.exists():
                    saved = receipts['takes'].get(path.name, {})
                    if saved.get('sha256') != sha(path) or saved.get('text') != text:
                        raise RuntimeError('Unreceipted/different raw take preserved: ' + str(path))
                    record['takes'].append(dict(saved, key=path.stem, reusedUnchanged=True))
                    continue
                print('Generating paragraph', len(record['takes']) + 1, 'of', len(jobs), flush=True)
                started = time.monotonic()
                waves, rate = model.generate_voice_clone(
                    text=[text], language='Korean', voice_clone_prompt=prompt,
                    non_streaming_mode=True, max_new_tokens=int(manifest['tts']['maxNewTokens']),
                )
                assert_owned_lease(lease)
                samples = np.asarray(waves[0], dtype=np.float32)
                if rate != 24000 or samples.ndim != 1 or not len(samples) or not np.isfinite(samples).all():
                    raise RuntimeError('Invalid generated paragraph PCM; no take saved.')
                temporary = path.with_suffix('.partial.wav')
                if temporary.exists():
                    raise RuntimeError('Incomplete raw take needs inspection before retry: ' + str(temporary))
                sf.write(temporary, samples, rate, subtype='FLOAT')
                temporary.rename(path)
                take = {'sha256': sha(path), 'text': text, 'seconds': len(samples) / rate,
                        'elapsedSeconds': time.monotonic() - started, 'rate': rate}
                receipts['takes'][path.name] = take
                save(receipt_path, receipts)
                record['takes'].append(dict(take, key=path.stem))
                save(L / 'tts-execution.partial.json', record)
            assert_owned_lease(lease)
            spec = importlib.util.spec_from_file_location('cuphead_assembly', P / 'production/assemble-paragraphs.py')
            assembly = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(assembly)
            assembly.main()
            record.update(state='completed', voiceSha256=sha(VOICE))
        except BaseException as error:
            record.update(state='failed', error=str(error))
            raise
        finally:
            if 'torch' in locals() and torch.cuda.is_initialized():
                record.update(peakAllocatedMiB=torch.cuda.max_memory_allocated() / 1048576,
                              peakReservedMiB=torch.cuda.max_memory_reserved() / 1048576)
            record['finishedAt'] = time.time()
            save(L / 'tts-execution.json', record)


if __name__ == '__main__':
    main()
