"""Render this revision's evidence-backed status without relabeling previous masters."""
from common import *
import collections,copy,html
c=read(B/'checkpoint.json');a=read(B/'scene-audit.json');counts=collections.Counter(x['episode'] for x in a['scenes']);stamp=now()
render_path=R/'projects/game-math-orientation-matrices/production/concept-fit-v2/render-progress.json';render=read(render_path) if render_path.exists() else {}
if render:
 c['entries'][0].update(status=render['state'],renderedScenes=len(render['scenes']),totalScenes=24)
 c['active']=[dict(episode='M03-original',stage=render['state'],scene=render.get('activeScene'),completedScenes=len(render['scenes']))] if render['state']=='rendering' else []
c['active']=[]
for e in c['entries']:
 h=R/'projects'/e['slug']/'production/concept-fit-v2';o=R/'projects'/e['slug']/'production/local/concept-fit-v2'
 if (h/'outputs.json').exists():
  out=read(h/'outputs.json');e.update(status='encoded-internal-qa-pending',outputFolder=f"output/{e['slug']}-concept-fit-v2",outputFiles=len(out['outputs']),newSeconds=out['seconds'])
 if (o/'audio/paragraph-takes.json').exists() and not (h/'outputs.json').exists():
  t=read(o/'audio/paragraph-takes.json');plan=read(h/'voice-plan.json');e.update(status='changed-game-narration-generating' if t['takeCount']<len(plan['jobs']) else 'changed-game-narration-generated',ttsDone=t['takeCount'],ttsTotal=len(plan['jobs']))
 if (h/'render-progress.json').exists():
  rp=read(h/'render-progress.json');timeline=read(h/'timeline.json');e.update(renderedScenes=len(rp['scenes']),totalScenes=len(timeline['scenes']))
  if not (h/'outputs.json').exists():e['status']=rp['state']
  if rp['state']=='rendering':c['active'].append(dict(episode=e['id'],stage='rendering',scene=rp.get('activeScene'),completedScenes=len(rp['scenes'])))
 if (h/'review-ledger.json').exists():
  ledger=read(h/'review-ledger.json')
  if ledger.get('status')=='local-review-ready-with-listening-notes':e['status']=ledger['status']
c['ready']=[e['id'] for e in c['entries'] if e['status']=='local-review-ready-with-listening-notes']
c.update(updatedAt=stamp,auditSummary=copy.deepcopy(a['reviewSummary']),status='local-review-ready-with-listening-notes' if len(c['ready'])==len(c['entries']) else 'rendering-and-source-selection',nextAction=('All18 revised episodes are locally available; actual listening and human review remain pending. No upload or further episode advancement.' if len(c['ready'])==len(c['entries']) else 'Complete current revised episodes through actual-file QA, then continue the remaining explicitly authorized episodes: '+', '.join(e['id'] for e in c['entries'] if e['id'] not in c['ready'])+'. Ready entries still require actual listening and human review.'))
c['auditSummary']['finalReady']=len(c['ready']);c['auditSummary']['finalReadyMeaning']='Local visual/technical review complete; actual listening and human review remain pending'
c['auditSummary']['movingQA']='See the final per-episode review-ledger and playback evidence. The588-frame initial selection audit is not continuous viewing/listening.'
save(B/'checkpoint.json',c)
wpath=R/'shared/publishing/video-worklist.json';w=read(wpath);revision=w['privateMathPolish']['conceptFitRevision'];revision.update(updatedAt=stamp,entries=copy.deepcopy(c['entries']),auditSummary=c['auditSummary'],readyCount=len(c['ready']),status=c['status'] if len(c['ready'])==len(c['entries']) else ('rendering-and-source-selection' if c['active'] else 'revision-in-progress'));save(wpath,w)
labels={'sampled-scene-audit-complete-replacement-selection':'1차 장면 검수 완료 · 교체/재편집 준비','rendering':f'새 음성 연결 완료 · 화면 {len(render.get("scenes",{}))}/24 렌더링','rendered-qa-pending':'화면 렌더 완료 · 게임 합성/전체 QA 진행','failed':'렌더 오류 수정 중','changed-game-narration-generating':'바뀐 게임 설명 음성 생성 중','changed-game-narration-generated':'바뀐 게임 음성 생성 완료 · 연결/검사 중','encoded-internal-qa-pending':'1080p60 4종 출력 · 실제 재생/화면 검수 중','local-review-ready-with-listening-notes':'로컬 검수본 준비 · 발음/연결 청취 확인 필요'}
rows=[];htmlrows=[]
for e in c['entries']:
 label=labels.get(e['status'],e['status']);count=counts[e['id']]
 if e['status']=='rendering':label=f'화면 {e["renderedScenes"]}/{e["totalScenes"]} 렌더링'
 if e['status']=='changed-game-narration-generating':label+=f" ({e['ttsDone']}/{e['ttsTotal']}문단)"
 rows.append(f'| {e["id"]} | {e["title"]} | {count} | {label} | 대기 |')
 previous='기존 15:03 원본·음성 복원 완료' if e['id']=='M03-original' else f'<a href="../{e["slug"]}-private-polish/index.html">이전 보강본</a>'
 new=(f'<a href="../{e["slug"]}-concept-fit-v2/index.html">검수 폴더</a> · <a href="../{e["slug"]}-concept-fit-v2/{e["slug"]}.captioned.mp4">전체 영상</a>' if e.get('outputFolder') else '새 수정본 대기')
 htmlrows.append(f'<tr><td>{e["id"]}</td><td>{html.escape(e["title"])}</td><td>{count}</td><td>{html.escape(label)}</td><td>{new}</td><td>{previous}</td></tr>')
summary=f'이번 수정 대상 **18편**, 새 수정본 화면·기술검사 후 로컬 검수 대기 **{len(c["ready"])}편**. 전체147개 기존 게임 구간의 1차 분산 프레임 검수(588프레임/53연락판)에 이어, 완료된 편은 교체 장면·최종 자막·모바일 화면과 실제 파일도 확인했다. 전체 청취나 사용자 승인을 뜻하지 않는다.'
text=f'''# 기존 비공개 게임수학 · 게임 장면 적합성 재검수

갱신: {stamp}

{summary}

15:03 ‘방향과 회전 행렬’은 YouTube에 비공개로 남아 있다. 이전 목록에서는 나중에 만든 대체본 때문에 제외됐으며, 이번에는 M03-original로 다시 포함했다. 원본 AAC를 복원했고 720p 다운로드 화면은 검수에만 사용한다. 새 화면은 기존 코드로1920×1080/60fps에서 렌더링한다. 다른25분 V8 및 후속34분판과 합치지 않는다.

첫 편은140문단 중 게임 예시 지칭25문단만 수정하고115문단·수학 설명 순서를 보존했다. 새 음성 연결 후9개 변경 장면의 무힌트 ASR을 대조했다. ‘비시즈’·‘기울기’ 발음은 최종 청취 확인 항목으로 남아 있다. 첫 편4종 출력은 생성했고 표의 새 수정본 링크에서 내부 검수 상태를 구분해 볼 수 있다. 회전②는156문단 중30문단만 바꾸고126문단을 보존한다.

| 번호 | 강의 | 검수한 기존 게임 구간 | 이번 제작 상태 | 새 수정본 검수 |
|---|---|---:|---|---|
'''+ '\n'.join(rows)+'''

[검수 페이지](../output/private-game-math-polish/index.html)

기존 보강본과 모든 업로드는 보존한다. 이번 수정본의 사용자 검수는 전부 대기이며 업로드·삭제·예약은 하지 않는다.

근거: `production/batches/private-math-concept-fit-20261023/scene-audit.json`, `checkpoint.json`, 각 프로젝트의 `production/concept-fit-v2`.
'''
(R/'docs/GAME_MATH_PRIVATE_POLISH.md').write_text(text,encoding='utf8')
(R/'output/private-game-math-polish/index.html').write_text('''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>게임수학 진행표</title><style>body{font:17px/1.65 system-ui;background:#101512;color:#f2f5f2;max-width:1400px;margin:32px auto;padding:0 20px}h1{color:#ffdf73}a{color:#8cdbbc}table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:12px;border-bottom:1px solid #405147}.scroll{overflow:auto}p{max-width:1000px}.status{padding:14px;border-left:4px solid #ffdf73;background:#18201b}</style><h1>게임수학 · 개념에 맞는 게임 장면으로 수정</h1><p>'''+html.escape(stamp)+''' 갱신</p><p class="status">18편 대상 · 기존147개 게임 구간 1차 검수 완료 · 화면·기술검사 완료 / 청취 대기 '''+str(len(c['ready']))+'''편</p><p>첫 편 ‘방향과 회전 행렬’의 원본 음성을 복원했습니다. 수학 설명은 유지하고 비행 예시를 물체 회전·조립 장면으로 바꾸고 있습니다. 아래 ‘이전 보강본’은 이번 수정 결과가 아닙니다.</p><div class="scroll"><table><thead><tr><th>번호</th><th>강의</th><th>기존 게임 구간</th><th>이번 제작 상태</th><th>새 수정본</th><th>이전 버전</th></tr></thead><tbody>'''+''.join(htmlrows)+'''</tbody></table></div><p>147구간의 분산 프레임588개를 대본과 대조했습니다. 수정 후 실제 재생·자막·음성 검수는 별도로 진행합니다. 기존 업로드와 파일은 그대로 보존합니다.</p></html>''',encoding='utf8')
print('Updated 18 rows; ready',len(c['ready']),'M03 rendered',len(render.get('scenes',{})))
