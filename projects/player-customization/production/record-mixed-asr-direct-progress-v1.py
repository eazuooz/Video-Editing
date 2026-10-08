"""Record only explicitly read windows; never infer final approval from ASR."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'));now=lambda:datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,j):
 t=p.with_name(p.name+f'.{os.getpid()}.writing')
 for n in range(60):
  try:t.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(t,p);return
  except OSError:
   if n==59:raise
   time.sleep(.15)
ap=argparse.ArgumentParser();ap.add_argument('--labels',nargs='+',required=True);a=ap.parse_args()
path=W/'mixed-asr-direct-progress.json';s=read(path) if path.exists() else dict(schemaVersion=1,slug='player-customization',windows=[])
for label in a.labels:
 p=W/'mixed-asr-v1'/f'{label}.json';x=read(p)
 assert x['exactStereoMixSampleBytesMatched'] and not x['expectedWasRecognizerPrompt']
 assert label not in [r['label'] for r in s['windows']], 'Window already directly recorded.'
 s['windows'].append(dict(label=label,path=p.relative_to(ROOT).as_posix(),sha256=sha(p),expectedKo=x['expectedKo'],actualText=x['text'],
  expectedAndEntireActualTextDirectlyRead=True,directlyCompared=True,independentContextResolutionPending=label.startswith('whole-'),technicalApprovalPending=True))
s.update(updatedAt=now(),mixSha256=read(W/'mix-settings.json')['wavSha256'],planSha256=sha(W/'plan.json'),
 readCount=len(s['windows']),wholeReadCount=sum(x['label'].startswith('whole-') for x in s['windows']),contextReadCount=sum(x['label'].startswith('context-') for x in s['windows']),
 all32WindowsDirectlyCompared=False,technicallyApproved=False,automaticApproval=False,finalMixedAsrApproved=False,
 humanWholeListening='pending',humanPronunciation='pending',allFinalPixels=False,collected=False,uploaded=False,
 currentObservedDifferences=[
  dict(scope='whole02',detail='경로의→경로에, 바닥에→바닥의; complete expected/actual sentences intact; independent context pending.'),
  dict(scope='whole10',detail='단테→단태 and 내게임의→내게임에; name/particle readback uncertainty retained; independent context pending.'),
  dict(scope='whole11',detail='바닥에→바닥의, 앞의→앞에 and spacing; independent context pending.'),
  dict(scope='whole12',detail='화면의→화면에; full centre/nearby-target/relative-position clauses retained; context pending.'),
  dict(scope='whole13',detail='단테→단태 and 같게→갖게; current-build/ranking caveat and complete ending retained; context pending.')])
save(path,s);print(json.dumps(dict(readCount=s['readCount'],whole=s['wholeReadCount'],contexts=s['contextReadCount'],approved=False)))
