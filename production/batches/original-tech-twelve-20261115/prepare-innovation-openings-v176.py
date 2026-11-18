"""Prepare the user's finite twelve opening additions; preserve every current body."""
from pathlib import Path
import copy,hashlib,importlib.util,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');C=M/'innovation-openings-v176'
KEY='explicitOriginalTechTwelve20261115'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def save(p,d):
 assert not p.exists(),p
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 hooks=read(H/'innovation-opening-lines-v176.json');manifest=read(H/'local-final-review-manifest-v7.json');assert len(hooks['rows'])==len(manifest['projects'])==12
 C.mkdir(exist_ok=True);rows=[];units=[];paragraphs=[];sourcepins=[pin(H/'innovation-opening-lines-v176.json'),pin(H/'local-final-review-manifest-v7.json')]
 starts={1:[210,230],2:[1174],3:[102],4:[20],5:[210],6:[29,50],7:[29],8:[0,34],9:[9],10:[252],11:[10],12:[237]}
 limits={1:[6.4,15],2:[20],3:[22],4:[19],5:[22],6:[14.5,9.5],7:[21],8:[14.5,8.5],9:[19.5],10:[22],11:[23],12:[21]}
 for row,h in zip(manifest['projects'],hooks['rows']):
  i=row['order'];slug=row['slug'];p=ROOT/'projects'/slug;assert i==h['order']
  for f in row['artifacts'].values():assert pin(f['path'])['sha256']==f['sha256']
  rel={1:'revision-ninja-turns-20261116/film-v78',2:'camera-paired-v164/film-v171',4:'film-v10',8:'clarity-revision-v83/film-v130',9:'film-v10'}.get(i,'clarity-revision-v83/film-v95');fp=M/slug/rel/'pilot-proof.json';film=read(fp);games=[b for b in film['identity']['beats']if b['kind']in['game','pairedGame']]
  src=games[0].get('rightSource',games[0]['source'])if i==2 else games[0]['source']
  if i==11:src=games[-1]['source']
  assert pin(src['path'])['sha256']==src['sha256']
  used=[]
  for beat in games:
   if beat['source']['path']==src['path']:used.append([beat['sourceStartSeconds'],beat['sourceStartSeconds']+beat['end']-beat['start']])
   if beat.get('rightSource',{}).get('path')==src['path']:used.append([beat['rightSourceStartSeconds'],beat['rightSourceStartSeconds']+beat['end']-beat['start']])
  windows=[dict(sourceStartSeconds=a,availableSeconds=n)for a,n in zip(starts[i],limits[i])]
  for w in windows:
   assert all(w['sourceStartSeconds']+w['availableSeconds']<=a or w['sourceStartSeconds']>=z for a,z in used),'No repeated source frames within this revised video'
  primary=p/'planning'/({1:'topic-source-review-v1.json',2:'source-order-map-v1.json'}.get(i,'primary-source-review-v1.json'));d=read(primary);url=d.get('source');url=url.get('url')if isinstance(url,dict)else url
  sourcepins.append(pin(primary));para='o'+f'{i:02}';texts=[]
  for j,(ko,en)in enumerate(zip(h['ko'],h['en'])):
   uid=f'o{i:02}u{j+1:02}';text=' '.join(ko);texts.append(text);units.append(dict(id=uid,paragraph=para,order=i,slug=slug,ko=text,en=' '.join(en),clausesKo=ko,clausesEn=en))
  paragraphs.append(dict(id=para,order=i,slug=slug,ko=' '.join(texts),en=' '.join(' '.join(e)for e in h['en'])))
  bundle=read(row['bundle']['path']);mixes=[e for e in bundle['evidence']if Path(e['path']).name=='audio-build.json']
  if not mixes:mixes=[e for e in film['identity']['inputs']if Path(e['path']).name=='audio-build.json']
  assert len(mixes)==1;mix=read(mixes[0]['path']);assert pin(mix['mix']['path'])['sha256']==mix['mix']['sha256']
  rows.append(dict(order=i,slug=slug,titleKo=row['titleKo'],baseline=row,baselineFilm=pin(fp),baselineMix=pin(mixes[0]['path']),primaryReview=pin(primary),primaryUrl=url,innovationTag=h['tag'],newOpening=paragraphs[-1],introSource=src,candidateWindows=windows,bodyUsedSourceRanges=used,bodyOriginalSubtitles=Path(row['artifacts']['subtitlesKo']['path']).read_text('utf8'),bodyOriginalMix=mix['mix'],sourceLabel=games[0]['label']if i!=2 else'마리오64 (1996) · 닌텐도64 녹화',sourceSpeed=1,sourceAspectPreserved=True,rawSourceAudioUsed=False,bodyPreserved=True))
 plan=H/'innovation-opening-plan-v176.json';save(plan,dict(request=hooks['userRequest'],scope=[r['slug']for r in rows],baselineManifest=pin(H/'local-final-review-manifest-v7.json'),newUnits=24,bodyPcmAndVideoMustBePreserved=True,actualSourcesSameAsPriorVerifiedVersions=True,candidateNewSourceWindowsNeedVisualReview=True,sourceInputs=sourcepins,rows=rows,old111Unchanged=True,youtubeAuthorized=False,driveDeliveryAuthorizedBySession=True,intermediateApprovalRequired=False,actualListening=False,humanApproval=False))
 locked=H/'innovation-opening-narration-v176.json';save(locked,dict(narrationLocked=True,approvedForTts=True,sourceOrderPreserved=True,sourceAndNarrationSemanticsReady=True,baselineManifest=pin(H/'local-final-review-manifest-v7.json'),sourceInputs=sourcepins+[pin(plan)],newUnits=units,reuseUnits=[],units=units,paragraphs=paragraphs,scope='new opening voice only; retain old bodies separately'))
 script=H/'innovation-opening-script-v176.json';save(script,dict(title='Twelve narrated innovation openings',scenes=[dict(id=u['id'],title=u['paragraph'],lines=[u['ko']])for u in units]))
 tts=read(ROOT/'projects/shorts-mario64-lakitu-camera/production/tts-manifest-repair-v147.json');tts['revision']='innovation-openings-v176';tts['paths']['script']=str(script.relative_to(ROOT)).replace('\\','/');tts['tts'].update(outputDir='shared/output/original-tech-twelve-20261115/innovation-openings-v176',filenameStem='innovation-openings-v176');save(H/'innovation-opening-tts-manifest-v176.json',tts)
 spec=importlib.util.spec_from_file_location('intro176_authority',H/'finalize-cpu-preparation-v1.py');sp=importlib.util.module_from_spec(spec);spec.loader.exec_module(sp)
 for name in ['video-production-control.json','video-worklist.json']:
  p=ROOT/'shared/publishing'/name;before=p.read_bytes();raw=before.decode('utf-8-sig');data=json.loads(raw);own=copy.deepcopy(data[KEY]);own.update(status='innovation-opening-revision-preparation',latestUserRequest=str(plan.relative_to(ROOT)).replace('\\','/'),automaticAdvanceWithinExactList=True,automaticAdvanceOutsideList=False,automaticHeartbeatContinuation=False,currentSelectedProject='shorts-mario64-lakitu-camera',activeRevisionScope=[r['slug']for r in rows],completedRevisionScope=[],intermediateApprovalRequired=False)
  own['currentFiniteRevision']=dict(request=pin(H/'innovation-opening-lines-v176.json'),plan=pin(plan),scope=[r['slug']for r in rows],maximumSelectedProjects=12,otherProjectsAuthorized=False,status='preparing-new-opening-voice-and-actual-game-footage',newRecurringAutomation=False,youtubeAuthorized=False,previousBodiesPreserved=True)
  updated=sp.replace_value(raw,KEY,own);a,b=copy.deepcopy(data),json.loads(updated);a.pop(KEY);b.pop(KEY);assert a==b;assert p.read_bytes()==before;p.write_bytes((b'\xef\xbb\xbf'if before.startswith(b'\xef\xbb\xbf')else b'')+updated.encode('utf8'))
 print(json.dumps(dict(plan=pin(plan),newVoiceUnits=24,selectedProjects=12,bodyVersionsPreserved=True)))
if __name__=='__main__':main()
