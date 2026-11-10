"""Pin verified follow-up masters and produce a combined local review page."""
import argparse
import html
import io
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw

from finish_review import MEDIA, sha
from plan_observations import BATCH, HERE, OUTPUT, load, save


SOURCE_CREDIT = {
    'description': 'Open Motion Project by ACCAD / The Ohio State University. Male2_G20 Reverse Spin Crescent Right. Retargeted to an Unreal mannequin and retimed for comparison.',
    'label': 'ACCAD 모션 캡처 자료',
    'url': 'https://accad.osu.edu/research/motion-lab/mocap-system-and-data',
}
LICENSE = {'description': 'Creative Commons Attribution 3.0 Unported', 'label': 'CC BY 3.0',
           'url': 'https://creativecommons.org/licenses/by/3.0/'}
STYLE = ('<style>body{background:#0a110c;color:#f3f4ef;font:17px/1.6 system-ui;margin:28px auto;max-width:1120px;'
         'padding:0 20px}h1{color:#f2d787}a{color:#a8dec1}section{border-top:1px solid #394b40;padding:14px 0}'
         'video{width:100%;max-height:76vh;background:black}nav{display:flex;flex-wrap:wrap;gap:14px;margin:14px 0}</style>')


def page(title, body):
    title = html.escape(title)
    return ('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" '
            f'content="width=device-width,initial-scale=1"><title>{title}</title>{STYLE}<h1>{title}</h1>{body}</html>')


def sample(ep):
    out = OUTPUT / ep
    d = load(out / 'delivery.json')
    master = next(q for q in d['files'] if q['kind'] == 'captioned.mp4')
    assert sha(master['path']) == master['sha256']
    times = [(f'관찰 안내 {q["id"]}', (q['startSample'] + q['endSample']) / 96000) for q in d['cues']]
    if d['pictureEdited']:
        spans = load(MEDIA / ep / 'new-pictures/manifest.json')['spans']
        interesting = {
            'A06': ('A06-cut-005', 'A06-cut-013', 'A06-cut-038'),
            'A08': ('A08-cut-003', 'A08-relocated-flow-1', 'A08-edge-pass-1',
                    'A08-cut-010', 'A08-cut-043', 'A08-cut-061'),
            'A11': ('A11-cut-005', 'A11-cut-011', 'A11-cut-015', 'A11-cut-022'),
        }[ep]
        for row in spans:
            name = row.get('reference', {}).get('id')
            if name in interesting or 'game' in row:
                times.append((name or row['game']['label'], (row['start'] + row['end']) / 120))
    folder = MEDIA / ep / 'final-qa'
    folder.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB', (1125, 239 * ((len(times) + 2) // 3)), '#0b120d')
    pen = ImageDraw.Draw(sheet)
    samples = []
    for i, (label, second) in enumerate(times):
        capture = subprocess.check_output(['ffmpeg', '-v', 'error', '-threads', '1', '-ss', f'{second:.6f}',
                    '-i', master['path'], '-frames:v', '1', '-c:v', 'png', '-threads', '1', '-f', 'image2pipe', '-'])
        image = Image.open(io.BytesIO(capture)).convert('RGB')
        assert image.size == (1920, 1080)
        path = folder / f'{i:02d}.jpg'
        image.save(path, quality=94)
        x, y = 375 * (i % 3), 239 * (i // 3)
        sheet.paste(image.resize((375, 211), Image.Resampling.LANCZOS), (x, y))
        pen.text((x + 7, y + 214), f'{i+1:02d}  {second:.2f}s', fill='white')
        samples.append({'label': label, 'seconds': second, 'file': str(path), 'sha256': sha(path)})
    sheet.save(folder / 'contact-375.jpg', quality=94)
    save(folder / 'samples.json', {'episode': ep, 'masterSha256': master['sha256'], 'samples': samples})
    print(ep, len(samples), 'encoded samples', flush=True)


def episode_page(d):
    title = d['id'] + ' · ' + d['title']
    path = OUTPUT / d['id'] / 'index.html'
    slug = d['slug']
    credits = ''.join('<p>' + html.escape(c['description']) + ' <a href="' + html.escape(c['url'], quote=True)
                      + '">' + html.escape(c['label']) + '</a></p>' for c in d.get('sourceCredits', []))
    links = ''.join(f'<a href="{slug}.{key}">{name}</a>' for key, name in (
                    ('captioned.mp4', '자막 영상'), ('clean.mp4', '무자막 영상'), ('ko.srt', '한국어 자막'), ('en.srt', '영어 자막')))
    jumps = ''.join(f'<a href="#t={p["seconds"]:.3f}" data-time="{p["seconds"]:.3f}">{html.escape(p["label"])}</a>'
                    for p in sorted(d['reviewPoints'], key=lambda p: p['seconds']))
    path.write_text(page(title, '<a href="../index.html">전체 목록</a><p>' + html.escape(d['description']) +
                         f'</p><nav>{jumps}</nav><video controls playsinline preload="metadata" src="{slug}.captioned.mp4"></video>'
                         f'<nav>{links}</nav>{credits}<script>document.querySelectorAll("a[data-time]").forEach(a=>a.onclick='
                         'e=>{e.preventDefault();document.querySelector("video").currentTime=Number(a.dataset.time)})</script>'),
                    encoding='utf8')


def build():
    prior = load(BATCH / 'review-manifest.json')
    earlier = {d['id']: d for d in prior['records']}
    checks = load(HERE / 'sampled-visual-review.json')
    observation_plan = load(HERE / 'observation-plan.json')['episodes']
    records = []
    for ep in prior['scope']:
        d = load(OUTPUT / ep / 'delivery.json')
        expected_cues = observation_plan[ep]
        actual_cues = [
            {key: cue[key] for key in expected}
            for cue, expected in zip(d['cues'], expected_cues, strict=True)
        ]
        assert actual_cues == expected_cues, f'{ep}: delivered observation cues differ from the current plan'
        for f in d['files']:
            assert sha(f['path']) == f['sha256']
        master = next(f for f in d['files'] if f['kind'] == 'captioned.mp4')
        assert checks['episodes'][ep]['masterSha256'] == master['sha256'] and checks['episodes'][ep]['passed']
        d['sampledVisualQa'] = checks['episodes'][ep]
        d['reviewPoints'] += earlier[ep].get('reviewPoints', [])
        if ep == 'A06':
            d['reviewPoints'] += [{'label': '데이지의 동작으로 비교하기', 'seconds': 78.2},
                                  {'label': '마리사의 동작으로 비교하기', 'seconds': 140.9}]
        if ep == 'A08':
            d['reviewPoints'] += [{'label': '전사 자세 기울임과 복귀', 'seconds': 86.983},
                                  {'label': '오른손이 몸 앞에서 올라가는 장면', 'seconds': 104.7}]
        if ep == 'A11':
            d['sourceCredits'] = [SOURCE_CREDIT, LICENSE]
            d['reviewPoints'].append({'label': '회전 발차기 좌우 비교', 'seconds': 110.61})
        for cue in d['cues']:
            if not cue['semanticMatch']:
                d['reviewPoints'].append({'label': '발음 확인', 'seconds': cue['startSample'] / 48000})
        episode_page(d)
        records.append(d)
    manifest = {'scope': prior['scope'], 'revision': 'review-notes-20261110', 'records': records,
                'preservedA03': prior['preservedA03'], 'url': 'http://127.0.0.1:9296/',
                'outputFolder': str(OUTPUT), 'humanReviewed': False, 'platformChanged': False}
    save(HERE / 'review-manifest.json', manifest)
    save(OUTPUT / 'review-manifest.json', manifest)
    cards = ''.join(f'<section><h2><a href="{d["id"]}/index.html">{d["id"]} · '
                    + html.escape(d['title']) + '</a></h2><p>' + html.escape(d['description']) + '</p></section>'
                    for d in records)
    (OUTPUT / 'index.html').write_text(page('애니메이션 17편 · 피드백 반영 검수',
                  '<p>각 편의 동작 안내, 1080p60 자막 영상과 무자막 영상, 한국어와 영어 자막을 모았습니다.</p>' + cards),
                  encoding='utf8')
    print('Combined review ready', len(records), manifest['url'], flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', nargs='+')
    args = parser.parse_args()
    if args.sample:
        for episode in args.sample:
            sample(episode)
    else:
        build()
