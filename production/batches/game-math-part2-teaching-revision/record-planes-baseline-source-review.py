"""Retained footage review; final annotations remain separately unapproved."""
from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision/planes-baseline-review'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
notes={
 '02':'Sandy shoreline, water edge, finite boat/bridge surfaces and camera movement. Reject explosions, enemies and weapon-dominated intervals as surface anchors. Use briefly unobscured shoreline boundaries; screen geometry is not a measured infinite collision plane.',
 '05':'Layered Noita ledges and waterline. The waterline and character above it are readable in the first source group; fire obscures later ledges. Keep separate source changes and hide effects, never screen bottom as world floor.',
 '08':'Uncle grapple path and glowing markings. The floor triangle at32.3–32.4 is directly visible;32.5 moves into caption clearance. It is an observed symbol, not known mesh connectivity. Hide rapid dark camera turns.',
 '11':'Noita multi-level ledges. The wooden platform at16–17 is readable while the character moves above it. Most earlier/later fire intervals are unsuitable for three-corner observations.',
 '14':'Uncle finite bridge/platform at12–13; most camera turns and dark cavern have unreliable corners. Reject draft26 glyph as a triangle surface. The bright floor marking in dense review is not sufficient to infer game mesh.',
 '17':'Noita ledges, traversal and potion colors. Refer to visible finite platform boundaries; do not claim potion colors demonstrate barycentric engine interpolation. Reject lava/explosions and source switch as continuous geometry.',
 '19':'Noita character above and landing on a finite wooden ledge at24–25. Floor direction/extent motivates distinct surface and inside tests. Potions and effects obscure upper edges; only visible lower/front boundary may be traced.',
 '21':'Serious Sam combat obscures most floor regions. Short platform/stair approach47–47.25 shows readable wood boundaries; hide gun, enemies, fire and abrupt turns. Preserve the approved baseline, supplement its weak long combat section with the freshly compared Portal surfaces.'
}
native=read(O/'native-playback.json');assert len(native)==8 and all(r['ended'] and r['rate']==1 for r in native)
records=[]
for row in native:
 ident=row['id'];file=ROOT/f'shared/output/game-math-planes-barycentric/clips/{ident}.mp4'
 assert hashlib.sha256(file.read_bytes()).hexdigest()==row['sha256']
 pages=sorted(O.glob(ident+'-sheet-*.jpg'))
 records.append({**row,'sourceFile':file.relative_to(ROOT).as_posix(),'denseMovingSheets':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'directlyViewed':True} for p in pages],'review':notes[ident],'sourcePreserved':True,'finalAnnotatedPixelReview':False})
assert sum(len(r['denseMovingSheets']) for r in records)==30
(B/'planes-baseline-footage-review.json').write_text(json.dumps({'reviewedAt':datetime.datetime.now().astimezone().isoformat(),'records':records,'originalNarrationAndTimingPreserved':True,'measuredWorldOrEngineClaims':False,'finalAnnotationApproval':False},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('Original8 native1x ended +30 dense sheets directly reviewed; final annotated render pending.')
