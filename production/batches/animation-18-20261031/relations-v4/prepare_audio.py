from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2];L=H/'local';L.mkdir(exist_ok=True)
p=json.loads((H/'planning/relations-plan.json').read_text('utf-8'));assert p['status']=='ready'
assert len(p['episodes'])==18
script={'scenes':[{'id':e['id'],'title':e['title'],'lines':[' '.join(s.get('spokenKo',s['ko']) for s in e['sentences'])]} for e in p['episodes']]}
(H/'added.ko.json').write_text(json.dumps(script,ensure_ascii=False,indent=2)+'\n','utf-8')
manifest={'slug':'animation-relations-v4','revision':'relations-v4','voice':'same approved own-voice Qwen3 1.7B additive narration','paths':{'script':str((H/'added.ko.json').relative_to(R)).replace('\\','/')},'editing':{'narrationPlacement':'continuous-across-example-and-explanation'},'tts':{'language':'Korean','model':'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base','reference':'shared/voice-reference/reference-15-35s.wav','referenceText':'shared/voice-reference/reference-15-35s.ko.txt','outputDir':str((L/'voice').relative_to(R)).replace('\\','/'),'filenameStem':'relations','renderMode':'scene','sceneGapSeconds':.4,'tailRatioThreshold':.07,'tailDecayMsThreshold':70,'maxRenderAttempts':3,'maxNewTokens':2048,'edgeFadeSeconds':.006,'gpuMinimumFreeMiB':8192,'gpuProfileReason':'18 additive paragraphs, one continuous synthesis per episode, batch1; existing cooperative GPU lease, no concurrent model loads. Existing delivered audio untouched.'}}
(H/'tts-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
print('18 additive paragraphs ready; no original narration changed')
