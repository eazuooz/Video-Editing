"""Meaning-first bilingual clauses; only future reviewed ASR words set time."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
DATA={
'shorts-returnal-particle-tentacles': '''
리터널의 적은 || Enemies in Returnal have
촉수가 살아 있는 것처럼 꿈틀거립니다. || tentacles that writhe as if alive.
개발진은 이런 표현에 || For this kind of effect, the developers used
서로 연결된 입자를 사용했습니다. || particles connected to one another.
점들이 관계를 맺고, 지난 움직임을 따라가고, || Points form relationships and follow past motion,
그 위에 굵기 있는 표면이 만들어지는 과정을 보겠습니다. || then a surface with thickness is built around them.

처음 생각한 방법은 || The initial idea was
뼈대마다 물리 몸체를 연결하는 것이었습니다. || to attach a physical body to each bone.
하지만 비용과 표현 조절에 어려움이 있었습니다. || Cost and artistic control proved difficult.
개발진은 지피유에서 동작하는 이펙트 도구 안에서, || Within their GPU-based effects tool,
부모와 자식 관계를 가진 입자 구조를 발전시켰습니다. || they developed parent–child particle structures.

각 자식은 부모 하나를 참조하고, || Each child references one parent,
부모에는 여러 자식이 달릴 수 있습니다. || while a parent can have multiple children.
여기서 자식이 읽는 것은 || What the child reads here
부모의 한 프레임 전 정보입니다. || is its parent’s data from one frame earlier.
부모가 먼저 움직이고 || The parent moves first,
뒤쪽 점들이 뒤따르는 차이가 || and later points follow with a delay,
유기적인 움직임을 만듭니다. || producing organic motion.

점의 움직임만으로는 || Moving points alone
굵은 촉수가 보이지 않습니다. || do not make a thick tentacle visible.
처음의 납작한 띠 대신, || Instead of the initial flat strips,
점들을 따라 부드러운 곡선을 만들고 || smooth curves were built along the points
원통형 표면을 그렸습니다. || and rendered as cylindrical surfaces.
옆에서 보거나 그림자가 생겨도 || Even from the side or in shadow,
부피가 읽히도록 한 겁니다. || their volume remains readable.

표면이 뒤틀리면 || If the surface twists,
빛도 이상하게 돌 수 있습니다. || its lighting can rotate strangely too.
그래서 표면이 향하는 방향을 || So the surface orientation
부모 쪽에서 이어 받고 다듬는 || is inherited and refined from the parent
별도 계산을 더했습니다. || using an additional calculation.
움직임을 만드는 점과, || The motion-driving points
그 위에 안정적인 표면을 만드는 작업은 함께 필요합니다. || and a stable surface built around them are both needed.

이 움직임은 || This motion also connects to
적이 공격을 준비할 때 같은 상태 표현에도 연결됩니다. || states such as an enemy preparing an attack.
아티스트와 애니메이터가 || Artists and animators
타이밍을 맞춰 행동을 읽게 한 거죠. || coordinate timing to make the action readable.
부모의 지난 움직임을 잇는 입자와, || Particles following a parent’s past motion
그 둘레를 감싼 표면이 || and the surface wrapped around them
촉수의 생동감을 함께 만듭니다. || bring the tentacle to life together.
''',
'shorts-ratchet-dimension-streaming': '''
라쳇 앤 클랭크의 차원 전환은 || Dimensional transitions in Ratchet & Clank
화면 속 세계가 크게 바뀌는 순간입니다. || can transform the world on screen.
위치만 바꾼다고 끝나지는 않죠. || Changing position alone is not enough.
피시판 개발진의 설명을 따라, || Following the PC developers’ explanation,
다음 장면의 자료를 읽고 풀어 쓰는 과정을 보겠습니다. || we will follow the reading and unpacking of scene data.

게임에는 모델과 텍스처 같은 자료가 필요합니다. || Games need data such as models and textures.
압축해서 저장했다면 || If it is stored in compressed form,
읽은 뒤 풀어야 합니다. || it must be decompressed after reading.
피시판은 다이렉트스토리지를 사용하고, || The PC version uses DirectStorage,
높은 그래픽 설정에서는 || and at higher graphics settings,
지피유 압축 해제로 자료 공급을 돕습니다. || GPU decompression helps supply the data.

보통 중앙 처리 장치인 씨피유가 맡던 압축 해제를 || Decompression, traditionally handled by the CPU,
그래픽 장치가 도울 수 있다는 뜻입니다. || can be assisted by the graphics processor.
배경에서 자료가 준비되어야, || Data needs to be prepared in the background
차원을 넘은 뒤 화면을 만드는 데 쓸 수 있죠. || so it is available after crossing dimensions.
읽기와 압축 해제는 구별되는 단계입니다. || Reading and decompression are distinct stages.

모든 피시의 저장 속도는 같지 않습니다. || Storage speeds differ between PCs.
개발진은 실제로 공급할 수 있는 대역폭을 살피며 || The developers examine available bandwidth
스트리밍 방식을 조절한다고 설명합니다. || and adapt the streaming strategy.
빨리 읽는 장치와 느린 장치에 || Fast and slow storage devices
같은 공급 계획을 무조건 적용하지 않는 겁니다. || do not always receive the same data-supply plan.

이 기능은 빠른 저장 장치만을 위한 것은 아닙니다. || This feature is not only for fast storage.
공식 피시 안내는 하드디스크도 지원하고, || The official PC guidance also supports HDDs,
더 좋은 경험을 위해 에스에스디를 권장합니다. || recommending an SSD for a better experience.
차원 전환의 뒤에서는 || Behind a dimensional transition,
자료 읽기, 압축 해제, || reading and decompression
속도에 맞춘 공급이 함께 움직이는 겁니다. || work with a supply plan adapted to storage speed.
'''
}
def main():
    spec=importlib.util.spec_from_file_location('ot12_rr_caption_writer',HERE/'prepare-camera-caption-clauses-v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    for slug,text in DATA.items():
        m.P=m.ROOT/'projects'/slug;m.PAIRS=[[line.split(' || ',1)for line in block.splitlines()]for block in text.strip().split('\n\n')];m.main()
if __name__=='__main__':main()
