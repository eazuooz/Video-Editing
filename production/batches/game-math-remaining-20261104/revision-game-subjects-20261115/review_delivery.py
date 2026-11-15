"""Local review artifacts; evidence never substitutes for human approval."""
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from subject_revision import *
import progress


def reuse_m21():
    e=EPISODES['M21'];p=work(e)
    previous=ROOT/'projects'/e['slug']/'production/local/teaching-sync-v2'
    enc=read(previous/'encoded.json');visual=read(previous/'visual-review.json')
    tech=read(previous/'technical-qa.json');audit=read(HERE/'scene-audit.json')
    assert visual['status']==tech['status']=='pass'
    assert visual['captionedSha256']==enc['files']['captioned']['sha256']
    for record in enc['files'].values():assert sha(record['path'])==record['sha256']
    save(p/'encoded.json',{**enc,'revision':REV,'reusedUnchanged':True,
        'reuseReason':'The inspected M21 already uses the requested material sphere, sampled-surface vectors and independent games, not a generic robot.',
        'status':'unchanged-verified-master','humanReviewed':False,'finalReviewReady':True})
    save(p/'qa.json',dict(episode='M21',status='pass',reusedUnchanged=True,
        originalTechnicalEvidence=str(previous/'technical-qa.json'),
        originalPictureEvidence=str(previous/'visual-review.json'),
        currentSceneAudit=str(HERE/'scene-audit.json'),
        scope='Current all-scene midpoint picture audit plus exact-hash reuse of prior encoded, formula, audio and visual QA. No new full human viewing is claimed.',
        humanReviewed=False,finalReviewReady=True))


def page(e,enc,title):
    folder=Path(enc['files']['captioned']['path']).parent
    if enc.get('reusedUnchanged'):return folder/'index.html'
    plan=read(work(e)/'subject-plan.json')
    moments={r['scene']:r for r in plan['evidence']}
    if e['id']=='M33':moments['029']={'asset':'mario'}
    items=[]
    for sid,item in sorted(moments.items()):
        scene=next(s for s in e['scenes'] if s['scene']==sid)
        t=scene['start'];stamp=f'{int(t)//60:02}:{int(t)%60:02}'
        items.append(f'<li><button data-time="{t:.5f}">{stamp} · {html.escape(item.get("asset",sid))}</button></li>')
    links=' · '.join(f'<a href="{Path(enc["files"][k]["path"]).name}">{label}</a>' for k,label in [('captioned','자막 영상'),('clean','Clean MP4'),('ko','한국어 SRT'),('en','영어 SRT')])
    credits=ROOT/'output'/(e['slug']+'-teaching-sync-v2')/'supplemental-credits.txt'
    if credits.exists():shutil.copy2(credits,folder/'supplemental-credits.txt')
    assets=read(HERE/'assets.json');source_ids={item.get('asset') for item in plan['evidence']}
    if e['id']=='M33':source_ids.add('mario')
    provenance=[{**a,'review':'Actual encoded pictures inspected for this episode'} for a in assets if a['id'] in source_ids]
    frame_ids={Path(a['sourceFrame']).stem for a in provenance}
    sources=[{**r,'visualReview':'Frame/crop and its realized explanation inspected'} for r in read(HERE/'sources.json') if r['id'] in frame_ids]
    rights=[r for r in read(HERE/'source-rights-review.json')['sources'] if r['frameId'] in frame_ids]
    credit_lines=['Additional game-image credits (description / course notes):','']
    for r in rights:
        credit_lines.extend([r['title']+' — '+r['uploader'],r['recordingUrl'],r['licenseLabel'] or r['recorderPermissionEvidence'],r['changes'],''])
    (folder/'game-image-credits.txt').write_text('\n'.join(credit_lines),encoding='utf8')
    save(folder/'game-image-provenance.json',dict(episode=e['id'],assets=provenance,sources=sources,recorderCredits=rights,
        meaning='Actual independent game-recording frames/cutouts in an explanatory animation; not measured game vectors or internal algorithms.'))
    exception='<p>기존 음성이 로봇을 직접 언급하는 엘리베이터 사고실험 한 장면은 대사와 맞도록 보존했습니다.</p>' if e['id']=='M27' else ''
    text=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e['id']} {html.escape(title)}</title><style>body{{max-width:1200px;margin:auto;padding:24px;background:#080808;color:white;font:18px/1.65 system-ui}}h1,h2{{color:#e8cf83}}a,button{{color:#73c7c2}}video{{width:100%}}button{{background:transparent;border:0;border-bottom:1px solid #444;font:inherit;text-align:left;padding:10px;cursor:pointer}}small{{color:#bbb}}</style>
<h1>{e['id']} · {html.escape(title)}</h1><p>1920×1080 · 60fps · 내부 검사 완료 / 사용자 검수 대기</p>
<video id="master" src="{Path(enc['files']['captioned']['path']).name}" controls playsinline preload="metadata"></video><p>{links}</p>
<p>실제 게임에서 가져온 캐릭터·물체 이미지를 기존 설명의 위치·벡터·그래프와 연결했습니다. 게임 녹화와 해설 애니메이션을 구분하며, 내레이션·음성·수식 전개·전체 길이는 보존했습니다.</p>{exception}
<h2>이미지 연결 수정 구간</h2><ul>{''.join(items)}</ul><p><a href="game-image-provenance.json">게임 이미지 출처·원본 프레임 기록</a> · <a href="game-image-credits.txt">추가 이미지 크레딧</a></p>
<small>내부 검수는 수정 장면의 실제 인코딩 프레임·동작 샘플·연결과 전체 파일 디코딩을 확인한 결과입니다. 전체 사용자 시청·청취 승인은 아직 기록하지 않았습니다.</small>
<p><a href="{(ROOT/'output/game-math-game-subjects-20261115/index.html').as_uri()}">13편 통합 검수표</a></p>
<script>document.querySelectorAll('[data-time]').forEach(b=>b.onclick=()=>{{let v=document.getElementById('master');v.currentTime=Number(b.dataset.time);v.play();v.scrollIntoView({{behavior:'smooth',block:'center'}});}});</script></html>'''
    (folder/'index.html').write_text(text,encoding='utf8');return folder/'index.html'


class Links(HTMLParser):
    def __init__(self):super().__init__();self.items=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a' and a.get('href'):self.items.append(a['href'])
        if tag=='video':self.items.append(a.get('src'))


def check_links(path):
    h=Links();h.feed(path.read_text(encoding='utf8'));n=0
    for link in h.items:
        assert link,('Empty target',path)
        u=urlsplit(link)
        if u.scheme in ('http','https'):continue
        target=Path(unquote(u.path).lstrip('/')) if u.scheme=='file' else (path.parent/unquote(u.path)).resolve()
        assert target.is_file(),(path,link,target)
        n+=1
    return n


def main():
    rows=progress.update();assert all(r['ready'] for r in rows),'Unreviewed pictures cannot be delivered as complete'
    results=[];linkcount=0
    for row in rows:
        e=EPISODES[row['id']];p=work(e);enc=read(p/'encoded.json');qa=read(p/'qa.json')
        assert qa['status']=='pass' and qa['finalReviewReady'] and not qa['humanReviewed']
        for f in enc['files'].values():assert sha(f['path'])==f['sha256']
        review=page(e,enc,row['title']);linkcount+=check_links(review)
        results.append(dict(id=e['id'],reviewPage=str(review),files=enc['files'],frames=enc['frames'],duration=enc['duration'],
            qaEvidence=dict(path=str(p/'qa.json'),sha256=sha(p/'qa.json')),reusedUnchanged=enc.get('reusedUnchanged',False),humanReviewed=False))
    linkcount+=check_links(ROOT/'output/game-math-game-subjects-20261115/index.html')
    report=dict(status='all-thirteen-local-user-review-pending',at=datetime.now(timezone.utc).isoformat(),episodes=results,
        outputFileCount=sum(len(r['files']) for r in results),verifiedLocalLinks=linkcount,
        originalAudioPreserved=True,originalLengthPreserved=True,uploaded=False,deleted=False,automation=False,
        limitations='Internal sampled visual QA and whole-stream decode; actual full human viewing/listening is pending. M21 was already a matching sphere/surface explanation and is reused unchanged. M27 retains one robot explicitly named by its preserved narration.')
    assert report['outputFileCount']==52;save(HERE/'delivery.json',report)
    cp=read(HERE/'checkpoint.json');cp.update(status=report['status'],completedFinalMasters=[r['id'] for r in results],
        delivery=str(HERE/'delivery.json'),next='Wait for human review of these exact local masters; no upload or automatic next work.')
    save(HERE/'checkpoint.json',cp)
    control_path=ROOT/'shared/publishing/video-production-control.json';control=read(control_path)
    control['explicitMathRemainingBatch20261104']['gameSubjectRevision20261115'].update(status=report['status'],localReadyCount=13,delivery=str(HERE/'delivery.json'),humanReviewed=False)
    save(control_path,control)
    print('13 local review deliveries / 52 verified files /',linkcount,'checked local links')


if __name__=='__main__':
    import sys
    reuse_m21() if '--reuse-m21' in sys.argv else main()
