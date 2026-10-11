"""Extract current final pixels; inherit direct review only for exact RGB identity."""
from pathlib import Path
source=Path(__file__).with_name('extract-part3-final-pixels-v151.py').read_text('utf-8')
# Keep the unchanged timing/cue request sealed; create separate actual execution.
source=source.replace("part3-reviewed-pair-build-v149.json","part3-reviewed-pair-build-v160.json")
source=source.replace("local/part3-final-pixel-qa-v151","local/part3-final-pixel-qa-v161")
source=source.replace("part3-final-pixel-review-execution-v151.json","part3-final-pixel-review-execution-v161.json")
source=source.replace('episode04Part3FinalPixelExtractionV151','episode04Part3FinalPixelExtractionV161')
source=source.replace('resources = m.resources();', """old=m.read(P/'part3-final-pixel-review-execution-v151.json')
direct=m.read(P/'part3-final-board-direct-progress-v158.json')
assert old['status']=='complete' and len(old['images'])==2169
assert direct['directlyReadBoards']==direct['plannedBoards']==362
assert all(r['directlyRead'] for r in direct['records'])
assert len(old['images'])==len(request['points'])
resources = m.resources();""")
source=source.replace("font = ImageFont.truetype", """from PIL import ImageChops
 identity=[]
 for current,previous in zip(state['images'],old['images']):
  assert current['frame']==previous['frame'] and m.sha(ROOT/previous['path'])==previous['sha256']
  with Image.open(ROOT/current['path']) as a,Image.open(ROOT/previous['path']) as b:
   equal=ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is None
  current['exactRgbIdentityToDirectlyReviewedSource']=equal
  identity.append(dict(index=current['index'],frame=current['frame'],equal=equal,previousPath=previous['path'],previousSha256=previous['sha256'],currentSha256=current['sha256']))
 state['pixelIdentity']=identity
 state['priorDirectBoardReview']=dict(path=m.rel(P/'part3-final-board-direct-progress-v158.json'),sha256=m.sha(P/'part3-final-board-direct-progress-v158.json'),directlyReadBoards=362)
 state['priorSourceSha256']=old['sourceSha256']
 font = ImageFont.truetype""")
source=source.replace("group = state['images'][i:i+6]; board =", """group = state['images'][i:i+6]
  if all(p['exactRgbIdentityToDirectlyReviewedSource'] for p in group):
   previousboard=old['boards'][i//6];assert m.sha(ROOT/previousboard['path'])==previousboard['sha256']
   state['boards'].append(dict(previousboard,inheritedExactRgbDirectReview=True,directlyRead=True,board=i//6+1))
   continue
  board =""")
source=source.replace("'directlyRead': False})", "'directlyRead': False,'board':i//6+1,'inheritedExactRgbDirectReview':False})")
source=source.replace("'boards': len(state['boards']), 'newGitImages'", "'boards': len(state['boards']), 'exactRgbFrames':sum(q['equal'] for q in identity),'boardsRequiringDirectRead':sum(not q['directlyRead'] for q in state['boards']), 'newGitImages'")
exec(compile(source,str(Path(__file__)), 'exec'))
