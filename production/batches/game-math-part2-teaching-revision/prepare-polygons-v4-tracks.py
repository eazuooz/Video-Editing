"""Append manually observed native seeds, without approving generated tracking."""
from pathlib import Path
import copy,json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
seeds=read(B/'polygons-observed-track-seeds.json');by_id={s['id']:s for s in seeds}
# These are the same source-native intervals previously selected for partition;
# the new centers comparison discloses their reuse across episodes.
for old,new in [('QG04-notch','QG08-notch'),('QG05-opening','QG08-opening')]:
 s=copy.deepcopy(by_id[old]);s['id']=new
 if new=='QG08-notch':s['end']=466.5
 s['meaning']+=' New independent centers episode: distinguish marker and terrain outline. Reuse disclosed; keep native camera map.'
 by_id[new]=s
dorf='shared/output/game-math-part2-full-series/sources/dorfromantik-official/Dorfromantik_Explanation_Trailer.webm'
by_id['QG09-tile']={'id':'QG09-tile','file':dorf,'start':99,'end':100.7,'region':[[464,191],[606,187],[609,252],[526,272],[464,245]],'shapes':{'red':[[480,237],[527,263],[600,245],[601,224]]},'meaning':'Visible partial outside edge of newly placed water hexagon; shape is observed screen geometry, not exact game-world coordinates. Hide before region cut at101.','affine':True,'translationOnly':True,'closed':False}
by_id['QG09-undo']={'id':'QG09-undo','file':dorf,'start':117,'end':118.3,'region':[[283,236],[347,240],[349,282],[279,297]],'shapes':{'red':[[354,250],[343,285],[281,298]]},'meaning':'Exposed partial land rim beside the new tile before separate undo/zoom shot. Do not extrapolate across zoom or tile replacement.','affine':True,'translationOnly':True,'closed':False}
by_id['QG09-after-undo']={'id':'QG09-after-undo','file':dorf,'start':120,'end':122.3,'region':[[270,230],[352,231],[352,288],[267,306]],'shapes':{'red':[[354,250],[343,285],[281,298]]},'meaning':'Separate post-undo view of the exposed green land rim; manually reseeded after the camera cut.','affine':True,'translationOnly':True,'closed':False}
write(B/'polygons-observed-track-seeds.json',list(by_id.values()))
registry=read(B/'polygons-annotation-tracks.json')
registry['scenes']['QG08']={'landmarkSources':[f'production/batches/game-math-part2-teaching-revision/polygons-tracks/{ident}.json' for ident in ['QG08-notch','QG08-opening']],'revealAtLine':0,'redAtLine':0,'redKeyword':'빨간','redLabel':'빨강: 발판 옆 빈틈의 노출된 지형 경계','mathNote':'한 점으로 표시한 위치 ≠ 전체 지형 경계','mathNoteAtLine':0,'mathNotePosition':[390,85],'movingPixelApproval':False}
registry['scenes']['QG09']={'landmarkSources':[f'production/batches/game-math-part2-teaching-revision/polygons-tracks/{ident}.json' for ident in ['QG09-tile','QG09-undo','QG09-after-undo']],'revealAtLine':0,'redAtLine':0,'redKeyword':'바깥선','redLabel':'빨강: 보이는 타일·땅의 바깥 경계 일부','mathNote':'타일 하나의 외곽 ≠ 합쳐진 땅의 외곽','mathNoteAtLine':0,'mathNotePosition':[390,85],'movingPixelApproval':False,'omitMathNote':True}
write(B/'polygons-annotation-tracks.json',registry)
print('Five new native seeds appended; all prior scenes kept. Render/pixels pending.')
