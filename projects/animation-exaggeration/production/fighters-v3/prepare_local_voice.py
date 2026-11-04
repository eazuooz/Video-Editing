"""Local Qwen-only changed paragraphs, preserving the previous delivery."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[3];L=H.parent/'local/fighters-v3'
def save(p,d):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
auth=json.loads((H/'authorization.json').read_text(encoding='utf-8'))
auth.update(slug='animation-exaggeration',platformMutation=False)
evidence='일래븐랩스 말고 tts 로 만들면돼'
if evidence not in auth['userEvidence']:auth['userEvidence'].append(evidence)
auth['preservation']['voiceForChangedParagraphs']='Local Qwen3-TTS-12Hz-1.7B-Base; existing own-voice reference; latest user selection supersedes ElevenLabs for changed paragraphs only'
auth['rendererSelection']['assetInstallStatus']='Verified GameAnimationSample/GameAnimationSample.uproject, UE5.8.4, UEFN mannequin and idle animation; isolated editable worker created'
save(H/'authorization.json',auth)
paragraphs=(H/'additional-narration.ko.txt').read_text(encoding='utf-8').strip().split('\n\n')
save(H/'additional-qwen-script.json',{'scenes':[{'id':f'F{i+1:02d}','title':title,'lines':[p]} for i,(title,p) in enumerate(zip(['셸미의 상체','지오바나의 실루엣','셸미의 회전'],paragraphs))]})
save(H/'qwen-manifest.json',{'slug':'animation-exaggeration','paths':{'script':(H.relative_to(R)/'additional-qwen-script.json').as_posix()},'editing':{'narrationPlacement':'continuous-across-all-three-segments'},'tts':{'reference':'shared/voice-reference/reference-15-35s.wav','referenceText':'shared/voice-reference/reference-15-35s.ko.txt','model':'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base','outputDir':(L.relative_to(R)/'voice/qwen').as_posix(),'filenameStem':'additional-qwen','language':'Korean','renderMode':'scene','sceneGapSeconds':.28,'lineGapSeconds':.28,'maxNewTokens':4096,'maxRenderAttempts':3,'gpuMinimumFreeMiB':8192,'gpuProfileReason':'Batch1, one complete paragraph per scene on this 16GiB GPU; preserve other processes, check idle capacity before loading.'}})
print('Three complete paragraphs registered for local own-voice Qwen; original14 unchanged.')
