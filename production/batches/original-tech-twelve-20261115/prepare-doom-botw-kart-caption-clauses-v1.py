"""Meaning-paired captions for the last three selected lessons. No timing."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
DATA={
'shorts-doom-push-forward-healing': '''
둠에서 체력이 줄면 || When health runs low in DOOM,
적에게 더 가까이 가야 할 때가 있습니다. || getting closer to an enemy can be the answer.
개발진은 숨어서 기다리기보다 || The developers wanted reasons to engage,
전투에 참여할 이유를 만들고 싶었습니다. || rather than hide and wait.
회복이 접근과 공격으로 이어지는 순환을 보겠습니다. || Let’s follow how recovery encourages approach and attack.

적을 공격하면 비틀거리며 || Attacking can make an enemy stagger,
마무리할 기회가 생깁니다. || opening a finishing opportunity.
이 상태가 스태거입니다. || This state is called stagger.
영원히 멈춰 있는 것은 아니어서, || It does not last forever.
기회를 놓치면 적이 다시 전투에 돌아올 수 있습니다. || Miss the opportunity and the enemy may resume fighting.
가까이 갈지 판단할 시간이 생기는 거죠. || You have a moment to decide whether to close in.

가까이서 글로리 킬로 마무리하면 || Finish at close range with a Glory Kill
자원 보상을 얻습니다. || and receive resource rewards.
공격에 쓸 도구만 주는 것이 아니라, || This provides more than a tool for attacking:
위험을 감수하고 다가갈 이유도 주는 겁니다. || it gives a reason to take the risk of approaching.
체력이 낮을 때 필요한 회복을 얻는 구조가 || Getting needed recovery when health is low
전진을 돕습니다. || helps encourage forward movement.

발표는 체력이 낮을 때 || The presentation also explains how low health
회복 보상을 조절하는 방법도 설명합니다. || can affect the recovery reward.
다만 탄약까지 똑같이 따라가는 것은 아닙니다. || Ammunition does not follow an identical rule.
어떤 자원을 주고 얼마나 줄지는 || Reward type and quantity
구별해서 설계해야, || need to be designed separately,
한 행동만 계속 반복하는 해법이 되지 않습니다. || so one repeated action does not solve everything.

탄약이 부족할 때는 || When ammunition runs short,
전기톱이 큰 보상을 주는 역할을 합니다. || the chainsaw provides a large resource reward.
대신 연료가 필요하죠. || It costs fuel in return.
적에게서 자원을 얻되 || Enemies become a source of resources,
그 행동에도 비용을 두어, || while the action itself still has a cost,
공격과 회복이 한쪽으로만 굴러가지 않게 한 겁니다. || keeping attack and recovery from becoming one-sided.

비틀거림을 만들고, || Create a stagger opportunity,
다가가 마무리하고, || close in for a finish,
얻은 자원으로 다시 싸웁니다. || and use the rewards to keep fighting.
둠은 회복을 전투 바깥의 쉬는 시간에만 두지 않았습니다. || DOOM makes recovery part of combat itself.
살아남기 위해 앞으로 나가도록 || To survive, move forward:
보상을 연결한 겁니다. || the rewards support that behavior.
''',
'shorts-botw-chemistry-rules': '''
야생의 숨결에서는 || In Breath of the Wild,
풀에 불을 붙였다가 비로 끌 수 있습니다. || grass can catch fire and rain can put it out.
이런 조합을 장면마다 따로 준비했을까요? || Was every combination scripted scene by scene?
개발진은 물체가 움직이는 계산과, || The developers separated physical movement
불붙음 같은 상태가 바뀌는 계산을 구별했습니다. || from changes of state, such as catching fire.

상태를 다루는 쪽에서는 || The state system distinguishes
원소와 물질을 나눕니다. || elements from materials.
불 같은 원소와 나무 같은 물질이 || Elements such as fire and materials such as wood
어떤 관계를 갖는지 정하는 거죠. || are assigned relationships.
이름은 화학 엔진이지만, || Although it is called a chemistry engine,
현실의 모든 화학을 계산하겠다는 뜻은 아닙니다. || it does not simulate all real-world chemistry.

첫 번째 규칙은 || The first rule:
원소가 물질의 상태를 바꾼다는 겁니다. || elements change the state of materials.
불이 나무에 닿으면 || Fire touching wood
불붙은 상태가 되는 식입니다. || can put it into a burning state.
이 관계를 규칙으로 두면, || Express this relationship as a rule,
정해진 장소 하나만을 위한 연출보다 || rather than an effect for one specific location,
여러 곳에 적용하기 쉽습니다. || and it becomes easier to apply elsewhere.

두 번째는 || The second rule:
원소가 다른 원소의 상태도 바꿀 수 있다는 겁니다. || elements can also change other elements’ states.
물과 불의 관계를 || The relationship between water and fire
같은 틀 안에서 다룹니다. || is handled within the same framework.
불붙은 물체만 따로 검사하는 데서 더 나아가, || Beyond checking only burning objects,
효과끼리도 연결되는 구조입니다. || effects themselves can interact.

세 번째는 || The third rule:
물질끼리는 이 화학 규칙에서 || within this chemistry model, materials
서로의 상태를 직접 바꾸지 않는다는 겁니다. || do not directly change one another’s states.
이것은 물체가 서로 부딪힐 수 없다는 뜻이 아닙니다. || This does not mean physical collisions are impossible.
움직임의 물리와 상태 변화의 규칙을 || Movement physics and state-change rules
구별하는 설명입니다. || are being distinguished.

이제 비를 물 원소로 보면, || Treat rain as the water element,
이미 만든 물과 불의 관계를 다시 쓸 수 있습니다. || and the existing water–fire relationship can be reused.
전기와 바람도 || Electricity and wind also belong
이 게임의 단순한 상태 모형 안에 들어옵니다. || within the game’s simplified state model.
서로 연결할 수 있는 규칙이 늘면서, || As more rules can be combined,
플레이어가 시험할 조합도 많아집니다. || players gain more combinations to try.

움직임은 물리로, || Use physics for movement
상태 변화는 공통 규칙으로 연결합니다. || and shared rules for state changes.
그래서 불을 붙이고 비로 끄는 행동이 || Setting a fire and extinguishing it with rain
같은 세계의 약속처럼 느껴지는 거죠. || feel like consistent rules of one world.
중요한 것은 이벤트를 많이 만드는 것뿐 아니라, || The goal is more than producing many events:
다시 조합할 수 있는 관계를 만드는 겁니다. || create relationships that can be recombined.
''',
'shorts-mariokart8-spin-boost': '''
마리오 카트 에이트에서는 || In Mario Kart 8,
부딪히는 것이 가속 기회가 될 때가 있습니다. || a collision can become a chance to accelerate.
조건은 반중력 구간입니다. || The condition is an anti-gravity section.
어디서 무엇과 부딪혔는지가 중요하니, || Where you collide, and with what, both matter.
모든 충돌이 빨라지는 것은 아닙니다. || Not every collision gives a speed boost.

반중력 구간에서는 || In anti-gravity sections,
벽이나 거꾸로 된 길도 달립니다. || racers can drive on walls or upside-down roads.
길의 방향만 바뀌는 것이 아니라, || The road’s orientation is not the only change:
접촉의 의미도 달라집니다. || the meaning of contact changes too.
평소에는 피하려던 다른 카트가 || Another kart you would normally avoid
여기서는 이용할 대상이 될 수 있죠. || can become something useful here.

닌텐도는 반중력 상태에서 || Nintendo introduced a move where, in anti-gravity,
다른 카트와 부딪히면 || colliding with another kart
회전하며 속도를 얻는 스핀 터보를 소개했습니다. || makes you spin and gain speed: Spin Turbo.
상대 가까이 다가가는 행동에 || Moving closer to another racer
보상이 생기는 겁니다. || now offers a reward.
다만 이 설명은 || Remember that this explanation
반중력 상태라는 조건 안에서 봐야 합니다. || is conditional on anti-gravity mode.

일부 장애물과의 접촉도 같은 기회가 됩니다. || Certain obstacles offer the same opportunity.
여기서 일부라는 말이 중요합니다. || “Certain” is important here.
길의 모든 벽과 장식물을 || Every wall and decoration
가속 장치라고 생각하면 안 됩니다. || should not be treated as a boost device.
실제로 이 효과를 주는 대상을 보고 || Identify objects that actually give this effect
경로를 고르는 거죠. || and plan your route around them.

반중력 구간, 정해진 접촉 대상, 회전 가속. || Anti-gravity, eligible contact, a spinning boost.
이 조건들이 모이면 || With those conditions combined,
충돌이 단순한 실수에서 선택지가 됩니다. || a collision becomes a choice, rather than just a mistake.
마리오 카트 에이트는 길을 비트는 것과 함께, || Along with twisting the road, Mario Kart 8
다른 카트에 다가갈 이유도 바꾼 겁니다. || changes why you might approach another racer.
'''
}
def main():
    spec=importlib.util.spec_from_file_location('ot12_dbk_caption_writer',HERE/'prepare-camera-caption-clauses-v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    for slug,text in DATA.items():
        m.P=m.ROOT/'projects'/slug;m.PAIRS=[[line.split(' || ',1)for line in block.splitlines()]for block in text.strip().split('\n\n')];m.main()
if __name__=='__main__':main()
