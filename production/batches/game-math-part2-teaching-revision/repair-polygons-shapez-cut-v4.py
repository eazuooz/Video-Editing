"""Keep narration exact; align the second game shot with the spoken square cut."""
from pathlib import Path
import copy,datetime,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent;R=B/'cross-game-review-20261011'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
proof=read(R/'shapez-aligned-native-proof.json');assert len(proof)==1 and proof[0]['ended'] and proof[0]['rate']==1
p=ROOT/'projects/game-math-polygon-partition-v2/production/lesson.json';lesson=read(p);s=next(s for s in lesson['scenes'] if s['id']=='QG06');old=copy.deepcopy(s)
s['intervals'][1]=[41.9,49.2];s['sourceSegments'][1].update({'in':41.9,'maxSeconds':7.3})
s['sourceAmendment']='production/batches/game-math-part2-teaching-revision/cross-game-review-20261011/shapez-cut-amendment-v4.json'
assert s['ko']==old['ko'] and s['en']==old['en'];write(p,lesson)
write(R/'shapez-cut-amendment-v4.json',{'recordedAt':datetime.datetime.now().astimezone().isoformat(),'scene':'QG06','old':old,'new':s,'change':'Only selected source interval; all earlier approved narration retained.','normalPlaybackProof':'shapez-aligned-native-proof.json','priorCutProblem':'39.5–41.1 throughput panel and prolonged paint shot separate spoken square noun from cutting.','newCutMeaning':'A brief paint lead-in then square cutting42.7–44.05 at spoken square/cut words. Later shots are distinct processing outputs, not the same before/after or triangulation implementation.','trackerHidesAtActualCut':44.06666666666667,'nativeSourceSpeed':1,'sourceAudioUsed':False,'newMovingCaptionApproval':False})
data=read(R/'polygon-cross-game-content-v4.json');data['shapezCutRepair']='QG06 second native interval41.9–49.2; square cut42.7–44.05 occurs with spoken square noun, tracker stops at source cut44.0667. Final narration/captioned pixel inspection pending.';write(R/'polygon-cross-game-content-v4.json',data)
print('QG06 shot aligned to narration; no previous words or PCM changed.')
