"""Build publishing/youtube-upload.json from the collected four outputs: measured
chapters from edit-plan.json, description bodies from the KO/EN publishing drafts,
verified source credits (description-sources-last-v1), subtitle/thumbnail hashes.
Local preparation only; it records nothing as uploaded."""
from pathlib import Path
import json, hashlib, subprocess, datetime, re
R = Path(__file__).resolve().parents[3]; P = R / 'projects/steam-next-fest-ai-flood'; O = R / 'output/steam-next-fest-ai-flood'; L = P / 'production/local/edit'
def read(p): return json.loads(p.read_text(encoding='utf8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
project = read(P / 'project.json'); plan = read(L / 'edit-plan.json'); LEAD = plan['leadSeconds']
CHAPTERS = {'ko': {'01': '인트로 — 미래가 먼저 도착한 화면', '02': '넥스트 페스트에서 벌어진 일 — 데모 1,000개 → 8,000개', '03': '36%는 무엇을 센 숫자인가 — 도구 vs 결과물', '04': '만드는 쪽 — 더 많이 만들고, 더 싫어하고, 선을 긋는다', '05': '유저에게 돌아온 것 — 품질과 가격', '06': '인디 시장과 복제', '07': '앞으로 3년, 개발자의 준비'},
            'en': {'01': 'Intro — where the future arrived first', '02': 'What happened at Next Fest — 1,000 demos to 8,000', '03': 'What 36% actually counts — tool vs output', '04': 'The makers — more games, less love, lines drawn', '05': 'What players got — quality and price', '06': 'The indie market and cloning', '07': 'The next three years — what to prepare'}}
def mmss(t): t = int(round(t)); return f'{t // 60:02d}:{t % 60:02d}'
starts = {s['id']: (0.0 if i == 0 else s['paragraphs'][0]['start'] + LEAD) for i, s in enumerate(plan['scenes'])}
chapters = {lang: '\n'.join(f'{mmss(starts[sid])} {name}' for sid, name in names.items()) for lang, names in CHAPTERS.items()}
def section(md, heading):
    m = re.search(r'^## ' + re.escape(heading) + r'\s*\n(.*?)(?=^## |\Z)', md, re.S | re.M); return m.group(1).strip()
ko_md = (P / 'publishing/youtube.ko.md').read_text(encoding='utf8'); en_md = (P / 'publishing/youtube.en.md').read_text(encoding='utf8')
body = {'ko': section(ko_md, '설명(본문)') + '\n\n' + chapters['ko'], 'en': section(en_md, 'Description (body)') + '\n\n' + chapters['en']}
# refresh the measured chapter blocks in both drafts
for lang, md_path, md in [('ko', P / 'publishing/youtube.ko.md', ko_md), ('en', P / 'publishing/youtube.en.md', en_md)]:
    total = mmss(plan['totalFrames'] / 60)
    note = f'측정 완료: edit-plan.json 장면 시작 + 브랜딩 2초, 총 {total}.' if lang == 'ko' else f'Measured: edit-plan.json scene starts + 2 s branding; total {total}.'
    block = '\n'.join('- ' + line for line in chapters[lang].split('\n'))
    heading = '## 실측 챕터' if lang == 'ko' else '## Chapters'
    md = re.sub(r'(^' + re.escape(heading) + r'\s*\n).*?(?=^## |\Z)', lambda m: m.group(1) + '\n' + note + '\n\n' + block + '\n\n', md, flags=re.S | re.M)
    md_path.write_text(md, encoding='utf8', newline='\n')
video = O / 'steam-next-fest-ai-flood.captioned.mp4'
probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames,r_frame_rate:format=duration', '-of', 'json', str(video)]))
assert probe['streams'][0]['r_frame_rate'] == '60/1'
cues = lambda p: len(re.findall(r'(?m)^\d+\s*$', p.read_text(encoding='utf8')))
credits = {lang: (P / f'publishing/source-credits.{lang}.txt').read_text(encoding='utf8').strip() for lang in ['ko', 'en']}
upload = {'slug': 'steam-next-fest-ai-flood', 'status': 'prepared-local-not-uploaded', 'preparedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'video': {'name': video.name, 'source': str((L / 'steam-next-fest-captioned.mp4').relative_to(R).as_posix()), 'bytes': video.stat().st_size, 'sha256': sha(video), 'path': video.relative_to(R).as_posix(), 'seconds': float(probe['format']['duration']), 'frames': int(probe['streams'][0]['nb_frames'])},
          'qa': 'projects/steam-next-fest-ai-flood/production/review-ledger.json',
          'metadata': {'title': project['titles']['ko'], 'description': body['ko'], 'privacyStatus': 'private', 'category': 'Education', 'language': 'ko', 'madeForKids': False},
          'englishMetadata': {'title': project['titles']['en'], 'description': body['en'], 'language': 'en', 'status': 'pending'},
          'descriptionBody': body, 'sourceCredits': credits,
          'subtitles': [{'language': lang, 'path': (O / f'steam-next-fest-ai-flood.{lang}.srt').relative_to(R).as_posix(), 'sha256': sha(O / f'steam-next-fest-ai-flood.{lang}.srt'), 'cues': cues(O / f'steam-next-fest-ai-flood.{lang}.srt'), 'status': 'pending'} for lang in ['ko', 'en']],
          'thumbnail': {'path': 'projects/steam-next-fest-ai-flood/publishing/thumbnail.png', 'sha256': sha(P / 'publishing/thumbnail.png'), 'recipe': 'projects/steam-next-fest-ai-flood/publishing/thumbnail-recipe.json', 'status': 'pending'},
          'chapters': {lang: [{'time': line.split(' ', 1)[0], 'title': line.split(' ', 1)[1]} for line in chapters[lang].split('\n')] for lang in chapters},
          'actualVideoId': None, 'scheduled': False, 'privateUploadSaved': False, 'fullSettingsVerified': False,
          'openReviewItems': ['User whole listening after the line-level regeneration; 6 flagged level windows and pronunciation listening remain pending until actually done.'],
          'userAuthorization': {'message': '1번 진행해주고 업로드까지 해줘 (2026-10-21)', 'scope': 'scene 04 retake + private YouTube upload of the reviewed captioned master; public publication and scheduling stay with the user'}}
(P / 'publishing/youtube-upload.json').write_text(json.dumps(upload, ensure_ascii=False, indent=2) + '\n', encoding='utf8', newline='\n')
print('receipt prepared', upload['video']['sha256'][:16], upload['video']['seconds'], 'chapters', chapters['ko'].replace('\n', ' | '))
