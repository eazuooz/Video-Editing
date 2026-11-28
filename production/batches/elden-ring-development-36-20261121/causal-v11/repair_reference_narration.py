"""Clarify unresolved wording without altering the original speaker or prior PCM."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha
WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11/voice')
EDITS={
 '01':('01','01-r2',{
  1:('전부 올리면 멀리 있어 보지도 않는 땅까지 자리를 차지합니다. 반대로 다음 구역에 도착해서야 준비하면 풍경이 늦게 나타날 수 있죠. 그래서 이동할 주변 구역을 먼저 준비해야 합니다.',
     'Loading everything occupies memory with distant terrain you cannot see. If preparation begins only after you reach the next area, its landscape may appear late. Nearby areas need to be prepared before you reach them.'),
  2:('이 게임은 월드를 격자로 나누고 주변 데이터를 관리했습니다. 말은 빠르게 구역을 넘고 큰 적은 한 구역 밖까지 움직이니, 지금 발밑의 칸만 보면 충분하지 않습니다.',
     'The game divided its world into a grid to manage surrounding data. A horse crosses areas quickly and a large enemy can move beyond one cell, so considering only the cell beneath your feet is not enough.')}),
 '03':('03','03-r2',{
  3:('시연에서 색, 적용 범위, 법선 층을 따로 켜 보세요. 빛을 움직이면 법선을 더한 쪽은 밝고 어두운 부분이 달라집니다. 얼굴 모양을 실제로 파내지 않아도, 달라진 명암 때문에 상처가 패인 듯 보이는 겁니다.',
     'Turn on the color, coverage and normal layers separately in the demonstration. Move the light: the normal layer changes which parts are bright or dark. The face geometry is not carved out; the changed shading makes the scar appear recessed.')}),
 '12':('12-r2','12-r3',{
  2:('길을 직접 걸어 보고 새로운 길을 더하는 일은 사람이 합니다. 반면 오류가 난 곳이나 처리가 느린 곳을 찾는 검사는 자동화할 수 있죠. 제작진은 맵을 자동으로 돌아다니며 이런 문제와 발생 위치를 모았습니다.',
     'People walk the routes and propose new connections. Checks for errors or slow processing can instead be automated. The team used automated traversal to collect such problems together with their locations.'),
  3:('시연의 두 과정을 나눠 보세요. 사람은 탑을 잇는 길이 재미있는지 걸어 봅니다. 자동 검사는 같은 구간을 돌며 문제 위치를 표시합니다. 어디를 더 탐험하게 할지는 사람이 다듬고, 넓은 공간의 기술 문제는 반복 검사로 찾는 겁니다.',
     'Compare the two processes. A person walks the route between towers to judge exploration. An automated check revisits the area and marks problem locations. People refine where exploration should lead, while repeated tests find technical problems across the large space.')})}
def main():
    for n,(old,new,edits) in EDITS.items():
        path=HERE/'locked'/f'{old}.json';previous=read(path);item=deepcopy(previous);root=WORK/n/sha(path)[:12]
        for i,(ko,en) in edits.items():item['narrationKo'][i]=ko;item['narrationEn'][i]=en
        item.update(revisionReason='Clarify unresolved source/mix recognition using ordinary concrete wording; preserve causal meaning and original voice. No gain-shaping of the problematic raw audio.',
          priorLockSha256=sha(path),reuseUnchangedVoice=[])
        for i in range(len(item['narrationKo'])):
            if i in edits:continue
            wav=root/'approved-voice'/f'{n}-{i}.wav'
            item['reuseUnchangedVoice'].append(dict(take=i,lock=str(path),lockSha256=sha(path),wav=str(wav),sha256=sha(wav)))
        target=HERE/'locked'/f'{new}.json'
        if target.exists():assert read(target)==item
        else:save(target,item)
        print(n,sha(target),'new takes',list(edits))
if __name__=='__main__':main()
