"""Review current immutable ASR; select out only same-clock stride hypotheses."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[4];P=R/'projects/start-with-climax';H=P/'production/batch-v1';V=P/'production/local/batch-v1/voice'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
a=read(V/'whole-source-asr.json');c=read(V/'whole-source-comparison.json');w=a['words'];digest=sha(V/'narration-source.wav');raw_digest=sha(V/'whole-source-asr.json')
assert a['audio_sha256']==digest==c['audioSha256']
norm=lambda t:re.sub(r'\W','',t)
original=' '.join(x['text']for x in w[324:345]);duplicate=' '.join(x['text']for x in w[346:366])
assert norm(original)==norm(duplicate)
assert w[345]['text'].strip()=='2.' and w[346]['timestamp'][0]<w[345]['timestamp'][0]
removed=set(range(345,366));keep=[i for i in range(len(w))if i not in removed]
starts=[w[i]['timestamp'][0]for i in keep];assert starts==sorted(starts)
save(V/'alignment-selection-review.json',{'sourceAsrSha256':raw_digest,'sourceAudioSha256':digest,'fullRawTextCompared':True,'reason':'Root and delegated reference agent directly read full frozen spoken input, complete raw recognized text and every comparison difference. Only duplicated same-audio stride hypotheses346–365 and adjoining unsupported tail345 are excluded for alignment; no audio/text/timestamps edited.','keepWordIndices':keep,'removed':[{'indices':[345],'reason':'Unsupported chunk-tail 2. at169.72–169.98s before ASR clock regresses; not evidence of extra actual speech. Final contextual listening remains pending.'},{'indices':list(range(346,366)),'reason':'Recognizer regresses169.72→160.00s. Same Korean text already present in retained324–344; timestamps cover the same159.98–169.66 source interval, with minor per-word boundary variation.'}],'duplicateEvidence':{'retainedRange':[324,344],'excludedRange':[346,365],'retainedText':original,'excludedText':duplicate,'sameTextIgnoringPunctuationWhitespace':True,'retainedSeconds':[w[324]['timestamp'][0],w[344]['timestamp'][1]],'excludedSeconds':[w[346]['timestamp'][0],w[365]['timestamp'][1]]},'humanListening':'pending; no perceptual approval inferred','audioAltered':False,'rawAsrAltered':False,'newRecognitionPass':False})
save(H/'source-comparison-review.json',{'audioSha256':digest,'comparisonSha256':sha(V/'whole-source-comparison.json'),'sourceAsrSha256':raw_digest,'fullTextDirectlyCompared':True,'reviewer':'Root full direct read and /root/d22_reference full expected/recognized/difference read','all24ParagraphClaimsAndOrderPresent':True,'notes':'Canonical1/일 and2/투 notation differences are recognition spelling. Three 스핀 tokens recognized as 스피/스피를 remain final pronunciation/context listening flags, not an asserted TTS error or silent speech correction. The overlap hypotheses are selected out separately while immutable PCM and rawASR remain preserved.','pronunciationListeningFlags':['스핀 versus 스피/스피를 at three mentions','Unsupported ASR chunk-tail2. before the recognized-clock regression'],'humanListening':'pending','newRecognitionPass':False,'audioAltered':False})
assert sha(V/'narration-source.wav')==digest and sha(V/'whole-source-asr.json')==raw_digest
print('Current full-text comparison and exact indexed alignment selection saved; source audio/rawASR unchanged.')
