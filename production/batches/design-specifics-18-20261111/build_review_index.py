"""Build the local review page from the recorded delivery receipts."""

from html import escape
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTPUT = Path('C:/Users/1/Videos/YamyamCoding/design-specifics-18-review')


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def page(title, content):
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title>
<style>body{{margin:0;background:#0a110d;color:#f5f4ec;font:16px/1.7 system-ui,sans-serif}}
main{{max-width:1050px;padding:22px;margin:auto}}h1{{color:#f2d786;font-size:clamp(23px,5vw,36px);line-height:1.35}}
nav{{display:flex;flex-wrap:wrap;gap:8px 18px;margin:16px 0}}video{{display:block;width:100%;background:#000}}
a{{color:#94d8c9;text-underline-offset:4px}}small{{color:#b7c9bf}}li{{padding:5px 0}}summary{{cursor:pointer}}
</style></head><body><main><small>얌얌코딩 · 로컬 영상 검수</small>{content}</main></body></html>'''


def main():
    batch = read(HERE / 'batch.json')
    assert len(batch['episodes']) == 18 and batch['publicationAuthorized'] is False
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for episode in batch['episodes']:
        episode_id = episode['id']
        title = escape(episode['workingTitle'])
        receipt = episode.get('deliveryManifest')
        if not receipt:
            stages = {'voice-generated-readback-pending': '내레이션·자막 확인 중',
                      'independent-footage-and-narration-finalized': '게임 장면·대본 확정 · 편집 준비',
                      'bilingual-draft-gameplay-and-visuals-in-production': '게임 장면·시연 확인 중'}
            status = stages.get(episode.get('stage'), '한영 대본 초안' if episode.get('draftLanguages') == ['ko', 'en']
                                else '한국어 대본 초안')
            rows.append(f'<li>{episode_id} · {title} <small>{status}</small></li>')
            continue
        delivery = read(Path(receipt))
        assert delivery['episode'] == episode_id and delivery['stage'] == 'local-final-review-ready'
        folder = OUTPUT / episode_id
        for file in delivery['files']:
            assert Path(file['path']).resolve().parent == folder.resolve() and Path(file['path']).is_file()
        mp4 = f'{episode_id}.captioned.mp4'
        seconds = round((delivery['bodyFrames'] + 720) / 60)
        duration = f'{seconds // 60}분 {seconds % 60:02}초'
        controls = ''.join(f'<a href="{episode_id}.{ext}" download>{label}</a>' for ext, label in (
            ('captioned.mp4', '자막 영상'), ('clean.mp4', '무자막 영상'),
            ('ko.srt', '한국어 SRT'), ('en.srt', '영어 SRT')))
        cues = ''.join(f'<a href="{mp4}#t={cue["seconds"]}">{escape(cue["label"])}</a>'
                       for cue in delivery['reviewPoints'])
        content = (f'<nav><a href="../index.html">전체 목록</a></nav><h1>{episode_id} · {title}</h1>'
                   f'<p>{duration} · 1080p 60fps · 실제 영상 60% / 설명 40%</p>'
                   f'<video controls playsinline preload="metadata" src="{mp4}"></video>'
                   f'<nav>{controls}</nav><nav>{cues}</nav>')
        (folder / 'index.html').write_text(page(episode['workingTitle'], content), encoding='utf-8')
        rows.append(f'<li><a href="{episode_id}/index.html">{episode_id} · {title}</a> <small>검수 가능</small></li>')
    ready = sum(bool(episode.get('deliveryManifest')) for episode in batch['episodes'])
    content = f'<h1>게임 설계 디테일</h1><p>{ready}편 검수 가능 · 전체 18편</p><ul>{"".join(rows)}</ul>'
    (OUTPUT / 'index.html').write_text(page('게임 설계 디테일 · 검수', content), encoding='utf-8')
    print(OUTPUT / 'index.html')


if __name__ == '__main__':
    main()
