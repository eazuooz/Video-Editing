"""Verify cached whole-voice/mix ASR and captions without repeating GPU work."""
from pathlib import Path
import datetime,difflib,hashlib,json,subprocess
from tutorial_speech_evidence import compare_speech

H=Path(__file__).resolve().parent
L=H/'local/full-video-v5'

def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def norm(text):return ''.join(c.lower() for c in text if c.isalnum())

timing=json.loads((L/'timeline.json').read_text('utf-8'))
alignment=json.loads((L/'alignment-review.json').read_text('utf-8'))
asr={k:json.loads((L/'qa'/f'{k}.timestamps.json').read_text('utf-8')) for k in ('narration','mix')}
for key,path in [('narration',L/'narration-aligned.wav'),('mix',L/'final-mix.m4a')]:
    assert asr[key]['audio_sha256']==sha(path),(key,'stale ASR')
    assert asr[key]['timestampMode']=='word'
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-i',str(path),'-f','null','-'],check=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
assert alignment['audioSha256']==asr['narration']['audio_sha256']
assert len(alignment['paragraphs'])==len(timing['scenes'])==31
missing=[{'id':p['id'],'spans':p['missingSpans']} for p in alignment['paragraphs'] if p['missingSpans']]
assert not missing,missing
coverage=compare_speech(asr['narration'],asr['mix'],timing,L/'narration-aligned.wav')
mix_missing=coverage['materialMissingSpans']
assert coverage['ratioAgainstFullNarrationAsr']>.94 and not mix_missing,coverage
cues=json.loads((L/'captions.json').read_text('utf-8'))
for i,cue in enumerate(cues):
    assert 0<=cue['start']<cue['end']<=timing['duration']
    assert cue['ko'].strip() and cue['en'].strip()
    if i:assert cues[i-1]['end']<=cue['start']+.000001
assert {c['scene'] for c in cues}=={s['id'] for s in timing['scenes']}
report={
    'revision':'tutorial-v5','checkedAtKst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),
    'durationSeconds':timing['duration'],'paragraphs':31,'captionCues':len(cues),
    'narrationSha256':asr['narration']['audio_sha256'],'encodedMixSha256':asr['mix']['audio_sha256'],
    'cachedWholeAsrValidated':True,'newAsrRuns':0,'bothAudioFilesFullyDecoded':True,
    'paragraphLongMissingSpans':missing,'mixLongMissingSpans':mix_missing,
    'mixRatioAgainstNarrationAsr':coverage['ratioAgainstFullNarrationAsr'],
    'speechCoverageEvidence':coverage,
    'minimumRawParagraphAlignment':min(p['ratio'] for p in alignment['paragraphs']),
    'captionTimingMonotonicAndNonoverlapping':True,'captionLanguages':['ko','en'],
    'knownAsrAmbiguities':[
        {'scene':'07','context':'ComfyUI / Hunyuan3D / Image-to-3D','finding':'Raw spelling differs for tool names/numbers and includes the next sentence at its timing boundary. No long omitted phrase; exact audio and matching word ASR retained.'},
        {'scene':'01','context':'뼈대를 얻습니다','finding':'ASR recognizes 넣습니다. One-word recognition ambiguity, not independently resolved by listening.'},
        {'scene':'18','context':'표지 바깥에서 받칩니다','finding':'ASR recognizes 맞춥니다. One-word recognition ambiguity, not independently resolved by listening.'}
    ],
    'wholeHumanListening':'pending','humanFinalVideoReview':False,
    'limitation':'ASR coverage and decode do not certify pronunciation, natural prosody or human listening.'
}
(H/'tutorial-v5-audio-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
qa=json.loads((H/'full-video-audio-qa.json').read_text('utf-8'))
qa['asr']={'status':'whole-narration-and-encoded-mix-coverage-checked','report':'production/tutorial-v5-audio-check.json','ratio':coverage['ratioAgainstFullNarrationAsr'],'longMissingSpans':mix_missing,'humanListening':'pending'}
(H/'full-video-audio-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:report[k] for k in ('durationSeconds','paragraphs','captionCues','mixRatioAgainstNarrationAsr','paragraphLongMissingSpans','wholeHumanListening')},ensure_ascii=False))
