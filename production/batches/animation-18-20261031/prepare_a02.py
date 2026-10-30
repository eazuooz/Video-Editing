"""Prepare A02's isolated text/audio workspace. No media generation or shared-state selection."""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
R=H.parents[2]
P=R/'projects/animation-exaggeration'
PH=P/'production/grid-v1'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 assert not p.exists(),str(p)+' already exists; preserve later work'
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 auth=read(R/'shared/publishing/video-production-control.json')['finiteBatchAuthorizations']['animation-18-20261031']
 assert auth['productionAuthorized'] and auth['ttsAuthorized'] and 'A02' in auth['episodeIds']
 source=H/'scripts/A02/narration.ko.json';ko=read(source)
 ko.update(slug='animation-exaggeration',revision='grid-v1',status='source-ordered-draft-final-footage-binding-pending')
 save(P/'script/grid-v1/narration.ko.json',ko)
 row=next(x for x in read(H/'batch.json')['episodes'] if x['id']=='A02')
 save(P/'project.json',{'schemaVersion':2,'slug':'animation-exaggeration','series':'animation','seriesOrder':'A02','revision':'grid-v1','title':row['titleKo'],'status':'footage-binding-and-scene-preparation','batch':H.relative_to(R).as_posix()+'/batch.json','sourceReference':row['sourceUrl'],'sourceClassification':'research-reference-only','voice':{'provider':'ElevenLabs','approvedSample':'B','ownVoice':True,'voiceId':'jIRSnF8OWAsWEChVwCuK','status':'not-generated'},'delivery':{'status':'not-rendered','directory':'projects/animation-exaggeration/production/local/grid-v1/delivery/output/animation-exaggeration'},'review':{'actualUserViewed':False},'youtube':{'authorized':False,'state':'not-uploaded'}})
 save(PH/'authorization.json',{'episode':'A02','slug':'animation-exaggeration','revision':'grid-v1','batch':'animation-18-20261031','localProductionAuthorized':True,'platformMutation':False,'noUiOrFocus':True})
 save(PH/'execution-grant.json',{'episode':'A02','revision':'grid-v1','batch':'animation-18-20261031','stages':[],'resourcePolicy':'Root grants coordinated stages after source/script binding; no background media job from workspace preparation.','grantedBy':'root'})
 records=[]
 for name in ['audio_pipeline.py','caption_pipeline.py','storage_paths.py','register_voice.py']:
  src=R/'projects/animation-assigning/production/grid-v1'/name
  text=src.read_text('utf8').replace('A01','A02').replace('animation-assigning','animation-exaggeration')
  target=PH/name;assert not target.exists();target.write_text(text,'utf8')
  records.append({'source':src.relative_to(R).as_posix(),'sourceSha256':sha(src),'target':target.relative_to(R).as_posix(),'targetSha256':sha(target)})
 save(PH/'pipeline-provenance.json',{'files':records,'sourceDraft':{'path':source.relative_to(R).as_posix(),'sha256':sha(source)},'jobsStarted':False,'scope':'Isolated A02 workspace only; shared selection and existing A01 work remain unchanged'})
 save(PH/'checkpoint.json',{'episode':'A02','status':'source-and-scene-binding','completed':['Full source-order draft audit retained','Isolated audio pipeline prepared'], 'nextAction':'Bind exact independent FHD source cuts, matched native explanation design and full KO/EN before voice generation','ttsGenerated':False,'finalMasterRendered':False,'platformMutation':False,'userReviewed':False})
 print('Prepared isolated A02 text/audio workspace; no TTS or render job started')
if __name__=='__main__':main()
