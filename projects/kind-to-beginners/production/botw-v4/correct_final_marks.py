"""Apply the two directly observed final-review mark corrections, preserving V1."""
import copy, datetime, hashlib, json, shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
LOCAL=HERE.parent/'local/botw-v4'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
def rel(p):return p.relative_to(ROOT).as_posix()
def main():
 edit=LOCAL/'edit'; old=read(HERE/'edit-plan.json'); plan=copy.deepcopy(old)
 assert sha(HERE/'edit-plan.json')=='e9a7007a2ad328db51eb33b97b1b7c801867a03cc6bf2b07adf4dee8f3fe4e87'
 changes=[]
 for c in plan['cuts']:
  if c['id']=='04-05':
   m=c['marks'][0];assert m['t1']==4.8;m['t1']=1.75
   changes.append({'cut':c['id'],'reason':'Inventory temperature gauge is absent after switching to System. End before the verified visible boundary.','before':old['cuts'][plan['cuts'].index(c)]['marks'],'after':copy.deepcopy(c['marks'])})
  elif c['id']=='07-01':
   m=c['marks'][0];assert m['labelPosition']==[65,817]
   m['labelPosition']=[65,690];m['points']=[[65,748],[140,748]]
   changes.append({'cut':c['id'],'reason':'Keep the game title and underline above the lower-left golden-feather HUD.','before':old['cuts'][plan['cuts'].index(c)]['marks'],'after':copy.deepcopy(c['marks'])})
 assert len(changes)==2
 preserved=edit/'review-v1-preserved';preserved.mkdir(exist_ok=True)
 paths=[HERE/'edit-plan.json',HERE/'production-plan.json',edit/'kind-to-beginners-clean.mp4',edit/'kind-to-beginners-captioned.mp4',edit/'pair-build.json',edit/'structural-verification.json',edit/'cuts-build.json']
 paths += [edit/(cid+s) for cid in ['04-05','07-01'] for s in ['.mp4','-marks.ass','-render.json']]
 records=[]
 for p in paths:
  dest=preserved/p.name
  if not dest.exists():shutil.copy2(p,dest)
  assert sha(p)==sha(dest)
  records.append({'path':rel(dest),'sha256':sha(dest)})
 invariant={p.name:sha(p) for p in [edit/'pair-audio.m4a',edit/'final-mix.wav',edit/'captions.ko.ass',edit/'captions.en.ass',edit/'captions.ko.srt',edit/'captions.en.srt',HERE/'native-binding.json',HERE/'timing-lock-receipt.json']}
 unchanged=[{'cut':c['id'],'sha256':sha(edit/(c['id']+'.mp4'))} for c in old['cuts'] if c['id'] not in ['04-05','07-01']]
 save(HERE/'edit-plan.json',plan)
 prod=read(HERE/'production-plan.json')
 for c in prod['cuts']:
  new=next((v for v in plan['cuts'] if v['id']==c['id']),None)
  if c['id'] in ['04-05','07-01']:
   c['marks']=copy.deepcopy(new['marks']);c['annotations']=copy.deepcopy(new['marks'])
   c['annotationState']='Final V1 pixel correction applied; final V2 delta pixel review pending.'
 prod['finalEditPlan']['sha256']=sha(HERE/'edit-plan.json')
 prod['finalVisualCorrections']=rel(HERE/'final-visual-corrections.json')
 save(HERE/'production-plan.json',prod)
 marks=read(HERE/'source-marks.json');marks['finalReviewCorrection']=rel(HERE/'final-visual-corrections.json');save(HERE/'source-marks.json',marks)
 save(HERE/'final-visual-corrections.json',{'status':'two-mark-corrections-applied-awaiting-final-delta-review','updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'priorEditPlanSha256':sha(preserved/'edit-plan.json'),'editPlanSha256':sha(HERE/'edit-plan.json'),'reasonEvidence':rel(HERE/'gameplay-final-pixel-review.json'),'changes':changes,'preservedV1':records,'unchangedInputs':invariant,'unchangedCutMedia':unchanged,'timelineAudioCaptionsNativeUnchanged':True,'newTts':False,'newNativeCapture':False})
 print('Preserved V1 and applied two marks only',sha(HERE/'edit-plan.json'))
if __name__=='__main__':main()
