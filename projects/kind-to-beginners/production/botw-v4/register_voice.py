"""Bind one UI-verified own-voice Sample B download; preserve old takes."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path(__file__).resolve().parents[4];H=Path(__file__).resolve().parent;P=H.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n','utf-8')
ap=argparse.ArgumentParser();ap.add_argument('download');ap.add_argument('--credits-before',required=True,type=int);ap.add_argument('--credits-after',required=True,type=int);a=ap.parse_args()
auth=json.loads((H/'authorization.json').read_text('utf8'));assert auth['localProductionAuthorized']and auth['platformMutation']is False
control=json.loads((R/'shared/publishing/video-production-control.json').read_text('utf-8-sig'))
assert control['finiteBatchAuthorizations']['design-25-30-review-actions-20261029']['selectedD29Revision']['revision']=='botw-v4'
src=Path(a.download).resolve();assert src.is_file()and src.is_relative_to(Path('C:/Users/1/Downloads'))
script=P/'script/botw-v4/narration.spoken-ko.txt';assert script.is_file()
dest=P/'production/local/botw-v4/voice/elevenlabs-sample-b-take-01.mp3';assert not dest.exists()
dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest);assert sha(src)==sha(dest)
text=script.read_text('utf8').strip()
record={'createdAt':datetime.now(timezone.utc).isoformat(),'provider':'ElevenLabs','approvedSample':'B',
    'voiceId':'jIRSnF8OWAsWEChVwCuK','model':'Eleven v4','settings':{'stability':.5,'similarity':.75,'speed':1,'audioTags':False},
    'settingsVerification':{'voiceModelStabilitySimilarity':'direct current UI readback','speed':'unchanged Sample B default; no separate speed control exposed in current v4 UI','audioEffects':'none added'},
    'format':'MP3 44.1kHz 192kbps','script':{'path':script.relative_to(R).as_posix(),'sha256':sha(script),
    'submittedTextSha256':hashlib.sha256(text.encode()).hexdigest(),'submittedCharacters':len(text)},
    'source':{'path':dest.relative_to(R).as_posix(),'sha256':sha(dest),'bytes':dest.stat().st_size},
    'browserDownload':str(src),'uiVoiceAndModelVerified':True,'creditsBefore':a.credits_before,'creditsAfter':a.credits_after,
    'creditsConsumed':a.credits_before-a.credits_after,'planChanged':False,'purchasePerformed':False,
    'humanListening':'pending','technicalVerification':'pending','oldTakesPreserved':True}
save(H/'voice-generation-record.json',record);save(dest.parent/'voice-generation.json',record)
save(dest.parent/'raw-inputs.json',{'sources':[record['source']],'joinSilenceSeconds':.2})
print(json.dumps({'source':record['source'],'characters':len(text),'creditsConsumed':record['creditsConsumed']},ensure_ascii=False))
