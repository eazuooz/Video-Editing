"""Keep the selected final tutorial timeline/cut provenance in Git, not media."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;R=P.parents[1];L=H/'local/full-video-v5'
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
module=ast.parse((H/'render-film.py').read_text('utf-8'))
constants={a.targets[0].id:ast.literal_eval(a.value) for a in module.body if isinstance(a,ast.Assign) and len(a.targets)==1 and isinstance(a.targets[0],ast.Name) and a.targets[0].id in ('MOTION','DELAYED','END_HOLD')}
motion=constants['MOTION']
t=json.loads((L/'timeline.json').read_text('utf-8'));rows=[]
for item in t['scenes']:
 row=dict(item);row['narrationSource']=row.pop('source');row['narrationSourceSha256']=row.pop('sourceSha256');row['board']=(L/'boards'/(row['id']+'.png')).relative_to(R).as_posix();row['boardSha256']=sha(R/row['board']);row['segments']=[]
 n=int(row['id'])
 if n in motion or n==27:
  folder,start,length=motion[n] if n in motion else ('living-room-v11',0,20)
  source=H/'local'/folder/'unity-native-clean.mp4'
  row['segments'].append({'source':source.relative_to(R).as_posix(),'sourceSha256':sha(source),'sourceIn':start,'sourceDurationSeconds':length,'sourceFps':60,'sourceDimensions':[1920,1080],'presentation':'actual own Unity capture','screenRect':[76,216,1120,630] if n!=27 else [994,260,850,478],'repeat':n not in constants['END_HOLD'],'endObservationHold':n in constants['END_HOLD'],'placementStartWithinScene':(row['frames']//2)/60 if n in constants['DELAYED'] else 0})
  if n==30:row['inputSequence']='CC0 real photo + image-AI-derived input, then actual Tripo job UI at 8 seconds, then native cat capture in the second half.'
  if n==17:row['inputSequence']='Single continuous computer approach/sit source 26–45 seconds; hold the seated observation at the end without looping the transition.'
  if n==18:row['inputSequence']='Single continuous sofa-entry source: approach, native seat transition, feet lift onto the low table, and book raise. End with a reading observation hold.'
 else:row['presentation']='Own input image, actual tool/browser still or independent explanatory diagram; not moving game footage.'
 rows.append(row)
out={'revision':'rattan-cat-motion-v11-and-tutorial-v5','fps':60,'duration':t['duration'],'frames':t['frames'],'introSeconds':2,'outroSeconds':10,'renderer':'production/render-film.py','audio':'production/build-film-audio.py','captionSource':'production/build-film-captions.py','humanFinalReview':False,'scenes':rows}
(H/'timeline.final.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n','utf-8')
p=json.loads((P/'project.json').read_text('utf-8'));p['paths']['timeline']='projects/ai-3d-lofi-gaming-room/production/timeline.final.json';(P/'project.json').write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Recorded',len(rows),'selected final scenes and source cuts')
