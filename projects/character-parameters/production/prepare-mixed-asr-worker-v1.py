"""Adapt a guarded CPU2 worker; execution is separately gated on reviewed mix."""
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[2]
out=BASE/'review-character-mixed-v1.py';assert not out.exists()
text=(ROOT/'projects/presenting-game-scores/production/review-current-final-mix-v1.py').read_text('utf-8')
begin=text.index('windows=[]');end=text.index("assert not STATE.exists()",begin)
windows='''windows=[]
def add(label,scene,start,end,expected,independent,purpose):
 assert 48000<=start<end<=22797*400
 windows.append(dict(label=label,scene=scene,fromSample=start*2,toSample=end*2,
  padSamplesEachSide=28800 if independent else 0,expectedKo=expected,independent=independent,
  scope=purpose,expectedWasRecognizerPrompt=False))
for chapter in plan['chapters']:
 expected=[p['ko']for p in cap['paragraphs']if p['scene']==chapter['id']]
 assert len(expected)==(4 if chapter['id']=='06-role-and-limitation' else 3)
 add('whole-'+chapter['id'],chapter['id'],chapter['startFrame']*400,chapter['endFrameExclusive']*400,expected,False,
  'Entire current mixed chapter, including observation intervals and every complete literal paragraph.')
placements=plan['voicePlacements']
def mapped(voice_id,start,end):
 rows=[p for p in placements if p['voiceId']==voice_id and p['sourceStartSample']<=start and p['sourceEndSampleExclusive']>=end]
 assert len(rows)==1,(voice_id,start,end)
 row=rows[0];return row['startSample']+start-row['sourceStartSample'],row['startSample']+end-row['sourceStartSample']
for para in cap['paragraphs']:
 start,end=mapped(para['scene'],round(para['sourceStartSeconds']*24000),round(para['sourceEndSeconds']*24000))
 add('context-'+para['scene']+'-complete-p'+str(para['paragraph']),para['scene'],start,end,[para['ko']],True,
  'Independent entire current paragraph, exact final stereo mix bytes with0.6sec zero padding on each side; no recognizer prompt.')
assert len(windows)==49 and sum(w['independent']for w in windows)==37
'''
text=text[:begin]+windows+text[end:]
for a,b in [('presenting-game-scores','character-parameters'),('6388323','8430001'),('19052','23397'),('all19CurrentPcmSamplesIdentical','all12CurrentPcmSamplesIdentical'),("voice['currentVoiceApproved']","voice['currentCompleteVoiceReadyForMeasuredPlanning']"),("['node',","['C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe',"),('totalWhole=10,totalIndependentContexts=21','totalWhole=12,totalIndependentContexts=37'),('total=31','total=49'),('total=31','total=49'),('len(results)==31','len(results)==49'),('text/words of10 mixed chapters and21','text/words of12 mixed chapters and37'),('10 mixed chapters +21 complete contexts','12 mixed chapters +37 complete contexts')]:
 text=text.replace(a,b)
out.write_text(text,'utf-8');print('Prepared49 complete mixed contexts only; no model instantiated')
