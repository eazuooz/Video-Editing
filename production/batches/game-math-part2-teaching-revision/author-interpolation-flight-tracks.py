"""Directly observed flight/gear landmarks; hidden/cut spans do not interpolate."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;D=B/'interpolation-tracks'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def save(ident,keys,hidden):
    frames=read(ROOT/f'shared/output/game-math-part2-teaching-revision/interpolation-track-authoring/O{ident}/frames.json')
    (D/f'original-{ident}-flight.json').write_text(json.dumps({'id':ident,'sourceFile':frames['source'],'sourceSha256':hashlib.sha256((ROOT/frames['source']).read_bytes()).hexdigest(),'coordinatePixels':[800,450],'keyframes':keys,'hideIntervals':hidden,'trackingMethod':'Direct native2s observed body/wing guides; dense moving draft review required; no interpolation across gear cuts/fast hidden turns','meaning':'Projected visible body or wing line only; no measured game-world axes/angles','movingPixelApproval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Body line runs from the visible hip/torso region toward the upper torso.
body14=[(330,178,373,183),(337,183,383,190),(334,182,384,198),(335,182,379,207),None,(350,219,340,182),(330,210,348,185),(330,208,348,184),(332,212,349,185),(330,190,350,170),(337,186,360,165),(330,212,334,190),(330,190,353,178),(337,219,359,185),(335,218,346,193),(330,213,345,189),(336,217,355,191),(338,213,349,189),(325,213,348,185),(335,203,355,182),(330,211,362,196),(331,211,349,187),(330,215,348,189),(329,213,343,189),None,(334,210,347,187),(345,285,331,224),(363,279,337,220),(368,254,367,191),(300,230,283,168),(363,259,362,207),(426,238,411,185),(342,260,330,184),(282,287,288,233),(335,281,331,235)]
keys=[]
for i,p in enumerate(body14):
    if p:keys.append({'t':i*2.,'lower':list(p[:2]),'upper':list(p[2:]),'directAuthoringFrame':f'shared/output/game-math-part2-teaching-revision/interpolation-track-authoring/O14/{i:03}.png'})
keys.append({**keys[-1],'t':69.999});save('14',keys,[[6.5,9.7],[47.0,49.3],[51.6,52.2]])
# The spread of each visible wing is directly observable; no arrow direction is inferred.
wing17=[(267,234,403,241),(270,226,413,241),(276,263,440,240),(300,246,453,267),(233,242,408,261),(280,240,411,252),(219,246,387,260),(274,263,432,242),(256,242,414,240),(199,227,337,240),(270,250,421,248),(264,248,416,247),(290,212,381,213),(286,213,373,210),(286,203,384,211),(310,219,370,185),(298,220,369,206),(252,267,430,283),(247,234,390,245),(269,251,416,252),(266,252,417,261),(271,266,379,272),(221,268,406,281),(269,265,432,282),(233,256,413,269),(322,248,380,220),(237,252,405,272),(272,245,381,240),(229,266,409,262),(272,264,445,269),(274,241,420,242),(224,262,406,271)]
keys=[{'t':i*2.,'left':list(p[:2]),'right':list(p[2:]),'directAuthoringFrame':f'shared/output/game-math-part2-teaching-revision/interpolation-track-authoring/O17/{i:03}.png'} for i,p in enumerate(wing17)]
keys.append({**keys[-1],'t':62.399});save('17',keys,[[22.6,23.4],[29.3,33.5],[33.6,34.3],[49.0,51.2],[53.3,55.0]])
print('Flight guides saved with cut/occlusion hides; final moving approval pending.')
