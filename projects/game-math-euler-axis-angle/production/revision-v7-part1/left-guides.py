"""Editable source-space editorial guides, never reconstructed game telemetry.

Anchors come from actually inspected native stills/contact samples. The dense
clock interpolates those source-space anchors; that is not a claim that every
intermediate frame was manually reviewed. Unknown/occluded parts stay hidden.
Final tracking approval requires current moving1920/375 output review.
"""
from pathlib import Path
import argparse, bisect, hashlib, json

H=Path(__file__).resolve().parent;R=H.parents[3]
P=R/'projects/game-math-euler-axis-angle';G=P/'production/local/revision-v7-part1/gameplay'
FPS=60
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rel(p):return Path(p).resolve().relative_to(R).as_posix()
def save(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def guide(label,point,color='focus',box=None):
    d=dict(label=label,point=point,colorRole=color)
    if box:d['attentionBox']=box
    return d

# Each row is sourceSeconds, normalized observed screen point. A marker is an
# attention pointer; it does not assert a forward vector or a world-space axis.
FLIGHT=[
 (160,.51,.52),(164,.51,.51),(168,.51,.51),(172,.51,.51),(176,.51,.51),(180,.51,.51),
 (182.983333,.51,.51),(183,.51,.51),(185,.50,.55),(187,.48,.55),(189,.49,.53),
 (191,.49,.56),(193,.51,.07),(195,.49,.56),(197,.50,.49),(199,.53,.46),
 (201,.51,.50),(203,.49,.55),(205,.49,.53),(207,.48,.55),(209,.53,.48),(210.983333,.51,.52),
 (294,.49,.60),(296,.50,.56),(298,.45,.51),(300,.45,.50),(302,.53,.53),
 (304,.50,.51),(306,.49,.53),(308,.50,.51),(310,.46,.53),(312,.51,.55),
 (313.983333,.50,.52),(314,.50,.52),(316,.50,.53),(318,.46,.52),(320,.50,.51),
 (322,.55,.51),(324,.543,.493),(326,.50,.52),(328,.48,.54),(330,.49,.53),
 (332,.46,.50),(333.983333,.51,.51)]

# Attention to the visible assembly only; cloth/mast tip can be out of frame.
SAIL=[(995.75,.63,.47),(998.75,.60,.53),(1000,.49,.64),(1001,.49,.60),
 (1002,.50,.16),(1002.75,.49,.23),(1003.25,.49,.22),(1003.5,.49,.50),
 (1004.5,.52,.36),(1005.5,.53,.30),(1006.5,.518,.31),(1007.75,.48,.42),
 (1008.733333,.48,.42),(1008.75,.48,.42),(1010.75,.50,.45),(1012,.53,.50),
 (1013.5,.46,.50),(1015,.52,.50),(1016.5,.52,.46),(1018,.51,.46),
 (1019.5,.52,.46),(1020.5,.51,.52),(1021.5,.52,.55),(1023,.52,.58),(1025.483333,.50,.60)]
HOOK=[(287.5,.51,.23),(288,.51,.22),(288.5,.51,.22),(289,.51,.24),
 (290,.40,.33),(291,.45,.37),(292,.45,.35),(293,.49,.27),(294,.50,.27),
 (295,.50,.27),(296,.50,.20),(297,.49,.15),(298,.52,.18),(299,.50,.23),
 (300,.55,.27),(301,.55,.28),(302,.55,.27),(303,.52,.26),(304,.52,.28),
 (305,.35,.42),(306,.35,.38),(307,.49,.57),(309,.48,.53),(310,.47,.52)]

def key(seconds,guides,visible=True,reason='observed-target'):
    return dict(sourceFrame=round(seconds*60),visible=visible,guides=guides if visible else [],
                classification='manual-source-anchor',visibilityReason=reason)

def build():
    j=read(H/'game-inputs.json');streams={x:[]for x in j['sources']}
    observed={}
    def evidence(source,seconds,file,nominal=False):
        observed[(source,round(seconds*60))]=dict(file=file,sha256=sha(R/file),
            nominalSampleClock=nominal,review='source/contact frame directly inspected; intermediate moving review pending')
    for s in j['stills'].values():evidence(s['sourceId'],s['sourceSeconds'],s['file'])
    research=P/'production/local/revision-v7-script/other-game-research'
    for name in ['local-frames.json','local-long-frames.json']:
        for group in read(research/name):
            source='superflight'if group['game'].startswith('superflight')else'mariokart'if group['game'].startswith('mariokart')else'odyssey'
            for im in group['images']:
                if(source,round(im['time']*60))not in observed:evidence(source,im['time'],im['path'])
    for group in read(G/'expanded-temporal-inspection.json'):
        if group['id'].startswith('superflight'):
            for im in group['samples']:evidence('superflight',im['time'],im['file'],True)
    td=P/'production/local/revision-v7-script/totk'
    for prefix,start,step in [('raft',976,.25),('hook',232,.5),('sail-result',1024,.5),('rail-result',302,.5)]:
        for i,f in enumerate(sorted(td.glob(prefix+'-*.jpg'))):
            frame=round((start+i*step)*60)
            if('totk',frame)not in observed:evidence('totk',frame/60,rel(f),True)
    for t,x,y in FLIGHT:
        streams['superflight'].append(key(t,[guide('몸통·펼친 팔',[x,y],box=[x-.055,y-.055,.11,.11])]))
    # Camera collision/near-edge samples do not justify a continuous contour.
    # No interpolation bridges the explicitly unobservable near-edge193state.
    for t in [190.5,191.5,192.5,193,193.5,194]:
        streams['superflight'].append(key(t,[],False,'edge/foreground ambiguity; hide the editorial guide'))
    for t,x,y in SAIL:
        streams['totk'].append(key(t,[guide('돛·뗏목',[x,y])]))
    for t,x,y in HOOK:
        streams['totk'].append(key(t,[guide('갈고리의 열린 쪽',[x,y])]))
    # The rail occludes the opening, then the hook leaves the shot on landing.
    for t in [281,284,286.9,307.4,307.5,308,308.5,308.6,310.5,311,312,313,314,315,316,317,318,319,320,320.983333]:
        streams['totk'].append(key(t,[],False,'nativeUI sufficient, rail occlusion, or opening not verifiable; do not invent contour'))
    for t,point in [(239.5,[.56,.23]),(241.5,[.56,.23])]:
        streams['totk'].append(key(t,[guide('열린 쪽',point)]))
    old=read(P/'production/revision-v6/footage-plan.json')['clips'][0]['annotation']['directionPointers']['sourceKeyframes']
    for k in old:
        assert sha(R/k['evidence'])==k['evidenceSha256']
        evidence('mariokart',k['sourceTime'],k['evidence'])
        streams['mariokart'].append(key(k['sourceTime'],[
            guide('차체 앞쪽',[v/scale for v,scale in zip(k['front'],[1920,1080])],'reference'),
            guide('머리 쪽',[v/scale for v,scale in zip(k['up'],[1920,1080])],'focus')]))
    for t in [108,109,110,111,112,113,114,115,116]:
        streams['mariokart'].append(key(t,[],False,'entry/trick/wheels context; front/head guides start at verified116.5'))
    for t,head,front in [(161,[.50,.49],[.52,.65]),(163,[.50,.53],[.52,.68]),(165,[.42,.55],[.52,.66])]:
        evidence('mariokart',t,rel(research/f'mariokart-glide-{t:09.3f}.jpg'))
        streams['mariokart'].append(key(t,[guide('차체 앞쪽',front,'reference'),guide('머리 쪽',head)]))
    for t in [165.5,166,167,168,168.983333]:
        streams['mariokart'].append(key(t,[],False,'item/hit/body-camera ambiguity; no extrapolation of head/front'))
    # Native samples distinguish articulated head/feet from rigid-body rotation.
    mario=[(1349.6,[.52,.43],[.52,.57]),(1350.4,[.52,.48],[.52,.56]),
           (1350.6,[.52,.39],[.52,.50]),(1350.7,[.52,.414],[.52,.333]),
           (1350.8,[.52,.40],[.51,.33]),(1351,[.52,.40],[.51,.36]),
           (1351.4,[.52,.43],[.52,.53]),(1351.6,[.52,.43],[.52,.57]),
           (1351.983333,[.52,.43],[.52,.57])]
    for t,head,feet in mario:streams['odyssey'].append(key(t,[guide('머리',head),guide('발',feet,'reference')]))
    for source,rows in streams.items():
        # Explicit hide anchors win ties; never bridge a cut/unknown target.
        dedup={x['sourceFrame']:x for x in rows}
        streams[source]=sorted(dedup.values(),key=lambda x:x['sourceFrame'])
        for row in streams[source]:
            row['evidence']=observed.get((source,row['sourceFrame']))
            if not row['visible']:row['classification']='explicit-conservative-hide'
            elif row['evidence']is None:
                # A hand-entered point without a currently linked source image
                # must never be silently promoted into a tracked annotation.
                row.update(visible=False,guides=[],classification='hidden-unlinked-anchor',visibilityReason='No exact inspected source-image link for this planned anchor')
    evidence=[j['sources'][s]['evidence']for s in streams]
    result=dict(schemaVersion=1,sourceRaster=[1920,1080],sourceToCanvas=dict(x=40,y=250,scale=7/15),
        classification='editorial2Dsource-screen guides, not recovered game engine data',
        axisRings='Native gameUI only on the left. Our3DXYZrings/angles are restricted to the right controlled model.',
        streams=streams,sourceHashes={s:q['sourceSha256']for s,q in j['sources'].items()},
        sourceEvidence=evidence,inputs=dict(gameInputsSha256=sha(H/'game-inputs.json'),implementationSha256=sha(Path(__file__))),
        interpolation=dict(sourceFrameRate=60,maximumGapSeconds=4.1,method='linear source-screen points between inspected anchors only; no extrapolation',
                           hides='If either bracketing key is hidden, target label differs, source cut occurs or gap exceeds limit, draw nothing.'),
        frameReview='anchors derive from directly viewed native/contact samples; dense intermediate moving output approval pending',
        colorRoles=dict(focus='#66c49a',reference='#7db5dd',caution='#e58b78'),
        protectedAreas='originalUI/watermark and full source bounds; captions at960970 unchanged. No guide path crosses the right pane.',
        productionReadiness='prototype source-keyed overlays; inspect whole current moving1920and375output for occlusion/target tracking')
    save(G/'guide-keys.json',result);return result

def at(data,source,frame):
    rows=data['streams'].get(source,[])
    if not rows:return []
    n=bisect.bisect_left([x['sourceFrame']for x in rows],frame)
    if n<len(rows)and rows[n]['sourceFrame']==frame:
        return rows[n]['guides']if rows[n]['visible']else []
    if n==0 or n==len(rows):return []
    a,b=rows[n-1],rows[n]
    if not a['visible']or not b['visible']or b['sourceFrame']-a['sourceFrame']>data['interpolation']['maximumGapSeconds']*60:return []
    if [x['label']for x in a['guides']]!=[x['label']for x in b['guides']]:return []
    t=(frame-a['sourceFrame'])/(b['sourceFrame']-a['sourceFrame']);out=[]
    for x,y in zip(a['guides'],b['guides']):
        z=dict(x);z['point']=[u+(v-u)*t for u,v in zip(x['point'],y['point'])]
        if x.get('attentionBox')and y.get('attentionBox'):z['attentionBox']=[u+(v-u)*t for u,v in zip(x['attentionBox'],y['attentionBox'])]
        z['classification']='interpolated-editorial-screen-anchor';out.append(z)
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--build',action='store_true');a=ap.parse_args()
    if a.build:
        j=build();print(json.dumps(dict(manualKeys=sum(len(x)for x in j['streams'].values()),status=j['productionReadiness'],noVideoDecoded=True)))
    else:ap.print_help()
if __name__=='__main__':main()
