"""Contextual signal audit: distinguish source phrase endings from mix gain loss.

Never treats recognition or signal measurements as human pronunciation approval.
"""
from pathlib import Path
import json,statistics
R=Path(__file__).resolve().parents[4];P=R/'projects/making-game-sequels';O=P/'production/local/reference-preserving-v2/edit';N=R/'shared/output/narration/making-game-sequels/reference-preserving-v2'
a=json.loads((O/'qa/audio-continuity.json').read_text());plan=json.loads((P/'production/reference-preserving-v2/edit-plan.json').read_text());rows=[]
for c in a['sustainedLocalDropCandidates']:
 scene=next(s for s in plan['scenes'] if s['id']==c['scene']);words=json.loads((N/'asr'/f"{c['scene']}.json").read_text(encoding='utf8'))['words']
 context=''.join(w['text'] for w in words if w['timestamp'][0] is not None and scene['voiceStart']+w['timestamp'][0]<=c['end']+1 and scene['voiceStart']+(w['timestamp'][1] or w['timestamp'][0])>=c['start']-1)
 samples=[w for w in a['windows'] if w['scene']==c['scene'] and c['start']<=w['time']<=c['end']-.35];gains=[w['stemMinusSourceDb'] for w in samples]
 delta=max(gains)-min(gains)
 rows.append({**c,'completePhraseContext':context,'sourceToStemGainRangeDb':delta,'classification':'source phrase-ending/pause dynamics retained, no sustained mixer-induced attenuation' if delta<1.5 else 'requires inspection','humanListening':'pending user final review'})
low=[{**w,'classification':'very-low-energy source tail; additive game/music makes scalar projection unreliable','sourceBelowMinus50Dbfs':w['sourceDbfs']<-50} for w in a['flaggedVoiceTransferWindows']]
active=[w for w in a['windows'] if w['sourceDbfs']>-40]
out={'basis':'Aligned original PCM, processed stem and encoded mix; full original ASR phrase contexts. Source amplitudes and transfer values are measurements, listening is separately pending.','candidateCount':len(rows),'candidates':rows,'lowEnergyProjectionFlags':low,'activeSourceThresholdDbfs':-40,'activeWindowCount':len(active),'minimumActiveVoiceTransferDb':min(w['estimatedVoiceTransferDb'] for w in active),'maximumSceneMedianChangeDb':max(abs(w['speechMedianDifferenceDb']) for w in a['sceneJoins']),'technicalGainFlagsResolved':all(r['sourceToStemGainRangeDb']<1.5 for r in rows) and all(w['sourceBelowMinus50Dbfs'] for w in low) and min(w['estimatedVoiceTransferDb'] for w in active)>-1,'humanWholeListening':'pending','humanPronunciation':'pending','naturalProsodyNotNormalizedAway':True}
(O/'qa/level-candidate-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in out.items() if k not in ['candidates','lowEnergyProjectionFlags','basis']}))
