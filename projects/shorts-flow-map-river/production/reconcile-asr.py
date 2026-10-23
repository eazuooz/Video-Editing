"""Bind spelling reconciliation to one unchanged voice and raw recognizer result.

This is caption alignment, not evidence of human listening or pronunciation approval.
"""
import hashlib,json
from audio_revision import L,VOICE,guard
guard()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=L/('asr-voice-'+sha(VOICE)[:12]+'.json')
aliases={'빨강의':'빨강에','초록의':'초록에','쉐이더는':'셰이더는','바위 주변에':'바위 주변의','되감돼':'되감되','되감던 순간':'되감는 순간'}
data={'voiceSha256':sha(VOICE),'asrSha256':sha(source),'aliases':aliases,'basis':'Full unprompted CPU ASR compared against supplied synthesized text; Korean spelling/particle recognition differences preserved here for caption timing only. No words/clauses omitted.','rawRecognitionPreserved':True,'humanListening':'pending','pronunciationReview':'Remaining particle and 되감는 phrase require final listening; this mapping does not certify pronunciation.'}
target=L/'asr-reconciliation.json'
if target.exists():assert json.loads(target.read_text(encoding='utf8'))==data
else:target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
