"""Bind inspected independent sources and source-ordered A02 teaching decisions."""
from pathlib import Path
import copy,datetime,hashlib,json
H=Path(__file__).resolve().parent
R=H.parents[2]
P=R/'projects/animation-exaggeration';S=P/'script/grid-v1';PH=P/'production/grid-v1'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def record(p):return {'path':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 auth=read(R/'shared/publishing/video-production-control.json')['finiteBatchAuthorizations']['animation-18-20261031']
 assert auth['productionAuthorized'] and 'A02' in auth['episodeIds']
 ko=read(S/'narration.ko.json');en=read(S/'narration.en.json');ready=read(H/'research/A02/production-readiness.json')
 assert en['sourceKoSha256']==record(S/'narration.ko.json')['sha256']
 assert [len(s['lines']) for s in ko['scenes']]==[2,3,3,2,4]
 for a,b in zip(ko['scenes'],en['scenes']):assert a['id']==b['id'] and len(a['lines'])==len(b['lines'])
 for item in ready['selectedSourceRecords']:
  t=item['technical'];assert record(R/t['fullMediaPath'])['sha256']==t['fullMediaSha256']
  assert t['width']>=1920 and t['height']>=1080
 spoken=copy.deepcopy(ko);spoken['language']='ko';spoken['pronunciationOnly']=True;spoken['pronunciationAliases']={}
 target=S/'narration.spoken-ko.json';assert not target.exists();save(target,spoken)
 text='\n\n'.join(line for scene in ko['scenes'] for line in scene['lines'])
 (S/'narration.spoken-ko.txt').write_text(text+'\n','utf8')
 bound=read(PH/'caption-units.json');assert len(bound['paragraphs'])==14
 bound['scriptInputs'].append(record(target));bound['status']='authored-paired-clauses-verified';bound.pop('pendingSpokenScriptBinding',None);save(PH/'caption-units.json',bound)
 native=H/'scripts/A02/native-stage-proposal.json'
 plan={'schemaVersion':2,'slug':'animation-exaggeration','episode':'A02','revision':'grid-v1','title':ko['title'],
  'scope':'Explicit finite Animation18 batch; this A02 local-review production only; no platform mutation',
  'status':'source-and-script-bound-native-preflight-pending','sourceMap':record(H/'research/A02/source-map.json'),
  'fullSourceReview':read(H/'research/A02/source-map.json')['reviewEvidence'],
  'sourceOrder':['A02-S01','A02-S02','A02-S03','A02-S04','A02-S05'],
  'retainedThesis':'Judge motion at actual gameplay size and speed; sufficiently exaggerated poses and overshoot preserve readable force.',
  'sourceFootageBinding':record(H/'research/A02/production-readiness.json'),
  'primaryGameExamples':ready['selectedSourceRecords'],'reviewedNativeWindows':ready['nativeCutSelections'],'gameMix':ready['gameMix'],
  'nativeSceneProposal':{'path':native.relative_to(R).as_posix(),'status':'Implementation and measured timing pending; source phrase precision correction separately recorded'},
  'scriptInputs':[record(S/x) for x in ['narration.ko.json','narration.en.json','narration.spoken-ko.json']],
  'precisionCorrection':record(PH/'script-precision-correction.json'),
  'glossary':[
   {'en':'Exaggeration','ko':'동작의 과장','plain':'동작의 특징을 화면에서 읽히도록 더 크게 드러내기','source':'source-map A02-S02'},
   {'en':'Rig','ko':'리그','plain':'캐릭터를 움직이는 뼈대와 조절 장치','source':'https://activation.unity3d.com/glossary/rigging-in-animation'},
   {'en':'Rotation','ko':'회전','plain':'관절의 기준점을 중심으로 방향을 바꾸기','source':'https://docs.unity3d.com/Manual/class-Transform.html'},
   {'en':'Translation','ko':'이동','plain':'관절 기준점의 위치 자체를 옮기기','source':'https://docs.unity3d.com/Manual/class-Transform.html'},
   {'en':'Overshoot','ko':'오버슈트','plain':'목표 위치나 모양을 잠깐 넘어선 뒤 돌아오기','source':'source-map A02-S05'}],
  'boundaries':[
   {'from':'01','to':'02','link':'Keep the same strike and actor; ask how its visible force changes at small gameplay size.'},
   {'from':'02','to':'03','link':'The emphasized shoulder becomes the rig control whose permitted transforms limit exaggeration.'},
   {'from':'03','to':'04','link':'More flexible controls create unusual intermediate poses; judge their role in continuous motion.'},
   {'from':'04','to':'05','link':'Carry motion energy into a linear endpoint and demonstrate overshoot, then shape overshoot.'}],
  'visualContract':{'style':'animation-grid-presentation-v1','sourceKinds':['actual independent gameplay','our Unity demonstration','labelled source-frame analysis'],'fps':60,'width':1920,'height':1080,'fixedCaptionCenter':[960,970],'normalGameSpeed':True,'originalAspectPreserved':True,'foregroundExtractionForced':False,'referenceLessonProductionAllowed':False},
  'timing':{'locked':False,'source':'Measure actual SampleB continuous PCM; no invented narration timestamps or fixed duration'},
  'screenTimeDecision':{'status':'pending measured editorial plan','default':'60:40; any episode-scoped clarity choice must be explicitly recorded with delegated choice basis','paddingAllowed':False},
  'voice':{'provider':'ElevenLabs','ownVoiceId':'jIRSnF8OWAsWEChVwCuK','style':'Sample B','stability':.5,'similarity':.75,'audioTags':False,'status':'not-generated','characters':len(text),'noNewPurchase':True},
  'delivery':{'boundary':'four local review outputs before upload','humanReviewed':False,'youtubeAuthorized':False,'driveAuthorized':False},
  'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 save(P/'planning/production-plan.json',plan)
 save(PH/'script-binding-review.json',{'status':'source-order-and-full-KO-EN-readthrough-complete-native-preflight-pending','scriptInputs':plan['scriptInputs'],'paragraphs':14,'pairedCaptionUnits':sum(len(x['captionUnits']) for x in bound['paragraphs'].values()),'characters':len(text),'sourceFactsBound':True,'meaningOrderPreserved':True,'actualTtsGenerated':False,'nativeRuntimeVerified':False,'humanListening':False,'basis':'Full source map and independently inspected source windows; root KO/EN readthrough plus independent agent audit, with one geometry-precision wording correction.'})
 print('A02 bound:14paragraphs,',len(text),'characters; no TTS or render started')
if __name__=='__main__':main()
