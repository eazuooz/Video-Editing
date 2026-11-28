"""Revise two ambiguous passages; preserve all unaffected approved-speaker PCM."""
from copy import deepcopy
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha
WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11/voice')

def main():
    edits={
     '09':(0,'이 성에서는 넓은 곳을 지나 좁은 통로로 들어가면 걷는 방식까지 달라집니다. 장식이 달라져서일까요? 먼저 보이는 정보를 비교해 봅시다.',
           'In this castle, moving from an open area into a narrow passage changes how you move. Is this just different decoration? First, compare the information you can see.',
           'The proper name remained ambiguous in an independent full-sentence transcription. Use the castle already identified in the title and footage, preserving the causal question.'),
     '12':(1,'탑에 올라 옆 탑을 봅시다. 저곳에 가고 싶다면 두 탑을 잇는 길을 더해 볼 수 있죠. 실제 제작진도 성을 여러 번 플레이하며 탑 사이의 새 길을 검토했습니다.',
           'Climb the tower and look at the next one. Wanting to reach it can inspire a connecting route. The actual team also repeatedly played through the castle and considered a new route between towers.',
           'Independent context retained the proper-name/proposal ambiguity and a -9.14 dB second-half speech median. Make the same supported example shorter and concrete without gain-shaping the raw speech.')}
    for n,(take,ko,en,why) in edits.items():
        prior_path=HERE/'locked'/f'{n}.json';prior=read(prior_path);root=WORK/n/sha(prior_path)[:12]
        item=deepcopy(prior);item['narrationKo'][take]=ko;item['narrationEn'][take]=en
        item['revisionReason']=why;item['priorLockSha256']=sha(prior_path)
        item['reuseUnchangedVoice']=[]
        for i in range(4):
            if i==take:continue
            wav=root/'approved-voice'/f'{n}-{i}.wav'
            item['reuseUnchangedVoice'].append(dict(take=i,lock=str(prior_path),lockSha256=sha(prior_path),wav=str(wav),sha256=sha(wav)))
        dest=HERE/'locked'/f'{n}-r2.json'
        if dest.exists():assert read(dest)==item
        else:save(dest,item)
        print(n,sha(dest))

if __name__=='__main__':main()
