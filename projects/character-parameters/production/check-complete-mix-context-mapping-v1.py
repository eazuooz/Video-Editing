from pathlib import Path
import json
b=Path(__file__).resolve().parent/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
p=read(b/'plan.json');c=read(b/'captions.json');bad=[]
for a in c['paragraphs']:
 s=round(a['sourceStartSeconds']*24000);e=round(a['sourceEndSeconds']*24000)
 if len([r for r in p['voicePlacements']if r['voiceId']==a['scene']and r['sourceStartSample']<=s and r['sourceEndSampleExclusive']>=e])!=1:bad.append(a)
print(json.dumps(dict(bad=bad),ensure_ascii=False))
