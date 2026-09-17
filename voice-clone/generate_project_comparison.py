"""Generate an approved same-text local voice comparison; never upload references.

Run A in qwen3-tts/.venv and B in voice-clone/.venv. Outputs are immutable takes.
This is a sample renderer, not the full narration/timing pipeline.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import random
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

ROOT = Path(__file__).resolve().parents[1]


def local_path(relative: str) -> Path:
    result = (ROOT / relative).resolve()
    result.relative_to(ROOT)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--variant', choices=['A', 'B'], required=True)
    parser.add_argument('--take', type=int, default=1)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--checkpoint-dir', type=Path)
    args = parser.parse_args()
    if args.take < 1:
        raise ValueError('take must be positive')
    manifest = json.loads(local_path(f'projects/{args.project}/project.json').read_text(encoding='utf-8'))
    if manifest['slug'] != args.project:
        raise ValueError('project mismatch')
    if any(manifest['approvals'].get(key) != 'approved' for key in ('script', 'sampleText')):
        raise RuntimeError('Script and sample-text approval are required before synthesis')
    plan_path = local_path(manifest['tts']['voiceSamplePlan'])
    plan = json.loads(plan_path.read_text(encoding='utf-8'))
    if plan['status'] not in ('approved-for-sample-generation', 'awaiting-listening-selection'):
        raise RuntimeError('Sample plan is not approved for generation')
    variant = next(v for v in plan['variants'] if v['id'] == args.variant)
    reference = local_path(plan['reference'])
    ref_text_path = local_path(plan['referenceText'])
    for path in (reference, ref_text_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    if not torch.cuda.is_available():
        raise RuntimeError('CUDA GPU required')
    output_dir = local_path(f'shared/audio-samples/{args.project}/tone-v1')
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f'{args.variant.lower()}-take{args.take:02d}'
    output = output_dir / f'{stem}-raw.wav'
    report_path = output_dir / f'{stem}.json'
    if output.exists() or report_path.exists():
        raise FileExistsError('Do not overwrite a previous take; choose --take N')
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    text = plan['text']
    settings = {}
    if args.variant == 'A':
        from qwen_tts import Qwen3TTSModel
        model = Qwen3TTSModel.from_pretrained(
            str(local_path(manifest['tts']['model'])),
            device_map='cuda:0', dtype=torch.bfloat16,
        )
        prompt = model.create_voice_clone_prompt(
            ref_audio=str(reference),
            ref_text=ref_text_path.read_text(encoding='utf-8').strip(),
            x_vector_only_mode=False,
        )
        settings = {'non_streaming_mode': True, 'max_new_tokens': 512}
        wavs, sr = model.generate_voice_clone(
            text=text, language='Korean', voice_clone_prompt=prompt, **settings,
        )
        wav = np.asarray(wavs[0], dtype=np.float32).reshape(-1)
        package = 'qwen-tts'
    else:
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        if args.checkpoint_dir is None:
            raise ValueError('B requires a complete local --checkpoint-dir')
        checkpoint = args.checkpoint_dir.resolve()
        for name in ('ve.pt', 't3_mtl23ls_v2.safetensors', 's3gen.pt',
                     'grapheme_mtl_merged_expanded_v1.json'):
            if not (checkpoint / name).is_file():
                raise FileNotFoundError(checkpoint / name)
        model = ChatterboxMultilingualTTS.from_local(checkpoint, device='cuda')
        settings = variant['proposedSettings']
        tensor = model.generate(text, language_id='ko', audio_prompt_path=str(reference), **settings)
        wav = tensor.detach().cpu().numpy().reshape(-1).astype(np.float32)
        sr = model.sr
        package = 'chatterbox-tts'
    if len(wav) == 0 or not np.isfinite(wav).all() or float(np.max(np.abs(wav))) < 0.001:
        raise RuntimeError('Invalid/empty generated audio')
    duration = len(wav) / sr
    peak = float(np.max(np.abs(wav)))
    # Preserve all raw samples, including model endings. Normalization is a later step.
    sf.write(output, wav, sr, subtype='FLOAT')
    report = {
        'createdUtc': datetime.now(timezone.utc).isoformat(),
        'project': args.project, 'variant': args.variant, 'label': variant['label'],
        'take': args.take, 'seed': args.seed, 'text': text,
        'textSha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
        'reference': plan['reference'],
        'referenceSha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
        'referenceUploaded': False, 'externalVoiceCloned': False,
        'engine': variant['engine'], 'model': variant['model'],
        'packageVersion': importlib.metadata.version(package),
        'torchVersion': torch.__version__, 'settings': settings,
        'durationSeconds': duration, 'sampleRate': sr, 'rawPeak': peak,
        'wav': str(output.relative_to(ROOT)).replace('\\', '/'),
        'needsDurationReview': not (10 <= duration <= 45),
        'asrReviewed': False, 'humanListeningApproved': False,
        'note': 'Expression is a listening hypothesis, not a measured emotion score.',
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(output), 'seconds': duration, 'peak': peak}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
