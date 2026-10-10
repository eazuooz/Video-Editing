"""Record direct review of corrected moving render pixels, never auto approve."""
from pathlib import Path
import json, datetime
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-math-bounds-transform-v2'
W=ROOT/'shared/output/game-math-bounds-transform-v2'
digest='1ac7539fe255bd80c916f5e40fb3ec4a901c39139bd428d63dce91aa0aaaa548'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
idx=read(W/'corrected-annotation-pixels/index.json');assert idx['sha256']==digest
native=read(W/'native-final-playback.json');assert native['sha256']==digest and native['ended'] and native['playbackRate']==1
review={'sha256':digest,'reviewedAt':datetime.datetime.now().astimezone().isoformat(),
 'currentMovingPixelsDirectlyReviewed':True,'fineReviewIndex':'shared/output/game-math-bounds-transform-v2/corrected-annotation-pixels/index.json',
 'allNineFineSheetsDirectlyViewed':True,'allThirtyOneActualMovingSheetsDirectlyViewed':True,
 'source13':{'validLocalIntervals':[[26,26.5],[33.6,34]],'observation':'Selected visible gray leg/torso and blue head/torso. One uncertain interior frame hides the outline; no interpolation across gaps. Old gun/ground selections at 0 and 10 now hidden.'},
 'source16':{'validLocalIntervals':[[28,29.25],[30,30.5]],'observation':'Selected visible head/torso or arm/torso. Outline hides before weapon/camera ambiguity. Old ground/sky/post/weapon windows now hidden.'},
 'scope':'Only selected visible body parts during 2.65 seconds of admitted windows; no continuous whole-body or measured engine-collider claim.',
 'semantics':'Red selected visible contour; blue screen extent of those same points. Hidden during uncertain selection, occlusion and rapid camera turns.',
 'narrationCaptionsAndClearance':'Reviewed with current 216 cue sheets, 27 composition scenes, 25 additive explanation motion sheets and whole 1x native playback.',
 'rejectedFinalSha256':'33acbad6b7980c3d56f952e66cb9f7614f683e1e4fcc315b2d852a9067c1e29f',
 'humanWholeListening':'pending','gameIPHumanRights':'pending'}
write(P/'production/annotation-correction-review.json',review)
idx['directReviewPassed']=True;idx['reviewedAt']=review['reviewedAt'];write(W/'corrected-annotation-pixels/index.json',idx)
print('Corrected moving annotation review saved:',digest)
