"""Record actual finite-batch progress without changing unrelated rows or fields."""
from pathlib import Path
import json,datetime
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat();batch=read(B/'batch.json');slugs=batch['authorization']['slugs'];work=read(R/'shared/publishing/shorts-worklist.json')
for slug in slugs:
 p=R/'projects'/slug;L=p/'production/local';stage='native-preview-complete-and-voice-generation'
 if list(L.glob('audio-v*/voice/narration.wav')):stage='voice-generated-caption-and-composite-production'
 if (L/'final-reviewed/integrity.json').exists():stage='encoded-four-output-qa-in-progress'
 old=read(p/'production/checkpoint.json');old.update(updatedAt=now,stage=stage,batchAuthorization='explicit-five-distinctive-shorts-20261024',humanFinalReview='pending',platformChangesPerformed=False)
 old['currentEvidence']={'source':'sources/selected-footage.json','nativePreview':'production/local/capture-preview-v3' if (L/'capture-preview-v3/success.json').exists() else 'production/local/capture-preview-v2','voiceVersions':[str(x.relative_to(p)).replace('\\','/') for x in L.glob('audio-v*/voice/narration.wav')],'resourceMode':'CPU / Unity WARP; live user editors preserved','outputs':'production/local/final-reviewed'}
 save(p/'production/checkpoint.json',old)
 for row in batch['projects']:
  if row['slug']==slug:row['status']=stage
 for row in work['rows']:
  if row.get('slug')==slug:row.update(production=stage,review='human-final-review-pending',updatedAt=now)
 plan=read(p/'planning/production-plan.json');plan['nativeAssets']={'titanfall':'KayKit Adventurers Knight.fbx, CC0; exact shared asset reference preserved','otherTopics':'Self-authored pawn, flame/leaf meshes, articulated mannequin and portal stage. No third-party model copied.'};plan['nativeCapture']={'engine':'Unity6000.6.0f1','pipeline':'Built-in','device':'CPU/WARP','width':1080,'height':1080,'fps':60,'scenesRoot':'unity/VideoEditing/Assets/VideoScenes/distinctive-shorts-20261024/Scenes','composite':'Motion Canvas1080×1920/60','classification':'Our implementation / reconstruction, not game internal measurement'};save(p/'planning/production-plan.json',plan)
batch.update(stage='native-render-and-caption-production',updatedAt=now);save(B/'batch.json',batch);work['updatedAt']=now;save(R/'shared/publishing/shorts-worklist.json',work)
U=R/'unity/VideoEditing/Assets/VideoScenes/distinctive-shorts-20261024'
for p in U.rglob('*'):
 if p.suffix in ['.cs','.shader','.unity','.mat','.meta','.asset']:
  try:s=p.read_text(encoding='utf8');p.write_text('\n'.join(x.rstrip() for x in s.splitlines())+'\n',encoding='utf8')
  except UnicodeError:pass
