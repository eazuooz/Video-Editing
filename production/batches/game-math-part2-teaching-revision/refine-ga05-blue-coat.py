"""Native-timed directly observed coat landmarks, retaining historical drafts."""
from pathlib import Path
import json, shutil
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
p=B/'ga05new-landmarks.json';d=json.loads(p.read_text(encoding='utf8'))
archive=B/'baselines/landmark-drafts-before-native-time-fix/ga05new-before-coat-refinement.json'
if not archive.exists():shutil.copy2(p,archive)
# White back emblem to the middle of the coat hem in the already inspected
# 800x450 exact native references. No world axis is recovered from this line.
observed={
 372:(342,203,356,290),372.5:(316,218,315,287),373:(310,168,310,249),
 373.5:(310,239,312,310),374:(337,213,309,278),374.5:(294,212,280,275),
 375:(287,208,275,284),375.5:(300,216,280,298),376:(307,221,291,304),
 376.5:(297,218,273,285),377:(298,206,277,275),377.5:(324,199,321,264),
 378:(306,184,308,244),378.5:(304,173,299,253),
 380.5:(278,245,278,314),381.5:(304,223,306,289),382.5:(330,214,333,283),
 383.5:(275,175,272,245),384.5:(340,214,310,280),385.5:(353,199,358,270),
 386.5:(376,213,384,287),387.5:(332,225,322,300),388.5:(318,201,301,270),
 389.5:(309,199,285,269),390.5:(318,198,294,268),391.5:(294,196,270,266),
}
for k in d['keyframes']:
 if k.get('authoringLabelTime') in observed:
  ux,uy,lx,ly=observed[k['authoringLabelTime']];k.update(upper=[ux,uy],lower=[lx,ly])
d['nativeCoatRefinement']='White emblem and coat hem directly observed; native times retained. Fast zoom/occlusion/crash windows remain hidden. Moving pixels still pending.'
d['movingPixelApproval']=False;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
r=B/'quaternion-annotation-tracks.json';reg=json.loads(r.read_text(encoding='utf8'));reg['scenes']['GA05']['labelOutline']=3.5;r.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Refined observed coat landmarks without changing voice, duration or native timestamps.')
