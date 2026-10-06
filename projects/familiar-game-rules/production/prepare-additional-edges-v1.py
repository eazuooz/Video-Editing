"""Prepare exact boundary review of observed actions; no automatic approval."""
from pathlib import Path
import json, hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
PROOF=ROOT/'production/batches/sakurai-planning-game-design/proof-familiar-game-rules'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
rows=[]
metadata={}
for v in [1,2,3]:
    for s in read(PROOF/f'additional-source-execution-v{v}.json')['results']:metadata[s['videoId']]=s
# Intervals use integer native frames. These are candidate boundaries, not cut approval.
groups={
 'FVkDc6u_4GQ':[(240,690,'Corridor then pink-door aim/fire'),(690,960,'Purple room and close doorway kick'),(960,1110,'Escalator upper targets'),(1110,1380,'Sewer-platform firing and weapon throw'),(1410,1620,'Stair doorway and bathroom movement'),(1680,1740,'Bathroom kick'),(1830,2100,'Room upper-target aim and movement')],
 'XbW4873OPZo':[(930,1170,'Pink doorway then tentacle/kick montage'),(1320,1500,'Escalator and purple crate doorway'),(1650,1920,'Crossbow/rocket downward and hallway kick'),(2070,2280,'Airborne targets and rooftop shield kick'),(2370,2550,'Bathroom launch and upper corridor kick'),(2640,2820,'Lobby doorway fire and explosion'),(2940,3150,'Upper platform and shield group shaft')],
 'q8iWixSvfsI':[(930,1110,'Railcar traversal'),(1110,1290,'City rooftop umbrella movement'),(1290,1470,'Wire forest then laundry roof'),(1470,1590,'Letterboxed city firing'),(1590,1830,'Cult and industrial jump/fire montage'),(1830,2010,'Factory catwalk umbrella/fire'),(2280,2490,'Wire container and vertical factory movement')],
 'zxzPcsI8l2o':[(240,420,'Rail-side then rainy city-wall ascent'),(1140,1320,'Wire containers then airborne cult and city dash'),(1620,1740,'Library lower-floor traversal'),(1740,1860,'Swamp target and wire-container fire/traversal'),(1920,2040,'City-wall umbrella/attack and rooftop traversal')],
}
for sid,clips in groups.items():
    s=metadata[sid];num,den=map(int,s['frameRate'].split('/'))
    for start,end,action in clips:
        assert 0<=start<end<=s['frameCount']
        rows.append(dict(id=f'additional-{len(rows)+1:02d}',sourceVideoId=sid,sourcePath=s['localMediaPath'],sourceSha256=s['fileSha256'],sourceFrameRate=s['frameRate'],inFrameInclusive=start,outFrameExclusive=end,inSeconds=start*den/num,outSeconds=end*den/num,seconds=(end-start)*den/num,visibleAction=action,classification='candidate-existing-game-action',sourceAudio=False,loop=False,editorSlowdown=False,exactEdgeApproval=False,crossSourceDuplicateSelectionApproved=False,finalCutAndCaptionApproval=False))
dest=PROOF/'additional-action-bank-candidates-v1.json'
assert not dest.exists(),'Read preserved candidates'
dest.write_text(json.dumps(dict(schemaVersion=1,slug='familiar-game-rules',preparedAt=datetime.now(timezone.utc).isoformat(),clipCount=len(rows),candidateSeconds=sum(c['seconds'] for c in rows),clips=rows,allEdgesDirectlyRead=False,ratioApproved=False,crossSourceDuplicateSelectionApproved=False,sourceAudioUsed=False,imagesGitPolicy='local-only'),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(candidateCount=len(rows),candidateSeconds=sum(c['seconds'] for c in rows),approval=False)))
