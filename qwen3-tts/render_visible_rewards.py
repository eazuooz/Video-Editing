"""Approval-gated, seeded full narration for visible-rewards only.

Reuse the established scene renderer without changing other projects' behavior.
Do not assemble or sync an output while any scene fails the ending checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path

import render_narration as renderer

ROOT = Path(__file__).resolve().parents[1]
PROJECT = 'visible-rewards'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int)
    parser.add_argument('--force-scenes', default='')
    args = parser.parse_args()
    path = ROOT / 'projects' / PROJECT / 'project.json'
    manifest = json.loads(path.read_text(encoding='utf-8'))
    if not (manifest['approvals']['script'] == 'approved'
            and manifest['approvals']['voice'] == 'approved-A-balanced'
            and manifest['tts']['fullRenderApproved']
            and manifest['tts']['selectedVoiceSample'] == 'A'):
        raise RuntimeError('Approved script and A voice selection are required')
    renderer.configure_project(PROJECT)
    if renderer.narration_lead_seconds() != 0:
        raise RuntimeError('Narration must also continue during example footage')
    jobs = renderer.load_jobs()
    renderer.load_tts_dependencies()
    seed = manifest['tts']['seed'] if args.seed is None else args.seed
    random.seed(seed)
    renderer.np.random.seed(seed)
    renderer.torch.manual_seed(seed)
    renderer.torch.cuda.manual_seed_all(seed)
    items = renderer.build_render_items(jobs)
    force = {value.strip().zfill(2) for value in args.force_scenes.split(',') if value.strip()}
    if force - {job.scene_id for job in jobs}:
        raise ValueError('Unknown scene in --force-scenes')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    for item in items:
        if item.path.exists() and renderer.needs_render(item.path) and item.key[:2] not in force:
            shutil.copy2(item.path, item.path.with_name(f'{item.path.stem}-previous-{stamp}.wav'))
    print(f'{PROJECT}: {len(items)} approved scenes, Qwen3 1.7B Base, seed {seed}', flush=True)
    renderer.render_chunks(items, 1, force)
    checks = []
    for item in items:
        wav, sr = renderer._read_mono(item.path)
        tail = renderer._tail_ratio(wav, sr)
        decay = renderer._tail_decay_ms(wav, sr)
        checks.append({'scene': item.key[:2], 'path': str(item.path.relative_to(ROOT)),
                       'seconds': len(wav) / sr, 'sha256': hashlib.sha256(item.path.read_bytes()).hexdigest(),
                       'tailRatio': tail, 'tailDecayMs': decay if math.isfinite(decay) else None,
                       'endingPassed': renderer._passes_quality(tail, decay)})
    audit = {'project': PROJECT, 'seed': seed, 'createdUtc': stamp,
             'seedScope': 'This run only; reused scene audio retains its earlier render audit',
             'requestedRerenderScenes': sorted(force),
             'scriptSha256': hashlib.sha256(renderer.SCRIPT_PATH.read_bytes()).hexdigest(),
             'selectedSample': 'A', 'scenes': checks, 'humanFullListeningApproved': False}
    audit_path = renderer.OUTPUT_DIR / f'render-audit-{stamp}.json'
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    failed = [c['scene'] for c in checks if not c['endingPassed']]
    if failed:
        raise RuntimeError(f'Scenes need ending review before assembly: {failed}; see {audit_path}')
    renderer.assemble_outputs(jobs)
    print('Narration assembled; ASR, bilingual caption alignment and editor sync remain.', flush=True)


if __name__ == '__main__':
    main()
