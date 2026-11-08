"""Prepare content-addressed changed speech only, preserving all existing takes."""
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[3]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,j):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108']
assert control['fullLocalProductionAuthorized'] and control['renderAuthorized'] and control['candidateUserApproval']['text']=='이 목록으로 진행'
source=H/'narration/source-verified-revisions.json';revisions=read(source);items=[];mapping=[]
for ep in revisions['episodes']:
 assert ep['id'] in control['episodes'] and ep['id']!='A03'
 for c in ep['changes']:
  if not c.get('localReviewTextReleased'):continue
  assert ep['completeKoEnReadThrough'] and c['completeKoEnReadThrough'] and c['sourceVerified']
  assert (R/c['evidence']).is_file()
  text=c.get('spokenKo',c['ko']);key=ep['id']+'S'+c['id']+'X'+hashlib.sha256(text.encode('utf8')).hexdigest()[:10]
  items.append({'id':key,'title':ep['id']+' passage '+c['id'],'lines':[text]})
  mapping.append({'key':key,'episode':ep['id'],'sentence':c['id'],'text':text,'ko':c['ko'],'en':c['en'],'evidence':c['evidence'],'sourceVerified':True,'textSHA256':hashlib.sha256(text.encode('utf8')).hexdigest()})
assert items
save(H/'narration/released-tts.ko.json',{'scenes':items})
save(H/'narration/released-tts-map.json',{'inputSHA256':sha(source),'entries':mapping,'existingA10TakesPreserved':True})
m=read(H/'narration/tts-manifest.json');m['paths']['script']=(H/'narration/released-tts.ko.json').relative_to(R).as_posix();m['tts'].update(outputDir=(H/'local/voice-reviewed').relative_to(R).as_posix(),filenameStem='released-game-passages',gpuMinimumFreeMiB=8192,gpuProfileReason='Same approved1.7B voice, scene-mode batch1, shared GPU guard serialized; no engine capture or concurrent GPU model. Content-addressed changed passages only. Foreign work preserved.')
save(H/'narration/released-tts-manifest.json',m)
print(json.dumps({'releasedChangedPassages':len(items),'scriptSHA256':sha(H/'narration/released-tts.ko.json'),'manifest':(H/'narration/released-tts-manifest.json').relative_to(R).as_posix()}))
