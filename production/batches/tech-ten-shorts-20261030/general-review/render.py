import json
import sys
import time
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'feedback-nov05'))
import build as editor
MEDIA=editor.MEDIA
WORK=MEDIA/'general-review'
SPEC=editor.read(HERE/'nine.json')
DIRECTORY='final-reviewed-general-v3'
SOURCES={r['order']:r for r in editor.read(MEDIA/'delivery/review-ten-62f9b9be1224.json')['projects']}
EDITS={row['n']:row for row in SPEC['episodes']}

def pins(n, edit, scratch):
    folder=editor.ROOT/'shared/output/tech-nine-general-review/voice/chunks'
    log=WORK/'voice.log'
    while True:
        raw=log.read_bytes() if log.exists() else b''
        text=raw.decode('utf-16' if raw.startswith(b'\xff\xfe') else 'utf-8',errors='replace')
        result={}
        for j in range(1,len(edit['lines'])+1):
            key=f'{n:02}-{j:02}-scene'
            path=folder/(key+'.wav')
            if path.exists() and f'Rendered {key} (' in text:
                result[str(j)]={'path':str(path),'sha256':editor.sha(path)}
        if len(result)==len(edit['lines']):break
        if 'Traceback (most recent call last)' in text or 'capacity is insufficient' in text:
            raise RuntimeError('Speech synthesis must be resumed before these edits can be rendered.')
        time.sleep(3)
    editor.save(scratch/'voice-files.json',result)

def render(n):
    row=SOURCES[n];edit=EDITS[n];scratch=WORK/f'{n:02}'
    scratch.mkdir(parents=True,exist_ok=True)
    ranges={}
    description=row['description']
    draw=None
    if n in (5,10):
        from diagrams import render_window
        pins(n,edit,scratch)
        while not (WORK/'native-final/complete.txt').exists():time.sleep(2)
        ranges={5:(947,2154),10:(2568,2569)}
        draw=render_window
        new=('같은 지프와 기둥을 위와 옆에서 봅니다. 줄이 처졌다 펴지는 모습, 기둥 내부를 지나는 선분, 모서리에 닿아 돌아가는 경로를 Unity 단면 실험으로 비교합니다.'
             if n==5 else '같은 전차와 명령에서 시드만 바꾼 두 번의 Unity 실행을 비교합니다. 이어 이동 속도만 바꾼 실험으로, 옛 리플레이를 보려면 당시 실행 파일·게임 데이터·맵이 필요한 이유를 설명합니다.')
        desc_parts=description.split('\n\n',1)
        description=new+'\n\n'+desc_parts[-1]
    editor.build(n,source=row,edit=edit,scratch=scratch,directory=DIRECTORY,revision=SPEC['revision'],
                 body_ranges=ranges,draw_body=draw,description=description)
if __name__=='__main__':
    for value in sys.argv[1:]:render(int(value))
