"""Record directly viewed original footage and all29 dense pages; no final approval."""
from pathlib import Path
import json,datetime
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
O=ROOT/'shared/output/game-math-part2-teaching-revision/remaining-native-review/game-math-polygons-triangulation'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
pages=sorted(O.glob('O*-sheet-*.jpg'));assert len(pages)==29
native=read(O/'native-playback.json')
notes={
 '02':'All4 pages: actual hex tile placement and rotation; early green map is clearer than purple montage after local35s. Preview tile has exposed edges; forest-covered map corners rejected. Reference dot is an illustrative projected choice, not proof of internal centroid.',
 '05':'All4 pages: beach first25s then night combat. Only exposed sand/water edge is an observable boundary; no three-sided triangle, incenter, numerical clearance or engine collision is visible. Avoid weapon, palm trunk and enemies; night combat offers poor geometric focus.',
 '08':'All4 pages: local16–30 exposed gold rock/platform boundaries around traversable empty opening; camera scroll must be tracked. Pink character change, potion, explosion and bright later fire reduce clarity; do not close a purported whole polygon through offscreen terrain.',
 '11':'All4 pages: tile placement changes joined land; local26–33 new map offers sparse exposed boundary, then montage cuts reset observation. Trees, quest badges and trains occlude inner details. Follow exposed perimeter only; no universal convexity test inferred from the game.',
 '14':'All3 pages: camera follows character across an inward terrain notch and empty space; local7 rock boundaries are distinguishable. Later local28+ fire/potion occludes. Illustrate preservation of empty space; no actual triangle mesh visible.',
 '17':'All4 pages: snowy terrain opening around local20–28 and again50–54 makes retained empty space visible during movement. Recharging text, enemies and projectiles require clearance; no ear algorithm or removed game vertices asserted.',
 '19':'All4 pages: visible gap between wooden platforms at16–26 provides a clearer narrow-opening comparison; reset at28 and39 montage cuts, hide explosions. Numerical thin-triangle conditioning belongs to the separate defined diagram.',
 '21':'All2 pages: successive whole tile maps summarize center versus compound boundary; montage cuts reset tracking. Exposed water/land rim can be observed, while submerged/vegetation-covered geometry is unverified. Final24s UI tile is too brief for a new annotation.'}
record={'reviewedAt':datetime.datetime.now().astimezone().isoformat(),'baseline':'game-math-polygons-triangulation','normalSpeedNativePlaybackProof':native,'all29TwoSecondPagesDirectlyViewed':True,'pages':[p.relative_to(ROOT).as_posix() for p in pages],'sceneObservations':notes,'originalFootageAndNarrationRetained':True,'currentTrackedMovingPixelsApproved':False,'humanListeningAndRights':'pending'}
(B/'polygons-original-footage-dense-review.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print('29 original dense pages recorded; current tracked render still pending.')
