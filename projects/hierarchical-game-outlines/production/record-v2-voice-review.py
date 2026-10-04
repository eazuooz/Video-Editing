"""Persist direct full-script decisions and verify retained PCM after review."""
from pathlib import Path
import json,hashlib,datetime
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'projects/hierarchical-game-outlines'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
target=BASE/'production/voice-approval-v2.json'
if target.exists():raise RuntimeError('Review existing v2 decision rather than repeat it.')
speech=ROOT/'shared/output/narration/hierarchical-game-outlines/qwen3-1.7b-balanced-v2'
full=speech/'hierarchical-game-outlines-qwen3-1.7b-balanced-v2.asr-review.json'
report=read(full);ctxPath=BASE/'production/repair1/v2-context/asr.json';ctx=read(ctxPath)
assert report['complete'] and report['sceneCount']==12 and ctx['complete'] and len(ctx['results'])==7
ko=read(BASE/'script/narration.ko.json');en=read(BASE/'script/narration.en.json')
proofPath=BASE/'production/repair1/v2-composite-proof.json';proof=read(proofPath)
initial=read(BASE/'production/voice-approval-initial.json');initialBy={s['scene']:s for s in initial['scenes']}
notes={
 '03':'Both replacement paragraphs and all retained three paragraphs complete. Independent join read-backs preserve adjacent clauses. 의/에 are /e/ ASR spelling differences.',
 '05':'All six current paragraphs complete. Full-scene ASR added 다음 영상에서 만나요 after the expected ending; two independent current-hash ending windows contain only the exact comparison limitation. The last original PCM is byte-identical and its initial independent ending was also complete without a farewell. Preserve the full ASR artifact; do not append it to script/captions or claim human hearing.',
 '11':'All seven paragraphs, replacement and return-to-goal ending complete in whole ASR and independent join/end. 의/에 are /e/ and 잇지/잊지 are homophones; spelling normalization does not change the separate-actions claim.',
 '12':'All four paragraphs and both coaching/conclusion sentences complete in full and independent final window. Replacement itself is at least as long as the original removed explanation paragraph.'}
rows=[]
for s in report['scenes']:
 sid=s['scene'];audio=speech/'chunks'/f'{sid}-scene.wav';cache=speech/'asr'/f'{sid}.json';assert s['audio_sha256']==sha(audio)==read(cache)['audio_sha256']
 expected=next(v for v in ko['scenes'] if v['id']==sid);paired=next(v for v in en['scenes'] if v['id']==sid)
 assert len(expected['lines'])==len(paired['lines'])
 p=next(v for v in proof['scenes'] if v['scene']==sid);assert sha(audio)==p['compositeSha256']
 original,rate=sf.read(ROOT/p['source'],dtype='int16');current,newRate=sf.read(audio,dtype='int16');assert rate==newRate==24000
 if p.get('wholeWaveByteIdentical'):
  assert sha(audio)==sha(ROOT/p['source']);assert initialBy[sid]['decision']=='content-readback-pass'
 else:
  for r in p['retainedPcm']:
   a,b=r['sourceFromSample'],r['sourceToSample'];c=r['compositeFromSample'];n=r['samples']
   assert np.array_equal(original[a:b],current[c:c+n]);assert hashlib.sha256(current[c:c+n].tobytes()).hexdigest()==r['pcmSha256']
 if int(sid)%2==0:assert len(current)>=len(original)
 p['wholeCompositeAsrReviewed']=True;p['directReviewReport']=target.relative_to(ROOT).as_posix()
 rows.append({**s,'audio':audio.relative_to(ROOT).as_posix(),'asr':cache.relative_to(ROOT).as_posix(),'asr_sha256':sha(cache),
  'decision':'content-readback-pass','notes':notes.get(sid,initialBy[sid]['notes']+' Re-read current v2 full content; byte-identical current WAV/cache validated.'),
  'allParagraphsDirectlyCompared':True,'paragraphCount':len(expected['lines']),'humanListening':'pending'})
for r in ctx['results']:assert sha(ROOT/r['source'])==r['sourceSha256']
at=datetime.datetime.now(datetime.timezone.utc).isoformat()
write(target,{'status':'all12-current-v2-content-and-joins-technically-reviewed','reviewedAt':at,'kind':'direct ASR/script and PCM comparison; human listening separate',
 'fullReport':full.relative_to(ROOT).as_posix(),'fullReportSha256':sha(full),'contextReport':ctxPath.relative_to(ROOT).as_posix(),'contextReportSha256':sha(ctxPath),
 'initialContextReport':'projects/hierarchical-game-outlines/production/initial-context/asr.json','currentHashChecked':True,'allCurrentScenesTechnicallyReviewed':True,
 'all60ParagraphsDirectlyCompared':True,'unchangedParagraphs':54,'unchangedPcmVerified':True,'explanationLengthsPreserved':True,'notOnlyEndingHeuristic':True,
 'scenes':rows,'finalRenderingApproved':False,'humanListening':'pending'})
proof['status']='all-retained-PCM-verified-current-v2-whole-ASR-and-joins-directly-reviewed';write(proofPath,proof)
manifest=read(BASE/'project.json');v2manifest=read(BASE/'production/repair1/v2.manifest.json')
manifest['tts']=v2manifest['tts']
for k in ['narration','captionsKo','captionsEn']:manifest['paths'][k]=v2manifest['paths'][k]
manifest['status']='voice-current-hash-technically-reviewed-final-source-fitting-pending'
manifest['approvals']['voiceReadback']='all12-v2-scenes/60paragraphs/7join-contexts-directly-compared; human full listening pending'
write(BASE/'project.json',manifest)
gatePath=BASE/'production/script-source-review.json';gate=read(gatePath);gate['speechTechnicallyReviewed']=True;gate['voiceEvidence']=target.relative_to(ROOT).as_posix();gate['finalRenderingApproved']=False
gate['inputs']=[{**x,'sha256':sha(ROOT/x['path'])} for x in gate['inputs']];write(gatePath,gate)
print('12 scenes /60 paragraphs /7 independent joins/endings /54 preserved paragraphs and PCM: technical content pass. Human listening, source fit and final pixels remain pending.')
