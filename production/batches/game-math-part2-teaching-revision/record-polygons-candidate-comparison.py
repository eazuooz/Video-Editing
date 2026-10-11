"""Record performed source playback/pixel comparison; final overlays remain pending."""
from pathlib import Path
import json, hashlib, datetime
ROOT=Path(__file__).resolve().parents[3]; B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
proofs={}
for name in ['polygons-extra-comparison','polygons-extra-noita','polygons-fresh-candidates']:
 records=read(O/name/'native-playback.json')
 if isinstance(records,dict):records=records['records']
 assert all(r['ended'] and r['rate']==1 for r in records)
 proofs[name]=records
tiny=read(O/'polygons-fresh-candidates/tiny-glade/native-playback.json')
records=json.loads(tiny['completion']);assert all(r['ended'] and r['rate']==1 for r in records)
proofs['tiny-glade']=records
rows=[]
def candidate(source,game,compared,chosen,rejected,action,reason,camera,occlusion,ui,pixels):
 rows.append(dict(source=source,game=game,compared=compared,chosen=chosen,rejected=rejected,
 visibleBeforeActionAfter=action,chosenOrRejectedReason=reason,camera=camera,occlusion=occlusion,UI=ui,
 performedPixelReview=pixels,nativeNormalSpeedComplete=True,finalAnnotationPixelsApproved=False))
candidate('tiny-glade-257046593','Tiny Glade',[[0,68.3]],[[0,8.8],[10,24],[30.5,40.3]],
 [[8.8,10],[24,30.5],[40.3,68.3]],
 'Open ground → wall stroke/arch cut → changed enclosure; separate shot: placed building → drag/resize → changed position/extent; lake brush → concave water edge → remaining land and water boundary.',
 'Bright visible edits show the operation and its resulting outline; night flyovers, painting menus, trees and closing logos do not resolve this chapter question.',
 'Reset annotated reference on actual trailer cuts; camera orbit means projected outlines, not measured ground coordinates.',
 'Hide rear wall/roof anchors behind visible walls/trees; use only observed edges.',
 'Sparse building tools; fixed narration caption clearance remains required.',
 'Whole native1x playback; all five2-second full-source sheets directly viewed.')
candidate('tiny-glade-256965562','Tiny Glade',[[0,69.65]],[[0,18.7],[23,31.7],[33,46.5]],
 [[18.7,23],[31.7,33],[46.5,69.65]],
 'Wall erase/draw → path touches wall → arch opens; terrain raise/lower → altered slope; new building → rotate/resize → changed reference and outline.',
 'Continuous daylight edits make changes easier to follow than sheep shots, menus, timelapse and night cinematics. Terrain height illustrates changing the input, not proof of a flat polygon.',
 'Several cuts/orbits; announce independent shots and reset tracks.',
 'Use visible front outline; mask overlays while brush/building hides its edge.',
 'Tool menu pauses excluded. No game height or radius inferred from brush pixels.',
 'Whole native1x playback; all five2-second full-source sheets directly viewed.')
candidate('shapez2-257294952','Shapez2',[[0,45]],[[0,4]],[[4,45]],
 'A disk enters a cutter → separates → two halves exit.',
 'A short clear input/action/result motivates preserving pieces. It is cutting a factory item, not evidence of engine triangulation.',
 'Near top view; use screen outlines and reset at source end.',
 'Belts/machines cover part of the item; hide item outline inside cutter.',
 'Explain circle/halves before comparison; no world units.',
 'Whole native1x playback and all full-source fine sheets directly viewed.')
candidate('shapez2-257312662','Shapez2',[[0,108]],[[30,34],[39.5,46.8]],
 [[0,30],[34,39.5],[46.8,108]],
 'L-shaped belt path placed; separate shot: disk and square enter cutter → differently oriented halves exit.',
 'Visible paths and cutting show boundary/order and retained pieces. Static Half Cutter title38–39.5, dense layouts, menus and promotional montage excluded from added actual quota.',
 'Top/oblique views change at actual cuts; do not imply the disk and square are one object.',
 'Track visible piece only; mask at machine ingress/egress.',
 'Cutter name card is explanation, excluded. Retain required bottom caption clearance.',
 'Whole native1x playback and all full-source fine sheets directly viewed.')
for ident,compared,chosen,rejected,action,reason,camera,occlusion in [
 ('noita-outline-a',[170,202],[],[[170,202]],'Mostly shop/inventory; a very brief walk.', 'Shop prompts obscure the exact boundary and fail to provide a sustained observable change.','Little useful movement.','Shop/inventory cover central terrain.'),
 ('noita-outline-b',[445,478],[[451,469]],[[445,451],[469,478]],'Character falls/flies past angular ledges → follows the opening → reaches another exposed ledge.', 'Right-side stepped boundary and empty space remain visible during movement; reject combat before/after.','Follow vertical camera motion; reset on source cuts.','Fire at left; annotate the clean right boundary and hide covered edge.'),
 ('noita-outline-c',[601,632],[],[[601,632]],'Shop/inventory dominates; short initial movement.', 'Inventory obscures the teaching target; original source title alone does not qualify it.','Not a sustained action comparison.','Large menus cover the floor.'),
 ('noita-outline-d',[780,813],[[788,802]],[[780,788],[802,813]],'Character descends past a gray cave/stepped platform → crosses the gap → returns upward.', 'Exposed gray outline and dark empty corridor teach what must remain unfilled more clearly than combat or shop.','Track scroll; distinct steps are observed screen geometry.','Flames after802 rejected; hide edge behind character.'),
 ('noita-e',[65,110],[[79,99]],[[65,79],[99,110]],'Character descends a thin opening → lands at right ledge → flies across the exposed boundary.', 'Sparse action over a visible outline is clearer than polymorph effects, potion popup and red flash outside the chosen interval.','Slow vertical then horizontal scrolling; camera-aware anchors required.','Hide local edge behind character; no projected distance used as world measurement.'),
 ('noita-f',[244,282],[[258,277.3]],[[244,258],[277.3,282]],'Character climbs an angular corridor → drops into the coal area → jumps across stepped ledges.', 'Clear angular-to-natural boundaries illustrate why nearby points and empty openings must survive partition. Inventory and purple explosion excluded.','Vertical scrolling, then lateral motion; reset when entering new shot.','Coal area banner266–269: hide overlapping math until it disappears; explosions after277.3 excluded.'),
 ('noita-g',[304,338],[],[[304,338]],'Repeated potion/drinking/blood-color effects precede a brief basin crossing.', 'Red flashes and stationary action compete with the mathematical target; choose the clearer E/F/B/D passages.','Character is stationary too long, then camera scrolls.','Color flashes and red effects mask the boundary.')]:
 candidate(ident,'Noita',[compared],chosen,rejected,action,reason,camera,occlusion,
  'HUD retained. Labels avoid top health/ammo and bottom-center captions. Any area banner resets/hides nearby math.',
  'Whole native1x excerpt plus all three2-second fine pages directly viewed.')
base=read(B/'baselines/game-math-polygons-triangulation/sources/gameplay-cuts.json')
chosen=[{'sourceFile':r['source'],'interval':w} for r in rows for w in r['chosen']]
# Broad current cuts audit, keeping prior use visible rather than treating a familiar title as new.
overlaps=[]
source_paths={r['id']:r['sourceFile'] for d in ['polygons-extra-comparison','polygons-extra-noita'] for r in read(O/d/'inputs.json')}
source_paths.update({
 'tiny-glade-257046593':'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/tiny-glade-257046593.mp4',
 'tiny-glade-256965562':'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/tiny-glade-256965562.mp4',
 'shapez2-257294952':'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/shapez2-257294952.mp4',
 'shapez2-257312662':'shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/shapez2-257312662.mp4'})
for path in (ROOT/'projects').glob('*/sources/gameplay-cuts.json'):
 try:doc=read(path)
 except (ValueError,OSError):continue
 cuts=doc.get('cuts',[])
 if not isinstance(cuts,list):continue
 for cut in cuts:
  for seg in cut.get('sourceSegments',[]) or [cut]:
   file=seg.get('sourceFile',cut.get('sourceFile'));start=seg.get('in');length=seg.get('maxSeconds',seg.get('seconds'))
   if file is None or start is None or length is None:continue
   for row in rows:
    if source_paths[row['source']]!=file:continue
    for a,z in row['chosen']:
     if max(a,start)<min(z,start+length):overlaps.append(dict(existingLesson=path.parts[-3],scene=cut.get('scene'),source=row['source'],chosen=[a,z],existing=[start,start+length]))
assert not any(r['existingLesson']=='game-math-polygons-triangulation' for r in overlaps),'Do not count retained footage twice'
hashes={k:hashlib.sha256((ROOT/v).read_bytes()).hexdigest() for k,v in source_paths.items()}
write(B/'polygons-candidate-comparison.json',dict(reviewedAt=datetime.datetime.now().astimezone().isoformat(),
 baseline='game-math-polygons-triangulation',nativeProofs=proofs,candidates=rows,sourcePaths=source_paths,sourceSha256=hashes,
 review=dict(allSelectedNativePlaybackCompared=True,denseActionPixelsCompared=True,overlaps=overlaps,
 freshTitles='Tiny Glade and Shapez2 reviewed as fresh titles; Noita retained as familiar with newly selected intervals.',
 finalMovingAnnotationPixels=False),rights='Developer Steam trailer/public page is a source, not an automatic broad license. Existing Noita creator record retained. Human/IP publishing review pending.',
 originalMaterialsPreserved=True,newDependentNarrationMayBeAuthored=True))
print('Performed polygon comparisons recorded; moving overlays and publishing review pending.',len(overlaps),'prior-source overlaps')
