"""Source-reviewed environment lessons; retained media are examples, not development recordings."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha
WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11')
EN={
 '05':['Would planting many large trees make the opening field more impressive? Adding nearby detail can instead hide the wide landscape.',
 'Keep the viewpoint fixed and place large trees in front. The foreground becomes richer, but distant structures and the horizon disappear. Size and position matter as much as the number of trees.',
 'The Elden Ring team balanced vegetation against an open first vista. Placing visual interest in distant silhouettes can preserve both the breadth of the field and a readable destination.',
 'Now reduce the large foreground trees without moving the camera. The distant outline becomes visible between smaller plants. Empty space has a purpose: it lets us notice the breadth before the nearby decoration.'],
 '06':['Why assemble a new game world with models from older projects first? Even an unfinished-looking world could answer important questions.',
 'Try walking through the narrow demonstration doorway. We can discover that it is too narrow before polishing the walls. Testing while the structure is easy to change reduces later rework.',
 'The Elden Ring team used existing resources to evaluate field scale, production effort, features and memory. Temporary models provided a playable space early, rather than replacing the final appearance.',
 'Widen the doorway, follow the same route again, and add detail after passage works. This doorway is our explanatory example. A prototype is a tool for discovering what needs to be built.'],
 '15':['Why place some flowers individually when making this enormous flower field? Would using one method everywhere not be simpler?',
 'Placing every flower by hand is expensive. Filling space without regard to composition can obscure a path or an important view. Broad coverage and carefully placed details have different jobs.',
 'For important Cerulean Coast views, luminous flowers were placed by hand. Distant flower fields also used hand-painted textures with carefully adjusted density and brightness.',
 'Move the flowers covering our demonstration path toward its edges, and the direction becomes visible. Compare the nearby flowers with the distant field too. Work is concentrated where its placement and viewing distance matter.'],
 '16':['A destination looks clear from one position but disappears after a step. Is one attractive screenshot enough to evaluate a game landscape?',
 'Walking along our path reveals a foreground pillar hiding the distant tower. Checking only the starting view missed that obstruction. Move the pillar and repeat the same route.',
 'Elden Ring environment artists reviewed composition at important viewpoints. What is visible at an entrance or a place where a direction is chosen affects how the space is read.',
 'After moving the pillar, the tower outline remains visible longer during the walk. Occlusion is not always bad. Decide what matters at a particular moment and verify it while moving.'],
 '34':['The first blessing fragments in the expansion became more helpful after an update. Why does the amount gained early matter, as well as the maximum?',
 'Compare the same early level in two illustrative curves. If that level grants a larger increase, the same amount of early exploration provides more preparation for battle.',
 'The official update increased attack and damage negation in the first half of Scadutree Blessing levels, then made later growth more gradual. The final level also became slightly stronger.',
 'The diagram illustrates the direction of the change, not measured game values. Check both the early increases and the final level. Balance depends on how help is distributed along the progression, not just its maximum.']}
KO34=['확장팩에서 처음 얻는 가호가 더 크게 도와주도록 바뀌었습니다. 마지막에 얼마나 강해지는지뿐 아니라, 초반 상승폭도 왜 중요할까요?',
 '시연의 두 그래프에서 같은 초반 단계를 비교해 봅시다. 그 단계에서 오르는 폭이 크면, 초반에 같은 만큼 탐험해도 전투를 준비하는 데 받는 도움이 커집니다.',
 '공식 조정은 그림자 나무의 가호에서 앞쪽 단계의 공격력과 피해 경감을 높이고, 뒤쪽 증가는 더 완만하게 바꿨습니다. 마지막 단계의 효과도 조금 높였습니다.',
 '이 그림은 실제 게임 수치가 아니라 조정 방향을 보여 줍니다. 초반 상승폭과 마지막 단계를 따로 확인해 보세요. 보상은 최대치뿐 아니라, 올라가는 과정에서 도움을 어떻게 나눠 주는지도 중요합니다.']
RANGES={'05':[(0,271,290),(2,497,508)],'06':[(0,1629,1637),(2,820,840)],
 '15':[(0,21,33),(2,268,293)],'16':[(0,269,289),(2,497,508)],'34':[(0,17,30),(2,151,176)]}
NOTES={'05':'Moving horse, low grass and grave markers leave the far arch visible. 509.6 map and 512.7 transition excluded.',
 '06':'Finished-game rock traverse and cave exit demonstrate spatial constraints. They are not the prototype or an asset-reuse comparison.',
 '15':'Tree-framed entry opens onto blue flowers; later travel brings individual glowing flowers beside the path into view. No claim of observing the editor.',
 '16':'Foreground pillar overlaps and then reveals the far arch during movement. Menu at509.6 and transition at512.7 excluded.',
 '34':'Fragment and blessing-help panel are visibly obtained at17–30. A different recording shows combat at151–176. Neither measures the patch benefit or establishes equal equipment.'}
def pin(p):return dict(path=str(p),sha256=sha(p))
def main():
    manifest=Path('C:/Users/1/Videos/YamyamProduction/elden-ring-development-36/pc-review-v10/manifest.json')
    data=read(manifest);drafts={r['id']:r for r in read(HERE/'plan.json')['episodes']}
    reference=Path('D:/Github/VideoEditing/projects/shorts-mario-one-action/production/local/tts-execution.json')
    layout=['https://cedil.cesa.or.jp/cedil_sessions/view/3156.html','https://www.4gamer.net/games/866/G086614/20250724066/','https://cgworld.jp/article/202508-cedec-eldenring.html']
    for n in EN:
        ko=list(drafts[n]['narrationKo'])
        if n=='15':ko[2]='청해안의 중요한 구도에서는 빛나는 꽃을 직접 배치했습니다. 멀리 있는 꽃밭은 손으로 그린 텍스처로 밀도와 밝기를 맞췄죠.'
        if n=='34':ko=KO34
        rec=data['episodes'][n]['record'];sources=[];observations=[]
        for idx,a,b in RANGES[n]:
            path=Path(rec['formatSources'][idx]['source']);assert sha(path)==rec['cuts'][idx]['sha256']
            if path not in sources:sources.append(path)
            observations.append({**{k:rec['cuts'][idx][k] for k in ['url','recorder','rights','sha256','size']},'path':str(path),'start':a,'end':b})
        urls=layout if n in ['05','15','16'] else (['https://www.too.com/dc/report/elden_ring_220708/'] if n=='06' else ['https://en.bandainamcoent.eu/elden-ring/news/elden-ring-calibration-update-1122'])
        sheet=WORK/'sources'/f'extended-{n}-reference.jpg';assert sheet.exists()
        item=dict(id=n,version='causal-v11',scriptLockedForVoice=True,narrationKo=ko,narrationEn=EN[n],
          claimEvidence=[dict(url=u,reviewed='2026-11-28',scope=('Official abstract plus on-site first-hand presentation reports; full slides require login and were not downloaded.' if n in ['05','15','16'] else 'Official organizer speaker transcript.' if n=='06' else 'Official historical 1.12.2 patch notes; no invented numeric curve or developer intention.')) for u in urls],
          footageEvidence=dict(retainedRights=observations,sourceManifest=str(manifest),sampleReview=NOTES[n],contactSheet=pin(sheet),continuousPlaybackReviewed=False,audioUse='video only',timedFinalSelection='pending narration timing within these observed ranges'),
          demonstration=dict(nativeProject='unity/VideoEditing',sceneMethod={'05':'VistaV8','06':'CausalPrototype','15':'CausalFlowers','16':'CausalLandmark','34':'CausalBlessingCurve'}[n],classification='independent principle model; not original game implementation',finalVoiceTimedCapture=False),
          inputs=[pin(p) for p in sources+[manifest,reference,HERE/'reference-adoption-20261128.json']],humanReview='pending',finalRenderComplete=False)
        p=HERE/'locked'/f'{n}.json'
        if p.exists():assert read(p)==item
        else:save(p,item)
        print(n,sha(p))
if __name__=='__main__':main()
