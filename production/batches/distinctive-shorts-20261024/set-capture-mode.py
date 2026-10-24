import json,re,sys
from pathlib import Path
R=Path(__file__).resolve().parents[3];slug,topic,mode=sys.argv[1:];p=R/'projects'/slug
for f in [p/'production/visual-timing.json',p/'production/local/visual-timing.json',*p.glob('production/local/audio-v*/visual-timing.json')]:
 d=json.loads(f.read_text(encoding='utf8'));d['captureMode']=mode;f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
f=p/'production/render-visual.cjs';f.write_text(re.sub(r'capture-full-v\d+/success.json','capture-'+mode+'/success.json',f.read_text(encoding='utf8')),encoding='utf8')
f=R/f'motion-canvas/src/projects/distinctive-shorts-20261024/{topic}/scene.tsx';f.write_text(re.sub(r'capture-full-v\d+/readback.json','capture-'+mode+'/readback.json',f.read_text(encoding='utf8')),encoding='utf8')
