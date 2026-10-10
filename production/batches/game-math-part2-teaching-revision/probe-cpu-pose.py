"""CPU-only diagnostic. Detection is never automatic video approval."""
import os,sys,json
from pathlib import Path
os.environ['CUDA_VISIBLE_DEVICES']='-1'
ROOT=Path(__file__).resolve().parents[3];O=ROOT/'shared/output/game-math-part2-teaching-revision'
sys.path.insert(0,str(O/'cpu-pose-packages'));os.environ['YOLO_CONFIG_DIR']=str(O/'cpu-pose-config')
import torch
torch.set_num_threads(2)
from ultralytics import YOLO
from PIL import Image,ImageDraw
model=YOLO(str(O/'cpu-pose-model/yolo26n-pose.pt'))
files=[O/'landmark-authoring/GA05tail/386.50.png',O/'landmark-authoring/GA07/63.00.png',O/'landmark-authoring/O05/57.00.png']
records=[]
for path in files:
 if not path.exists():continue
 r=model.predict(str(path),device='cpu',imgsz=640,conf=.25,verbose=False)[0]
 im=Image.open(path);draw=ImageDraw.Draw(im)
 for box,key in zip(r.boxes.xyxy.tolist(),r.keypoints.data.tolist()):
  draw.rectangle(box,outline='yellow',width=2)
  a=[sum(key[i][j] for i in (5,6))/2 for j in (0,1)];b=[sum(key[i][j] for i in (11,12))/2 for j in (0,1)]
  draw.line([tuple(a),tuple(b)],fill='red',width=4)
  for k in key:
   if k[2]>.4:draw.ellipse((k[0]-3,k[1]-3,k[0]+3,k[1]+3),fill='lime')
 dst=O/'cpu-pose-probe'/path.parent.name;dst.mkdir(parents=True,exist_ok=True);im.save(dst/path.name)
 records.append({'image':path.relative_to(ROOT).as_posix(),'boxes':r.boxes.xyxy.tolist(),'boxConfidence':r.boxes.conf.tolist(),'keypoints':r.keypoints.data.tolist(),'approval':False})
(O/'cpu-pose-probe/result.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
print(json.dumps({'images':len(records),'device':'cpu','detections':[len(r['boxes']) for r in records]}))
