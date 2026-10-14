"""Prepare one retry after the verified premodel research-validation failure."""
from pathlib import Path
import json
B=Path(__file__).resolve().parent;ROOT=B.parents[2]
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
f=json.loads((R/'research-handoff-premodel-failure-verification-v2.json').read_text('utf-8-sig'))
assert f['actualOuterSession']==46624 and f['actualOuterExitCode']==1 and f['restorationVerified'] and f['newPcmCount']==0
for name in ['render-motion-four-additions','verify-motion-four-voice-resume']:
    s=(B/(name+'-v2.py')).read_text('utf-8-sig')
    for record in ['narration-tts-execution','narration-tts-session','narration-tts-waiting','research-handoff-verification']:
        s=s.replace(record+'-v2.json',record+'-v3.json')
    s=s.replace('research-handoff-premodel-failure-verification-v1.json','research-handoff-premodel-failure-verification-v2.json')
    p=B/(name+'-v3.py');assert not p.exists();p.write_text(s,'utf-8')
print('Single V3 runtime prepared; validation failure preserved, no PCM/model/research changes.')
