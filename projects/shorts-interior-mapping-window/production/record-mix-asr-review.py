"""Compare the complete unchanged mix recognition without claiming listening."""
import difflib,hashlib,json,re
from audio_revision import P,L,guard
guard()
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
mix=L/'final-mix.m4a';record=L/('asr-mix-'+sha(mix)[:12]+'.json');d=read(record)
assert d['sha256']==sha(mix) and d['fullInput'] and not d['expectedTextPromptUsed']
normalize=lambda s:re.sub(r'[^가-힣a-zA-Z0-9]','',s.replace('맵핑','매핑'))
a,b=normalize(d['expected']),normalize(d['text'])
differences=[{'operation':t,'expected':a[i:j],'recognized':b[k:l]} for t,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes() if t!='equal']
assert not differences,'Inspect actual differences; never silently broaden pronunciation aliases.'
result={'status':'full-input-technical-text-match','inputSha256':sha(mix),'asrRecord':record.relative_to(P.parents[1]).as_posix(),'asrSha256':sha(record),'normalization':'Punctuation and spacing removed; 맵핑→매핑 orthography only. Raw recognition preserved.','differences':differences,'durationSeconds':d['inputDurationSeconds'],'humanListening':'pending','pronunciationAndNaturalProsody':'pending human listening, not inferred from ASR'}
(L/'mix-asr-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
continuity=read(L/'audio-continuity.json');continuity['finalMixAsr']='complete; see mix-asr-review.json; human listening remains pending';(L/'audio-continuity.json').write_text(json.dumps(continuity,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':result['status'],'humanListening':'pending'}))
