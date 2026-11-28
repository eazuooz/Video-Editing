"""Lock reviewed design examples with explicit source and model boundaries."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha
WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11')
PS='https://blog.ja.playstation.com/2022/01/29/20220129-eldenring/'
XBOX='https://news.xbox.com/en-us/2019/06/09/hidetaka-miyazaki-and-george-rr-martin-present-elden-ring/'
EN={
 '17':[
 'In a field you choose where to travel; inside a castle you inspect the next foothold. Why join such different spaces in one game?',
 'An open field makes distant destinations and their visiting order important. In a layered dungeon, nearby routes, enemies and drops matter. Moving through each asks you to judge a different scale of space.',
 'Elden Ring combines open fields with intricate legacy dungeons. Choosing a direction for a journey connects with working through the details of a nearby space.',
 'Our character chooses between two destinations, then enters a castle and chooses between upper and lower paths. The combination alternates broad exploration with detailed local decisions.'
 ],
 '18':[
 'How does Martin’s mythology connect to a boss we fight? The world’s past and the events we play have different roles.',
 'Past characters and their relationships provide a foundation. The developers turn it into present characters, events and environments. History becomes material for what we encounter.',
 'The Elden Ring collaboration distinguishes a mythical foundation from its realization as a game. Players infer the past from the completed characters and places they encounter.',
 'Our model connects a past relationship, its present form and a trace the player discovers. Written background becomes something the player can meet and observe.'
 ],
 '19':[
 'You can pass the Tree Sentinel instead of fighting immediately. How does boss placement change a decision before the first attack?',
 'An enemy in an open field leaves room to go around or observe from afar. A gate channels movement toward an encounter. Approaching the same enemy can involve different choices.',
 'Read Elden Ring’s field bosses and dungeon encounters together with their surroundings. Compare your approach direction, your choice of when to fight, and the route leading to the encounter.',
 'Our demonstration keeps the enemy and character while changing the route. The open side allows a detour; the gate narrows the approach. Designing an encounter includes how players reach it.'
 ],
 '22':[
 'Why do friends tell different stories about the same Elden Ring? Even the same places can be discovered in a different order.',
 'Give two characters two destinations, then let each visit a different one first. They arrive at the second place with different information, changing the context of their next choice.',
 'Open exploration lets visiting order and choices shape an individual experience. The world’s past is shared, while the sequence of encounters and discoveries can differ.',
 'Reveal each route’s discovered clues in order. The two places remain the same, but their sequence differs. Within a fixed world, discovering and choosing creates a personal adventure.'
 ],
 '24':[
 'If a powerful enemy defeats you, must you win immediately? Elden Ring also leaves room to explore elsewhere.',
 'Our model shows two paths: try again now, or explore and prepare. Having only one action after failure can make a challenge feel like a closed route.',
 'Open spaces and preparation options let you change when to attempt a challenge. Returning after exploring can mean approaching the same enemy with different equipment or a different method.',
 'The demonstration leaves the enemy in place while the player takes another route and returns. Failure remains, but the next choice opens up. Difficulty can suggest what to prepare next.'
 ],
 '32':[
 'Must weakening a powerful PvP weapon also make boss fights harder? Applying the same adjustment to every opponent can create that conflict.',
 'Apply one attack to a player and a monster. Reducing a shared value changes both. A separate modifier for player targets creates room to tune PvP independently.',
 'Elden Ring patch 1.07 introduced separate PvP damage scaling. Changes through that feature do not affect solo or cooperative play. General balance changes can still apply to both PvP and PvE.',
 'The demonstration bars are illustrative. A shared adjustment changes both bars; a separate adjustment changes the relevant target. Distinguishing opponent types creates room to balance different combat settings.'
 ]}
BOUNDARIES={
 '17':('Open fields and layered castles are supported by the direct interview. Player-information scale is our explanation, not measured emotion.',[XBOX,PS]),
 '18':('Direct account of mythos as a foundation. Abstract relationship diagram is invented for teaching, not Martin’s manuscript or a claim about specific unpublished characters.',[XBOX]),
 '19':('Map and boss gameplay were adjusted in relation to each other. Controlled same-enemy gate comparison is our model; actual clips contain different enemies.', ['https://news.xbox.com/ja-jp/2022/05/26/elden-ring-interview/']),
 '22':('Own-pace exploration and freedom are direct statements. Two-route information example is explanatory inference, not recorded participant research.',[PS]),
 '24':('Direct recommendation permits returning later with other options. Actual clips are different encounters and must not be edited as a before/after against the same enemy.',[PS]),
 '32':('Historical patch 1.07, 2022-10-13, separate damage scaling. Distinguish this feature from general changes; no exact damage values inferred from footage.', ['https://en.bandainamcoent.eu/elden-ring/news/elden-ring-patch-notes-107'])}

def main():
    manifest=Path('C:/Users/1/Videos/YamyamProduction/elden-ring-development-36/pc-review-v10/manifest.json')
    baseline=read(manifest);scripts=read(HERE/'narration-ko.json')
    reference=Path('D:/Github/VideoEditing/projects/shorts-mario-one-action/production/local/tts-execution.json')
    observation=HERE/'retained-source-observations.json'
    for n in EN:
        record=baseline['episodes'][n]['record'];sources=[];footage=[]
        for i in [0,2]:
            source=Path(record['formatSources'][i]['source']);assert sha(source)==record['cuts'][i]['sha256']
            sources.append(source)
            footage.append({k:record['cuts'][i][k] for k in ['url','recorder','rights','sha256','size','start','end','observed']})
        ko=list(scripts[n]);boundary,links=BOUNDARIES[n]
        if n=='32':ko[2]='엘든 링은 패치 일 점 영칠에서 대인전 전용 피해 보정을 도입했습니다. 이 보정은 혼자 하는 전투와 협력 플레이에 영향을 주지 않습니다. 다만 공통 밸런스 변경은 여전히 양쪽에 적용될 수 있습니다.'
        if n=='17':
            sources.append(WORK/'sources/stormveil-uS9SiEYW6gE-647-950.mp4')
            footage.append(dict(replacementForShot=2,sourceUrl='https://www.youtube.com/watch?v=uS9SiEYW6gE',
              provenance=str(WORK/'sources/stormveil-provenance.json'),selectedCandidate=[224,243],
              observed='High tower ledges, character turning view down; no developer map data.'))
        item=dict(id=n,version='causal-v11',scriptLockedForVoice=True,narrationKo=ko,narrationEn=EN[n],
            claimEvidence=[dict(url=u,reviewed='2026-11-28',scope=boundary) for u in links],
            footageEvidence=dict(retainedRights=footage,sourceManifest=str(manifest),observations=str(observation),
              scope='18 opening is an actual game cinematic, labeled as such; not a playable camera demonstration.' if n=='18' else boundary,
              continuousPlaybackReviewed=False,audioUse='video only',timedFinalSelection='Pending measured narration and precise source-window review; no replay.'),
            demonstration=dict(nativeProject='unity/VideoEditing',pilotFingerprint='47f665555481861946ba29bb8456d94e3d1f64fa9787836003df77807e22776f',
              classification='independent illustrative model, not original game source or measured player behavior',finalVoiceTimedCapture=False),
            inputs=[dict(path=str(p),sha256=sha(p)) for p in dict.fromkeys(sources+[manifest,reference,observation])],humanReview='pending',finalRenderComplete=False)
        path=HERE/'locked'/f'{n}.json'
        if path.exists():assert read(path)==item
        else:save(path,item)
        print(n,sha(path))

if __name__=='__main__':main()
