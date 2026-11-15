from pathlib import Path
import json,subprocess
import numpy as np
from PIL import Image
H=Path(__file__).resolve().parent;M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');R=M/'production-resume-20261115T055255Z'
findings={
'shorts-spiderman-swing-anchor': ['All31 actual375px caption samples were inspected. The full independent PC Remastered swing footage retains its aspect ratio and returns in the recap.','The source order remains: attachment affects path, sparse-ray misses, markup volumes, candidate construction, scoring and movement focus.','The native anchor-height comparison is explicitly an authored illustration. The diagrams introduce raycasts and attachment criteria without inventing original numeric weights.','Captions and arrows remain readable and separated from the subject. No source game replay, padding, speed change or caption timing interpolation was used.'],
'shorts-control-destruction-pipeline': ['All29 actual375px caption samples were inspected, with individual cue013 opened to resolve a contact-preview display artifact.','The independent Xbox Series S recording supplies office context; the authored desk comparison and diagrams explain the destruction process without claiming the brief game context proves an exact intact-to-break event.','Source order remains: preparation, hierarchy, material rules, connections, physics/debris and surface-mark versus actual-hole distinction.','The repaired clause-boundary cuts move to the hierarchy diagram exactly when material preparation and combined effects are explained, within actual native source ranges.','The weak/strong desk examples, clear diagram levels and captions retain subject visibility and margins. No freeze, loop, speed change or voice processing was introduced.']}
for slug,notes in findings.items():
 B=M/slug/'film-v10/pilot-encoded-qa-v1';files=sorted(B.glob('cue-*-375.jpg'));assert len(files)==(31 if'spiderman'in slug else 29);ref=np.asarray(Image.open(files[0]).convert('RGB'),dtype=np.float32)[30:100,:345];checks=[]
 for p in files:
  a=np.asarray(Image.open(p).convert('RGB'),dtype=np.float32)[30:100,:345];mse=float(np.mean((a-ref)**2));assert mse<2,(p,mse);checks.append(dict(file=p.name,titleHeaderMse=mse))
 body=[]
 if'control'in slug:
  ref=np.asarray(Image.open(B/'cue-012-375.jpg').convert('RGB'),dtype=np.float32)[140:510,:345]
  for i in[13,14,15]:
   a=np.asarray(Image.open(B/f'cue-{i:03}-375.jpg').convert('RGB'),dtype=np.float32)[140:510,:345];mse=float(np.mean((a-ref)**2));assert mse<2,(i,mse);body.append(dict(cue=i,bodyMse=mse))
 note=R/(slug+'-pilot-observed-notes-v58.json');assert not note.exists();note.write_text(json.dumps(dict(project=slug,actualEncodedSamplesInspected=len(files),allCaptionSamplesOpened=True,sourceOrderAndAspectReviewed=True,captionMarginsAndSubjectVisibilityReviewed=True,titlePixelChecks=checks,contactArtifactBodyChecks=body,findings=notes+['The contact display intermittently obscures repeated headers/graphics; actual decoded sample pixels retain them.']),ensure_ascii=False,indent=2)+'\n','utf8');r=subprocess.run([str(H.parents[2]/'qwen3-tts/.venv/Scripts/python.exe'),'-u','-X','utf8',str(H/'record-inspected-pilot-v46.py'),'--project',slug,'--notes-file',str(note)],cwd=H.parents[2]);assert r.returncode==0
