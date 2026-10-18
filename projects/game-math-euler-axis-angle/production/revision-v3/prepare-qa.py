"""Current v3 QA wrappers; retain hash-identical explanations' prior pixel evidence."""
from pathlib import Path
P=Path(__file__).resolve().parents[2];OLD=P/'production/revision-v2';NEW=Path(__file__).parent
for name in ['verify-output.py','review-final-audio.py']:
 text=(OLD/name).read_text(encoding='utf8').replace('revision-v2','revision-v3')
 if name=='review-final-audio.py':
  text=text.replace('one-constant-gain-per-scene-plus-one-global-gain-and-short-peak-limiter','constant scene gain plus constant global gain')
  text=text.replace('build.get("sourceAudioUsed") is False','build.get("sourceAudioUsed") is True and build["music"]["addedBgm"] is False')
  text=text.replace('including joins and music','including joins and quiet native game sound; no added music')
 else:
  text=text.replace("sha(O/'unity-spatial-placement.json')","sha(P/'production/local/revision-v2/unity-spatial-placement.json')")
  text=text.replace("placement=read(O/'unity-spatial-placement.json')","placement=read(P/'production/local/revision-v2/unity-spatial-placement.json')")
  text=text.replace("for c in layout['rows']:samples.setdefault(round((c['start']+c['end'])*30),[]).append('cue'+str(c['cue']))", "for c in layout['rows']:\n  scene=next(s for s in plan['scenes'] if s['start']<=c['start']<s['start']+s['seconds'])\n  if not scene.get('retainedRender'):samples.setdefault(round((c['start']+c['end'])*30),[]).append('cue'+str(c['cue']))")
  text=text.replace("if s['kind']=='explanation':", "if s['kind']=='explanation' and not s.get('retainedRender'):")
  start=text.index(" # Inspect every finite authored Unity motion")
  end=text.index(" rows=[dict(frame=f",start)
  text=text[:start]+''' # Retained17 source clips, local caption text/timing and renderer settings
 # are hash-checked; prior moving explanation evidence is reused. Current
 # source cuts, changed captions and all inter-scene joins are sampled here.
 annotations=read(P/'sources/annotation-plan-v3.json')
 for c in plan['cuts']:
  for w in annotations['windows']:
   if w['scene']!=c['scene'] or w['sourceId']!=c['sourceId']:continue
   a=max(w['sourceIn'],c['sourceStart']);b=min(w['sourceOutExclusive'],c['sourceEnd'])
   if b<=a:continue
   for t in [a+.1,(a+b)/2,b-.1]:
    if not a<=t<b:continue
    frame=c['globalStartFrame']+round((t-c['sourceStart'])*60)
    samples.setdefault(frame,[]).append(w['id']+' guide')
'''+text[end:]
 (NEW/name).write_text(text,encoding='utf8')
print('Prepared current integrity/level/pixel and complete final-mix ASR checks.')
