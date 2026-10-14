"""Version the premodel retry; retain failed v1 records and its proven restoration."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
R=ROOT/'projects/motion-sickness-games/production/revision-cross-game-four-v1'
failure=json.loads((R/'research-handoff-premodel-failure-verification-v1.json').read_text('utf-8-sig'))
assert failure['actualOuterSession']==57445 and failure['actualOuterExitCode']==1 and failure['restorationVerified'] and failure['newPcmCount']==0
for name in ['render-motion-four-additions','verify-motion-four-voice-resume']:
    s=(B/(name+'-v1.py')).read_text('utf-8-sig')
    for record in ['narration-tts-execution','narration-tts-session','narration-tts-waiting','research-handoff-verification']:
        s=s.replace(record+'-v1.json',record+'-v2.json')
    if name.startswith('render'):
        s=s.replace("request=read(REQUEST)","failed=read(R/'research-handoff-premodel-failure-verification-v1.json')\nassert failed['restorationVerified'] and failed['newPcmCount']==0\nrequest=read(REQUEST)",1)
    p=B/(name+'-v2.py');assert not p.exists();p.write_text(s,'utf-8')
print('Versioned single retry prepared; original failure and all14PCM preserved.')
