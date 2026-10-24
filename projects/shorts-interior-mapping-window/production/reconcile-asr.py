"""One raw-ASR spelling variant, bound to this unchanged voice hash."""
import hashlib,json
from audio_revision import L,VOICE,guard
guard()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=L/('asr-voice-'+sha(VOICE)[:12]+'.json')
data={'voiceSha256':sha(VOICE),'asrSha256':sha(source),'aliases':{'인테리어 맵핑':'인테리어 매핑'},'basis':'Full unprompted CPU ASR differs only in Mapping orthography. All narration words retained. Canonical display spelling is 매핑.','rawRecognitionPreserved':True,'humanListening':'pending','pronunciationReview':'Whole-voice listening remains pending; this spelling reconciliation is not human approval.'}
target=L/'asr-reconciliation.json'
if target.exists():assert json.loads(target.read_text(encoding='utf8'))==data
else:target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
