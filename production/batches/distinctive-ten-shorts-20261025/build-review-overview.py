"""Collect exact local deliverables for the selected ten, without cloud actions."""
from pathlib import Path
import datetime
import html
import json

BATCH = Path(__file__).resolve().parent
ROOT = BATCH.parents[2]
MEDIA = Path('C:/Users/1/Videos/YamyamProduction/distinctive-ten-shorts-20261025')
DEST = MEDIA / 'delivery'

def read(path):
    return json.loads(path.read_text(encoding='utf8'))

def main():
    rows, cards = [], []
    for selected in read(BATCH / 'batch.json')['projects']:
        slug = selected['slug']
        project = ROOT / 'projects' / slug
        manifest = read(project / 'project.json')
        state_path = project / 'production/local/finite-finalizer-v1/state.json'
        state = read(state_path) if state_path.exists() else {}
        delivery = state.get('delivery')
        record = dict(order=selected['order'], slug=slug, title=selected['title'],
                      currentStage=state.get('currentStage'), productionStatus=state.get('status', manifest['status']),
                      humanReview='pending', uploadAuthorized=False)
        if delivery and Path(delivery['captioned']).is_file():
            record.update(delivery=delivery)
            folder = Path(delivery['directory']).relative_to(DEST).as_posix()
            mp4 = folder + '/captioned.mp4'
            files = ' · '.join('<a href="' + html.escape(folder + '/' + name, quote=True) + '">' + label + '</a>'
                               for name, label in [('clean.mp4','자막 없는 영상'),('captions.ko.srt','한국어 자막'),('captions.en.srt','영어 자막')])
            media = '<video controls preload="metadata" playsinline src="' + html.escape(mp4, quote=True) + '"></video>'
            metadata = '<details><summary>제목·설명·파일 확인</summary><h3>' + html.escape(delivery['title']) + '</h3><pre>' + html.escape(delivery['description']) + '</pre><p class="hash">SHA256 ' + html.escape(delivery['masterSha256']) + '</p></details>'
            content = media + '<p><a href="' + html.escape(mp4, quote=True) + '">전체 자막 영상 열기</a></p><p>' + files + '</p><p class="status">완성 파일 생성 · 사용자 최종검수 대기</p>' + metadata
        else:
            content = '<p class="status">제작·보완 중</p>'
        cards.append('<article><h2>' + str(selected['order']) + '. ' + html.escape(selected['title']) + '</h2>' + content + '</article>')
        rows.append(record)
    DEST.mkdir(parents=True, exist_ok=True)
    count = sum('delivery' in r for r in rows)
    document = '<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>얌얌코딩 · 게임 기술 쇼츠 10편</title><style>body{background:#090b0a;color:#fff;font:17px/1.6 "Malgun Gothic",sans-serif;margin:0;padding:28px}main{max-width:1200px;margin:auto}h1{color:#ffd25a}h2{font-size:19px;min-height:60px}h3{font-size:17px}a{color:#76d8cc}section{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}article{border-top:2px solid #46524c;padding:10px 0}video{width:100%;max-height:640px;background:#000}pre{white-space:pre-wrap;font:14px/1.5 inherit;overflow-wrap:anywhere}.hash{font-size:12px;overflow-wrap:anywhere}.status{color:#d0d6d2}details{margin-top:20px}summary{cursor:pointer}@media(max-width:450px){body{padding:16px}section{display:block}article{margin:24px 0}}</style><main><h1>게임 개발 기술 쇼츠 · 10편</h1><p>' + str(count) + '/10편 완성 파일 생성. 1080×1920 · 60fps · BGM · 한영 자막.</p><p>화면·음성·제목을 최종 확인해 주세요. 사용자 승인이나 업로드는 아직 진행하지 않았습니다. 실제 청취 확인이 필요한 구간은 각 제작 검수 기록에 남아 있습니다.</p><section>' + ''.join(cards) + '</section></main></html>'
    (DEST / 'index.html').write_text(document, encoding='utf8')
    # The per-project finalizer also owns index.html. Preserve this aggregate
    # snapshot under a separate stable name while the remaining queue runs.
    (DEST / 'review-ten.html').write_text(document, encoding='utf8')
    (DEST / 'overview.json').write_text(json.dumps(dict(updatedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),generatedVideos=count,requestedVideos=10,rows=rows), ensure_ascii=False, indent=2)+'\n',encoding='utf8')
    print(json.dumps({'generatedVideos':count,'requestedVideos':10,'index':str(DEST/'index.html')}))

if __name__ == '__main__':
    main()
