"""Plan optional page-local animation without changing the approved narration."""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'planning/page-plan.json').read_text(encoding='utf-8'))
still={1,2,15,46,58,59,60,87,88}
focus={5,7,8,10,13,18,27,51,53,54,63,66,84,85}
corrections=set()
for line in (ROOT/'planning/corrections.ko.md').read_text(encoding='utf-8').splitlines():
    if not re.match(r'^\| \d',line): continue
    label=line.split('|')[1].strip()
    if not re.fullmatch(r'\d+(?:[·~]\d+)*',label): continue
    for part in label.split('·'):
        if '~' in part:
            a,b=map(int,part.split('~'));corrections.update(range(a,b+1))
        else: corrections.add(int(part))
entries=[]
for scene in data['scenes']:
    page=scene['sourcePage']
    mode='hold-with-pointer' if page in still else 'focused-highlight' if page in focus else 'stepwise-flow'
    entries.append({'page':page,'sceneId':scene['id'],'title':scene['title'],
        'mode':mode,'optional':True,'sourceVisualInstruction':scene['visual'],
        'requiresCorrectionBeforeFullRender':page in corrections,
        'status':'preview-excerpt-rendered' if page in {1,14,48} else 'planned-not-rendered',
        'synchronization':'actual-narration-word-cues-required',
        'constraints':['preserve-page-order','preserve-original-source','no-decoration-only-motion','no-caption-overlap']})
result={'scope':'88-page-production-plan-not-completed-render','pageCount':88,'bgm':'none-user-approved',
        'originalPdfIsUnmodified':True,'pages':entries}
(ROOT/'planning/animation-plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rows=['# 페이지별 선택적 애니메이션 계획','','모든 페이지를 원래 순서로 유지한다. 애니메이션은 설명에 도움이 될 때만 사용하며 원본을 대체하지 않는다. 현재 렌더 범위는 1·14·48쪽 발췌 프리뷰이며, 본편 전체가 완성된 상태가 아니다.','','| 페이지 | 방식 | 설명 포인트 | 본편 전 내용 수정 |','|---|---|---|---|']
names={'hold-with-pointer':'원본 유지·포인터','focused-highlight':'영역 강조·필요시 확대','stepwise-flow':'내레이션에 맞춘 단계·흐름 강조'}
for p in entries:
    rows.append(f"| {p['page']} | {names[p['mode']]} | {p['sourceVisualInstruction'].replace('|','/')} | {'보완표 반영 필요' if p['requiresCorrectionBeforeFullRender'] else '-'} |")
(ROOT/'planning/animation-plan.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
print(f"Planned {len(entries)} pages; {len(corrections)} pages require correction checks before full render.")
