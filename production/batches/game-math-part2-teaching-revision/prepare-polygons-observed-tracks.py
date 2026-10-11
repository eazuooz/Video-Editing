"""Author seeds only from directly inspected pixels, then use native bidirectional tracking."""
from pathlib import Path
import math,json
import numpy as np
B=Path(__file__).parent
base='shared/output/game-math-polygons-triangulation/clips/'
tiny='shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/'
fresh='shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/'
noita='shared/output/game-math-part2-full-series/sources/igcymdI4XYM.mp4'
def circle(x,y,r=4):return [[x+r*math.cos(t),y+r*math.sin(t)] for t in np.linspace(0,2*math.pi,17)[:-1]]
def job(ident,file,a,z,region,shapes,meaning,affine=False,closed=False):
 return dict(id=ident,file=file,start=a,end=z,region=region,shapes=shapes,meaning=meaning,affine=affine,closed=closed)
jobs=[
 job('02',base+'02.mp4',11,12.8,[[696,228],[790,228],[790,286],[696,286]],{'red':[[716,232],[766,232],[786,258],[767,281],[715,282],[698,259]],'blue':circle(741,258)},'Exposed preview-tile perimeter and selected projected reference; forest-covered map corners omitted.',True,True),
 job('05',base+'05.mp4',46,47.2,[[329,168],[390,172],[411,238],[356,239]],{'red':[[343,174],[348,191],[365,211],[389,237]]},'Visible right grass/path margin during actual walking; reject the diffuse left margin and failed beach tracking. This screen edge is not a triangular collider, incenter or measured clearance.',True),
 job('08',base+'08.mp4',24,28,[[522,248],[681,248],[683,312],[523,312]],{'red':[[522,254],[570,248],[586,258],[608,255],[639,280],[678,293]]},'Exposed gold-rock perimeter facing traversable empty space; open contour avoids offscreen inferred closure.',True),
 job('11',base+'11.mp4',27,30,[[358,264],[392,245],[460,247],[489,271],[480,303],[363,314]],{'red':[[357,271],[358,282],[424,307],[480,288]]},'Exposed compound-land rim beside an unfilled tile cell; hide the quest badge and montage changes.',True),
 job('14',base+'14.mp4',7,10,[[272,142],[394,141],[447,172],[459,223],[384,229],[286,198]],{'red':[[292,180],[353,154],[387,164],[432,193],[469,219]]},'Observed inward roof contour; not game mesh triangles or an engine partition.',True),
 job('17',base+'17.mp4',26,28,[[286,241],[361,234],[428,240],[496,253],[479,276],[308,277]],{'red':[[336,239],[364,226],[383,211],[403,215],[416,238]]},'Snow slope and empty passage traversed by the character; reseed after the local24.35 motion failure, no artificial closed collider.',True),
 job('19',base+'19.mp4',18,21,[[364,247],[438,247],[441,273],[364,274]],{'red':[[368,253],[437,253]]},'Exposed top of the right platform beside the narrow gap; no numerical thin-mesh claim.',True),
 job('21',base+'21.mp4',10,12,[[502,205],[566,184],[613,198],[593,238],[548,248],[508,226]],{'red':[[512,215],[551,194],[595,210],[574,237]]},'Exposed shoreline on a finite tile, observed through the montage camera; no whole-map center inferred.',True),
 job('QG01-reference',tiny+'tiny-glade-257046593.mp4',18,20,[[330,215],[438,190],[472,262],[355,295]],{'red':[[311,204],[420,152],[472,222],[347,295]],'blue':circle(395,247)},'Observed near roof outline and selected roof reference, reset before later window edits; not the game pivot.',False,True),
 job('QG01-rotate',tiny+'tiny-glade-256965562.mp4',42,44,[[564,127],[680,150],[745,205],[648,246],[555,183]],{'red':[[567,126],[693,158],[745,205],[648,246],[550,186]],'blue':circle(650,182)},'Observed exposed right-building roof after rotation/height changes; no centre of mass or internal transform asserted.',False,True),
 job('QG02-arch',tiny+'tiny-glade-257046593.mp4',6,8.7,[[361,218],[429,245],[444,303],[382,310],[352,272]],{'red':[[370,302],[370,279],[381,260],[398,259],[415,275],[419,300]]},'Observed open arch rim in the drawn wall; omit its occluded rear boundary.',True),
 job('QG02-gameplay',tiny+'tiny-glade-256965562.mp4',8.8,10.8,[[242,210],[419,217],[423,289],[243,297]],{'red':[[272,291],[272,260],[295,238],[312,248],[324,279]]},'Observed wall opening after erase/redraw; track the remaining arch rim, never the editing cursor.',True),
 job('QG03-height',tiny+'tiny-glade-256965562.mp4',27,29,[[443,315],[530,307],[587,337],[531,353],[447,350]],{'red':[[452,337],[489,323],[526,321],[564,343]]},'Visible raised-ground rock rim during height edit; screen contour is not a single planar world polygon.',True),
 job('QG03-opening',noita,86,94,[[350,214],[469,209],[480,263],[345,273]],{'red':[[346,250],[373,236],[397,225],[451,219],[478,232]]},'Exposed rock ledge around the actual traversed gap; preserve empty space and track camera scroll. Extended only through native observed frames to cover the measured narrated red-boundary cue.',True),
 job('QG04-notch',noita,457,462,[[391,104],[526,104],[526,181],[391,181]],{'red':[[408,104],[523,104],[525,177],[400,179]],'yellow':[[531,166],[569,162],[568,200],[532,218]]},'Red traces the exposed stepped ledge; yellow encloses a small visibly empty part beside it, not any filled terrain or measured mesh.',True),
 job('QG05-opening',noita,794,798,[[449,182],[548,166],[590,226],[537,274],[445,265]],{'red':[[471,171],[451,186],[433,221],[443,252],[446,278]]},'Observed rocky opening edge while character moves between platforms; no ear clipping implementation inferred.',True),
 job('QG06-circle',fresh+'shapez2-257294952.mp4',1,2.5,[[543,41],[698,41],[723,189],[546,230]],{'red':[[637,82],[637,131]]},'Visible circle-cutter symbol divider in the fixed machine; reset before the montage cut at2.55s, not a triangulation algorithm.',True),
 job('QG06-square',fresh+'shapez2-257312662.mp4',43,45.8,[[252,99],[317,99],[318,226],[253,226]],{'red':[[282,107],[282,215]]},'Observed square cutter splitting its input; line follows the visible divider, not a manufactured source triangle.',True),
 job('QG07-passage',noita,262,265,[[333,176],[408,176],[410,264],[331,264]],{'red':[[336,186],[401,186],[403,304]]},'Exposed upper step and vertical corridor boundary during actual ascent; hide at source banner and later disappearance.',True),
 job('QG07-return',noita,274,277.3,[[69,293],[247,296],[248,330],[65,331]],{'red':[[65,306],[168,306],[168,317],[225,318]]},'Same later chamber has an exposed ledge after the area banner; separate observed patch, not a forced extrapolation across it.',True),
 job('QG07-path',fresh+'shapez2-257312662.mp4',31,32.3,[[151,290],[376,290],[378,180],[588,171],[588,217],[379,350],[152,350]],{'red':[[183,322],[360,323],[360,199],[560,198]]},'Observed L-shaped belt centerline used to compare ordered turns; end before the32.366s camera cut, explicitly screen route, not a polygon-triangulation demonstration.',True)
]
# Direct coordinate-frame review rejected several approximate borders. Keep
# revised observations on exposed physical edges and stop before montage cuts.
refinements={
 '02':dict(end=12.2),
 'QG01-reference':dict(end=23.8),
 '11':dict(region=[[283,236],[347,240],[349,282],[279,297]],shapes={'red':[[354,250],[343,285],[281,298]]},meaning='Exposed green-land rim adjoining the unfilled cell; the rejected draft on the empty cell itself is not used.'),
 '14':dict(region=[[286,109],[421,104],[465,145],[445,169],[291,164]],shapes={'red':[[290,164],[329,152],[359,139],[403,127],[433,143],[457,161]]}),
 '19':dict(shapes={'red':[[365,228],[435,228]]}),
 '21':dict(start=12,end=13.5,region=[[586,267],[689,273],[710,323],[608,315]],shapes={'red':[[601,289],[628,304],[656,304],[680,316],[703,324]]},meaning='Exposed lower farmland-tile rim after the dissolve finishes; reject tracking across the former winter-to-summer crossfade.'),
 'QG01-rotate':dict(region=[[576,120],[686,127],[701,190],[576,190]],shapes={'red':[[608,80],[714,105],[684,226],[548,168]],'blue':circle(650,182)}),
 'QG02-arch':dict(start=6.5,end=7.8,region=[[359,207],[428,214],[438,278],[357,278]],shapes={'red':[[370,263],[371,242],[381,226],[391,220],[405,230],[417,246],[420,269]]}),
 'QG02-gameplay':dict(start=9.8,end=10.8,region=[[317,268],[380,270],[386,318],[318,319]],shapes={'red':[[331,318],[332,298],[339,287],[349,281],[363,287],[372,298],[377,312]]}),
 'QG06-square':dict(region=[[290,124],[330,124],[330,216],[293,216]],shapes={'red':[[268,146],[268,181]]}),
 'QG03-height':dict(region=[[473,304],[537,301],[583,320],[564,347],[476,347]],shapes={'red':[[477,311],[507,310],[532,311],[555,300],[574,289]]},meaning='Exposed upper rim of the right-hand rock as a height-comparison reference while the adjacent entrance is raised/lowered; this is projected geometry, not a single planar game-world polygon.'),
 'QG07-passage':dict(region=[[339,267],[393,251],[405,262],[405,313],[344,314]],shapes={'red':[[351,282],[374,263],[398,251],[404,251],[404,306]]}),
 'QG07-path':dict(shapes={'red':[[183,303],[360,303],[360,177],[550,177]]},meaning='Projected comparison route through the visible belt preview while its L-shaped route is built; explicitly illustrative route, not a measured world boundary or triangulation engine.')
}
for spec in jobs:
 spec.update(refinements.get(spec['id'],{}))
 if spec['file']==noita or spec['id'] in ['08','14','17','19','QG06-square','QG07-path']:
  spec['translationOnly']=True
source=(B/'draft-planes-observed-tracks.py').read_text(encoding='utf8').replace('planes','polygons').replace('game-math-polygons-barycentric','game-math-polygons-triangulation')
start=source.index('jobs=[');end=source.index('\nparser=argparse',start)
source=source[:start]+"jobs=json.loads((B/'polygons-observed-track-seeds.json').read_text(encoding='utf8'))"+source[end:]
source=source.replace("'closed':True,'seedDefinition':spec", "'closed':spec.get('closed',False),'seedDefinition':spec")
source=source.replace("('teal','#26c6b8')", "('teal','#26c6b8'),('yellow','#ffd54f')")
source=source.replace("np.vstack([p,p[0]])", "(np.vstack([p,p[0]]) if spec.get('closed',False) or k in ['blue','yellow'] else p)")
source=source.replace("required=3 if spec['affine'] else 8", "required=8 if spec.get('translationOnly') else (3 if spec['affine'] else 8)")
source=source.replace("     if spec['affine']:","""     if spec.get('translationOnly'):
      delta=(moved[good]-features[good]).reshape(-1,2);shift=np.median(delta,axis=0)
      inliers=(np.linalg.norm(delta-shift,axis=1)<1.3).astype(np.uint8).reshape(-1,1)
      H=np.array([[1,0,shift[0]],[0,1,shift[1]],[0,0,1]],dtype=np.float64)
     elif spec['affine']:""")
(B/'polygons-observed-track-seeds.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(B/'draft-polygons-observed-tracks.py').write_text(source,encoding='utf8')
print(len(jobs),'manually authored observed seeds; native tracking and final pixels still pending.')
