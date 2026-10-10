"""Derive reviewed single-batch wrappers without starting a model or research job."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, py_compile
ROOT=Path(__file__).resolve().parents[3]; BASE=Path(__file__).resolve().parent
voice=BASE/'render-voice-v1.py'; verifier=BASE/'verify-own-voice-research-resume-v1.py'
assert not voice.exists() and not verifier.exists(), 'Preserve the current wrappers; do not recreate them.'
original=ROOT/'projects/presenting-game-scores/production/render-voice-v1.py'
code=original.read_text('utf-8-sig').replace('presenting-game-scores','character-parameters')
code=code.replace('Prepared10 scenes/30 paragraphs','Prepared12 scenes/37 paragraphs')
code=code.replace('total=10','total=12').replace('ten-scenes-measured','twelve-scenes-measured')
code=code.replace("assert request['pairedWholeTextReview'] and request['overviewPromiseReview']", "assert request['pairedWholeTextReview'] and request['overviewPromiseReview']\nassert request['total']==12 and request['paragraphs']==37\nassert not any((ROOT/s['path']).exists() for s in request['scenes']), 'Inspect existing PCM before retrying any synthesis'")
voice.write_text(code,'utf-8')
original_verifier=ROOT/'projects/presenting-game-scores/production/verify-own-voice-research-resume-v1.py'
verify=original_verifier.read_text('utf-8-sig').replace('presenting-game-scores','character-parameters')
verify=verify.replace("assert args.session_id==30677,'Require the actual original serialized request session'", "session=read(BASE/'narration-tts-session-v1.json')\nassert args.session_id==session['sessionId'], 'Require the actual original serialized request session'")
verify=verify.replace("state['total']==10","state['total']==12").replace('allTenCurrentPcmHashesMatched','allTwelveCurrentPcmHashesMatched').replace('Actual ten-scene','Actual twelve-scene')
verifier.write_text(verify,'utf-8')
py_compile.compile(str(voice),doraise=True); py_compile.compile(str(verifier),doraise=True)
audit=dict(preparedAt=datetime.now(timezone.utc).isoformat(),scope='Own character-parameters wrappers only',
    voice=dict(path=voice.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(voice.read_bytes()).hexdigest(),source=original.relative_to(ROOT).as_posix(),sourceSha256=hashlib.sha256(original.read_bytes()).hexdigest()),
    verifier=dict(path=verifier.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(verifier.read_bytes()).hexdigest()),
    pyCompileExitCode=0,modelLoaded=False,newPcm=0,researchControlsChanged=0,
    note='The shared renderer assembles WAV/SRT/timing only; it does not create or overwrite Motion Canvas sources. Verifier needs observed outer completion and actual current original research ownership.')
(BASE/'prepared-voice-wrappers-v1.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Own twelve-scene wrapper and actual-session verifier prepared; compile0, no model/process/control mutation.')
