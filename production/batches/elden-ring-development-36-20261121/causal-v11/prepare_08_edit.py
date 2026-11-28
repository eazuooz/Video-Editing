"""Bind the revised Rykard lesson to measured voice and whole-word captions."""
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from make_approved_voice_v2 import read,save,sha
import render_established_format_v6 as film


def normalized(text):
    return re.sub('[^가-힣a-z0-9]','',text.lower())


def main():
    lock_path=HERE/'locked/08-r2.json';lock=read(lock_path)
    root=Path('D:/YamyamProduction/elden-ring-development-36-causal-v11/voice/08')/sha(lock_path)[:12]
    timing=read(HERE/'timing-08-r2.json');lengths=timing['allSceneFrames']
    ends=[[2,5,9,11,13,18],[4,8,10,15,18,22,26,29],
          [5,9,14,18,21,25],[3,6,9,12,16,19,23,27,31]]
    paragraphs=[];pins=[dict(path=str(lock_path),sha256=sha(lock_path)),
                         dict(path=str(HERE/'timing-08-r2.json'),sha256=sha(HERE/'timing-08-r2.json'))]
    position=0
    for take,script in enumerate(lock['narrationKo']):
        review_path=root/'voice-qa-source'/f'08-{take}.json';review=read(review_path)
        words=review['timestamped'];assert review['expected']==script
        parts=[normalized(w['text']) for w in words]
        spelling=[]
        if take==2:
            assert words[20]['text'].strip()=='8에는'
            # Korean numeral 8 and 팔 have identical spoken readings. Preserve the raw ASR;
            # use the entire positive word interval, never an interpolated internal boundary.
            parts[20]='팔에는'
            spelling=[dict(wordIndex=20,recognized='8에는',caption='팔에는',
                           reason='Numeral eight and the Korean word for arm share the same reading; arm context.',
                           rawAsrUnchanged=True)]
        assert ''.join(parts)==normalized(script)
        clean_positions=[i for i,c in enumerate(script) if normalized(c)]
        cumulative=[];total=0
        for p in parts:total+=len(p);cumulative.append(total)
        cues=[];first=0;char_start=0
        for last in ends[take]:
            char_end=clean_positions[cumulative[last]-1]+1
            while char_end<len(script) and not normalized(script[char_end]):char_end+=1
            text=script[char_start:char_end].strip()
            start=position+round((.13+words[first]['start'])*60)
            end=position+round((.13+words[last]['end'])*60)
            assert start<end
            cues.append(dict(text=text,startFrame=start,endFrame=end,firstWord=first,lastWord=last))
            first=last+1;char_start=char_end
        assert first==len(words) and normalized(' '.join(c['text'] for c in cues))==normalized(script)
        paragraphs.append(dict(episode='08',take=take,cues=cues,asrSpellingReview=spelling))
        pins.append(dict(path=str(review_path),sha256=sha(review_path)))
        position+=lengths[take]
    source=Path(lock['inputs'][0]['path']);assert sha(source)==lock['inputs'][0]['sha256']
    pins.append(dict(path=str(source),sha256=sha(source)))
    plan=dict(version='causal-v11',episode='08',lock=str(lock_path),voiceOutput=str(root),
              paragraphs=paragraphs,sceneFrames=lengths,appendixFrames=600,
              gameplay=[dict(index=0,path=str(source),start=134,frames=lengths[0]),
                        dict(index=2,path=str(source),start=180,frames=lengths[2]),
                        dict(index=4,path=str(source),start=210,frames=600)],
              nativeTiming=str(HERE/'timing-08-r2.json'),inputs=pins,
              selectionReview=dict(sampleSheet='D:/YamyamProduction/elden-ring-development-36-causal-v11/sources/rykard-final-selection.jpg',
                  opening='Sword extraction, small arms on blade, then close view; flames briefly obscure blade.',
                  appendix='Continuous 210–220 s combat: sword raised and swept, body turns; fire remains visible.',
                  sampleReview=True,continuousPlayback=False),
              phases={'1':dict(seconds=[0,2.63,9.61],labels=['팔 하나의 뼈대 설정','팔이 늘면 설정도 늘어남','움직임을 데이터로 저장']),
                      '3':dict(seconds=[0,3.05,6.01],labels=['세 시점의 점 위치 저장','지금 시간의 데이터를 읽기','저장된 위치로 표면 재생'])},
              finalEpisodeComplete=False,humanReview='pending')
    save(HERE/'edit-08-r2.json',plan)
    print(f'08: {sum(map(lambda p:len(p["cues"]),paragraphs))} whole-word caption cues; {sum(lengths)+600} frames including requested combat appendix.')


if __name__=='__main__':main()
