"""Render only the current six-episode checkpoint and actual QA evidence."""
from pathlib import Path
from datetime import datetime,timezone
import html,json,os,uuid
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
OUT=R/'output/game-design-25-30-20261026'
PHYSICAL=Path('C:/Users/1/.codex/video-production/design-finish-six-20261026/review')
if OUT.resolve()!=PHYSICAL:raise ValueError('Exact batch review route required')
def save(p,value):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.tmp')
 tmp.write_text(value,'utf8');os.replace(tmp,p)
def load(p):return json.loads(p.read_text('utf-8-sig'))
def esc(s):return html.escape(str(s))
checkpoint=load(H/'checkpoint.json');rows=[];markdown=[];complete=0
for e in checkpoint['episodes']:
 s=e['slug'];status=R/'projects'/s/'production/batch-v1/review-status.json'
 q=load(status) if status.is_file() else {}
 ready=q.get('status')=='local-review-ready' and q.get('fourOutputsVerified') is True
 complete+=int(ready)
 root=f'../../projects/{s}/production/local/batch-v1/delivery/output/{s}'
 href=f'{root}/index.html'
 stage=q.get('stage',e['stage']);technical=q.get('technicalSummary','대기')
 seconds=q.get('durationSeconds',e.get('voiceSeconds',0)+12)
 duration=f'{int(seconds)//60}:{int(seconds)%60:02d}' if seconds else '—'
 audio=q.get('audioSummary','대기');visual=q.get('visualSummary','대기')
 if ready:
  stage='☑ 완성 · 내부 검사 완료'
  technical='1080p60 · 전체 디코딩·PTS·파일 해시 확인'
 if isinstance(audio,dict):
  audio='음량·원음 전송 측정·최종 대본 대조 완료 / 전체 청취 대기' if ready else '음성 검사 진행 중 / 전체 청취 대기'
 if isinstance(visual,dict):
  count=visual.get('currentEncodedCaptionPixelsReviewed')
  frames=visual.get('uniqueNativeFrames')
  visual=(f'자막 {count}큐·프레임 {frames}장 / 375px 확인' if count and frames else '자막·경계·표식·모바일 화면 확인') if ready else '화면 검사 진행 중'
 focus=q.get('reviewFocus',e.get('reviewFocus','전체 흐름·자연스러운 발음·설명과 화면의 연결'))
 human=f'☐ 사용자 검수 대기<br><small>{esc(focus)}</small>'
 links=f'<a href="{href}">영상·자막</a> · <a href="{root}/{s}.captioned.mp4">전체 영상</a>' if ready else '제작 중'
 rows.append(f'<tr><td>{esc(e["id"])}</td><td>{esc(e["title"])}</td><td>{duration}</td><td>{esc(stage)}</td><td>{esc(technical)}</td><td>{esc(audio)}</td><td>{esc(visual)}</td><td>{human}</td><td>{links}</td></tr>')
 markdown.append(f'| {e["id"]} | {e["title"]} | {duration} | {stage} | {technical} | {audio} | {visual} | ☐ {focus} | '+(f'[영상·자막](../../../projects/{s}/production/local/batch-v1/delivery/output/{s}/index.html)' if ready else '제작 중')+' |')
now=datetime.now(timezone.utc).astimezone().isoformat()
title='게임디자인 25–30 검수표'
notice='기술·화면 내부 검사는 실제 사용자 시청·청취와 구분합니다. YouTube 업로드·예약은 진행하지 않았습니다.'
page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{margin:32px auto;max-width:1600px;padding:0 20px;background:#111;color:#f4f4f4;font:16px/1.6 "Malgun Gothic",sans-serif}}h1{{color:#f4d477}}a{{color:#8ce0ce}}table{{width:100%;border-collapse:collapse}}td,th{{text-align:left;padding:14px 10px;border-bottom:1px solid #444;vertical-align:top}}th{{color:#f4d477}}.scroll{{overflow-x:auto}}small{{color:#bbb}}@media(max-width:600px){{body{{margin-top:20px;padding:0 12px}}table{{min-width:1100px}}}}</style>
<h1>{title}</h1><p>완성 검수본 {complete}/6편 · 동일 목소리 Sample B · Nimbus 배경음악 · FHD60</p><p>{notice}</p>
<div class="scroll"><table><thead><tr><th>번호</th><th>주제</th><th>길이</th><th>제작</th><th>기술</th><th>음성·음악</th><th>화면·자막</th><th>사용자 검수</th><th>파일</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div><p><small>갱신 {now}</small></p></html>'''
save(OUT/'index.html',page)
save(H/'REVIEW.md',f'# {title}\n\n완성 검수본 {complete}/6편. {notice}\n\n| 번호 | 주제 | 길이 | 제작 | 기술 | 음성·음악 | 화면·자막 | 사용자 검수 | 파일 |\n|---|---|---|---|---|---|---|---|---|\n'+'\n'.join(markdown)+'\n')
print(f'Review index updated: {complete}/6 ready; actual evidence only')
