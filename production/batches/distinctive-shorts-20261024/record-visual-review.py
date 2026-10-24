"""Persist the exact sampled frames inspected in this production conversation."""
from pathlib import Path
import json,datetime,sys
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
reviews={
 'shorts-titanfall-time-shift':(2,7,[47],['All seven exact-master contact sheets inspected in the preceding segment of this same production turn.','At the numerical example, one height jump occurs and holds the upper floor; the camera-direction example retains the facing direction.','The gameplay opening and later passage show the era change; the native 10m readout is labeled our demonstration.']),
 'shorts-superliminal-perspective':(2,6,[27],['All six current-master contact sheets inspected. Removed the redundant label that entered the fixed two-line caption region.','Player-view size stays stable while observer-view distance and scale change; the final numerical result and caption are simultaneously readable.','Surface ray fan is labeled structure explanation; the large wedge gameplay shows traversal to the high doorway.']),
 'shorts-ghost-leaf-updraft':(1,7,[57],['All seven exact-master contact sheets inspected in the preceding segment of this same production turn.','Same initial leaves fall with wind OFF and rise with wind ON; compare panels retain labeled colors.','The historical non-burning leaf problem is narrated as a development issue, with current actual game foliage and our reconstruction clearly distinguished.']),
 'shorts-gears-inertialization':(4,7,[3,22,47],['Current-master sheets and listed full-size frames inspected after the final intro replacement.','Low movement transitions to stationary aiming in the game opening; Unity then compares the direct switch with a decaying residual.','First cat reaction starts after the arm has settled; the numerical angle and velocity demonstrations remain visible. Removed the redundant label beneath fixed captions.']),
 'shorts-portal-recursion':(2,7,[2,3,47],['All seven current-master contact sheets inspected.','The introductory arrow ends on the exposed inner portal and clears before subsequent camera movement.','The mask is revealed before nested views. The one-to-three-depth change increases visible nesting and the own-implementation view counter.'])
}
for slug in sys.argv[1:] or reviews:
 version,sheets,frames,notes=reviews[slug];p=R/'projects'/slug;project=read(p/'project.json');d=read(p/'production/delivery.json')
 suffix='' if version==1 else f'.v{version}'
 assert Path(d['files']['captioned']['path']).name==slug+suffix+'.captioned.mp4'
 q=p/project.get('currentFinalDirectory','production/local/final-reviewed')/('qa-sequential-'+d['files']['captioned']['sha256'][:12]);index=read(q/'index.json')
 assert index['masterSha256']==d['files']['captioned']['sha256']
 paths=[q/f'sheet-{n:02}.jpg' for n in range(1,sheets+1)];native=[q/f'frame-{n:03}.jpg' for n in frames]
 assert all(x.exists() for x in paths+native)
 save(p/'production/visual-review.json',{'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'masterSha256':d['files']['captioned']['sha256'],'masterVersion':d['masterVersion'],'status':'sampled-sequential-visual-review-complete; human-full-playback-pending','inspectedSheets':[x.relative_to(p).as_posix() for x in paths],'fullResolutionFrames':[x.relative_to(p).as_posix() for x in native],'contactTileWidthPixels':375,'nativeFrameDimensions':[1080,1920],'method':'Direct image inspection of sequentially decoded cue midpoints, scene joins and sampled animation states; native-resolution follow-up frames. This is not a claim to have watched or listened to every frame in real time.','observations':notes,'fullRealtimePlaybackClaimed':False,'humanFullViewing':'pending','humanFullListening':'pending'})
 print('RECORDED',slug)
