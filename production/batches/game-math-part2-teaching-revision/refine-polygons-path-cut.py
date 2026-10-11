"""Keep the narrated bent path visible by ending before the wide-camera cut."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
proof=read(ROOT/'shared/output/game-math-part2-teaching-revision/polygons-track-seeds/path-refined-native.json');assert proof['ended'] and proof['rate']==1 and proof['seconds']==4
files=[B/'polygons-game-insertions.json',ROOT/'projects/game-math-polygon-partition-v2/production/lesson.json']
for file in files:
 data=read(file);rows=data.get('additions',data.get('scenes',[]));scene=next(s for s in rows if s['id']=='QG07')
 assert scene['sourceSegments'][1]['in'] in [30,28.3]
 scene['sourceSegments'][1]['in']=28.3;scene['intervals'][1]=[28.3,32.3]
 scene['selection']['cameraRefinement']={'oldInterval':[30,34],'chosen':[28.3,32.3],'reason':'Earlier brief factory context precedes zoomed path editing. The narrated bent path remains visible until the end; reject the wide-camera cut at32.366s which hides its turn. Same4-second capacity, unchanged narration/source SHA.','actualNative1xProof':proof,'currentAnnotationPixels':'pending'}
 file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(B/'polygons-path-cut-refinement.json').write_text(json.dumps({'nativeProof':proof,'previewSha256':hashlib.sha256((ROOT/'shared/output/game-math-part2-teaching-revision/polygons-track-seeds/shapez-path-refined.mp4').read_bytes()).hexdigest(),'originalContentChanged':False,'newNarrationChanged':False,'changedFiles':[p.relative_to(ROOT).as_posix() for p in files]},indent=2)+'\n',encoding='utf8')
print('New source crop refined; all narration and original scenes unchanged.')
