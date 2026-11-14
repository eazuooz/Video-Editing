"""Insert a narrated 600-frame summary into a selected, verified episode."""
import argparse
import hashlib
import json
import re
import subprocess

from prepare import HERE, ROOT, WORK, OUTPUT, VOICE_LOCAL, read, save

FPS = 60
VENC = ['-c:v', 'libx264', '-threads', '4', '-preset', 'veryfast', '-crf', '18',
        '-pix_fmt', 'yuv420p', '-r', '60', '-video_track_timescale', '60000']
BULLETS = {
    'A03': ['준비 → 공격 → 후속 동작', '판정이 활성화되는 시간', '다음 입력이 가능한 시점'],
    'A04': ['공격 방향과 힘을 미리 알림', '첫 변화를 또렷하게', '읽는 데 필요한 시간'],
    'A05': ['공격하는 팔과 받치는 몸', '공격 방향과 실루엣', '타격 순간의 형태'],
    'A06': ['타격 뒤에도 이어지는 힘', '몸을 정리하는 후속 동작', '다음 입력 시점은 별도'],
    'A07': ['작아지면 사라지는 정보', '실제 플레이 크기로 확인', '전달할 몸짓을 강조'],
    'A08': ['몸 전체의 흐름', '팔다리 사이의 빈 공간', '체중을 받치는 디딤발'],
    'A09': ['눌림과 늘어남', '부피와 실루엣 확인', '필요한 순간에 집중'],
    'A10': ['맞은 위치와 충격 방향', '반응의 시작과 몸의 이동', '회복까지 이어지는 흐름'],
    'A11': ['같은 주요 자세', '준비와 타격의 시간 배분', '돌아오는 중간 경로'],
    'A12': ['눈썹 · 눈 · 입의 조합', '가까이서 세부 확인', '게임 크기에서 감정 확인'],
    'A13': ['동작과 이동 방향', '소품을 쥔 손', '장비와 글자의 반전'],
    'A14': ['각 클립의 재생 위치', '두 자세를 섞는 비율', '발과 몸의 연결 확인'],
    'A15': ['잡는 물체와 손의 역할', '가까운 손부터 자세 확인', '화면 크기에 맞춘 세부'],
    'A16': ['실제 무기의 이동 경로', '판정이 유효한 구간', '접촉과 결과의 연결'],
    'A17': ['뼈대가 만드는 움직임', '표면이 만드는 변형', '표현에 맞는 방법 선택'],
    'A18': ['회전하는 두 축', '각 축의 시간 배분', '시선과 동작의 연결'],
}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def ff(*args):
    subprocess.run(['ffmpeg', '-nostdin', '-hide_banner', '-v', 'error', '-y', '-filter_complex_threads', '2', *map(str, args)],
                   check=True, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)


def timestamp(seconds):
    millis = round(seconds * 1000)
    hours, rest = divmod(millis, 3600000)
    minutes, rest = divmod(rest, 60000)
    secs, ms = divmod(rest, 1000)
    return f'{hours:02}:{minutes:02}:{secs:02},{ms:03}'


def overlays(ep, row, folder):
    from PIL import Image, ImageDraw, ImageFont
    font = lambda size: ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf', size)
    frame = Image.new('RGBA', (1920, 1080), '#080c0a')
    draw = ImageDraw.Draw(frame)
    draw.text((92, 72), '이번 편 정리', font=font(66), fill='#f2d787')
    draw.text((92, 172), row['title'].split('|')[0].strip(), font=font(46), fill='#f3f5ef')
    for i, line in enumerate(BULLETS[ep]):
        y = 304 + i * 150
        draw.text((96, y), f'{i + 1}', font=font(46), fill='#94d8c9')
        draw.text((158, y), line, font=font(44), fill='#f3f5ef')
    frame.save(folder / 'summary-layout.png')


def finish(ep):
    import soundfile as sf
    from pathlib import Path
    control = read(ROOT / 'shared/publishing/video-production-control.json')['animationNativeClipsRevision20261114']
    assert ep in control['episodes'] and ep not in control['excludedUploaded']
    plan = read(HERE / 'plan.json')
    selected = next(row for row in plan['episodes'] if row['id'] == ep)
    baseline = selected['baseline']
    files = {row['kind']: row for row in baseline['files']}
    for file in files.values():
        path = ROOT / file['path']
        assert sha(path) == file['sha256']
    native = WORK / ep / 'native-picture-review.json'
    voice = VOICE_LOCAL / 'voice/chunks' / (ep + '-scene.wav')
    info = sf.info(voice)
    assert .3 < info.duration <= 9.65, (ep, 'Retake the summary naturally to fit ten seconds', info.duration)
    folder = WORK / ep / 'assembly'
    folder.mkdir(parents=True, exist_ok=True)
    target = OUTPUT / ep
    target.mkdir(parents=True, exist_ok=True)
    overlays(ep, selected, folder)
    clean = ROOT / files['clean.mp4']['path']
    body_frames = baseline['frames'] - 600
    body_seconds = body_frames / FPS
    source_at = 2.0
    if ep == 'A06':
        source_at = 107.3
    if ep == 'A09':
        source_at = 3.4
    layout = folder / 'summary-layout.png'
    picture = folder / 'summary-clean.mp4'
    ff('-loop', '1', '-framerate', 60, '-i', layout, '-ss', source_at, '-i', clean,
       '-filter_complex', '[1:v]scale=880:496:force_original_aspect_ratio=decrease,pad=880:496:(ow-iw)/2:(oh-ih)/2:color=0x080c0a[p];[0:v][p]overlay=948:266[v]',
       '-map', '[v]', '-frames:v', 600, '-an', *VENC, picture)
    # Keep the same approved music bed and add only the new summary voice.
    music = ROOT / 'projects' / baseline['slug'] / 'production/local/series-v1/music.wav'
    if ep == 'A03':
        music = ROOT / 'projects' / baseline['slug'] / 'production/local/grid-v1/music-stem.wav'
    assert music.is_file(), (ep, 'Original music bed missing')
    audio = folder / 'summary.m4a'
    ff('-i', voice, '-ss', min(5.0, body_seconds - 10), '-i', music,
       '-filter_complex', '[0:a]loudnorm=I=-18:TP=-2:LRA=7,aresample=48000,adelay=180|180,apad,atrim=duration=10,pan=stereo|c0=c0|c1=c0[v];[1:a]aresample=48000,atrim=duration=10,asetpts=PTS-STARTPTS,afade=t=in:d=0.12,afade=t=out:st=9.75:d=0.25[m];[v][m]amix=inputs=2:normalize=0,alimiter=limit=0.82:level=0[a]',
       '-map', '[a]', '-ar', 48000, '-ac', 2, '-c:a', 'aac', '-b:a', '192k', audio)
    caption_file = folder / 'summary.srt'
    caption_file.write_text('1\n' + timestamp(.18) + ' --> ' + timestamp(.18 + info.duration) + '\n'
                            + selected['recapKo'] + '\n', encoding='utf-8')
    # Final picture replacement and full-caption export are completed only after
    # native clips and the summary have passed their moving visual review.
    save(folder / 'summary-components.json', {'episode': ep, 'frames': 600, 'cleanPicture': str(picture),
         'audio': str(audio), 'summaryKo': selected['recapKo'], 'summaryEn': selected['recapEn'],
         'voiceSeconds': info.duration, 'voiceSha256': sha(voice), 'insertAtFrame': body_frames,
         'nativeMotionReady': ep == 'A06' or native.is_file(), 'finalAssemblyPending': True})
    print(ep, 'ten-second narrated summary components ready', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('episode')
    finish(parser.parse_args().episode)
