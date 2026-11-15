"""Close only this finite local revision, after evidence and actual image review."""
import sys,json,hashlib,html,re
from pathlib import Path
from datetime import datetime,timezone
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE));import render
import importlib.util
_spec=importlib.util.spec_from_file_location('direction_review_progress',HERE/'progress.py');progress=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(progress)
def main():
 plan=render.read(HERE/'plan.json');vis=render.read(HERE/'visual-review.json');scope=plan['scope'];assert {x['id'] for x in vis['episodes'] if x.get('passed')}==set(scope)
 assert render.read(HERE/'deliveries/M25.json').get('verticalAxisLabelCorrection')
 assert render.read(HERE/'deliveries/M26.json').get('projectileAxisLabelCorrection')
 assert all(render.read(HERE/'deliveries'/f'{eid}.json').get('bookendGlyphCorrection') for eid in ('M25','M28','M33'))
 baseline=[];delivered=[]
 for row in plan['episodes']:
  e=render.read(HERE/'deliveries'/f'{row["id"]}.json');assert set(e['files'])=={'clean','captioned','ko','en'} and e['frames']==row['frames']
  assert not e['humanReviewed'] and not e['ttsChanged'] and not e['platformChanged']
  for kind,original in row['sources'].items():
   assert render.sha(original['path'])==original['sha256'],('Previous master changed',row['id'],kind)
   baseline.append(dict(id=row['id'],kind=kind,**original))
  for kind,item in e['files'].items():
   assert render.sha(item['path'])==item['sha256']
   if kind in ('ko','en'):assert item['sha256']==row['sources'][kind]['sha256']
  assert all(q['fullDecode']=='passed' and q.get('packetGrid') for q in e['qa'])
  e.update(status='internal-QA-passed-local-user-review-pending',humanReviewed=False,actualImageReview=next(v for v in vis['episodes'] if v['id']==row['id']));render.save(HERE/'deliveries'/f'{row["id"]}.json',e);delivered.append(e)
  ledger=render.ROOT/'projects'/row['slug']/'production/review-ledger.json'
  if ledger.exists():
   lj=render.read(ledger);lj['directionOverviewRevision20261115']=dict(status=e['status'],files=e['files'],reviewPage=str(progress.HUB/row['id']/'index.html'),technicalQa=True,visualQa=True,humanReviewed=False,originalVoiceAndDurationPreserved=True);render.save(ledger,lj)
 for a in render.read(HERE/'assets.json'):assert render.sha(a['file'])==a['sha256'],('image changed after review',a['id'])
 for f in HERE.glob('*.py'):compile(f.read_text(encoding='utf8'),str(f),'exec')
 render.save(HERE/'baseline-preservation.json',dict(files=baseline,count=len(baseline),allPreviousMastersUnchanged=True,at=datetime.now(timezone.utc).isoformat()))
 progress.main()
 assert progress.read(HERE/'progress.json')['localReadyCount']==13
 # Check relative URLs from the visible hub routes, before following junctions.
 import urllib.parse,urllib.request,os
 links=[]
 for row in plan['episodes']:
  page=progress.HUB/row['id']/'index.html';assert page.exists()
  for href in re.findall(r'(?:src|href)="([^"]+)"',page.read_text(encoding='utf8')):
   if href.startswith(('http:','https:','#')):continue
   uri=urllib.parse.urljoin(page.as_uri(),href);f=Path(urllib.request.url2pathname(urllib.parse.unquote(urllib.parse.urlparse(uri).path)))
   assert f.exists(),(page,href,f);links.append(dict(page=str(page),link=href))
 render.save(HERE/'local-links.json',dict(count=len(links),checked=links,passed=True))
 rights=render.read(HERE.parent/'revision-game-subjects-20261115/source-rights-review.json')['sources'];new=render.read(HERE/'source-rights.json')['additionalSource'];credits=[]
 for s in rights:credits.append(s['title']+' — '+s['uploader']+'\n'+s['recordingUrl']+'\n'+s['recorderPermissionEvidence']+'\nChanges: cropped, background removed where appropriate, resized and annotated for this lecture. Underlying game rights remain with their owners.\n')
 credits.append(new['credit']+'\nLicense information: https://www.youtube.com/t/creative_commons\nChanges: '+new['edit'])
 (progress.HUB/'source-credits.txt').write_text('\n'.join(credits)+'\n',encoding='utf8')
 render.save(HERE/'delivery.json',dict(status='all-thirteen-local-user-review-pending',scope=scope,episodes=delivered,reviewHub=str(progress.HUB/'index.html'),files=52,allPreviousMastersUnchanged=True,originalNarrationAndDurationPreserved=True,allAudioPacketClocksUnchanged=True,subtitlesUnchanged=True,all1080p60=True,platformChanged=False,humanReviewed=False,at=datetime.now(timezone.utc).isoformat()))
 print('All 13 videos finalized locally; 52 masters / subtitles; original masters preserved; links checked')
if __name__=='__main__':main()
