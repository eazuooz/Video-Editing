"""Reuse visual evidence; measure only new mixed audio and new output integrity."""
from pathlib import Path
import importlib.util,sys
H=Path(__file__).parent;P=H.parent.parent
spec=importlib.util.spec_from_file_location('v3verify',P/'production/revision-v3/verify-output.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.O=P/'production/local/revision-v4';m.Q=m.O/'qa';m.Q.mkdir(exist_ok=True)
assert m.read(m.R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
t=m.read(P/'production/revision-v3/timeline.json')
stage=sys.argv[1] if len(sys.argv)>1 else 'all'
if stage in ['integrity','all']:m.integrity(t)
if stage in ['audio','all']:m.audio(t)
print('Current v4 output checks:',stage,'; visual/caption evidence reused only through exact video-stream equality.')
