"""Export only four reviewed MC cuts through the shared finite-batch runner."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
project = ROOT / 'motion-canvas/src/projects/start-with-climax/batch-v1/project.ts'
original = project.read_bytes()
if b"'./scene?scene'" not in original:
    raise ValueError('Expected the preserved complete scene entry')
temporary = original.replace(b"'./scene?scene'", b"'./patch-v2.scene?scene'")
try:
    project.write_bytes(temporary)
    subprocess.run([
        'C:/Program Files/nodejs/node.exe',
        'production/batches/design-finish-six-20261026/render-motion.cjs',
        'start-with-climax', 'start-with-climax-explanations-patch-v2', '1406'
    ], cwd=ROOT, check=True)
finally:
    project.write_bytes(original)
