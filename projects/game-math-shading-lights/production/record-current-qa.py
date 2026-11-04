"""Record measured M21 evidence, keeping visual/listening status explicit."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parents[1];A=P/'production/local/audio-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def evidence(p):return {'path':p.relative_to(P).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
ledger=read(P/'production/review-ledger.json')
def record(d):
    ledger['checks']=[x for x in ledger['checks'] if x['id']!=d['id']]+[d]
t=read(P/'production/local/edit-v1/word-aligned-timeline.json');pcm=read(A/'review/pcm-quality.json')
record({'id':'original-narration-word-alignment','status':'measured-aligned-final-composite-review-pending','paragraphs':len(t['scenes']),'koCues':len(t['ko']),'enCues':len(t['en']),'alignmentFlags':t['flags'],'briefKoCuesUnder085Seconds':sum(x['end']-x['start']<.85 for x in t['ko']),'canonicalTextPreserved':not any(x['type']=='display-text-not-preserved' for x in t['flags']),'evidence':[evidence(P/'production/local/edit-v1/word-aligned-timeline.json'),evidence(A/'review/source-full-asr.timestamps.json'),evidence(P/'production/local/edit-v1/anchor-refinement.json')],'originalAudioChanged':False,'humanListening':False,'limits':'Timestamp and transcript checks are not perceptual listening. Actual final caption/frame joins require final integrated review.'})
record({'id':'original-narration-pcm-levels','status':'numerical-pass-listening-pending' if not pcm['flags'] else 'needs-review','evidence':[evidence(A/'review/pcm-quality.json')],'scope':'All 79 paragraphs and 78 joins','sourceFloatPeak':max(x['samplePeak'] for x in pcm['paragraphs']),'floatHeadroom':'Values above 1 in FLOAT WAV remain unclipped; final normalization/limiting and AAC true-peak check required.','flags':pcm['flags'],'humanListening':False})
record({'id':'dynamic-font-regression','status':'earlier-full-image-preview-diagnosis-corrected','finding':'Full-size tool previews appeared to lose glyphs/objects, but independent original-PNG crops and pixel hashes show the source-kind label unchanged and intact in every SH sample. In v9/v10 the supposedly missing hero crop is byte-identical to frame 0. Direct inspection of cropped original v5/v6 labels confirms complete text. The original PNGs do not support the earlier missing-region diagnosis.','correction':'Discard experimental OS raster/overlay font replacement and restore ordinary editable Unity text with the original 4x MSAA transport. Keep a deliberate line break in the storage summary and enlarge the SH three-line label to protect its final line.','source':evidence(P/'production/unity-staging/LightLabCapture.cs'),'evidence':[evidence(P/'production/unity-staging/local-preflight-v10/crop-diagnostic.png'),evidence(P/'production/unity-staging/local-preflight-v10/original-label-crops.png')],'next':'Review encoded first production scene with actual captions, then full production and integrated QA. Human review remains pending.'})
save(P/'production/review-ledger.json',ledger)
cp=read(P/'production/checkpoint.json');cp.update(updatedAt=datetime.now(timezone.utc).isoformat(),stage='first-production-scene-encoder-QA',voiceWorker=read(A/'finite-worker.json'),wordReviewWorker=read(A/'finite-word-review.json'),nextAction='Inspect actual caption/NVENC sample, then full body rendering and integrated review. Original-PNG crop verification corrected a tool-preview false alarm.',localReviewReady=False)
v=max((P/'production/unity-staging').glob('local-preflight-v*/progress.json'),key=lambda p:p.stat().st_mtime)
if v.exists():
    cp['currentPreflight']=read(v);cp['runningCostlyJobs']=[cp['currentPreflight'].get('current','M21 font regression')] if cp['currentPreflight']['status']=='running-preflight' else []
save(P/'production/checkpoint.json',cp)
project=read(P/'project.json');project.update(status='voice-generated-visual-preflight');project['tts']['status']='generated-review-pending';save(P/'project.json',project)
print('Recorded actual timestamps, PCM statistics and corrected preview diagnosis; no final media completion claimed.')
