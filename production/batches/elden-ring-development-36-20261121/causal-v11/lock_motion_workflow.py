"""Prepare four reviewed motion/workflow narratives and bounded real-footage use."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha
EN={
 '14':[
 'How can we start dodging before Radahn attack reaches us? Waiting to see the collision can be too late.',
 'Separate the raised-weapon preparation, the swing and the recovery. The preparation reveals the direction of the weapon and body. That information helps us choose when to move away or evade.',
 'Watching the actual attack from its starting pose through its finish makes the available cues easier to identify. A striking pose can communicate the next danger as well as a character appearance.',
 'Our demonstration keeps the enemy attack fixed and changes only when the player responds. Moving from the preparation cue instead of waiting for contact changes the result. Learning a dodge begins with the clues before the hit.'
 ],
 '23':[
 'If a corridor becomes wider, is the environment team the only one affected? In a game, its shape connects to other functions.',
 'In our demonstration, changing corridor width affects enemy routes and the camera view. Moving a wall also calls for another look at lighting and occlusion. One edit affects several results.',
 'The Elden Ring team described adapting communication and production during the pandemic, expanding existing remote communication practices across the company. Our corridor edit is an illustration of why multiple departments need shared checks.',
 'After editing the route, check movement, enemies, visibility and lighting in turn. Completing each individual task is not enough. Connected changes need a shared basis for review so the space works as a whole.'
 ],
 '25':[
 'After finishing a large game, does the team retain only models and code? It also retains people experience of working at that scale.',
 'On an unfamiliar project, it is hard to judge the production volume and what needs checking. Experience from making and revising it provides a basis for deciding what to test first next time.',
 'Miyazaki reflected that Elden Ring large production scale helped other directors, designers and planners grow. It left people and experience for future production as well as completed assets.',
 'Our demonstration records a cycle of planning, testing and revision. On the next task, those records help select the first checks. Experience and criteria for judgment become production inputs alongside the assets.'
 ],
 '26':[
 'Can the same sword model look lighter if only its motion changes? The object in a hand does not communicate all of its weight.',
 'Compare an arm-only swing with a body that prepares, turns and recovers. The sword is unchanged, but applying and absorbing force looks different. Preparation and recovery are parts of the attack too.',
 'Follow the whole body in Elden Ring weapon animations instead of isolating the impact. The starting stance, body rotation and return after the swing communicate how the weapon is used and how heavy it feels.',
 'Our demonstration keeps the weapon and camera fixed while comparing motions. It does not enlarge the model to imply weight. Weight is expressed through effort and the body regaining balance.'
 ]}
URLS={'14':['https://www.too.com/dc/report/elden_ring_220708/'],
      '23':['https://www.gamesradar.com/elden-ring-fromsoftware-hidetaka-miyazaki-interview/'],
      '25':['https://www.gamespot.com/articles/hidetaka-miyazaki-on-bringing-elden-ring-to-a-close-and-the-future-of-from-software/1100-6524337/'],
      '26':['https://www.too.com/dc/report/elden_ring_220708/']}
BOUND={'14':'Motion-team explanation supports anticipation/wind-up/recovery. Radahn attack reading is our footage observation; no claim about invisible input-reading or measured reaction times.',
       '23':'Direct interview describes pandemic workflow and communication adaptation. Corridor dependency checks are our teaching example, not an identified development incident or tool.',
       '25':'Direct retrospective describes growth of directors, designers and planners. Checklist demonstration is illustrative; no measured speedup or commitment that all future games are open world.',
       '26':'Developer explanation connects weapon properties and body motion. Actual clips show different enemies and weapons; identical-weapon control exists only in our Unity model.'}

def main():
    manifest=Path('C:/Users/1/Videos/YamyamProduction/elden-ring-development-36/pc-review-v10/manifest.json')
    data=read(manifest);scripts=read(HERE/'narration-ko.json')
    observation=HERE/'retained-source-observations.json';observed={r['episode']:r for r in read(observation)['rows']}
    ref=Path('D:/Github/VideoEditing/projects/shorts-mario-one-action/production/local/tts-execution.json')
    for n in EN:
        r=data['episodes'][n]['record'];sources=[];rights=[]
        for i in [0,2]:
            p=Path(r['formatSources'][i]['source']);assert sha(p)==r['cuts'][i]['sha256']
            if p not in sources:sources.append(p)
            rights.append({k:r['cuts'][i][k] for k in ['url','recorder','rights','sha256','size','start','end','observed']})
        item=dict(id=n,version='causal-v11',scriptLockedForVoice=True,narrationKo=scripts[n],narrationEn=EN[n],
            claimEvidence=[dict(url=u,reviewed='2026-11-28',scope=BOUND[n]) for u in URLS[n]],
            footageEvidence=dict(retainedRights=rights,sampleReview=observed[n],continuousPlaybackReviewed=False,
                audioUse='video only',timedFinalSelection='pending narration timing; source context must be labeled; no repeated action'),
            demonstration=dict(nativeProject='unity/VideoEditing',sceneMethod={'14':'ObservedTelegraph14','23':'CausalHandoff','25':'CausalExperience','26':'CausalWeight'}[n],
                classification='independent illustrative model, not original implementation',finalVoiceTimedCapture=False),
            inputs=[dict(path=str(p),sha256=sha(p)) for p in sources+[manifest,observation,ref]],humanReview='pending',finalRenderComplete=False)
        p=HERE/'locked'/f'{n}.json'
        if p.exists():assert read(p)==item
        else:save(p,item)
        print(n,sha(p))

if __name__=='__main__':main()
