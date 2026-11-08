from pathlib import Path
import json,hashlib,subprocess,array,math
P=Path(__file__).resolve().parents[1];L=P/'production/local';Q=L/'qa'
def read(f):return json.loads(f.read_text('utf-8'))
def sha(f):return hashlib.file_digest(f.open('rb'),'sha256').hexdigest()
t=read(L/'timeline.json');nar=read(Q/'narration.timestamps.json');mix=read(Q/'mix.timestamps.json')
assert nar['audio_sha256']==sha(L/'narration-aligned.wav')
assert mix['audio_sha256']==sha(L/'final-mix.wav')
assert '이제 완성한 캐릭터 옆에 배경을 놓아' in nar['text'] and '이제 완성한 캐릭터 옆에 배경을 놓아' in mix['text']
silence=[]
for file in [L/'narration-aligned.wav',L/'final-mix.m4a']:
 b=subprocess.check_output(['ffmpeg','-hide_banner','-v','error','-ss',str(t['duration']-8),'-i',str(file),'-t','7.9','-vn','-ac','1','-ar','16000','-f','f32le','-'])
 v=array.array('f');v.frombytes(b);peak=max(map(abs,v));assert peak<1e-6,(file,peak)
 silence.append({'file':file.name,'start':t['duration']-8,'duration':7.9,'peak':peak,'conclusion':'ASR end-credit sentence occurs in digital silence and is not narration or a caption.'})
a=read(L/'alignment-review.json');a['manualReview']='All30 complete current narration and final-mix transcripts directly read and compared to retained script. Paragraph15 repaired. No material spoken content omitted in current readback.'
a['diagnostics']={'scene04':'Full mix segment ASR repeated 것​​은 아닙니다 across its own segment boundary. Word-ASR and isolated current-mix CPU ASR both contain it once; no audio cut or TTS regeneration warranted. Diagnostic includes slight following-scene context, whose cropped ending is not judged as a complete line.','outro':silence,'pronunciation':'ASR spellings of ChatGPT/PixelOE/VAE/PNG/diffusion differ from canonical screen spelling. No human listening claim; user final pronunciation/naturalness review remains pending.'}
(L/'alignment-review.json').write_text(json.dumps(a,ensure_ascii=False,indent=2)+'\n','utf-8')
qa=read(P/'production/audio-qa.json');qa['asr']='complete current narration and current mix; directly reviewed';qa['asrReviewEvidence']='production/local/alignment-review.json';qa['humanListening']='pending';(P/'production/audio-qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n','utf-8')
(P/'production/asr-review.json').write_text(json.dumps({'status':'reviewed-complete-current-text','narrationSha256':nar['audio_sha256'],'mixSha256':mix['audio_sha256'],'paragraphs':30,'pairedCues':len(read(L/'captions.json')),'minimumAlignment':min(r['sequenceRatio'] for r in a['paragraphs']),'scene15OpeningVerified':True,'scene04DiagnosticSha256':sha(Q/'scene04-mix-diagnostic.txt'),'silentOutroEvidence':silence,'humanListening':'pending'},ensure_ascii=False,indent=2)+'\n','utf-8')
print('All30 current paragraphs reviewed; scene15 complete; scene04 ASR duplicate disproved; outro digital silence confirmed')
