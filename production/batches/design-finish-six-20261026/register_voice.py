"""Preserve one browser-downloaded Sample B take and bind its current script."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
R=Path(__file__).resolve().parents[3]
SLUGS=['limited-color-world','computer-controlled-players','in-game-cutscenes','start-with-climax','kind-to-beginners','respect-player-time']
ap=argparse.ArgumentParser();ap.add_argument('slug',choices=SLUGS);ap.add_argument('download');ap.add_argument('--credits-before',type=int,required=True);ap.add_argument('--credits-after',type=int,required=True);args=ap.parse_args()
s=args.slug;local=R/'projects'/s/'production/local/batch-v1';physical=Path('C:/Users/1/.codex/video-production/design-finish-six-20261026')/s/'batch-v1'
if local.resolve()!=physical:raise ValueError('Exact episode media route required')
source=Path(args.download)
allowed=source.is_relative_to(Path('C:/Users/1/Downloads')) or ('browser' in str(source).lower() and source.is_relative_to(Path('C:/Users/1/AppData/Local/Temp')))
if not source.is_file() or not allowed:raise ValueError('Actual browser download required')
voice=local/'voice';voice.mkdir(exist_ok=True);dest=voice/'elevenlabs-sample-b-take-01.mp3'
if dest.exists():raise ValueError('Preserve existing take; no replacement')
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
shutil.copyfile(source,dest)
if sha(source)!=sha(dest):raise ValueError('Downloaded bytes changed')
script=R/'projects'/s/'script/batch-v1/narration.spoken-ko.json';data=json.loads(script.read_text('utf8'))
text='\n\n'.join(line for scene in data['scenes'] for line in scene['lines'])
rel=lambda p:p.relative_to(R).as_posix()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
save(voice/'raw-inputs.json',{'sources':[{'path':rel(dest),'sha256':sha(dest)}],'joinSilenceSeconds':.2})
save(voice/'voice-generation.json',{'createdAt':datetime.now(timezone.utc).isoformat(),'provider':'ElevenLabs','approvedSample':'B','voiceId':'jIRSnF8OWAsWEChVwCuK','model':'Eleven v4','settings':{'stability':.5,'similarity':.75,'speed':1,'audioTags':False},'format':'MP3 44.1kHz 192kbps','script':{'path':rel(script),'sha256':sha(script),'plainTextSha256':hashlib.sha256(text.encode()).hexdigest(),'charactersIncludingParagraphBreaks':len(text)},'source':{'path':rel(dest),'sha256':sha(dest),'bytes':dest.stat().st_size},'uiVoiceAndModelVerified':True,'creditsBefore':args.credits_before,'creditsAfter':args.credits_after,'creditsConsumed':args.credits_before-args.credits_after,'planChanged':False,'purchasePerformed':False,'humanListening':'pending'})
print(json.dumps({'slug':s,'raw':rel(dest),'sha256':sha(dest),'scriptCharacters':len(text),'creditsConsumed':args.credits_before-args.credits_after}))
