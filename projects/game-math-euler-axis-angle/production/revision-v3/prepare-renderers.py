"""Prepare selected v3 wrappers while leaving every v2 artifact immutable."""
from pathlib import Path
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';OLD=P/'production/revision-v2';NEW=Path(__file__).parent
for name in ['render-edit.py','prepare-captions.py','render-flat.py','math_visuals.py']:
 text=(OLD/name).read_text(encoding='utf8').replace('revision-v2','revision-v3')
 if name=='render-edit.py':
  start=text.index('def cut_ass(');end=text.index('def main():',start)
  text=text[:start]+'''import importlib.util
_spec=importlib.util.spec_from_file_location('annotations_v3',Path(__file__).with_name('annotation-render.py'))
_ann=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_ann)
cut_ass=_ann.cut_ass
'''+text[end:]
  text=text.replace("annotations=read(P/'sources/annotation-plan-v2.json')","annotations=read(P/'sources/annotation-plan-v3.json')")
  text=text.replace("annotations=read(P/'sources/annotation-plan-v3.json');rendered=[]", "annotations=read(P/'sources/annotation-plan-v3.json');assert annotations['status']=='source-keyframes-reviewed';rendered=[]")
  old="f=O/'spatial'/(s['id']+'.mp4') if s['id'] in ['03','04','06','07','09','10','12','16','18','19','21','22'] else O/'flat'/(s['id']+'.mp4')"
  text=text.replace(old,"f=R/s['retainedRender']['file'] if s.get('retainedRender') else O/'flat'/(s['id']+'.mp4')\n    if s.get('retainedRender'):assert sha(f)==s['retainedRender']['sha256'],'Reviewed explanation bytes changed'")
  text=text.replace('manual verified half-second keyframes; clear at each source cut/visibility interval','reviewed real-source tracking plus manually corrected paths; clear at each cut and visibility interval')
 elif name=='render-flat.py':
  text=text.replace("SCENE_IDS = ('01', '13', '15', '24', '25', '26')","SCENE_IDS = ('01',)")
  text=text.replace('current six-scene moving and caption review pending parent QA','current overview moving and caption review pending')
 (NEW/name).write_text(text,encoding='utf8')
print('Prepared current compositing/caption/overview wrappers; retained explanations referenced by hash.')
