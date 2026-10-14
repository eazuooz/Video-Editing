"""Prepare current own wrappers; never start a model or alter research controls."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,py_compile
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
voice=B/'render-voice-v1.py';verify=B/'verify-own-voice-research-resume-v1.py';asr=B/'review-current-voice-v1.py'
assert not any(p.exists() for p in [voice,verify,asr])
source=ROOT/'projects/character-parameters/production/render-voice-v1.py'
code=source.read_text(encoding='utf-8-sig').replace('character-parameters','limited-color-world')
for a,b in [('request[\'total\']==12','request[\'total\']==8'),("request['paragraphs']==37","request['paragraphs']==24"),('Prepared12 scenes/37 paragraphs','Prepared8 scenes/24 paragraphs'),('total=12','total=8'),('twelve-scenes-measured','eight-scenes-measured')]:code=code.replace(a,b)
voice.write_text(code,encoding='utf-8')
source_verify=ROOT/'projects/character-parameters/production/verify-own-voice-research-resume-v1.py'
v=source_verify.read_text(encoding='utf-8-sig').replace('character-parameters','limited-color-world').replace("state['total']==12","state['total']==8").replace('allTwelveCurrentPcmHashesMatched','allEightCurrentPcmHashesMatched').replace('Actual twelve-scene','Actual eight-scene')
verify.write_text(v,encoding='utf-8')
source_asr=ROOT/'projects/character-parameters/production/review-current-voice-v1.py'
a=source_asr.read_text(encoding='utf-8-sig').replace('character-parameters','limited-color-world').replace('narration-tts-execution-v2','narration-tts-execution-v1').replace('research-handoff-verification-v2','research-handoff-verification-v1')
for old,new in [("len(tts['results']) == 12","len(tts['results']) == 8"),("len(script['scenes']) == 12","len(script['scenes']) == 8"),("for x in script['scenes']) == 37","for x in script['scenes']) == 24"),("len(plan['contexts']) >= 12","len(plan['contexts']) >= 8"),('current-twelve-voice','current-eight-voice')]:a=a.replace(old,new)
asr.write_text(a,encoding='utf-8')
for p in [voice,verify,asr]:py_compile.compile(str(p),doraise=True)
audit={'preparedAt':datetime.now(timezone.utc).isoformat(),'scope':'Only own limited-color-world wrappers',
 'wrappers':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [voice,verify,asr]],
 'sources':[{'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)} for p in [source,source_verify,source_asr]],
 'pyCompileExitCode':0,'modelLoaded':False,'newPcm':0,'researchControlsChanged':0,
 'requiredInterpreter':'D:/Github/Video-Editing/qwen3-tts/.venv/Scripts/python.exe',
 'interpreterReason':'Completed char used this venv; its historical plain miniconda attempt lacked soundfile and is not repeated.',
 'note':'Single8scene24paragraph wrapper validates current protected text, waits before model on a foreign lease, then uses the shared owned cooperative coordinator; exact original research resume must be verified after actual outer exit.'}
(B/'prepared-voice-wrappers-v1.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(B/'prepared-current-asr-v1.json').write_text(json.dumps({'preparedAt':audit['preparedAt'],'worker':asr.relative_to(ROOT).as_posix(),'workerSha256':sha(asr),
 'plannedWholeScenes':8,'plannedMinimumIndependentCompleteContexts':8,'expectedScriptIsRecognizerPrompt':False,'cpuThreads':2,'gpu':0,
 'requiresObservedActualTtsExit':True,'requiresOwnedResearchRestoration':True,'requiresFreshResource':True,'executed':False,'modelLoaded':False,'narrationApproved':False,'finalMixedAsrApproved':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Own8scene TTS, actual-session restoration verifier and CPU2 ASR prepared; compile0, model/research mutation0.')
