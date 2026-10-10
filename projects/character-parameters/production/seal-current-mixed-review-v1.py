"""Require full manual comparison of every actual current mixed window."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,wave
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));rel=lambda p:p.relative_to(ROOT).as_posix()
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
dest=W/'full-mix-asr-review.json';assert not dest.exists(),'Preserve actual current mixed review'
notes=W/'mixed-asr-direct-notes-v1.json';manual=read(notes);actual_path=W/'mixed-asr-v1/asr.json';actual=read(actual_path)
execution=read(W/'mixed-asr-execution.json');settings=read(W/'mix-settings.json');plan=read(W/'plan.json')
assert execution['exitCode']==execution['outerExitCode']==0 and execution['outerExitDirectlyObserved'] and execution['sessionClosed']
assert actual['complete'] and len(actual['results'])==49 and sum(r['independent']for r in actual['results'])==37
assert manual['allFullExpectedActualTextsAndWordsRead'] and not manual['unresolvedContentDefects']
comparisons={r['label']:r for r in manual['windows']}
assert len(comparisons)==49 and all(r['directlyCompared']for r in comparisons.values())
assert set(comparisons)=={r['label']for r in actual['results']}
assert sha(W/'final-mix.wav')==settings['wavSha256']==actual['mixSha256']
assert sha(W/'final-mix.m4a')==settings['aacSha256']==actual['aacSha256']
assert sha(W/'plan.json')==settings['planSha256']==actual['planSha256']
rows=[]
with wave.open(str(W/'final-mix.wav'),'rb')as voice:
 assert (voice.getframerate(),voice.getnchannels(),voice.getsampwidth(),voice.getnframes())==(48000,2,2,23397*800)
 for r in actual['results']:
  path=ROOT/r['windowPath'];assert sha(path)==r['windowSha256'] and not r['expectedWasRecognizerPrompt']
  voice.setpos(r['fromSample']);slice_pcm=voice.readframes(r['toSample']-r['fromSample'])
  assert hashlib.sha256(slice_pcm).hexdigest()==r['mixPcmSliceSha256'] and r['exactStereoMixSampleBytesMatched']
  padding=bytes(r['padSamplesEachSide']*4);expected=padding+slice_pcm+padding
  with wave.open(str(path),'rb')as win:assert win.readframes(win.getnframes())==expected
  rows.append(dict(label=r['label'],path=r['windowPath'],sha256=r['windowSha256'],directlyCompared=True,expectedKo=r['expectedKo'],actualText=r['text'],actualAllWords=r['words'],completeStereoMixSliceReverified=True,**{k:v for k,v in comparisons[r['label']].items()if k not in ['label','directlyCompared']}))
proof=dict(schemaVersion=1,slug='character-parameters',reviewedAt=datetime.now(timezone.utc).isoformat(),
 currentMixedAudioSha256=settings['wavSha256'],currentAacSha256=settings['aacSha256'],planSha256=sha(W/'plan.json'),
 actualAsr=rel(actual_path),actualAsrSha256=sha(actual_path),manualNotes=rel(notes),manualNotesSha256=sha(notes),windows=rows,
 all49WindowsDirectlyCompared=True,all49CurrentMixedPcmSlicesReverified=True,totalWholeChapters=12,totalIndependentCompleteParagraphs=37,
 allFullExpectedActualTextsAndWordsRead=True,unresolvedContentDefects=[],technicallyApproved=True,
 humanWholeListeningApproved=False,humanPronunciationApproved=False,publicRightsApproved=False,
 recognitionAlternatives=manual.get('recognitionAlternatives',[]),humanPending=manual.get('humanPending',[]),
 approvalScope='Full current mixed chapter and independent complete paragraph text/word/PCM comparison; recognizer alternatives retained for human pronunciation review, not human whole listening or rights approval.',
 allFinalPixels=False,qa=False,collected=False,private=False,actualId=None,newTts=0,researchControlChanges=0)
dest.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(windows=49,technicallyApproved=True,humanPronunciationApproved=False,allFinalPixels=False)))
