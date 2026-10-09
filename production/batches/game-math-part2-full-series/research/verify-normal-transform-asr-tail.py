from pathlib import Path
import json,hashlib,datetime
import soundfile as sf
R=Path(__file__).resolve().parents[4];slug='game-math-normal-transform-uv'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
out=R/f'shared/output/narration/{slug}/qwen3-1.7b-balanced-v1'
rawfile=out/'asr/11.json';raw=read(rawfile);wave=out/'chunks/11-scene.wav'
assert raw['audio_sha256']==sha(wave)=='a36f0dba0a6471c40257d7d52d1f0b7b1ed23a803984427ae21514b871bcfef3'
tail=raw['words'][-3:];assert [w['text'].strip() for w in tail]==['다음','영상에서','만나요.']
duration=tail[-1]['timestamp'][1]-tail[0]['timestamp'][0]
assert duration<.07 and sum(w['timestamp'][0]==w['timestamp'][1] for w in tail)==2
diag=R/f'shared/output/{slug}/line-repair-11/final-line-readback'
indfile=diag/'asr/11.json';ind=read(indfile);source=read(diag/'source.json');sfdata,sr=sf.read(R/source['source'])
assert ind['audio_sha256']==source['sourceSha256']==sha(R/source['source'])
assert '다음' not in ind['text'] and '둘 다 지킵니다' in ind['text']
record={'status':'passed-independent-raw-final-line-check-inferred-decoder-artifact',
    'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scene':'11','fullWaveSha256':sha(wave),
    'fullRawAsr':{'path':rawfile.relative_to(R).as_posix(),'sha256':sha(rawfile),'text':raw['text']},
    'decoderAddedWords':tail,'addedPhraseTotalTimestampSeconds':duration,
    'independentFinalLine':{'exactSource':source['source'],'wavSha256':source['sourceSha256'],'durationSeconds':len(sfdata)/sr,'rawAsr':indfile.relative_to(R).as_posix(),'rawAsrSha256':sha(indfile),'text':ind['text']},
    'conclusion':'Both complete final-line sentences retained. The nine-syllable added farewell occupies only0.06s with two zero-duration words and is absent from independently transcribing its unchanged source line; infer a full-scene decoder artifact. Preserve all raw text and waveform.',
    'audioChangedForDiagnostic':False,'asrModelChanged':False,'humanListening':'pending'}
(R/f'projects/{slug}/production/asr-zero-duration-tail-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print({'waveUnchanged':True,'fullRawPreserved':True,'independentFinalLine':ind['text'],'addedPhraseSeconds':duration})
