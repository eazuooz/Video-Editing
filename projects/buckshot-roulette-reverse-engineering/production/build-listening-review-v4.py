"""Build local v4 listening clips and an honest, existence-filtered review page.

CPU only. --prepare writes an empty/pending index without touching audio.
--build extracts five complete new paragraphs and four retained ASR candidates.
--master additionally decodes the same intervals from the actual final MP4 AAC;
source auditions and encoded-mix clips are labeled separately. No listening
approval, media upload, narration mutation, or original-file replacement occurs.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
OUT = PROJECT / 'production/local/audio-v4'
FOLDER = OUT / 'review/listening'
FFMPEG = Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')
NEW_IDS = {'01-01', '01-02', '02-01', '02-02', '08-01'}
CANDIDATES = [
    {'id': 'cuffs-word', 'baselineId': '04-02', 'word': '건너뜁니다', 'asr': '건너집니다', 'baselineWordSeconds': [124.78, 125.72], 'baselineContextSeconds': [121.28, 129.28]},
    {'id': 'new-loading', 'baselineId': '04-02', 'word': '새 장전으로', 'asr': '3장전으로', 'baselineWordSeconds': [127.42, 128.36], 'baselineContextSeconds': [123.92, 131.92]},
    {'id': 'live-round', 'baselineId': '04-03', 'word': '실탄의', 'asr': '7탄의', 'baselineWordSeconds': [141.88, 142.76], 'baselineContextSeconds': [138.38, 146.38]},
    {'id': 'project-particle', 'baselineId': '06-01', 'word': '프로젝트에', 'asr': '프로젝트의', 'baselineWordSeconds': [199.24, 200.08], 'baselineContextSeconds': [195.74, 203.74]},
]


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            result.update(chunk)
    return result.hexdigest()


def key(entry):
    return f'{entry["scene_id"]}-{int(entry["paragraph"]):02}'


def clock(value):
    return f'{int(value // 60):02}:{value % 60:05.2f}'


def planned_clips(timing):
    new = {key(e): e for e in timing['entries']}
    old = {key(e): e for e in read(PROJECT / 'production/local/audio-v1/narration.timing.json')['entries']}
    mapping = read(PROJECT / 'planning/revision-v4-workflow.json')['audioReuseMapping']
    back = {f'{m["baselineScene"]}-{int(m["baselineParagraph"]):02}': new[f'{m["scene"]}-{int(m["paragraph"]):02}'] for m in mapping if m['mode'] == 'reuse'}
    rows = []
    for ident, entry in new.items():
        if ident in NEW_IDS:
            rows.append({'id': 'new-' + ident, 'group': 'new', 'title': f'{ident} · {entry["scene_title"]}',
                         'sourceStart': entry['start'], 'sourceEnd': entry['end'], 'text': entry['display_text'],
                         'reason': '새로 생성한 문단 전체: 누락·반복, 용어 발음, 문장 흐름을 확인합니다.'})
    for candidate in CANDIDATES:
        entry = back[candidate['baselineId']]
        shift = entry['start'] - old[candidate['baselineId']]['start']
        rows.append(dict(candidate, group='retained', title=candidate['word'],
                         sourceStart=candidate['baselineContextSeconds'][0] + shift,
                         sourceEnd=candidate['baselineContextSeconds'][1] + shift,
                         wordSeconds=[value + shift for value in candidate['baselineWordSeconds']],
                         baselineToV4ShiftSeconds=shift,
                         text=f'원고: {candidate["word"]} / 이전 자동 인식: {candidate["asr"]}',
                         reason='기존 음성을 그대로 사용한 구간의 발음 확인 후보입니다. 실제 발음 오류로 확정한 항목은 아닙니다.'))
    review_path = OUT / 'review/source-asr-direct-review.json'
    if review_path.exists():
        for row in rows:
            row['candidateNotes'] = [f'{clock(c["sourceSeconds"][0] - row["sourceStart"])} 부근 · 원고 {c["expected"]} / 자동 인식 {c["recognized"]}'
                                     for c in read(review_path).get('newSpeechCandidates', [])
                                     if row['id'] == 'new-' + c['paragraph']]
    return rows


def render_clip(row, kind, source, source_hash, offset, previous):
    ident = f'{kind}-{row["id"]}'
    destination = FOLDER / (ident + '.wav')
    begin, end = row['sourceStart'] + offset, row['sourceEnd'] + offset
    signature = {'sourceSha256': source_hash, 'begin': begin, 'end': end, 'kind': kind}
    old = previous.get(ident)
    if old and old.get('signature') == signature and destination.exists() and digest(destination) == old.get('sha256'):
        return dict(old, **{k: v for k, v in row.items() if k != 'id'})
    if destination.exists():
        raise FileExistsError(f'Existing audition differs; preserve it and inspect before regeneration: {destination}')
    filters = f'atrim=start={begin:.9f}:end={end:.9f},asetpts=PTS-STARTPTS'
    if kind == 'source':
        filters += ',volume=3.5dB,aresample=192000,alimiter=limit=0.7943282347:level=false:latency=true,aresample=48000'
    else:
        filters += ',aresample=48000'
    command = [str(FFMPEG), '-hide_banner', '-nostdin', '-v', 'error', '-threads', '2', '-i', str(source),
               '-vn', '-af', filters, '-t', f'{end-begin:.9f}', '-ac', '1' if kind == 'source' else '2', '-ar', '48000', '-c:a', 'pcm_s24le', '-n', str(destination)]
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    if result.returncode:
        raise RuntimeError(result.stderr[-3000:])
    import soundfile as sf
    info = sf.info(destination)
    assert abs(info.duration - (end - begin)) < .025 and info.frames > 0
    return dict(row, id=ident, kind=kind, path=destination.as_posix(), audioStart=begin, audioEnd=end,
                signature=signature, sha256=digest(destination), durationSeconds=info.duration,
                sampleRate=info.samplerate, subtype=info.subtype, humanListening=False,
                processing='Source audition copy only: +3.5 dB constant gain and -2 dB oversampled limiter, mono PCM24; original narration untouched.' if kind == 'source' else 'Actual final MP4 AAC decoded and excerpted to stereo PCM24; no gain or limiter added.')


def write_page(report):
    clips = [c for c in report['clips'] if Path(c['path']).is_file()]
    sections = []
    groups = [('source', 'new', '새 문단 · 소스 음성'), ('source', 'retained', '기존 발음 후보 · 소스 음성'),
              ('final', 'new', '새 문단 · 완성 영상 AAC'), ('final', 'retained', '기존 발음 후보 · 완성 영상 AAC')]
    for kind, group, title in groups:
        selected = [c for c in clips if c['kind'] == kind and c['group'] == group]
        if not selected:
            continue
        cards = []
        for clip in selected:
            href = quote(Path(clip['path']).relative_to(FOLDER).as_posix())
            notes = ''.join(f'<p class="time">{html.escape(note)}</p>' for note in clip.get('candidateNotes', []))
            cards.append(f'<article><h3>{html.escape(clip["title"])}</h3><p class="time">{clock(clip["audioStart"])}–{clock(clip["audioEnd"])} · {clip["durationSeconds"]:.1f}초</p><p>{html.escape(clip["reason"])}</p>{notes}<audio controls preload="none" src="{href}"></audio><details><summary>대본 / 확인 내용</summary><p>{html.escape(clip["text"])}</p></details><a href="{href}">음성 파일 열기</a></article>')
        sections.append(f'<section><h2>{title} <span>{len(selected)}개</span></h2><div class="grid">{"".join(cards)}</div></section>')
    pending = '<p class="notice">현재 생성된 청취 클립이 없습니다. 새 음성이 완성되면 실제 존재하는 파일만 여기에 표시됩니다.</p>' if not clips else ''
    page = f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>얌얌코딩 · REA 제작기 v4 음성 검수</title>
<style>body{{margin:0;background:#101010;color:#f6f5ef;font-family:system-ui,"Malgun Gothic",sans-serif;line-height:1.65}}main{{max-width:1100px;margin:auto;padding:32px 22px 70px}}h1,h2{{color:#f1c862;line-height:1.35}}h1{{font-size:clamp(25px,4vw,40px)}}h2{{margin-top:38px;font-size:23px}}h2 span,.time{{color:#bab8b0;font-size:14px}}.brand{{letter-spacing:.13em;font-size:12px;color:#f1c862}}.notice{{padding:16px;border:1px solid #555}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,310px),1fr));gap:18px}}article{{padding:18px;border-top:2px solid #a58b4e;background:#191919}}h3{{margin:0 0 6px;font-size:18px}}audio{{width:100%;margin:12px 0}}a{{color:#f1c862}}summary{{cursor:pointer}}details p{{font-size:15px}}.sub{{max-width:800px;color:#d1d0c9}}</style>
<main><p class="brand">YAMYAM CODING / LOCAL REVIEW</p><h1>REA 제작기 v4 · 음성 검수</h1>
<p class="sub">새 문단 5개의 전체 발화와 기존 발음 후보 4개를 구분해서 확인하는 페이지입니다. 지금 열 수 있는 파일은 {len(clips)}개입니다.</p>
<p class="notice">전체 인간 청취와 최종 사용자 검수는 아직 완료되지 않았습니다. 자동 인식의 차이는 확인 후보이며, 발음 오류를 확정한 결과가 아닙니다.</p>
<p class="sub"><b>소스 음성</b>은 원본을 보존한 청취용 사본입니다. 일정한 +3.5 dB와 피크 제한을 적용했고 게임 소리는 없습니다. <b>완성 영상 AAC</b>가 표시되면 해당 최종 MP4의 실제 소리를 그대로 추출한 항목입니다.</p>
{pending}{''.join(sections)}<p class="time">파일 생성 시각: {html.escape(report['generatedAt'])} · 외부 업로드 없음</p></main></html>'''
    (FOLDER / 'index.html').write_text(page, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--prepare', action='store_true')
    mode.add_argument('--build', action='store_true')
    parser.add_argument('--master', type=Path, help='Actual current final MP4; optional final AAC excerpts')
    parser.add_argument('--final-offset', type=float, default=2.0)
    args = parser.parse_args()
    FOLDER.mkdir(parents=True, exist_ok=True)
    ledger = FOLDER / 'listening-clips.json'
    report = read(ledger) if ledger.exists() else {'schemaVersion': 1, 'revision': 'v4', 'clips': []}
    report.update(generatedAt=datetime.now(timezone.utc).isoformat(), humanListening=False, userApproval=False, externalUpload=False)
    if args.build:
        source = OUT / 'narration.wav'
        assert source.is_file() and FFMPEG.is_file()
        timing = read(OUT / 'narration.timing.json')
        rows = planned_clips(timing)
        old = {c['id']: c for c in report['clips']}
        source_hash = digest(source)
        clips = [render_clip(row, 'source', source, source_hash, 0, old) for row in rows]
        report['sourceAudioSha256'] = source_hash
        if args.master:
            master = args.master.resolve()
            master.relative_to((ROOT / 'output/buckshot-roulette-reverse-engineering-v4').resolve())
            assert master.is_file() and master.suffix.lower() == '.mp4'
            master_hash = digest(master)
            clips.extend(render_clip(row, 'final', master, master_hash, args.final_offset, old) for row in rows)
            report.update(masterPath=master.as_posix(), masterSha256=master_hash, finalOffsetSeconds=args.final_offset)
        else:
            clips.extend(c for c in report['clips'] if c['kind'] == 'final')
        report['clips'] = clips
    report['clips'] = [c for c in report['clips'] if Path(c['path']).is_file()]
    report['actualClipCount'] = len(report['clips'])
    ledger.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    write_page(report)
    print(json.dumps({'index': str(FOLDER / 'index.html'), 'actualClipCount': report['actualClipCount'], 'gpuUsed': False, 'humanListening': False}))


if __name__ == '__main__':
    main()
