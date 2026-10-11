"""Prepare current final moving controls and delivery adapter guards."""
from pathlib import Path
import argparse
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--adapter',action='store_true');args=ap.parse_args()
if args.adapter:
 source=(R/'prepare-part3-delivery-project-v157.py').read_text('utf-8')
 source=source.replace('part3-reviewed-pair-build-v149.json','part3-reviewed-pair-build-v160.json')
 source=source.replace('part3-annotated-visual-build-v148.json','part3-annotated-visual-build-v159.json')
 source=source.replace('part3-final-qa-v157.json','part3-final-qa-v162.json')
 source=source.replace('part3-final-pixel-review-direct-v157.json','part3-final-pixel-review-direct-v162.json')
else:
 source=(R/'prepare-part3-final-moving-review-v158.py').read_text('utf-8')
 source=source.replace('part3-reviewed-pair-build-v149.json','part3-reviewed-pair-build-v160.json')
 source=source.replace('v158','v160')
exec(compile(source,str(Path(__file__)), 'exec'))
