"""Record actual current-hash machine readback; preserve the human listening task."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
slug='game-math-interpolation-numeric-retakes-v4'
m=json.loads((ROOT/f'projects/{slug}/project.json').read_text(encoding='utf8'))
out=ROOT/m['tts']['outputDir'];rows=[]
requirements={'01':['첫 번째 성분은 루트 2 나누기 2','두 번째 성분도 루트 2 나누기 2','세 번째 성분은 0','마이너스 45도','1, 0, 0'],'02':['3의 제곱인 9','4의 제곱인 16','25입니다','제곱근은 5','45도']}
for ident,checks in requirements.items():
    asr=json.loads((out/f'asr/{ident}.json').read_text(encoding='utf8'))
    wav=out/f'chunks/{ident}-scene.wav';sha=hashlib.sha256(wav.read_bytes()).hexdigest()
    assert sha==asr['audio_sha256'] and all(x in asr['text'] for x in checks)
    rows.append({'scene':ident,'audioSha256':sha,'readbackText':asr['text'],'requiredNumericalPhrases':checks,'criticalNumeralsPresent':True,'directlyReadMachineTranscript':True,'humanListening':'pending'})
history=json.loads((ROOT/'shared/output/gpu-handoff/aa4ef790-cb3d-4c09-a222-66a218fc7ef5.json').read_text(encoding='utf8'))
assert history['ttsExitCode']==0 and history['state']=='research_resume_verified'
(B/'interpolation-numeric-v4-readback.json').write_text(json.dumps({'records':rows,'audioModifiedByReview':False,'gpuHandoffToken':history['token'],'researchQueueRestartedAndStateVerified':True,'resumedStatusAtHandoff':history['resumedStatus']['status'],'humanWholeListening':'pending','movingPixelsAndPublishing':'pending'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Current numerical readbacks recorded; human whole listening remains pending.')
