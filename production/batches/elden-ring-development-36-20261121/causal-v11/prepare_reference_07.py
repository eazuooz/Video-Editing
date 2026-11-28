"""A five-cut reference edit: natural voice timeline and separate picture beats."""
from pathlib import Path
import copy, math, sys, wave
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha
WORK=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11')
def pin(p):return dict(path=str(p),sha256=sha(p))
def main():
    prior=HERE/'edit-07.json';old=read(prior);lock=Path(old['lock']);root=Path(old['voiceOutput'])
    lengths=[];reviews=[];pins=[pin(prior),pin(lock),pin(HERE/'reference-adoption-20261128.json')]
    for i in range(len(read(lock)['narrationKo'])):
        wav=root/'approved-voice'/f'07-{i}.wav';q=root/'voice-qa-source'/f'07-{i}.json'
        review=read(q);assert review['sha256']==sha(wav)
        with wave.open(str(wav),'rb') as f:seconds=f.getnframes()/f.getframerate()
        lengths.append(math.ceil((seconds+.38)*60));reviews.append(review);pins.extend([pin(wav),pin(q)])
    # At most one frame of parity rounding, never pair padding or speech speed changes.
    if sum(lengths)%2:lengths[-1]+=1
    offsets=[sum(lengths[:i]) for i in range(len(lengths))]
    paragraphs=copy.deepcopy(old['paragraphs'])
    for i,p in enumerate(paragraphs):
        delta=offsets[i]-sum(old['sceneFrames'][:i])
        for cue in p['cues']:
            cue['startFrame']+=delta;cue['endFrame']+=delta
            assert offsets[i]<=cue['startFrame']<cue['endFrame']<=offsets[i]+lengths[i]
    end_verify=offsets[3]+round((.13+reviews[3]['timestamped'][13]['end']+.10)*60)
    native1=lengths[1];native3=sum(lengths)//2-native1
    start_verify=end_verify-native3
    assert offsets[2]<start_verify<offsets[3]<end_verify<sum(lengths)
    starts=[0,offsets[1],offsets[2],start_verify,end_verify,sum(lengths)]
    source=old['gameplay'][0];path=Path(source['path']);assert sha(path)==source['sha256'];pins.append(pin(path))
    labels=['왜 지형 제작 방식을 바꿨을까?','높이 수정과 착지 위치','완성된 길에서 발 디딤을 확인','같은 점프 · 착지면만 변경','게임에 필요한 땅을 고치는 방식']
    observations=['91초에서 출발해96초 낙하·97초 지붕 착지까지 관찰','격자 높이 수정 후 같은 착지 위치 비교','224초 이후 탑과 난간 이동: 메시 편집 녹화가 아님','같은 점프 실패→면 이동→같은 점프 재확인','235초 이후 발밑과 아래 지형을 보는 이동']
    cuts=[]
    for i,(a,b) in enumerate(zip(starts,starts[1:])):
        row=dict(id=f'07-beat-{i}',startFrame=a,endFrame=b,frames=b-a,label=labels[i],
          role=['question','problem-and-constraint','solution-context','controlled-verification','application-and-payoff'][i],
          observation=observations[i],kind='unity' if i in (1,3) else 'gameplay',appendix=False)
        if row['kind']=='unity':row.update(nativeId=f'07-{i}')
        else:
            start={0:91,2:224,4:235}[i]
            assert start+(b-a)/60<={0:108,2:243,4:243}[i]
            row.update(path=str(path),sha256=sha(path),sourceStart=start,sourceEnd=start+(b-a)/60)
        cuts.append(row)
    original_timing=read(Path(old['nativeTiming']));first=copy.deepcopy(original_timing['cuts'][0]);first['frames']=native1
    assert first['speechEndFrame']<native1
    # Same-camera jump demonstration spans the preceding landing example and the verification speech.
    speech0=(offsets[3]-start_verify)/60
    anchors=[(.13,0),(max(.25,speech0-.25),.34),(speech0+.13+2.38,.40),
             (speech0+.13+3.94,.57),(speech0+.13+4.10,.61),(speech0+.13+6.48,.92),(native3/60-.02,1)]
    assert all(a[0]<b[0] for a,b in zip(anchors,anchors[1:]))
    second=dict(id='07-3',episode=7,shot=3,frames=native3,speechStartFrame=8,speechEndFrame=native3-2,
      cueSeconds=[round(a,6) for a,b in anchors],cueProgress=[b for a,b in anchors],
      pilotFrames=[round(anchors[k][0]*60) for k in (1,3,5)])
    phases={'07-1':old['phases']['1'],'07-3':dict(seconds=[0,anchors[2][0],anchors[4][0]],
      labels=['수정 전: 같은 점프가 가장자리에 못 닿음','착지면의 모서리와 폭을 조정','수정 뒤: 같은 점프로 착지 확인'],
      description='독립 원리 모형 · 점프 경로 고정, 착지면만 변경')}
    timing=HERE/'timing-07-reference.json'
    save(timing,dict(version='causal-v11',voiceBoundariesVerified=True,cuts=[first,second],inputs=pins,
      anchorMethod='Positive reviewed ASR whole-word edges for changes and verification; picture cuts independent of takes.'))
    result=dict(version='reference-causal-demonstration-v1',episode='07',lock=str(lock),voiceOutput=str(root),
      voiceFrames=lengths,paragraphs=paragraphs,cuts=cuts,phases=phases,inputs=pins+[pin(timing)],
      nativeTiming=str(timing),bodyFrames=sum(lengths),appendixFrames=0,
      compactBodyTitle='엘든 링 · 지형 제작',voicePcmPreserved=True,
      ratio=dict(actualGameplay=sum(r['frames'] for r in cuts if r['kind']=='gameplay'),unity=sum(r['frames'] for r in cuts if r['kind']=='unity')),
      comprehensionReview='pending timed native and final moving review',finalEpisodeComplete=False)
    assert result['ratio']['actualGameplay']==result['ratio']['unity']
    save(HERE/'edit-07-reference.json',result)
    print(dict(seconds=sum(lengths)/60,voiceFrames=lengths,pictureCuts=len(cuts),ratio=result['ratio'],nativeFrames=[native1,native3]))
if __name__=='__main__':main()
