"""One scoped receipt migration for tuple/list-only cache comparison repair.
The old receipt bytes and output hashes are preserved; no video is encoded.
"""
from pathlib import Path
import json,copy
import audio_pipeline as a
import video_pipeline as v
import ui_compositor as ui
import render_explanation as e
H=Path(__file__).resolve().parent
OLD='2b60c2890bad5ec136b3830b3773454182d7b4837780a2d2ed834d9f6522c2f9'

def main():
 a.require_authorized('scoped-cache-representation-repair')
 plan=a.read(H/'edit-plan.json');out=a.repo_path(plan['outputDir']);manifest=a.read(out/'explanation-ui/ui-manifest.json');backup=out/'qa/cache-representation-repair';backup.mkdir(exist_ok=True)
 changes=[]
 for cut in plan['cuts']:
  receipt=out/(cut['id']+'-render.json')
  if cut['kind']!='explanation' or not receipt.exists():continue
  original=receipt.read_bytes();data=json.loads(original);signature=data['signature'];assert signature['codeSha256']==OLD
  source=out/(cut['id']+'.mp4');assert a.sha(source)==data['outputSha256'];v.assert_video(source,cut['frames'])
  currentRow=next(x for x in manifest['cuts'] if x['cutId']==cut['id'])
  assert signature['cut']==cut and signature['ui']==currentRow
  assert signature['pipelineSha256']==a.sha(Path(v.__file__)) and signature['uiModuleSha256']==a.sha(Path(ui.__file__))
  assert signature['cueFile']==a.artifact(H/'unity-cues.json') and signature['encoder']==v.ENCODER
  for phase in currentRow['phases']:assert a.sha(a.repo_path(phase['image']['path']))==phase['image']['sha256']
  native=signature['native']
  if native:
   for key in ['video','request','success']:assert a.sha(a.repo_path(native[key]['path']))==native[key]['sha256']
   for item in a.read(a.repo_path(native['request']['path']))['sourceFiles']:assert a.sha(a.repo_path(item['path']))==item['sha256']
  new=copy.deepcopy(data);new['signature']['codeSha256']=a.sha(Path(e.__file__))
  changes.append((receipt,original,new,{'cutId':cut['id'],'outputSha256Unchanged':data['outputSha256'],'oldReceipt':a.artifact(receipt)}))
 assert changes
 for receipt,original,new,record in changes:
  destination=backup/receipt.name;assert not destination.exists();destination.write_bytes(original)
  assert receipt.read_bytes()==original
  a.save(receipt,new);record['preservedReceipt']=a.artifact(destination);record['newReceipt']=a.artifact(receipt)
 a.save(H/'evidence/cache-representation-repair.json',{'reason':'PIL tuple sizes serialize to JSON lists; normalization before cache comparison changes representation only, not render arguments or pixels.','oldHelperSha256':OLD,'newHelper':a.artifact(Path(e.__file__)),'records':[x[3] for x in changes],'allCurrentCutUiCueSourceAndOutputHashesVerified':True,'videoBytesChanged':False,'newEncodingPerformed':False})
 print('Preserved and normalized',len(changes),'explanation receipts; media untouched.')
if __name__=='__main__':main()
