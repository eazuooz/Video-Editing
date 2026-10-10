"""Preserve the broad playback record; exclude its observed crash frames."""
from pathlib import Path
import json
B=Path(__file__).parent
p=B/'quaternion-source-corrections-v5.json'
d=json.loads(p.read_text(encoding='utf8'))
x={'id':'GB03','intervals':[[558,571.5],[573,594],[603,620]],'maximumSeconds':51.5,'sourceGroupStartsAtLines':[0,None,3],'selectionReason':'Saved native-frame page2 exposes a gray crash/backtrack at572. Exclude571.5–573; the two clear pieces form the first narrated group. The603–620 piece begins the explicitly separate second excerpt at line3. Original baseline remains unchanged.'}
d['scenes']=[s for s in d['scenes'] if s['id']!='GB03']+[x]
if not any(s['id']=='GB03-fine' for s in d['comparison']):
 d['comparison'].append({'id':'GB03-fine','interval':[558,594],'chosen':False,'reason':'Gray crash/backtrack at572 visible in source contact page2. Only558–571.5 and573–594 are eligible; moving review of the actual revised cut remains pending.'})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('GB03 clear source capacity51.5s; originals unchanged')
