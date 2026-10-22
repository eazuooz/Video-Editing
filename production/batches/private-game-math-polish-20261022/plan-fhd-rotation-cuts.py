"""Map inspected replacement candidates onto immutable original cut slots."""
import copy
from datetime import datetime,timezone
from polish_common import *

catalog=read(B/'fhd-candidate-catalog.json'); acquired=read(B/'fhd-candidate-acquisition.json')
starts={
 'M07':{'02':[220], '05':[493], '08':[575,462], '11':[79],
        'IG01':[8], 'IG10':[54], 'IG02':[275], 'IG07':[147,174]},
 'M08':{'20':[424,273], '23':[545,50,610], 'IG03':[98], 'IG04':[157],
        'IG11':[184], 'IG05':[326,449], 'IG08':[375,390], 'IG09':[28,233], 'IG06':[463]},
}
replacement={'ZFGdubPhasM':'yE_I6M-y9vo','TPkvx2W8CV8':'enMAmdW4UTs'}
for ident, mapping in starts.items():
 e=Episode(ident);e.authorized(); scenes={}
 if (e.H/'fhd-replacement-cuts.json').exists():
  print(ident,'existing cut map preserved; edit only its reviewed corrections',flush=True)
  continue
 for sid,new_starts in mapping.items():
  scene=next(s for s in e.T['scenes'] if s['id']==sid);original=scene['cut']
  new_id=replacement[original['sourceId']];meta=catalog[new_id];asset=acquired[new_id]
  assert len(new_starts)==len(original['segments']) and asset['verifiedFhd']
  segments=[]
  for old, start in zip(original['segments'],new_starts):
   seg=copy.deepcopy(old);seg['in']=start;seg['sourceFile']=asset['path']
   assert start+seg['frames']/60 <= asset['duration']
   segments.append(seg)
  scenes[sid]={
   'originalSourceId':original['sourceId'],'sourceId':new_id,'sourceFile':asset['path'],
   'sourceSha256':asset['sha256'],'sourceUrl':meta['url'],'sourceSpeed':1,
   'segments':segments,'frames':scene['frames'],'sourceAudioUsed':False,
   'sourceFraming':None,
   'game':meta['game'],'permissionMetadata':meta['permissionMetadata'],
   'permissionMetadataSha256':meta['permissionMetadataSha256'],
   'requiredDescriptionCredit':meta.get('requiredCredit',meta['uploader']+' - '+meta['url']),
   'teachingRole':scene.get('title',sid),
   'equivalence':'Same game and observable body/board or car heading, native motion and camera relationship; no internal rotation measurements inferred.',
   'difference':'New independently recorded playthrough; old tracking anchors cannot be reused. Preserve original narration, frame counts and source-cut positions.',
   'status':'proposed-await-cut-inspection','fullMasterApproval':False,
  }
 save(e.H/'fhd-replacement-cuts.json',{
  'version':1,'episode':ident,'recordedAt':datetime.now(timezone.utc).isoformat(),
  'authorization':rel(B/'authorization.json')+'#sourceReplacementDecision',
  'originalTimelineSha256':sha(e.P/'production/timeline.json'),
  'originalNarrationAudioAndTimingPreserved':True,'scenes':scenes,
  'status':'proposed-await-cut-inspection','fullMasterApproval':False,
 })
 print(ident,len(scenes),'replacement scene candidates mapped; no cut approval',flush=True)

observations={
 'yE_I6M-y9vo': 'All130 five-second states on11 sheets directly inspected. Road/chase driving at40-125,220-315,425-455,465-630; exclude showroom/menu/cinematic/loading at0-40,130-185,205-220,320-425,635-end and reset around460. Collisions/off-road at50,70,85,430,490,555,580,630 require exact-cut inspection; do not depict them as smooth interpolation results.',
 'enMAmdW4UTs': 'All132 five-second states on11 sheets directly inspected. Bowl/halfpipe aerial body and board actions at10-40,50-90,100-120,150-205,235-245,275-300; plaza rails/stairs at330,375-400,450-480. Exclude intro0-7; falls around45,145,260,655; running/respawn90-100,125-140,210-235,250-275 and later travel unless required context. Board occlusions must clear the blue guide.',
}
for key,summary in observations.items():
 report=read(B/(key+'-candidate-samples.json'))
 report.update(status='inspected-candidate-retained-for-cut-review',directInspection=summary,cutApproval=False)
 save(B/(key+'-candidate-samples.json'),report)
 catalog[key]['selectionStatus']='decoded-FHD-and-full-source-stills-inspected-await-cut-review'
 catalog[key]['fineReview']={'report':rel(B/(key+'-candidate-samples.json')),'sampleCount':len(report['samples']),'sheets':report['sheets'],'observed':summary,'cutApproved':False}
save(B/'fhd-candidate-catalog.json',catalog)
