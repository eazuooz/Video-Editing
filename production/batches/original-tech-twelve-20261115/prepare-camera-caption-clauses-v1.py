"""Exact Korean clauses and original, meaning-matched English subtitles.

No timing is assigned. Only separately reviewed whole ASR word boundaries may
anchor these clauses. English word order is never converted to time by ratio.
"""
from pathlib import Path
import hashlib,json,importlib.util
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
P=ROOT/'projects/shorts-mario64-lakitu-camera'
PAIRS=[
 [
  ['마리오 육십사에는','Super Mario 64 has a camera operator:'],
  ['카메라를 든 쥬게무가 나옵니다.','Lakitu, carrying a camera.'],
  ['마리오를 움직이는 것과,','Moving Mario'],
  ['그를 찍는 자리를 바꾸는 것은 다른 조작이죠.','and changing the filming position are separate controls.'],
  ['가까이 살펴보고, 주위를 돌고,','We will look closely, circle around,'],
  ['멀리서 보는 방법을 순서대로 보겠습니다.','and pull back, in that order.'],
 ],
 [
  ['쥬게무는 마리오를 따라가며 촬영합니다.','Lakitu follows and films Mario.'],
  ['플레이어는 씨 버튼으로','The player uses the C buttons'],
  ['그 촬영 위치와 방향을 조절합니다.','to adjust its position and direction.'],
  ['그래서 화면을 보는 자리를 뜻하는 시점도','So the viewpoint—where we see the scene from—'],
  ['직접 바꿀 수 있습니다.','is also under the player’s control.'],
 ],
 [
  ['주변이나 위쪽을 둘러보면','Looking around or upward'],
  ['길과 파워스타를 찾는 데 도움이 됩니다.','can help you find routes and Power Stars.'],
  ['마리오가 어디에 서 있는지와,','Think about where Mario stands'],
  ['카메라가 무엇을 향하는지를 나눠 생각하면 쉽습니다.','separately from what the camera points toward.'],
 ],
 [
  ['씨 위 버튼은 가까이 보는 시점입니다.','C-up enters a close view.'],
  ['여기서는 스틱으로 주변을 둘러봅니다.','The stick now looks around.'],
  ['에이, 비, 또는 씨 위를 제외한 씨 버튼으로','Press A, B, or a C button other than C-up'],
  ['이동 조작에 돌아옵니다.','to return to movement control.'],
 ],
 [
  ['씨 왼쪽과 오른쪽은','C-left and C-right'],
  ['마리오 주위를 도는 조작입니다.','move the camera around Mario.'],
  ['같은 자리에 선 마리오도','Mario can stand in the same spot'],
  ['다른 쪽에서 볼 수 있죠.','while you see him from another side.'],
  ['더 돌릴 수 없는 곳에서는','When the camera cannot go farther,'],
  ['경고음으로 한계를 알려 줍니다.','a buzz signals its limit.'],
 ],
 [
  ['씨 아래 버튼은 카메라를 뒤로 뺍니다.','C-down pulls the camera back.'],
  ['마리오는 작게 보이고','Mario looks smaller,'],
  ['주변 공간은 더 넓게 들어옵니다.','while more surroundings fit in view.'],
  ['가까이 보기, 주위를 돌기, 멀리 보기.','Look closely, circle around, and pull back.'],
  ['마리오 육십사에서는','In Super Mario 64,'],
  ['플레이어가 촬영자이기도 한 겁니다.','the player is also the cinematographer.'],
 ],
]
def main():
    source=P/'planning/narration-locked-v1.json';d=json.loads(source.read_text(encoding='utf8'));assert len(d['paragraphs'])==len(PAIRS)
    spec=importlib.util.spec_from_file_location('ot12_caption_geometry',HERE/'lockon-layout-v1.py');layout=importlib.util.module_from_spec(spec);spec.loader.exec_module(layout);f=layout.font(48)
    for p,pairs in zip(d['paragraphs'],PAIRS):
        assert ''.join(' '.join(a for a,b in pairs).split())==''.join(p['ko'].split()),p['id']
        for ko,en in pairs:layout.wrap(ko,f);layout.wrap(en,f)
    out=P/'planning/caption-clauses-v1.json';assert not out.exists();out.write_text(json.dumps(dict(schemaVersion=1,source=dict(path=str(source),sha256=hashlib.sha256(source.read_bytes()).hexdigest()),paragraphs=[dict(id=p['id'],clauses=pairs)for p,pairs in zip(d['paragraphs'],PAIRS)],englishRole='Original semantic subtitle translation; preserve every spoken claim, no character-ratio timing.',captionFontPixels=48,maximumLines=2,maximumWidth=800,timestampsAssigned=False,actualAsrWordAnchorsRequired=True,finalSubtitlesAccepted=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(P.name,'semantic clauses',sum(map(len,PAIRS)))
if __name__=='__main__':main()
