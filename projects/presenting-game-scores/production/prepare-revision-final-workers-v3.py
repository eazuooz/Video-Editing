"""Prepare guarded new revision mix/ASR/pair workers. Never run them here."""
from pathlib import Path
P=Path(__file__).parent
def adapt(t):
 t=t.replace("BASE/'final-v1'", "BASE/'revision-balatro60-v2/final-v3'")
 t=t.replace('6388323','6691203').replace('18332','19268').replace('19052','19988').replace('18452','19388')
 t=t.replace('currentVoiceSelectionSha256','voiceSelectionSha256').replace('currentVoiceSelection','voiceSelection')
 t=t.replace("voice_selection['currentVoiceApproved']", "voice_selection['currentCompleteVoiceApproved']")
 t=t.replace("voice['currentVoiceApproved']", "voice['currentCompleteVoiceApproved']")
 t=t.replace("['node',", "['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',")
 return t
mix=adapt((P/'build-reviewed-final-mix-v1.py').read_text('utf-8'))
mix=mix.replace("plan['narrationSamples']", "sum(p['samples'] for p in plan['voicePlacements'])")
mix=mix.replace("nextAction='Directly compare current mixed10 whole chapters and21 independent complete contexts", "nextAction='Directly compare current mixed10 whole chapters and42 independent complete contexts")
dest=P/'build-revision-final-mix-v3.py';assert not dest.exists();dest.write_text(mix,'utf-8')
asr=adapt((P/'review-current-final-mix-v1.py').read_text('utf-8'))
asr=asr.replace("plan['narrationSamples']", "sum(p['samples'] for p in plan['voicePlacements'])")
begin=asr.index("placements=plan['voicePlacements'];bounds=plan['paragraphBoundaries']")
end=asr.index("assert not STATE.exists()",begin)
asr=asr[:begin]+'''placements=plan['voicePlacements'];bounds=plan['paragraphBoundaries']
def mapped(voice_id,start,end):
 row=next(p for p in placements if p['voiceId']==voice_id and p['sourceStartSample']<=start and p['sourceEndSampleExclusive']>=end)
 return row['startSample']+start-row['sourceStartSample'],row['startSample']+end-row['sourceStartSample']
for chunk in cap['chunks']:
 vid=chunk['scene'];pi=chunk['paragraph'];b=bounds[vid]
 start,end=b[pi-1],b[pi]
 if vid[:2] in ['06','09','10'] and pi==2:
  split=plan['completeSentence'+vid[:2]+'BoundarySample']
  if chunk['chunk']==1:end=split
  else:start=split
 a0,b0=mapped(vid,start,end)
 add(f'context-{vid}-p{pi}-c{chunk["chunk"]}',vid,a0,b0,[chunk['ko']],True,
  'Independent complete current semantic clause; exact stereo current mix PCM including original quiet boundaries and0.6sec padding, never prompted.')
assert len(windows)==52 and sum(w['independent'] for w in windows)==42
'''+asr[end:]
asr=asr.replace('totalIndependentContexts=21','totalIndependentContexts=42').replace('total=31','total=52').replace('len(results)==31','len(results)==52')
asr=asr.replace('10 mixed chapters +21','10 mixed chapters +42').replace('10 mixed chapters and21','10 mixed chapters and42')
dest=P/'review-revision-final-mix-v3.py';assert not dest.exists();dest.write_text(asr,'utf-8')
pair=adapt((P/'render-reviewed-pair-v1.py').read_text('utf-8'))
pair=pair.replace('all31WindowsDirectlyCompared','all52WindowsDirectlyCompared').replace("len(review['windows'])==31", "len(review['windows'])==52")
pair=pair.replace('(168,68,[960,970])','(175,70,[960,970])')
pair=pair.replace('projects/presenting-game-scores/production/final-v1/captions.ko.ass','projects/presenting-game-scores/production/revision-balatro60-v2/final-v3/captions.ko.ass')
pair=pair.replace('all31 mixed','all52 mixed').replace('All31 current','All52 current').replace('Current31-window','Current52-window')
dest=P/'render-revision-reviewed-pair-v3.py';assert not dest.exists();dest.write_text(pair,'utf-8')
print('Prepared three guarded revision workers. Current input review/mix/ASR/pair still not executed.')
