from pathlib import Path
import json
R=Path(__file__).resolve().parents[3]
P=Path(__file__).resolve().parents[1]
L=P/'production/local/v1'
L.mkdir(parents=True,exist_ok=True)
def save(p,obj):
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(R).as_posix()
rows=json.loads((P/'script/lesson.json').read_text(encoding='utf-8'))
aliases={'2026년 11월 3일':'이천이십육년 십일월 삼일','11월 3일':'십일월 삼일','2027년':'이천이십칠년','5.9':'오 점 구','C++':'씨 플러스 플러스','UEFN':'유 이 에프 엔','AI':'에이아이','MCP':'엠 씨 피','엔진 6':'엔진 식스','엔진 5':'엔진 파이브','버전 6':'버전 식스','6월':'유월','11월':'십일월'}
def spoken(text):
    for key,value in aliases.items():text=text.replace(key,value)
    return text
def display(text):return text.replace('버스로','Verse로').replace('버스와','Verse와').replace('버스를','Verse를').replace('한 배 반에서 네 배','1.5배에서 4배')
for lang in ['spoken-ko','ko','en']:
    save(P/f'script/narration.{lang}.json',{'scenes':[dict(id=f'{i:02}',title=title,lines=[en if lang=='en' else (spoken(ko) if lang=='spoken-ko' else display(ko))]) for i,(title,ko,en) in enumerate(rows,1)]})
(P/'script/대본.md').write_text('# 언리얼 엔진 6에서 블루프린트로 만든 문은 어떻게 될까?\n\n'+'\n\n'.join(display(r[1]) for r in rows)+'\n',encoding='utf-8')
m=json.loads((P/'project.json').read_text(encoding='utf-8'))
m.update(titles={'ko':'언리얼 엔진 6에서 블루프린트로 만든 문은 어떻게 될까?'},status='production',sources=['https://www.youtube.com/watch?v=i0wZCIhqveQ','https://www.youtube.com/watch?v=GgKuY5UlWU0'],paths=dict(script=rel(P/'script/narration.spoken-ko.json'),scriptEn=rel(P/'script/narration.en.json'),videoClean=rel(L/'clean.mp4'),videoBurnedCaptions=rel(L/'captioned.mp4'),captionsKo=rel(L/'captions.ko.srt'),captionsEn=rel(L/'captions.en.srt')),editing={'narrationPlacement':'continuous-across-example-and-explanation','ratioPolicy':'reality-check-no-ratio-v1'},tts={'language':'Korean','model':'qwen3-tts/models/Qwen3-TTS-12Hz-1.7B-Base','reference':'shared/voice-reference/reference-15-35s.wav','referenceText':'shared/voice-reference/reference-15-35s.ko.txt','outputDir':rel(L/'voice'),'filenameStem':'narration','renderMode':'scene','sceneGapSeconds':0.28,'tailRatioThreshold':0.07,'tailDecayMsThreshold':70,'maxRenderAttempts':3,'maxNewTokens':2048,'gpuMinimumFreeMiB':8192,'gpuProfileReason':'Single scene, batch one on the installed 16GB card. Existing shared guard serializes GPU work.'},delivery={'localStorageRoot':rel(L/'delivery')})
save(P/'project.json',m)
