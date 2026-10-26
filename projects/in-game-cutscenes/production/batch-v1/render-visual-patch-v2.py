"""Export only one reviewed QTE cut through the shared finite-batch runner."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
project = ROOT / 'motion-canvas/src/projects/in-game-cutscenes/batch-v1/project.ts'
original = project.read_bytes()
if b"'./scene?scene'" not in original:
    raise ValueError('Expected the preserved complete scene entry')
temporary = original.replace(b"'./scene?scene'", b"'./patch-v2.scene?scene'")
try:
    project.write_bytes(temporary)
    subprocess.run([
        'C:/Program Files/nodejs/node.exe',
        'production/batches/design-finish-six-20261026/render-motion.cjs',
        'in-game-cutscenes', 'in-game-cutscenes-explanations-patch-v2', '1451'
    ], cwd=ROOT, check=True)
finally:
    project.write_bytes(original)
