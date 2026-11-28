"""Lock source-bounded world/navmesh narration after actual footage sampling."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha

EN={
 '01':[
 'Ride out of the ruins and the next field continues ahead. Is this entire enormous world kept in memory at once?',
 'Loading everything would occupy memory with distant terrain you cannot see. Waiting until you reach a boundary could leave the next landscape unprepared. Nearby areas need to be prepared before you reach them.',
 'Elden Ring divided its open world into a grid to manage surrounding data. A horse crosses areas quickly and a large enemy can move beyond one cell, so considering only the cell beneath your feet is not enough.',
 'As the demonstration character moves, cells ahead are prepared and distant cells are released. These cells are data divisions, not visible walls. The landscape stays connected while the data prepared behind it changes.'
 ],
 '02':[
 'Nearby rocks look clear while distant trees disappear into fog. How does the computer build the fog between them?',
 'Draw a line from the camera to a rock. Advance along it in small steps and check the fog at each point. Accumulating each contribution tells us how much the rock is obscured.',
 'Checking several points along a line is called ray marching. But keeping the same spacing all the way to distant mountains means more sampling points as distance increases.',
 'Elden Ring combined detailed nearby fog with a simpler calculation for distant atmosphere. This preserves nearby fog structure while retaining a sense of distance in the far landscape.'
 ],
 '11':[
 'When I move behind a rock, an enemy comes around it after me. Does it know what I will do next? First, it needs prepared information about where it can go.',
 'Moving straight toward the player would leave the enemy blocked by the rock. Mark the walkable ground and its connections, then find a connected route to the target and go around the obstacle.',
 'Elden Ring used navigation meshes for walkable regions and connections for movements such as jumping. Large enemies also had separate route handling. Planning a route is different from choosing an attack.',
 'Move the player to the other side and watch the route change in the demonstration. The prepared information describes possible paths, not the player future input. The enemy uses those paths to approach its target.'
 ]}

def main():
    manifest=Path('C:/Users/1/Videos/YamyamProduction/elden-ring-development-36/pc-review-v10/manifest.json')
    data=read(manifest);scripts=read(HERE/'narration-ko.json')
    reference=Path('D:/Github/VideoEditing/projects/shorts-mario-one-action/production/local/tts-execution.json')
    for n in EN:
        record=data['episodes'][n]['record'];sources=[];observations=[]
        for i in [0,2]:
            source=Path(record['formatSources'][i]['source']);assert sha(source)==record['cuts'][i]['sha256']
            if source not in sources:sources.append(source)
            observations.append({k:record['cuts'][i][k] for k in ['url','recorder','rights','sha256','size','start','end','observed']})
        links=(['https://cedil.cesa.or.jp/cedil_sessions/view/2567','https://www.4gamer.net/games/463/G046388/20220826111/'] if n=='02' else
               ['https://cedil.cesa.or.jp/cedil_sessions/view/2542','https://www.famitsu.com/news/202208/26273425.html'])
        boundary={'01':'Grid/load timing is not observable from gameplay. No fixed radius or original memory readings claimed; demonstration is a conceptual model.',
                  '02':'Actual atmospheric appearance does not prove per-pixel implementation. Near ray marching and distant analytic fog come from the developer session as reported on site. The sampling line is an illustrative model.',
                  '11':'Walkable routes, jump/drop links and separate large-enemy handling are supported. Do not claim future input reading, attack AI, or uniformly stricter large-enemy constraints.'}[n]
        notes={'01':'Expanded samples 0.3/5/10/16 show mounted travel from ruins to field; 137.3/142/147/153 show mounted enemy moving around rocks. These reveal movement, not actual cells.',
               '02':'Expanded samples 1629.3/1634/1639/1645 show near rocks and hazy distant trees; 821.3/826/831/837 show dark cave and foggy opening. Pickup UI appears near 1645; opening cut must end before that.',
               '11':'Expanded samples 91.3/96/101/107 show mounted enemy curving around a rock; 1944.3/1949/1954/1960 show human-scale approach near ruins and rock. This does not expose the internal route or its exact replanning time.'}[n]
        item=dict(id=n,version='causal-v11',scriptLockedForVoice=True,narrationKo=scripts[n],narrationEn=EN[n],
            claimEvidence=[dict(url=u,reviewed='2026-11-28',scope=boundary,
              access='Official abstract and first-hand on-site report. Full slide download requires login; full slides were not read.') for u in links],
            footageEvidence=dict(retainedRights=observations,sourceManifest=str(manifest),sampleReview=notes,
                continuousPlaybackReviewed=False,audioUse='video only',timedFinalSelection='pending narration duration; no UI intrusion or replay'),
            demonstration=dict(nativeProject='unity/VideoEditing',sceneMethod={'01':'Streaming','02':'CausalFog','11':'CausalNavigation'}[n],
                pilotFingerprint='47f665555481861946ba29bb8456d94e3d1f64fa9787836003df77807e22776f',
                classification='independent principle model; not original game implementation',finalVoiceTimedCapture=False),
            inputs=[dict(path=str(p),sha256=sha(p)) for p in sources+[manifest,reference]],humanReview='pending',finalRenderComplete=False)
        path=HERE/'locked'/f'{n}.json'
        if path.exists():assert read(path)==item
        else:save(path,item)
        print(n,sha(path))

if __name__=='__main__':main()
