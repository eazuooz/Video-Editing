"""Measured supplemental recognition for a complete-source ASR chunk omission.

Only a derived caption input changes. Source PCM, full/scene ASR and scripts
remain byte-preserved. The root's one unprompted bounded diagnostic supplies the
actual missing abbreviation and interval; no expected prompt or new ASR runs.
"""
from pathlib import Path
import copy,json,hashlib
R=Path(__file__).resolve().parents[4];P=R/'projects/in-game-cutscenes';V=P/'production/local/batch-v1/voice'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def supplement(data,out):
 bounded=Path('C:/Users/1/.codex/video-production/design-finish-six-20261026/review/asr-overlap/in-game-cutscenes.json')
 b=json.loads(bounded.read_text(encoding='utf-8'));assert b['sourceSha256']==sha(V/'narration-source.wav')
 assert b['noExpectedPrompt'] is True and b['oneBoundedPass'] is True
 part=next(x for x in b['segments']if 'qte' in x['text'].lower())
 lo=b['rangeSeconds'][0]+part['timestamp'][0];hi=b['rangeSeconds'][0]+part['timestamp'][1]
 assert (lo,hi)==(249.28,250.72)
 patched=copy.deepcopy(data);row=next(x for x in patched['paragraphs']if x['id']=='09-p01');w=row['words']
 idx=next(i for i,x in enumerate(w)if x['text'].strip()=='이벤트.');assert w[idx+1]['text'].strip()=='연출을'
 origin=w[idx]['sourceTimestamp'][0]-w[idx]['timestamp'][0]
 original=copy.deepcopy(w[idx:idx+2]);a=original[0]['timestamp'][0];z=original[1]['timestamp'][1]
 assert original[0]['sourceTimestamp'][1]>lo and original[1]['sourceTimestamp'][0]<hi
 merged={'text':original[0]['text']+part['text']+original[1]['text'],'timestamp':[a,z],
   'sourceTimestamp':[a+origin,z+origin],
   'measuredPhraseUnion':{'originalWholeSourceWords':original,'boundedSegment':part,'boundedSourceSeconds':[lo,hi],
    'reason':'Adjacent independent recognition intervals overlap by140ms/40ms. Preserve their complete text in the measured union248.62–251.18, rather than invent or force non-overlapping new endpoints.'}}
 w[idx:idx+2]=[merged]
 receipt={'paragraph':'09-p01','sourceAudioSha256':sha(V/'narration-source.wav'),
  'fullAsr':{'path':(V/'whole-source-asr.json').relative_to(R).as_posix(),'sha256':sha(V/'whole-source-asr.json')},
  'boundedEvidence':{'path':bounded.as_posix(),'sha256':sha(bounded),'sourceOffsetSeconds':241,'relativeSegmentSeconds':[8.28,9.72]},'supplement':merged,
  'rawAsrAndPcmUnchanged':True,'scriptsChanged':False,'newRecognition':False,'humanListening':'pending',
  'clock':'Measured source-time interval union converted by exact current scene PCM origin; normal within-phrase caption interpolation retained.'}
 save(P/'production/batch-v1/bounded-caption-recognition-review.json',receipt)
 row['boundedRecognitionSupplement']=receipt;patched['boundedRecognitionEvidence']=str(P/'production/batch-v1/bounded-caption-recognition-review.json')
 save(out/'caption-input.with-bounded-evidence.json',patched)
 return patched
