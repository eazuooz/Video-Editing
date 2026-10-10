"""Owned sequential media stages; completion still requires direct/platform QA."""
from pathlib import Path
import argparse, subprocess, sys
ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('slug',choices=['game-math-plane-distances-v2','game-math-triangle-addresses-v2']);a=p.parse_args()
for stage in ['mix','burn','qa']:
    print(a.slug,stage,flush=True)
    subprocess.run([sys.executable,'-u','-X','utf8',str(Path(__file__).with_name('build-planes-episodes.py')),a.slug,stage],cwd=ROOT,check=True)
for helper in ['prepare-planes-final-caption-review.py','extract-planes-moving-pixels.py']:
    print(a.slug,helper,flush=True)
    subprocess.run([sys.executable,'-u','-X','utf8',str(Path(__file__).with_name(helper)),a.slug],cwd=ROOT,check=True)
print('Current media/QA images complete; direct native playback, all-cue/moving review and upload remain pending.',flush=True)
