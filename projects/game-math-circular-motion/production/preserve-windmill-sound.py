"""Protect the original quiet Besiege interval from a 32 dB lift."""
from pathlib import Path
import json,re,subprocess,hashlib
P=Path(__file__).resolve().parents[1];R=P.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert read(R/'shared/publishing/video-production-control.json')['explicitMathRemainingBatch20261104']['productionAllowedNow']
a=next(w for w in read(P/'planning/game-sound-window-audit.json')['windows'] if w['scene']=='017')
assert a['sourceId']=='T3ncWUwKUns' and a['seconds']==10 and a['flags']==['near-silent-window-needs-listening']
cmd=['ffmpeg','-hide_banner','-nostdin','-threads','1','-ss',str(a['audioStart']),'-t','10','-i',str(R/a['soundFile']),'-vn','-af','atrim=end=10,loudnorm=I=-23:TP=-2:LRA=11:print_format=json','-f','null','-']
out=subprocess.run(cmd,capture_output=True,check=True);observed=json.loads(re.findall(r'\{\s*"input_i"[\s\S]+?\}',out.stderr.decode('utf-8','replace'))[-1])
assert float(observed['input_i'])< -50 and float(observed['input_tp'])< -38
decision=dict(policy='preserve-quiet-original',maxUpwardGainDb=6,observedLufs=float(observed['input_i']),observedTruePeakDbtp=float(observed['input_tp']),inputWindow=[338,348],decodedAudioSha256=a['measurement']['decodedWindowPcmSha256'],
 reason='This particular windmill interval is very quiet in the original. Limit upward gain instead of amplifying it over 30 dB or substituting sound. Retain synchronized native sound, normal gameplay ducking and no added BGM.',actualListening=False)
bp=P/'planning/scene-bindings.json';b=read(bp)
g=next(x['actualGamePart'] for x in b['scenes'] if x['id']=='017');assert g['sourceId']==a['sourceId'];g['sourceSoundDecision']=decision;save(bp,b)
pp=P/'planning/production-plan.json';p=read(pp);g=next(x for x in p['nativeGameCueBindings'] if x['sceneId']=='017');g['sourceSoundDecision']=decision
p['sceneBindingsSha256']=hashlib.sha256(bp.read_bytes()).hexdigest();save(pp,p)
print('Windmill:',observed['input_i'],'LUFS; original sound retained, gain limited for this one window.')
