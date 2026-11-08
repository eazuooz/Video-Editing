"""Validate the user-authorized YouTube downloads and stage identical upload files."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'shared/publishing/inflearn-game-design-345428.json'
OUT = ROOT / 'output/inflearn-game-design-345428'
course = json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
rows = []
missing = []
credits = ['재미있는 게임을 만드는 방법 — 영상별 참고자료와 출처',
           '얌얌코딩 / 인프런 무료 강의',
           '아래에는 각 수업의 기존 유튜브 게시 링크와 게시 설명을 보존했습니다.',
           '게임·음악·이미지 등 개별 자료의 크레딧과 이용 조건은 각 수업 설명을 참고해 주세요.', '']
for si, section in enumerate(course['sections'], 1):
    for li, lesson in enumerate(section['lessons'], 1):
        vid = lesson['id']
        if lesson.get('included') is False:
            continue
        source = OUT / 'videos' / f'{vid}.mp4'
        meta_file = OUT / 'videos' / f'{vid}.info.json'
        if not source.exists() or not meta_file.exists():
            missing.append(vid)
            continue
        meta = json.loads(meta_file.read_text(encoding='utf-8'))
        assert meta['channel_id'] == 'UCOgtkPoyC0VXhCs7Xk3jvjQ', vid
        assert meta['availability'] == 'public', (vid, meta['availability'])
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(source)], text=True, encoding='utf-8'))
        video = next(s for s in probe['streams'] if s['codec_type'] == 'video')
        audio = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
        assert (video['width'], video['height']) == (1920, 1080), vid
        assert video['avg_frame_rate'] == '60/1', (vid, video['avg_frame_rate'])
        duration = float(probe['format']['duration'])
        assert abs(duration - meta['duration']) < 2, vid
        filename = f'{si:02}_{li:02} ' + re.sub(r'[\\/:*?"<>|]', '', lesson['title']) + '.mp4'
        target = OUT / 'upload' / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            os.link(source, target)
        sha = hashlib.file_digest(source.open('rb'), 'sha256').hexdigest()
        rows.append(dict(id=vid, section=section['title'], title=lesson['title'], uploadFile=str(target), sourceUrl=f'https://www.youtube.com/watch?v={vid}', originalTitle=meta['title'], availability=meta['availability'], durationSeconds=duration, width=video['width'], height=video['height'], fps=video['avg_frame_rate'], audioCodec=audio['codec_name'], bytes=source.stat().st_size, sha256=sha))
        credits += [f'[{si}-{li}] {lesson["title"]}', f'https://www.youtube.com/watch?v={vid}', '기존 게시 제목: ' + meta['title'], '', meta.get('description', ''), '', '=' * 70, '']
(OUT / 'media-verification.json').write_text(json.dumps(dict(verified=rows, missing=missing), ensure_ascii=False, indent=2), encoding='utf-8')
(OUT / '영상별 참고자료와 출처.txt').write_text('\n'.join(credits), encoding='utf-8-sig')
print(json.dumps(dict(verified=len(rows), missing=missing, seconds=sum(r['durationSeconds'] for r in rows), bytes=sum(r['bytes'] for r in rows)), ensure_ascii=False))
