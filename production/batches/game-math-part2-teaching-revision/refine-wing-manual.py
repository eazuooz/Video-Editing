"""Hand corrected projected landmarks read from quarter-second source frames."""
from pathlib import Path
import json
B=Path(__file__).parent;f=B/'wing-annotation-keyframes.json';d=json.loads(f.read_text(encoding='utf8'))
coordinates=[
 (34,171,234,438,274),(34.25,153,247,441,279),(34.5,177,247,441,249),(34.75,187,250,439,232),
 (35,203,259,436,236),(35.25,221,259,434,225),(35.5,231,261,436,239),(35.75,240,271,437,251),
 (36,241,284,435,266),(36.25,232,264,428,293),(36.5,232,229,414,311),(36.75,232,258,424,285),
 (37,244,277,433,255),(37.25,242,265,430,252),(37.5,247,259,437,250),(37.75,239,266,431,236),
 (38,240,271,434,252),(38.25,242,261,430,264),(38.5,237,263,420,264),(38.75,225,256,395,302),
 (39,222,253,387,331),(39.25,249,285,428,268),(39.5,270,295,481,219),(39.75,282,308,471,188),
 (40,236,282,461,234),(40.25,213,257,454,250),(40.5,190,249,438,272),(40.75,202,264,454,253),
 (41,253,299,481,204),(41.25,318,304,510,174),(41.5,354,329,522,174),(41.75,340,311,518,205),
 (42,259,266,463,253)]
d['keyframes']=[{'t':t,'left':[lx,ly],'right':[rx,ry]} for t,lx,ly,rx,ry in coordinates]
d['trackingMethod']='manual projected wing-tip correction at 0.25-second intervals, linear interpolation; rendered intermediates require visual review'
d['authoringFrames']='shared/output/game-math-part2-teaching-revision/wing-manual/page-1.jpg through page-3.jpg'
d['motionPixelApproval']=False
f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('33 editable manual landmark pairs; pixel approval remains false')
