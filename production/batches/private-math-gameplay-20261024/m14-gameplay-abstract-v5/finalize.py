"""Publish local M14 review links and reconcile only its current ledger entry."""
from pathlib import Path
import json,html,hashlib,sys
from datetime import datetime
R=Path(__file__).resolve().parents[4];B=Path(__file__).resolve().parent;P=R/'projects/game-math-polygon-partition-v2';H=P/'production/gameplay-abstract-v5';D=R/'output/game-math-polygon-partition-v2-gameplay-abstract-v5'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def rel(p):return p.relative_to(R).as_posix()
assert '--visual-reviewed' in sys.argv,'Run only after actual final frame inspection.'
now=datetime.now().astimezone().isoformat();plan=read(H/'plan.json');qa=read(H/'technical-qa.json');out=read(H/'outputs.json');master=next(x for x in out['outputs'] if x['path'].endswith('.captioned.mp4'))
assert {x['path']:x['sha256'] for x in out['outputs']}=={x['path']:x['sha256'] for x in qa['checks']}
sourceRefs={'dorf':R/'projects/game-math-polygon-centers-v2/production/concept-fit-v2/source-evidence.json','tiny':R/'projects/game-math-bounds-transform-v2/production/concept-fit-v2/source-evidence.json'}
abstractSources={}
for beat in plan['beats']:
 key=beat['sourceKey'];source=next(s for s in read(sourceRefs[key])['sources'] if s.get('path',s.get('file'))==beat['source'])
 assert hashlib.sha256((R/beat['source']).read_bytes()).hexdigest()==source['sha256']
 abstractSources[key]=dict(path=beat['source'],sha256=source['sha256'],url=source.get('sourceUrl',source.get('url')),width=source['width'],height=source['height'],fps=source['fps'],rightsRecord=rel(sourceRefs[key]),sourceAudioUsed=False,sourceAudioReason='Mixed trailer soundtrack; no isolated music/effects clearance. Added intro is narration only.')
plan['abstractSources']=abstractSources
plan['boundaryLink']='The new opening asks how to cover the original ground while leaving water/empty areas intact. The preserved body continues with the prior L-shaped boundary and the method for non-overlapping triangles; it later verifies the same area/empty-space conditions.'
save(H/'plan.json',plan)
visual=dict(checkedAt=now,master=master['path'],masterSha256=master['sha256'],scope='Changed abstract and QG06 beginning/action/result/return final frames at1080p and375px, native quarter-second factory action, source overlays and speech-time correspondence.',frames=qa['frames'],reviewNotes=['The factory feeds a complete square bottom-to-top through half destroyer →90-degree rotator→half destroyer. 13 continuous native seconds, no freeze padding.','Tracked guide follows the camera pan; quarter-turn arc has no false closing diagonal.','Existing mathematical model kept alongside real game; partial old model footer excluded from comparison crop.','Abstract uses actual tile placement and pond drawing to introduce covered region versus empty space; no game-internal triangulation measurement claimed.','Old body narration/text/order/duration retained, shifted by intro duration.'],actualContinuousPlayback=False,actualWholeListening=False,newIntroBlindAsr=rel(B/'intro-asr-review.json'),humanReview='pending')
save(H/'visual-review.json',visual);qa['visualInspection']=rel(H/'visual-review.json');save(H/'technical-qa.json',qa)
mixedAsr=read(H/'intro-mix-asr.json')
mix=P/'production/local/gameplay-abstract-v5/intro-mix.wav'
assert mixedAsr['audioSha256']==hashlib.sha256(mix.read_bytes()).hexdigest()
assert mixedAsr['similarity']>=.98
allowed={('호','코'),('덮','덥')}
assert all(d['kind']=='replace' and (d['expected'],d['recognized']) in allowed for d in mixedAsr['differences'])
visual['newIntroBlindAsr']=rel(H/'intro-mix-asr.json')
visual['newIntroTailTreatment']=mixedAsr['edgeTreatment']
visual['newIntroListening']='Final human listening pending; ASR does not certify naturalness.'
visual['listeningChecks']=[{'time':8.4,'word':'호수','reason':'Final whole-intro ASR heard 코수; isolated original B and two preceding mixes recognized 호수. No omitted clause, but pronunciation needs listening.'},{'time':16.5,'word':'덮고','reason':'ASR 덥고 is a Korean homophone spelling difference; check natural phrasing in listening.'}]
save(H/'visual-review.json',visual)
out['status']='local-user-review-pending';save(H/'outputs.json',out)
credits='''Footage attribution — selected M14 revision

Shapez 2 EP01 - it's shaping up to be an awesome factory!
Creator: DataEngineerPlays
Source: https://www.youtube.com/watch?v=XIK3SqCHAvw
License displayed by source: Creative Commons Attribution license (reuse allowed).
CC BY: https://creativecommons.org/licenses/by/4.0/
YouTube license explanation: https://support.google.com/youtube/answer/2797468?hl=en
Changes: 18:35.6–18:48.6 excerpt; crop/enlargement, Korean narration, editorial guides and side-by-side lesson model. Original mixed creator commentary excluded. No endorsement implied.

Dorfromantik: Toukana Interactive official gameplay / explanation trailer.
Source: https://www.toukana.com/dorfromantik/presskit
Rights/source record: projects/game-math-polygon-centers-v2/production/concept-fit-v2/source-evidence.json
Tiny Glade: Pounce Light official release-date trailer.
Source: https://pouncelight.games/tiny-glade/
Rights/source record: projects/game-math-bounds-transform-v2/production/concept-fit-v2/source-evidence.json
The existing body retains its previous source records and credits.
The added abstract excludes the trailers' mixed music/soundtracks; existing body audio is preserved.

Keep these credits at the bottom of any future upload description. This delivery authorizes no upload.
'''
(D/'credits.txt').write_text(credits,encoding='utf8');(H/'credits.txt').write_text(credits,encoding='utf8')
e=read(H/'source-evidence.json');e.update(licenseGuide='https://support.google.com/youtube/answer/2797468?hl=en',licenseGuideCurrentTarget='https://creativecommons.org/licenses/by/4.0/',licenseVersionNote='Current YouTube Help links to4.0; source metadata gives CC Attribution without a version.',creditFile=rel(H/'credits.txt'));save(H/'source-evidence.json',e)
slug='game-math-polygon-partition-v2';delta=plan['introSeconds'];patches=read(P/'production/gameplay-motion-v4/patches.json')['patches'];jumps=[(2,'실제 게임으로 보는 전체 주제'),(2+delta,'기존 강의 본문'),(plan['patch']['oldStart']+delta,'사각형 절단 → 회전 → 작은 조각')]+[(p['start']+delta,'기존 게임 예시 '+p['scene']) for p in patches];jumps.sort()
jumps.append((8.4,'새 도입부 발음 확인: 호수'));jumps.sort()
buttons=''.join(f'<li><button data-time="{t:.3f}">{int(t)//60:02}:{int(t)%60:02} · {html.escape(title)}</button></li>' for t,title in jumps)
style='body{background:#101412;color:#f5f5ef;font:18px/1.7 system-ui;max-width:1200px;margin:30px auto;padding:20px}h1{color:#ffd773}video{width:100%}a,button{color:#a5e2bd}button{font:inherit;border:0;background:transparent;text-align:left;cursor:pointer;padding:6px 0;text-decoration:underline}small{color:#c1c8c2}li{margin:8px 0}table{width:100%;border-collapse:collapse}td,th{padding:12px;border-bottom:1px solid #465048;text-align:left}'
page=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>다각형 ② · 실제 게임 Abstract 검수본</title><style>{style}</style><h1>다각형 ② — 나누어도 원래 모양은 그대로</h1><p>1920×1080 · 60fps · {int(plan['seconds'])//60}분 {int(plan['seconds'])%60:02}초 · 사용자 검수 대기</p><p>사각형을 자르고 회전하는 실제 게임13초와, 실제 게임으로 전체 주제를 소개하는 도입부{delta:.2f}초를 추가했습니다. 기존 본문 설명·음성·순서는 유지했습니다.</p><video id="v" controls preload="metadata" src="{slug}.captioned.mp4"></video><p><a href="{slug}.captioned.mp4">전체 자막 영상</a> · <a href="{slug}.clean.mp4">무자막 영상</a> · <a href="{slug}.ko.srt">한국어 자막</a> · <a href="{slug}.en.srt">영어 자막</a></p><ol>{buttons}</ol><p><small>검사: 전체 파일 디코딩·1080p60·길이·기존 본문 PCM/자막 보존·원본과 최종 영상 프레임 대조·변경 화면1080p/375px·새 도입 음성의 독립 음성인식 대조. 전체 연속 청취와 사용자 최종 검수는 남아 있습니다.</small></p><p><a href="credits.txt">게임 화면 출처·이용 조건</a> · <a href="../private-math-gameplay-20261024/index.html">18편 검수표</a></p><details><summary>Shapez 2 화면 저작자 표시</summary><p><a href="https://www.youtube.com/watch?v=XIK3SqCHAvw">Shapez 2 EP01 - it's shaping up to be an awesome factory!</a> — DataEngineerPlays, <a href="https://creativecommons.org/licenses/by/4.0/">CC BY</a>. 일부 구간을 발췌·확대하고 설명·표식을 추가했습니다. 저작자의 보증이나 추천을 의미하지 않습니다.</p></details><small>자막 영상 SHA256: {master['sha256']}</small><script>const v=document.getElementById('v');document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{{v.currentTime=Number(b.dataset.time);v.play().catch(()=>{{}})}});</script></html>'''
page=page.replace('전체 연속 청취와 사용자 최종 검수는 남아 있습니다.</small>','전체 연속 청취와 사용자 최종 검수는 남아 있습니다. 특히 새 도입부8.4초의 ‘호수’는 자동 인식 결과가 엇갈려 발음 청취 확인이 필요합니다.</small>')
(D/'index.html').write_text(page,encoding='utf8')
wp=R/'shared/publishing/video-worklist.json';w=read(wp);g=w['privateMathPolish']['gameplayTimingRevision'];row=next(x for x in g['entries'] if x['id']=='M14');row.pop('blockers',None)
row.update(newReviewReady=True,status='실제 절단·회전 + Abstract 추가 · 사용자 검수 대기',nativeSeconds=round(35.85+13+delta,3),examples=9,bodyExamples=6,abstractExamples=3,revision='gameplay-abstract-v5',plan=rel(H/'plan.json'),newOutput=rel(D),masterSha256=master['sha256'],technicalQa=rel(H/'technical-qa.json'),nativeFrameQa=rel(H/'technical-qa.json'),motionContinuityQa=rel(H/'technical-qa.json'),visualQa=rel(H/'visual-review.json'),outputs=out['outputs'],seconds=plan['seconds'],abstractSeconds=delta,bodyPreserved=True,humanReview='pending',wholeListening=False)
ready=sum(x['newReviewReady'] for x in g['entries']);assert ready==18
g.update(status='local-human-review-pending',readyCount=ready,ready=ready,renderedCount=18,revision='gameplay-motion-v4 + M14 gameplay-abstract-v5',checkpoint=rel(B.parent/'checkpoint.json'),updatedAt=now);save(wp,w)
cp=read(B/'checkpoint.json');cp.update(status='local-human-review-pending',updatedAt=now,output=rel(D),outputs=out['outputs'],sourceBlockerResolved=True,bodySecondsPreserved=40231/60,introSeconds=delta,qa=rel(H/'technical-qa.json'),humanReview='pending',nextAction='User local review; no upload or automatic next video.');save(B/'checkpoint.json',cp)
aggregate=read(B.parent/'checkpoint.json');aggregate.update(status='local-human-review-pending',updatedAt=now,ready=18,encoded=18,fileDeliveries=18,current=[],entries=g['entries'],revision=g['revision'],latestSelectedCheckpoint=rel(B/'checkpoint.json'),newTts='M14 added abstract only; all previous body narration preserved',nextAction='18 local review bundles ready for human review. No upload or automatic continuation.');save(B.parent/'checkpoint.json',aggregate)
cpath=R/'shared/publishing/video-production-control.json';c=read(cpath);scope=c['scopedBatchAuthorizations']['m14-gameplay-abstract-v5'];scope.update(status='local-human-review-pending',completedAt=now,checkpoint=rel(B/'checkpoint.json'),masterSha256=master['sha256']);c['scopedBatchAuthorizations']['private-math-gameplay-20261024']['latestRevision'].update(status='local-human-review-pending',reviewReady=18,rendered=18,checkpoint=rel(B.parent/'checkpoint.json'),m14Revision='gameplay-abstract-v5');save(cpath,c)
summary=f'갱신: {now}\n\n**최신 수정본 렌더18/18 · 변경 화면 확인18/18 · 사용자 검수 승인0/18.**\n\nM14 다각형②의 실제 사각형 절단→회전13초를 보완하고, 실제 게임 Abstract{delta:.2f}초를 추가했습니다. 기존 본문 설명·음성·순서는 그대로이며, 나머지17편은 이전 검수본을 유지했습니다. 모든 게임 구간은 원래 속도이며 정지·반복·감속으로 길이를 채우지 않습니다. 전체 연속 청취·사용자 승인은 별도입니다.\n\n[현재 검수 페이지](../output/private-math-gameplay-20261024/index.html) · [이전본 조사 기록](../output/private-math-gameplay-20261024/audit.html)\n\n| 번호 | 강의 | 실제 재생 / 삽입 | 이번 상태 | 검수본 |\n|---|---|---:|---|---|\n'
htmlrows=[]
for e in g['entries']:
 summary+=f'| {e["id"]} | {e["title"]} | {e["nativeSeconds"]:g}초 / {e["examples"]}구간 | {e["status"]} | [보기](../{e["newOutput"]}/index.html) |\n'
 prefix='../'+Path(e['newOutput']).name;htmlrows.append(f'<tr><td>{e["id"]}</td><td>{html.escape(e["title"])}</td><td>{e["nativeSeconds"]:g}초 · {e["examples"]}구간</td><td>{html.escape(e["status"])}</td><td><a href="{prefix}/index.html">영상·자막</a></td></tr>')
summary+='\nM14의3구간은 새 도입부,6구간은 본문의 실제 게임 예시입니다. 아래 과거 기록의 원본 부족 표시는 이력이며 최신 상태는 위 표를 따릅니다.\n'
for path,start,end in [('docs/GAME_MATH_PRIVATE_POLISH.md','<!-- GAMEPLAY-20261024-START -->','<!-- GAMEPLAY-20261024-END -->'),('docs/VIDEO_WORKLIST.md','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-START -->','<!-- GAMEPLAY-PRESENCE-AUDIT-20261024-END -->')]:
 p=R/path;t=p.read_text('utf-8-sig');a=t.index(start);z=t.index(end,a)+len(end);p.write_text(t[:a]+start+'\n\n'+summary+'\n'+end+t[z:],encoding='utf8')
board=f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>게임수학 검수표</title><style>{style}</style><h1>게임수학 실제 게임 장면 수정</h1><p>렌더18/18 · 변경 화면 확인18/18 · 사용자 최종 검수 대기</p><p>다각형②: 실제 절단·회전 장면 보완 + 실제 게임 Abstract 추가. 나머지17편은 기존 검수본 유지.</p><p><small>본문 설명·음성 보존. 정지 화면 패딩0초. 전체 연속 청취와 사용자 승인은 별도입니다.</small></p><div style="overflow:auto"><table><thead><tr><th>번호</th><th>강의</th><th>실제 재생</th><th>상태</th><th>보기</th></tr></thead><tbody>'+''.join(htmlrows)+f'</tbody></table></div><p><a href="audit.html">이전본 전수조사 이력</a></p><small>{now}</small></html>'
(R/'output/private-math-gameplay-20261024/index.html').write_text(board,encoding='utf8')
save(B/'delivery-manifest.json',dict(updatedAt=now,revision='M14 gameplay-abstract-v5',outputs=out['outputs'],allCurrentReviewReady=18,humanApproved=0,old17MasterHashes={e['id']:e['masterSha256'] for e in g['entries'] if e['id']!='M14'}))
print('M14 local review bundle complete; 18 current deliveries awaiting human review. No platform mutation.')
