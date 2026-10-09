"""Correct the descriptive scale from the saved actual encoder command; no media edits."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,copy
P=Path(__file__).parent;ROOT=P.parents[2];B=P/'revision-balatro60-v2';p=B/'measured-native-inputs-execution-v1.json'
j=json.loads(p.read_text('utf-8'));assert j['exitCode']==j['actualOuterExitCode']==0
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
oldsha=sha(p);rows=[]
for r in j['results']:
 if 'bal-longplay-' not in r['id']:continue
 cmd=r['command'];filters=cmd[cmd.index('-filter_complex')+1]
 assert '[f]scale=1600:900[fg]' in filters and 'overlay=160:0' in filters
 assert sha(ROOT/r['path'])==r['sha256']
 rows.append(dict(id=r['id'],previousForegroundScale=r['foregroundScale'],correctForegroundScale=5/6,actualVideoRect=[160,0,1600,900],actualFilter=filters,mediaSha256=r['sha256']))
 r.update(foregroundScale=5/6,videoRect=[160,0,1600,900],creditOutsideGameplay=True,framingMetadataCorrectedFromActualCommand=True)
assert len(rows)==10
j['framingMetadataCorrection']='projects/presenting-game-scores/production/revision-balatro60-v2/native-framing-metadata-correction-v1.json'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
proof=dict(correctedAt=datetime.now(timezone.utc).isoformat(),executionSha256Before=oldsha,executionSha256After=sha(p),rows=rows,mediaChanged=False,encoderRerun=False,sourceChanged=False,finalCuePixelsReviewed=False)
(B/'native-framing-metadata-correction-v1.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(descriptiveMetadataCorrected=10,mediaChanged=False)))
