"""Record this session's direct still inspection, not automatic render approval."""
import datetime,sys
from polish_common import *
BASE='dd48fd9c67cdae38e0ff2a931381af4a4535cb84'
notes={
 'M09':['101 initial composite samples inspected at375px; original beam paths follow the visible red beam and clear at the source cut.',
  'Removed the top-right summary because it covered exit indicators. Post-repair native1080 LG01 12.88/20.10 and the selected normal-speed preview were inspected; source, guide coordinates and captions otherwise unchanged.'],
 'M10':['Ten initial LG05 composite states inspected; rejected late guide extents including the portal below the cube.',
  'Ended the original track at source82.5s and removed the redundant card. Repaired native1080 states30.5/34.48 and mobile states inspected.'],
 'M11':['42 initial composite states inspected: PG01 floor/wall edge, PG02 slope edge and PG03 doorway remain aligned.',
  'Removed redundant upper cards covering gel/panel context. Renamed floor/wall tangent wording to boundary line; changed current pixels rechecked.'],
 'M12':['42 initial composite states inspected: PG04 tile boundary, PG06 editorial triangle and PG07 platform edge follow their visible targets.',
  'Removed redundant upper cards. The comparison triangle is explicitly labelled an illustration, not the game mesh. Changed current pixels rechecked.'],
 'M17':['84 coarse original-source states and43 exact anchor frames directly inspected before creating anchors.',
  '28 new composited states inspected at375px plus native1080 pillar state; five observed-region rings identify the stationary pillar, cube front face and activated yellow indicator. No world coordinates or engine matrices inferred.']}
for ident in sys.argv[1:]:
 e=Episode(ident);e.authorized();assert ident in notes
 path=e.H/'observed-guide-preflight.json';p=read(path)
 composition=read(e.H/'observed-guide-composition.json')
 assert p['planSha256']==composition['planSha256']==sha(R/composition['plan'])
 assert p['assSha256']==composition['globalAssSha256']==sha(R/composition['globalAss'])
 old=json.loads(subprocess.check_output(['git','show',BASE+':'+rel(path)]))
 old_samples={(x['scene'],x['localSeconds']):x for x in old['samples']}
 reused=[];changed=[]
 for x in p['samples']:
  assert sha(R/x['image'])==x['imageSha256']
  prior=old_samples.get((x['scene'],x['localSeconds']))
  (reused if prior and prior['imageSha256']==x['imageSha256'] else changed).append(x['image'])
 p.update(status='passed-still-preflight',reviewedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  partial=False,fullMasterReady=False,reviewScope='Current source/guide still preflight only; whole encoded master and human review remain pending.',
  findings=notes[ident],unchangedPixelEvidence={'commit':BASE,'identicalImageCount':len(reused),'images':reused},
  newOrChangedImageCount=len(changed),newOrChangedImages=changed,
  originalResolutionException=rel(B/'portal-original-resolution-exception.json'))
 save(path,p);print(ident,'still preflight recorded; unchanged',len(reused),'new/changed',len(changed),'whole-master pending')
