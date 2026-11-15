"""CPU semantic clause preparation. No speech timestamp interpolation."""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
PAIRS=[
 [
  ['저니의 사막은 몸을 움직이면 반짝입니다.','Journey’s dunes sparkle as you move.'],
  ['화면보다 작은 모래알까지','Even grains smaller than a pixel'],
  ['전부 입체로 만들지 않아도 이런 느낌을 낼 수 있죠.','do not all need individual3D geometry.'],
  ['개발진은 모래의 거친 결, 작은 반짝임, 넓은 빛을','The developers separated rough grain, tiny glints,'],
  ['나누어 다뤘습니다.','and broad highlights.'],
 ],
 [
  ['먼저 모래가 어느 방향을 향하는지','First, small patterns describe'],
  ['작은 무늬로 표현합니다.','which way the sand surface faces.'],
  ['이 방향을 노멀이라고 합니다.','That direction is called a normal.'],
  ['그런데 멀리서 쓰는 작은 텍스처에서는','But in smaller textures used at a distance,'],
  ['방향 차이가 뭉개집니다.','those directional differences blur together.'],
  ['저니는 이 작은 단계에서도 결이 남도록','Journey preserves grain at these smaller levels'],
  ['방향의 분포를 다듬었습니다.','by adjusting the distribution of directions.'],
 ],
 [
  ['그 위에 반짝임을 올립니다.','Tiny glints are added on top.'],
  ['뾰족한 반사광을 작은 결에 적용하면','Apply sharp highlights to small grain,'],
  ['정지 화면은 그럴듯합니다.','and a still image can look convincing.'],
  ['하지만 카메라가 움직일 때','But when the camera moves,'],
  ['밝은 점이 불안정하게 튈 수 있습니다.','bright points may flicker unstably.'],
  ['반짝임 자체와 거슬리는 깜빡임을','The intended sparkle and distracting flicker'],
  ['구별해야 하는 겁니다.','need to be distinguished.'],
 ],
 [
  ['개발진은 반짝임을 계산할 때','For the glint calculation,'],
  ['빛과 시선의 중간 방향 대신,','instead of the light–view halfway direction,'],
  ['표면과 보는 방향의 관계를 사용했습니다.','they used the surface–view relationship.'],
  ['카메라가 움직일 때 드러나는 작은 빛을','This adjusts the tiny lights revealed'],
  ['이렇게 조절한 거죠.','as the camera moves.'],
  ['발표에서도 이것을 정확한 물리 법칙으로','The presentation does not establish this'],
  ['증명한 것은 아닙니다.','as an exact physical law.'],
 ],
 [
  ['모래 언덕의 가장자리처럼','Near the edge of a sand dune,'],
  ['비스듬히 보이는 곳에서는','when we see the surface obliquely,'],
  ['무늬가 길고 크게 번질 수 있습니다.','the pattern can stretch and spread.'],
  ['이런 구간을 찾아','A mask identifies these regions'],
  ['반짝임의 적용을 줄이는 마스크를 씁니다.','and reduces the glint effect there.'],
  ['모든 곳에 같은 효과를 세게 넣는 대신,','Instead of applying it strongly everywhere,'],
  ['깨지는 곳을 따로 다루는 겁니다.','the problematic regions are handled separately.'],
 ],
 [
  ['마지막으로 사구에 넓게 흐르는 반사광이','Finally, broad highlights across the dunes'],
  ['큰 형태를 살립니다.','bring out their larger shapes.'],
  ['작은 결을 남기고, 시선에 따라 반짝이고,','Preserve grain, add view-related glints,'],
  ['문제 구간을 가리는 과정이 함께 작동하죠.','and mask problematic regions: these work together.'],
  ['그래서 저니의 모래는 입자 수보다','Journey’s sand is less about counting particles'],
  ['빛을 어떻게 나눠 표현했는지가 중요합니다.','than about separating and shaping the light.'],
 ],
]
def main():
    spec=importlib.util.spec_from_file_location('ot12_caption_clause_writer',HERE/'prepare-camera-caption-clauses-v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    m.P=m.ROOT/'projects/shorts-journey-sand-sparkle';m.PAIRS=PAIRS;m.main()
if __name__=='__main__':main()
