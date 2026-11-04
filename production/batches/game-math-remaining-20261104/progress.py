"""Refresh only this finite batch's rows in the existing worklist."""
from pathlib import Path
import json
import re
import html

ROOT=Path(__file__).resolve().parents[3]
BATCH=Path(__file__).parent
data=json.loads((BATCH/'batch.json').read_text(encoding='utf-8'))
work=json.loads((ROOT/'shared/publishing/video-worklist.json').read_text(encoding='utf-8-sig'))
rows={r['id']:r for r in work['rows']}
lines=['# 남은 게임수학 13편 제작·검수표','','사용자 승인 범위: M21~M33 전체. 각 편의 로컬 완성본까지 제작하며 업로드·예약은 포함하지 않는다.','','| 편 | 강의 | 제작 단계 | 내부 검수 | 사용자 검수 |','|---|---|---|---|---|']
for item in data['items']:
    row=rows[item['id']]
    ready=item['localReviewReady']
    lines.append(f"| {item['id']} | {item['title']} | {row['productionStatus']} | {'완료' if ready else '미완료'} | {'확인 완료' if item['humanReviewed'] else '완성본 대기'} |")
lines+=['','완성본 제공 조건: 1080p60 clean·자막영상·한국어 SRT·영어 SRT, 실제 화면·음성 검사와 입력/출력 근거 기록.','현재 다른 작업의 프로세스·예약·기존 완성본은 보존한다.']
(BATCH/'progress.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
doc=ROOT/'docs/VIDEO_WORKLIST.md'
text=doc.read_text(encoding='utf-8-sig')
for item in data['items']:
    r=rows[item['id']]
    text=re.sub(r'^\| '+r['id']+r' \|.*$',f"| {r['id']} | {r['title']} | {'☑' if r['productionComplete'] else '☐'} {r['productionStatus']} | ☐ {r['reviewStatus']} | {r['platformStatus']} |",text,flags=re.M)
    text=re.sub(r'^\| '+r['id']+r' '+re.escape(r['title'])+r' \|.*$',f"| {r['id']} {r['title']} | {r['notes']} |",text,flags=re.M)
text=text.replace('- M21 이후는 기존 승인 상한 밖 후속 후보다. 이번 목록 작성으로 착수하지 않는다.','- 2026-11-04 사용자가 M21~M33 남은 13편 전체를 명시 승인했다. [해당 제작·검수표](../production/batches/game-math-remaining-20261104/progress.md)를 기준으로 로컬 검수본까지 진행한다. 다른 영상 자동 착수·업로드·예약은 포함하지 않는다.')
doc.write_text(text,encoding='utf-8')
out=ROOT/'output/game-math-remaining-20261104'
out.mkdir(parents=True,exist_ok=True)
body=''.join(f'<tr><td>{x["id"]}</td><td>{html.escape(x["title"])}</td><td>{html.escape(rows[x["id"]]["productionStatus"])}</td><td>{"내부 검수 완료" if x["localReviewReady"] else "제작 중 · 검수 전"}</td></tr>' for x in data['items'])
(out/'index.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>얌얌코딩 게임수학 제작·검수표</title><style>body{background:#101111;color:#f4f4f2;font:17px system-ui;margin:3vw;line-height:1.65}h1{color:#f5d15c}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:12px;border-bottom:1px solid #444}p{max-width:70em;color:#ddd}</style><h1>게임수학 M21–M33 제작·검수표</h1><p>13편 전체 제작 승인. 현재는 자료·대본·장면 준비 단계이며 완성 영상은 아직 없습니다. 각 편의 내부 검수가 끝나면 전체 영상과 네 가지 출력 링크를 여기에 연결합니다.</p><table><tr><th>편</th><th>강의</th><th>현재 단계</th><th>검수</th></tr>'+body+'</table></html>',encoding='utf-8')
print('Updated exact 13 rows and local review index; unrelated worklist content preserved.')
