"""Current raw transcript/math checks, separate from full listening and pixels."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/narration/game-math-polygons-retakes-v3/qwen3-1.7b-balanced-v1'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
records=[]
for ident,name in [('01','QB01'),('02','QB07')]:
 raw=read(O/f'asr/{ident}.json');wav=O/f'chunks/{ident}-scene.wav';assert raw['audio_sha256']==hashlib.sha256(wav.read_bytes()).hexdigest()
 records.append({'addition':name,'currentAudioSha256':raw['audio_sha256'],'rawTranscript':raw['text'],'rawMeaningReview':'Three equal one-third weights and unconstrained edge/vertex distances preserved.' if ident=='01' else 'Whole-at-once connection is unambiguous; three neighboring points, convexity, no boundary crossing, no contained remaining vertex and inside condition preserved.','timingGate':.93,'humanListeningComplete':False})
assert '3분의 1' in records[0]['rawTranscript'] and '한꺼번에' in records[1]['rawTranscript']
assert '3번' not in records[1]['rawTranscript']
r={'reviewedAt':datetime.datetime.now().astimezone().isoformat(),'scope':'Only two newly added phrases retaken; baseline22 explanations/order/approved PCM unchanged.','records':records,'asrMeaningReviewComplete':True,'completeHumanListeningOrFinalPixels':False}
(B/'polygons-retakes-v3-asr-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Current retake raw transcripts and numerical meaning reviewed; human listening remains separate.')
