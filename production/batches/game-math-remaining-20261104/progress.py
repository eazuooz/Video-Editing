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
    lines.append(f"| {item['id']} | {item['title']} | {row['productionStatus']} | {'완료' if ready else '진행 중'} | {'확인 완료' if item['humanReviewed'] else ('검수 대기' if ready else '완성본 대기')} |")
lines+=['','완성본 제공 조건: 1080p60 clean·자막영상·한국어 SRT·영어 SRT, 실제 화면·음성 검사와 입력/출력 근거 기록.','현재 다른 작업의 프로세스·예약·기존 완성본은 보존한다.']
(BATCH/'progress.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
doc=ROOT/'docs/VIDEO_WORKLIST.md'
text=doc.read_text(encoding='utf-8-sig')
for item in data['items']:
    r=rows[item['id']]
    text=re.sub(r'^\| '+r['id']+r' \|.*$',f"| {r['id']} | {r['title']} | {'☑' if r['productionComplete'] else '☐'} {r['productionStatus']} | ☐ {r['reviewStatus']} | {r['platformStatus']} |",text,flags=re.M)
    text=re.sub(r'^\| '+r['id']+r' [^|]+ \|.*$',f"| {r['id']} {r['title']} | {r['notes']} |",text,flags=re.M)
text=text.replace('- M21 이후는 기존 승인 상한 밖 후속 후보다. 이번 목록 작성으로 착수하지 않는다.','- 2026-11-04 사용자가 M21~M33 남은 13편 전체를 명시 승인했다. [해당 제작·검수표](../production/batches/game-math-remaining-20261104/progress.md)를 기준으로 로컬 검수본까지 진행한다. 다른 영상 자동 착수·업로드·예약은 포함하지 않는다.')
doc.write_text(text,encoding='utf-8')
out=ROOT/'output/game-math-remaining-20261104'
out.mkdir(parents=True,exist_ok=True)
def link_for(x):
    if not x.get('outputCandidatesAvailable'):return ''
    path=Path(x['outputs']['index']).relative_to(ROOT/'output').as_posix()
    return '<br><a href="../'+html.escape(path)+'">'+('검수본 보기' if x['localReviewReady'] else '생성된 영상 보기 — 내부 검수 중')+'</a>'
body=''.join(f'<tr><td>{x["id"]}</td><td>{html.escape(x["title"])}{link_for(x)}</td><td>{html.escape(rows[x["id"]]["productionStatus"])}</td><td>{"내부 검수 완료" if x["localReviewReady"] else "내부 검수 미완료"}</td></tr>' for x in data['items'])
(out/'index.html').write_text('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>얌얌코딩 게임수학 제작·검수표</title><style>body{background:#101111;color:#f4f4f2;font:17px system-ui;margin:3vw;line-height:1.65}h1{color:#f5d15c}a{color:#73c7c2}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:12px;border-bottom:1px solid #444}p{max-width:70em;color:#ddd}</style><h1>게임수학 M21–M33 제작·검수표</h1><p>13편 전체를 로컬 검수본까지 제작합니다. 영상 파일 생성과 내부 검수 완료를 구분하며, 사용자 시청·청취를 대신 완료 처리하지 않습니다. 생성된 영상은 해당 행에서 열 수 있습니다.</p><p>상태 갱신: '+html.escape(data['updatedAt'])+'</p><table><tr><th>편</th><th>강의</th><th>현재 단계</th><th>검수</th></tr>'+body+'</table></html>',encoding='utf-8')
print('Updated exact 13 rows and local review index; unrelated worklist content preserved.')
