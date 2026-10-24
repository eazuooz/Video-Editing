"""Record the current final-master frame inspection and publish an audit table."""
from pathlib import Path
import datetime, hashlib, html, json, os, re
B=Path(__file__).resolve().parent; R=B.parents[2]
def rd(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def h(s):return html.escape(str(s),quote=True)
def time(t):
 n=round(t);return f'{n//60:02}:{n%60:02}'
r=rd(B/'gameplay-presence-audit.json');now=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat()
notes={
 'M03-original':'왕국의 눈물·Besiege 녹화 확인. 마지막 게임 구간 이후 약7분25초 동안 게임 예시가 없음.',
 'M04':'왕국의 눈물·Dorfromantik 녹화 확인. 첫 예시와 다음 예시 사이 약7분25초 공백. 회전 순서·축 변화의 실제 비교 충분성은 미통과.',
 'M05':'왕국의 눈물·Space Engineers 2·Dorfromantik 녹화 확인. 마지막 예시가08:56경 끝나고 약10분56초 동안 게임 예시가 없음.',
 'M06':'Space Engineers 2 녹화3구간만 존재. 전체18분41초 중 정상 재생15.1초이며 같은 게임의 조립·배치 위주. 합성·역원·벡터 회전의 구체적 관찰 대응 재검수.',
 'M07':'정상 재생2.9초·2.9초·1.2초, 합계7초. 정지 화면28초. 중간 자세·경로·속도를 따라 보기에는 움직임 구간이 지나치게 짧음.',
 'M08':'Besiege 녹화3구간, 합계15.9초. 정지 화면25.65초. 시점 이동·부품 이동과 자세 변경을 구별하는 비교 길이 재검수.',
 'M09':'실제 녹화는 존재. 배선3초·다리 편집1.75초 등 짧은 구간과 재개1.5초 구간을 따로 점검해야 함.',
 'M10':'실제 녹화는 존재. 건물 높이 변경2.4초와 둥근 형태4초 등 짧은 예시의 설명 대응 재검수.',
 'M11':'Poly Bridge 3 세 예시 모두5초 미만(4초·3.7초·1.75초). 실제 동작 합계9.45초로 정지26.55초보다 짧음.',
 'M12':'Townscaper 네 예시 모두5초 미만. 움직임 합계14.95초. 삼각형 내부 주소·속성 보간 자체를 게임 화면이 직접 입증하지 않음.',
 'M13':'Dorfromantik·Tiny Glade 녹화 확인. 움직임 구간은5~9.8초. 존재 확인과 개념별 설명 충분성은 별도이며 자동 통과시키지 않음.',
 'M14':'Dorfromantik·Tiny Glade·Shapez2 녹화 확인. Shapez2는0.55초·0.65초·1.2초로 잘려 있어 동작 추적 보강 필요.',
 'M15':'Big Walk·Subnautica 녹화 확인. 일부1.5초·2초 구간은 정지 화면으로 이어짐. 전체 시간만으로 개별 예시를 통과시키지 않음.',
 'M16':'Split Fiction·Tiny Glade·Townscaper 녹화 확인. 짧은5개 구간과 시야·줌·창 크기 설명의 실제 변화 대응 재검수.',
 'M17':'Portal2·Tiny Glade·Townscaper 녹화 확인. 2~4초 삽입 구간과 좌표 변환 설명의 연결 재검수.',
 'M18':'Townscaper·Tiny Glade 녹화 확인. 정지37.6초가 실제 재생18.4초보다 김. 깊이·w 계산과 관찰 가능한 결과의 연결 재검수.',
 'M19':'Tiny Glade·Space Engineers 2·Big Walk 녹화 확인. 움직임21.1초에 비해 정지81초. 7개 예시 중6개의 움직임이5초 미만.',
 'M20':'Space Engineers 2·Tiny Glade 녹화 확인. 움직임25초·정지58.9초. 법선 변환·UV의 직접 설명을 게임 외형 관찰로 대신하지 않았는지 재검수.'}
old={e['id']:e for e in rd(B/'edit-list-audit.json')['entries']}
for e in r['entries']:
 t=rd(R/'projects'/e['slug']/'production/concept-fit-v2/timeline.json');slots={s['id']:s for s in t['scenes']}
 uncovered=[]
 for s in old[e['id']]['shots']:
  a=slots[s['scene']]['start']+s['offset'];remaining=[(a,a+s['seconds'])]
  for p in e['shots']:
   parts=[]
   for a,b in remaining:
    if p['start']>a:parts.append((a,min(b,p['start'])))
    if p['end']<b:parts.append((max(a,p['end']),b))
   remaining=[(a,b) for a,b in parts if b-a>.001]
  uncovered+=remaining
 assert not uncovered
 e['uncoveredPriorGameIntervals']=uncovered
 e['pixelReview']='all scheduled native-game intervals: two decoded final-master frames visually inspected'
 e['actualGameRecordingPresent']=True
 e['presenceOnlyVerdict']='present, not a pedagogical approval'
 e['pedagogicalAcceptance']=False
 e['note']=notes[e['id']]
 e['sampleEvidence']=[dict(path=p,sha256=hashlib.sha256((R/p).read_bytes()).hexdigest()) for p in e['contactSheets']]
 for s in e['shots']:s['recordedGameVisibleInSamples']=True
r.update(pixelReviewComplete=True,completedAt=now,zeroRecordedGameEpisodes=[],latestIndexMisdirections=[],
 summary=dict(episodes=18,withRecordedGame=18,withoutRecordedGame=0,nativeSegments=91,underFiveSecondNativeSegments=45,inspectedFrames=182),
 priorClaimCorrection='Prior 18/18 visual-review-ready wording is withdrawn as a claim of sufficient game examples. File integrity remains intact; decoded frames verify inclusion, not instructional adequacy. No full-length continuous viewing/listening was performed in this audit.',
 olderVersions=dict(scope='Link inventory only; not a new all-version pixel audit',finding='Legacy private-game-math-polish board still points to concept-fit-v2 and private-polish versions. Latest gameplay-v3 pages resolve to the expected masters; first three intentionally share byte-identical concept-fit-v2 files. No evidence that the user viewed a legacy version.'))
save(B/'gameplay-presence-audit.json',r)

O=R/'output/private-math-gameplay-20261024';out=O/'audit.html'
def url(p):return Path(os.path.relpath(R/p,O)).as_posix()
rows=[];sections=[]
for e in r['entries']:
 rows.append(f'<tr><td>{h(e["id"])}</td><td><a href="#{h(e["id"])}">{h(e["title"])}</a></td><td>{time(e["seconds"])}</td><td>있음</td><td>{e["nativeSeconds"]:g}초</td><td>{e["stillSeconds"]:g}초</td><td>{e["shortMotionSegmentsUnder5s"]}</td><td>{h(e["note"])}</td></tr>')
 buttons=[]
 for i,s in enumerate(e['shots']):
  for seg in s['segments']:
   if seg['kind']=='motion':buttons.append(f'<button data-video="{h(url(e["master"]))}" data-start="{seg["start"]:.4f}" data-end="{seg["end"]:.4f}" data-title="{h(e["id"]+" · "+s["title"])}">{time(seg["start"])} · {h(s["game"])} · {seg["seconds"]:g}초</button>')
 images=''.join(f'<a href="{h(url(p))}"><img loading="lazy" src="{h(url(p))}" alt="{h(e["id"])} 최종 영상의 게임 구간 비교 프레임"></a>' for p in e['contactSheets'])
 sections.append(f'<section id="{h(e["id"])}"><h2>{h(e["id"]+" · "+e["title"])}</h2><p>{h(e["note"])}</p><div class="buttons">'+''.join(buttons)+f'</div><p><a href="{h(url(e["index"]))}">현재 전체 영상 폴더</a></p><details><summary>게임 화면 존재 확인용 실제 프레임</summary>{images}</details></section>')
page='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>게임수학 실제 게임 삽입 전수조사</title><style>body{background:#101412;color:#f5f5ef;font:17px/1.6 system-ui;margin:24px}h1,h2{color:#ffd773}a{color:#80d3a2}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid #455047;text-align:left;vertical-align:top}button{background:#24392d;color:#fff;padding:12px;border:1px solid #80d3a2;border-radius:4px;cursor:pointer}.scroll{overflow:auto}.buttons{display:flex;gap:8px;flex-wrap:wrap}section{border-top:1px solid #455047;margin-top:32px;padding-top:18px}video{width:100%;max-height:70vh}img{max-width:100%;display:block;margin:12px 0}.notice{border-left:5px solid #ffd773;padding:16px;background:#1c241e}#player{max-width:1280px;margin:auto}</style>
<h1>실제 게임 녹화 삽입 전수조사 · 18편</h1><p class="notice"><b>최신 완성본 기준 완전 누락 0편 / 실제 게임 녹화 존재 18편.</b><br>존재와 설명에 충분한 예시는 다릅니다. 회전 보간①은13:53 중 실제 재생7초이며, 전체91개 재생 구간 중45개가5초 미만입니다. 종전 ‘18편 시각 검수 완료’를 예시 충분성 통과로 해석할 수 없도록 정정합니다.</p>
<p>최신 MP4 해시·폴더 재생 대상 확인, 모든 게임 재생 구간의 전후 프레임182장 확인. 자체 모형·정지 화면은 실제 게임 재생 시간에서 제외. 구간별 재생 시간을 계산한 표이며, 강의 전체 연속 시청·청취 또는 개념별 최종 합격을 의미하지 않습니다.5초는 진단용 수치이지 자동 합격 기준이 아닙니다.</p>
<div id="player"><h2 id="player-title">아래 시간 버튼으로 실제 게임 구간 확인</h2><video id="v" controls preload="metadata"></video><p id="player-info">버튼을 누르면 해당 완성본의 게임 구간으로 이동합니다. 해당 구간이 끝나면 정지합니다.</p></div>
<div class="scroll"><table><thead><tr><th>번호</th><th>강의</th><th>전체</th><th>실제 녹화</th><th>움직이는 게임 합계</th><th>분석 정지 합계</th><th>5초 미만 구간</th><th>발견 사항</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div>'''+''.join(sections)+'''
<script>let end=null;const v=document.getElementById('v');document.querySelectorAll('button[data-video]').forEach(b=>b.addEventListener('click',()=>{v.pause();end=Number(b.dataset.end);document.getElementById('player-title').textContent=b.dataset.title;const seek=()=>{v.currentTime=Number(b.dataset.start);v.play().catch(()=>{});};if(v.getAttribute('src')!==b.dataset.video){v.src=b.dataset.video;v.addEventListener('loadedmetadata',seek,{once:true});v.load();}else seek();document.getElementById('player').scrollIntoView({behavior:'smooth'});}));v.addEventListener('timeupdate',()=>{if(end!==null&&v.currentTime>=end){v.pause();end=null;}});</script></html>'''
out.write_text(page,encoding='utf8')

notice='<aside style="padding:20px;border:2px solid #ffd773"><b>전수조사 정정: 실제 게임 녹화는18편 모두 존재하지만, 예시 길이·설명 대응은 통과 상태가 아닙니다.</b> <a href="audit.html">실제 재생 시간·장면별 확인표</a></aside>'
p=O/'index.html';s=p.read_text('utf8');s=s.replace('<h1>게임수학 게임 장면 수정 검수표</h1>','<h1>게임수학 게임 장면 수정 검수표</h1>'+notice,1);s=s.replace('시각 검수 <b>18 / 18</b>','기술 납품 <b>18 / 18</b> · 게임 예시 충분성 재검수 필요');s=s.replace('시각 검수 완료 · 사용자 검수 대기','게임 녹화 존재 · 예시 충분성 재검수');p.write_text(s,encoding='utf8')

c=rd(B/'checkpoint.json');c.update(status='presence-audit-complete-quality-followup-required',ready=0,fileDeliveries=18,previousVisualReadyCount=18,presenceAudit='production/batches/private-math-gameplay-20261024/gameplay-presence-audit.json',gameplayPresenceConfirmed=18,pedagogicalReviewComplete=False,updatedAt=now)
for e in c['entries']:e['status']='게임 녹화 존재 · 예시 길이·설명 대응 재검수 필요'
c['next']='Report audit findings; no new render authorized by this presence-audit request.';save(B/'checkpoint.json',c)
wpath=R/'shared/publishing/video-worklist.json';w=rd(wpath);rev=w['privateMathPolish']['gameplayTimingRevision'];rev.update(status='게임 녹화 존재 확인 · 예시 충분성 재검수 필요',ready=0,fileDeliveries=18,presenceAudit='production/batches/private-math-gameplay-20261024/gameplay-presence-audit.json',presenceAuditHtml='output/private-math-gameplay-20261024/audit.html')
for e in rev.get('entries',[]):e['status']='게임 녹화 존재 · 예시 충분성 재검수 필요'
save(wpath,w)

table=['| 번호 | 강의 | 전체 길이 | 실제 게임 재생 | 분석 정지 | 5초 미만 구간 |','|---|---|---:|---:|---:|---:|']
for e in r['entries']:table.append(f'| {e["id"]} | {e["title"]} | {time(e["seconds"])} | {e["nativeSeconds"]:g}초 | {e["stillSeconds"]:g}초 | {e["shortMotionSegmentsUnder5s"]} |')
block='''<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-START -->
### 실제 게임 녹화 전수조사 정정 — 2026-10-24

최신18편 완성 MP4에서 실제 게임 녹화가 완전히 빠진 편은 **0편**이다. 모든 삽입 구간의 전후182개 최종 프레임과 파일 해시·재생 링크를 대조했다. 자체 설명 모형·분석 정지 화면은 실제 게임 재생 시간에서 제외했다. 전체91개 정상 재생 구간 중45개가5초 미만이며, 회전 보간①은13분53초 중7초뿐이다. **종전18/18 검수 완료는 예시가 충분하다는 판정으로는 철회한다.** 기술 출력18편은 보존하고, 게임 예시의 길이와 개념 대응은 재검수 필요로 표시한다.

[전체 조사표·구간 바로 재생](../output/private-math-gameplay-20261024/audit.html) · [해시·시간·프레임 근거](../production/batches/private-math-gameplay-20261024/gameplay-presence-audit.json)

'''+ '\n'.join(table)+'''

우선 문제: M06·M07·M08(사용자 지적 회전 계열), M11·M12(모든 실제 구간5초 미만), M14의 Shapez2 초단기 컷, M19·M20(긴 정지 화면). M03–M05도 실제 녹화는 있으나 예시 사이 긴 공백과 개념 대응을 다시 확인해야 한다. 시간 비율만으로 합격·불합격을 결정하지 않는다. 이 조사는 최신18편의 실제 삽입 여부와 시간 조사이며 전체 강의 연속 시청·청취 검수나 새 렌더링 완료가 아니다. 이전 버전 페이지도 남아 있으나 사용자가 어느 이전본을 보았다고 단정하지 않는다.
<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-END -->'''
for path in [R/'docs/GAME_MATH_PRIVATE_POLISH.md',R/'docs/VIDEO_WORKLIST.md']:
 s=path.read_text('utf-8-sig');start='<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-START -->';end='<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-END -->'
 if start in s:s=s.split(start)[0]+block+s.split(end,1)[1]
 else:s=s.split('\n',1)[0]+'\n\n'+block+'\n\n'+s.split('\n',1)[1]
 path.write_text(s,encoding='utf8')
print('Audit recorded. Latest master files unchanged. Complete absence: 0 / 18. Instructional sufficiency: not accepted.')
