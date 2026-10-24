import json
from pathlib import Path
R=Path(__file__).resolve().parents[3];p=R/'projects/shorts-titanfall-time-shift'
def save(f,d):f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for f in [p/'production/visual-timing.json',p/'production/local/visual-timing.json',p/'production/local/audio-v1/visual-timing.json']:
 d=json.loads(f.read_text(encoding='utf8'));d['captureMode']='full-v2';d['nativeTimingCorrection']='Transfer at p4-3 and p5-3; keep resulting upper position instead of automatically looping back.';save(f,d)
f=p/'project.json';d=json.loads(f.read_text(encoding='utf8'));d.update(currentFinalDirectory='production/local/final-reviewed-v2',deliveryFilenameSuffix='.v2');save(f,d)
f=p/'production/render-visual.cjs';f.write_text(f.read_text(encoding='utf8').replace('capture-full-v1/success.json','capture-full-v2/success.json'),encoding='utf8')
