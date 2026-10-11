from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;O=ROOT/'shared/output/game-math-part2-teaching-revision/polygons-track-seeds'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
proof=read(O/'path-timing-native.json');assert proof['ended'] and proof['rate']==1 and proof['sourceInterval']==[27.9,32.3] and abs(proof['duration']-4.4)<.03
for file in [B/'polygons-game-insertions.json',ROOT/'projects/game-math-polygon-partition-v2/production/lesson.json']:
 data=read(file);scene=next(s for s in data['scenes'] if s['id']=='QG07');assert scene['sourceSegments'][1]['in'] in [28.3,27.9]
 scene['sourceSegments'][1].update({'in':27.9,'maxSeconds':4.4});scene['intervals'][1]=[27.9,32.3];scene['maximumSeconds']=23.7
 scene['selection']['timingRefinement']={'previous':[28.3,32.3],'chosen':[27.9,32.3],'reason':'The same factory context and visible path edit now cover the complete measured3.58s second subject plus0.6s natural end; no freeze, loop, source speed change or spill into the camera cut at32.366s.','nativeProof':proof,'narrationChanged':False,'annotationPixels':'pending'}
 file.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(B/'polygons-path-timing-refinement.json').write_text(json.dumps({'proof':proof,'videoSha256':hashlib.sha256((O/'shapez-path-timing.mp4').read_bytes()).hexdigest(),'originalScenesChanged':False,'newNarrationChanged':False,'finalPixelsApproved':False},indent=2)+'\n',encoding='utf8')
print('QG07 refined real-time capacity to23.7s; original content and voice preserved.')
