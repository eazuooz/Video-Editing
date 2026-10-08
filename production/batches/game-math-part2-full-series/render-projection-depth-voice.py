"""One owned handoff for the new depth overview and complete UV numeric lines.

Unchanged full-chapter takes are adopted separately with exact text/hash proof.
The old interpolation take must be preserved before this replacement is made.
"""
from pathlib import Path
import argparse
import json
import subprocess
import sys
from production_control import require_current_authorization

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--project', required=True)
parser.add_argument('--device', choices=['cpu', 'cuda:0'], required=True)
args = parser.parse_args()
assert args.project == 'game-math-projection-depth'
require_current_authorization(args.project, 'depth episode narration')
sys.path.insert(0, str(ROOT / 'qwen3-tts'))
from gpu_handoff_guard import check_gpu_handoff
check_gpu_handoff(args.project, args.device)
manifest = json.loads((ROOT / f'projects/{args.project}/project.json').read_text(encoding='utf8'))
old_interpolation = ROOT / manifest['tts']['outputDir'] / 'chunks/04-scene.wav'
assert old_interpolation.is_file(), 'Adopt and preserve the full-chapter baseline before replacing scene04.'
subprocess.run([
    sys.executable, '-X', 'utf8', str(BATCH / 'render-voice.py'),
    '--project', args.project, '--batch-size', '1', '--device', args.device,
    '--scenes', '01',
], cwd=ROOT, check=True)
subprocess.run([
    sys.executable, '-X', 'utf8', str(BATCH / 'repair-scene-by-lines.py'),
    args.project, '04', '--device', args.device, '--defer-assembly',
], cwd=ROOT, check=True)
print('New overview and complete interpolation lines checkpointed; current raw readback and measured timing still required.', flush=True)
