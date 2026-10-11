"""Bind explicit direct CUA input-motion readings; final burned pixels remain separate."""
from pathlib import Path
import json,re,importlib.util
spec=importlib.util.spec_from_file_location('common',Path(__file__).with_name('review-media-common-v15.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
R=m.ROOT/'production/research/game-lighting-history';P=m.ROOT/'projects/game-lighting-history-04/production'
t=(R/'local/part3-explanation-moving-input-review-v151.html').read_text('utf-8')
rows=json.loads(t[t.index('const rows=')+len('const rows='):t.index('];const pick')+1])
notes={
'part3-overview':'Thick projected plates and orange/teal reveals connect appearance, exposure/focus and inspection. All three overview stages visible at normal playback.',
'original-22-1':'White rendered frame R0 followed by three teal generated plates; visible top/side faces.',
'original-22-2':'R0 followed by five generated plates; diagram count distinct from simulation rate.',
'18-pre-generated-frame-count':'Projected 1+3=4 and 1+5=6 comparisons; white rendered versus teal generated plates.',
'19-guide-generated-ui-diagram':'Same labeled rendered/generated responsibility comparison.',
'original-22-3':'Color/motion input plates feed appearance and output through spatial arrows.',
'appearance-prerequisite':'Four projected game platforms; March preview versus September release labels, common appearance question.',
'original-22-5':'Actual rendering, temporal reconstruction and display generation separated by spatial depth/plate grouping.',
'appearance-to-controls':'Orange control moves along dial; teal observed surface and gray inspection stage reveal in order.',
'original-22p-1':'Illustrative y=x/(1+x) example 2/4/16→.667/.8/.941 shown on projected inputs/outputs; not identified as ACES.',
'20-pre-display-transform':'Linear2→exposure×.5→linear1→tone curve→display plates with sequential arrows.',
'original-22p-2':'Input .25/1/4 doubled to .5/2/8 before curve; distinct illustrative mapped display values.',
'original-22p-3':'Screen bloom spread contrasted with world-space bounce on spatial objects; not described as GI.',
'original-22p-4':'Near/far blocks, focal/camera plane and moving orange object with fading motion trail.',
'focus-later-settings':'Near/reference/far projected faces appear over a tilted ground; red arrows mark changed depth regions.',
'focus-observation-protocol':'Three raised blocks for input/value/affected surface, orange value motion and teal connectors; camera changes separately recorded.',
'original-22p-5':'sRGB .5→linear .214×2=.428→display~.686; operations separated on projected plates.',
'original-22p-6':'Six thick geometry/visibility/light/material/reconstruction/post plates reveal through orange links.',
'focus-to-frame-inspection':'Observation→remaining question→event input/output projected stages; promotes resource inspection.',
'original-22r-1':'Resource generation, stored resource and consumers separated spatially.',
'original-22r-2':'Off-screen reflection and frame-resource/G-buffer plates; stored inputs differ.',
'original-22r-3':'Paired camera/path/settings/API/resolution/exposure conditions on thick plates.',
'original-22r-4':'4×4→2×2→1×1 mip grids raised above projected ground.',
'23-pre-capture-dataflow':'Frame622/EID14 sample RGBA→input.color→SV_Target; fixed conditions, own simple capture scope.',
'original-22r-5':'Near1/far100 depth formula and reversed-depth example; z1/2/10/100→d0/.505/.909/1 and1−d1/.495/.091/0; orange height comparison.',
'original-22r-6':'Surface normal (0,0,1) arrow and RGB(n+1)/2=(.5,.5,1); purple visualization distinguished from albedo.',
'original-22r-7':'Screen surface transformed to light-depth plate for comparison; actual partition rules not inferred.',
'original-22r-8':'Tilted screen-depth plane branches to orange alternative trace and green probe cubes; fallback distinguished.',
'original-22rb-1':'Transparent spatial grid and orange ray; T .8×.5=.4 accumulation on separate volumes.',
'original-22rb-2':'Previous translucent orange cube and present teal cube on separated planes; motion/depth/history check.',
'original-22rb-3':'HDR, reconstruction/conversion and display+UI three thick blocks; no universal engine ordering claim.',
'original-22rb-4':'Orange producer feeds teal shared resource and two gray consumers through branch arrows.',
'original-22rb-5':'Structure capture bars versus repeated performance measurements; hypothetical role heights not measured engine timings.',
'original-22rb-6':'Six equal-unit raised bars 8/10/9/11/8/10ms, mean9.33 and range8–11; labeled illustrative values.',
'original-22rb-7':'Observed changes and implementation evidence on two separated planes; scopes not conflated.',
'original-conclusion-1':'Six historical storage/calculation plates connect sequentially; coexistence claim retained.',
'original-conclusion-2':'Stacked brightness/triangle identity, surface/spatial light and depth/history pairs; what gets stored.',
'original-conclusion-3':'Tilted screen-depth plane, spatial grid and triangle with directed arrows; where search happens.',
'original-conclusion-4':'Samples/pages/caches/history four raised columns; cost and reuse responsibility.',
'original-conclusion-5':'Storage→inspection→computation/reuse three thick plates and arrows conclude the viewer question.'}
records=[];silent=[]
for row in rows:
    if 'silent-boundary' in row['id']:
        silent.append(dict(id=row['id'],reason='Preserved one-frame/silent boundary; moving approval is inapplicable and final boundary pixels must still be checked.'));continue
    key=row['id'].split(':')[-1];assert key in notes,key
    records.append(dict(id=row['id'],inputPath=row['path'],inputSha256=m.sha(m.ROOT/row['path']),ranges=row['ranges'],
        normalPlaybackRate=1,directInitialPlaybackAndEndStateRead=True,directSpatialPixelsRead=True,observation=notes[key]))
assert len(records)==40 and len(silent)==5
m.save(P/'part3-explanation-input-motion-direct-review-v157.json',dict(reviewedAt=m.stamp(),
    method='CUA tab53 prepared local player; selected normal-speed clips individually, direct start/motion/end screenshots and DOM currentTime/paused/rate; reviews span the preceding continuation and this continuation.',
    records=records,silentBoundaries=silent,all40MeaningfulInputMotionReviewed=True,allFinalPixelsReviewed=False,
    allFinalMovingPixelsReviewed=False,qaApproved=False,humanWholeListening='pending',newImages=0))
print(json.dumps(dict(inputMotionDirectRead=40,silentEdges=5,finalApproval=False)))
