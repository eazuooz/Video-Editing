"""Render the six-item review table from verified revision and upload receipts."""
from pathlib import Path
import datetime
import hashlib
import html
import json

ROOT = Path(__file__).resolve().parents[3]
BATCH = Path(__file__).resolve().parent
OUT = ROOT / 'output/game-design-25-29-clarity-v3-20261029'
ITEMS = [
    ('D25', 'limited-color-world', '색을 빼면 무엇이 보일까?', '같은 장면의 흑백 전환 → 명암·경계·무늬 보완 → 색 복원', True),
    ('D26', 'computer-controlled-players', '컴퓨터가 조작하는 플레이어', '검수한 Unity 설명 보완본 그대로 업로드', False),
    ('D27', 'in-game-cutscenes', '게임 속 컷신', '검수한 Unity 설명 보완본 그대로 업로드', False),
    ('D28', 'start-with-climax', '도입에도 절정이 필요하다', '검수한 Unity 설명 보완본 그대로 업로드', False),
    ('D29', 'kind-to-beginners', '처음 하는 사람에게 친절한 설계', '마리오 카트 8 디럭스 · 언패킹 · 어 쇼트 하이크로 예시 교체', True),
    ('D30', 'respect-player-time', '플레이어의 시간', '검수한 Unity 설명 보완본 그대로 업로드', False),
]
REVIEW_CUES = {
    'D25': [('c023', '흑백으로 보기'), ('c025', '명암과 경계 보완'), ('c027', '색 복원')],
    'D29': [('05-01', '운전 조작 보조'), ('06-01-a', '물건 배치'), ('07-03-a', '탐험과 선택')],
}

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def escape(value):
    return html.escape(str(value), quote=True)

def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def link(relative, label):
    return '<a href="../../' + escape(relative) + '">' + escape(label) + '</a>'

def main():
    rows, previews, records = [], [], []
    for episode, slug, title, change, revision in ITEMS:
        item = {'id': episode, 'slug': slug, 'title': title, 'change': change}
        if revision:
            status_path = ROOT / 'projects' / slug / 'production/clarity-v3/review-status.json'
            ready = False
            if status_path.exists():
                review = read(status_path)
                ready = review.get('status') == 'local-review-ready' and review.get('fourOutputsVerified') is True
            if ready:
                reported_directory = Path(review['localOutputDirectory'])
                if not reported_directory.is_absolute():
                    reported_directory = ROOT / reported_directory
                published_directory = ROOT / 'projects' / slug / 'production/local/clarity-v3/delivery/output' / slug
                assert reported_directory.resolve() == published_directory.resolve(), 'Unexpected review output directory'
                directory = published_directory.relative_to(ROOT)
                files = [directory / (slug + suffix) for suffix in ('.captioned.mp4', '.clean.mp4', '.ko.srt', '.en.srt')]
                assert all((ROOT / f).is_file() and (ROOT / f).stat().st_size for f in files)
                digest = sha256(ROOT / files[0])
                assert digest == review['captionedSha256'], 'Review receipt does not match delivered master'
                seconds = review['durationSeconds']
                duration = f'{round(seconds)//60}:{round(seconds)%60:02}'
                status = '수정본 완성 · 사용자 검수 대기'
                links = link(files[0].as_posix(), '전체 영상') + '<br>' + link((directory / 'index.html').as_posix(), '영상·한영 자막')
                focus = '흑백 전후의 차이와 개선 과정이 보이는지' if episode == 'D25' else '운전·정리·탐험 예시가 쉽게 이해되는지'
                edit = read(ROOT / 'projects' / slug / 'production/clarity-v3/edit-plan.json')
                cuts = {cut['id']: cut for cut in edit['cuts']}
                cue_buttons, cue_records = [], []
                for cut_id, label in REVIEW_CUES[episode]:
                    cue_seconds = cuts[cut_id]['startFrame'] / edit['fps']
                    cue_time = f'{int(cue_seconds)//60}:{int(cue_seconds)%60:02}'
                    cue_buttons.append(f'<button type="button" data-video="video-{episode}" data-seconds="{cue_seconds:.6f}">{cue_time} · {escape(label)}</button>')
                    cue_records.append({'label': label, 'cutId': cut_id, 'seconds': cue_seconds})
                previews.append(f'<section><h2>{episode} · {escape(title)}</h2><p>{escape(focus)}</p><video id="video-{episode}" controls preload="none" playsinline src="../../{escape(files[0].as_posix())}"></video><div class="cues">{"".join(cue_buttons)}</div><p>{links}</p></section>')
                item.update(status=status, durationSeconds=seconds, captionedSha256=digest, outputDirectory=directory.as_posix(), userReview='pending')
                item['reviewCues'] = cue_records
            else:
                duration, status, links = '—', '수정 제작 중', '새 검수본 준비 중'
                item.update(status=status, userReview='pending-new-version')
        else:
            progress = read(ROOT / 'projects' / slug / 'production/upload-20261029/youtube-progress.json')
            title = progress['title']
            done = progress.get('finalWorkflowSaved') is True
            pending = progress.get('remaining', [])
            if done:
                status = '비공개 업로드·설정 완료'
            elif any('AI-field' in value for value in pending):
                status = '비공개 초안 · 광고 평가·AI 표시 확인 대기'
            else:
                status = '비공개 초안 · 광고 평가·최종 저장 대기'
            package = read(ROOT / 'projects' / slug / 'production/upload-20261029/package.json')
            seconds = package['technical']['durationSeconds']
            duration = f'{round(seconds)//60}:{round(seconds)%60:02}'
            links = f'<a href="{escape(progress["url"])}">YouTube 영상</a><br><a href="{escape(progress["studioUrl"])}">Studio 설정</a>'
            item.update(title=title, status=status, userReview='upload-authorized-for-exact-master', platform=progress)
        rows.append(f'<tr><th scope="row">{episode}</th><td>{escape(title)}<small>{escape(change)}</small></td><td>{duration}</td><td>{escape(status)}</td><td>{links}</td></tr>')
        records.append(item)
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    display_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%d %H:%M (한국시간)')
    document = '''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>게임디자인 25–30 검수·업로드 현황</title>
<style>body{max-width:1200px;margin:32px auto;padding:0 20px;background:#111;color:#f5f5f5;font:16px/1.65 'Malgun Gothic',sans-serif}h1,h2,th{color:#e8cf83}a{color:#8ce0ce}small{display:block;color:#bbb;margin-top:8px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;min-width:760px}th,td{padding:14px;text-align:left;border-bottom:1px solid #444;vertical-align:top}td:nth-child(2){min-width:270px}td:last-child{min-width:130px}section{margin-top:38px;padding-top:12px;border-top:1px solid #444}video{display:block;width:100%;aspect-ratio:16/9;background:#000}p{max-width:920px}@media(max-width:600px){body{margin:20px auto;padding:0 12px}h1{font-size:25px}h2{font-size:22px}}</style>
<h1>게임디자인 25–30 검수·업로드 현황</h1><p>25·29편의 수정본과 변경한 부분을 확인할 수 있습니다. 26·27·28·30편은 승인받은 영상으로 YouTube 비공개 업로드를 진행했습니다.</p>
<div class="scroll"><table><thead><tr><th>번호</th><th>주제·변경 내용</th><th>길이</th><th>현재 상태</th><th>보기</th></tr></thead><tbody>'''
    document += ''.join(rows) + '</tbody></table></div>' + ''.join(previews)
    document += '<style>.cues{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.cues button{background:#202020;color:#e8cf83;border:1px solid #666;padding:10px 14px;border-radius:4px;font:inherit;cursor:pointer}.cues button:focus-visible{outline:2px solid #8ce0ce}</style>'
    document += '''<script>document.querySelectorAll('.cues button').forEach(button=>button.addEventListener('click',()=>{const video=document.getElementById(button.dataset.video);document.querySelectorAll('video').forEach(other=>{if(other!==video)other.pause()});video.currentTime=Number(button.dataset.seconds);video.scrollIntoView({block:'center'});video.play().catch(()=>{});}));</script>'''
    document += '<p><small>25·29편은 새 수정본을 시청한 뒤 검수 의견을 알려주세요.<br>갱신: ' + escape(display_now) + '</small></p></html>'
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'index.html').write_text(document, encoding='utf-8')
    (BATCH / 'review-hub.json').write_text(json.dumps({'updatedAt':now,'index':str(OUT.relative_to(ROOT)).replace('\\','/'),'items':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'index':str(OUT),'revisionReady':sum('captionedSha256' in r for r in records)},ensure_ascii=False))

if __name__ == '__main__':
    main()
