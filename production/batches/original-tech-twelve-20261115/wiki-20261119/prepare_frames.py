"""Extract two explicative frames from each version-8 captioned master."""

import hashlib
import json
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'local-final-review-manifest-v8.json'
PLAN = HERE.parent / 'innovation-opening-plan-v181.json'
OUTPUT = Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/wiki-20261119')

# Times are in the pre-intro body. Only our native demos or diagrams are used.
SELECTIONS = {
    1: [(35.4, '공격할 차례와 대기할 차례가 나뉩니다. Unity 모형에서 상대 선택과 공격 허가를 따로 보세요.'), (58.8, '대상을 바라본 채 옆 입력을 주면 상대를 기준으로 위치가 달라집니다. Unity 모형입니다.')],
    2: [(48.2, '같은 캐릭터와 공간에서 고정 구도와 조작 시점을 비교합니다. Unity 모형입니다.'), (82.8, '카메라가 뒤로 빠지면 같은 캐릭터 주변의 공간이 더 넓게 들어옵니다. Unity 모형입니다.')],
    3: [(84.3, '작은 표면이 서로 다른 방향을 향합니다. 보는 방향에 따라 밝아지는 면을 비교하세요.'), (108.8, '언덕을 비스듬히 바라볼 때 무늬가 길어지는 구간의 반짝임을 따로 다룹니다.')],
    4: [(46.2, '후보 중 물과 길의 점을 제외합니다. 실제 나무를 놓기 전에 빈 곳을 먼저 고릅니다.'), (55.5, '남은 후보에 실제 오브젝트를 놓고 지형 높이와 방향을 맞춥니다.')],
    5: [(65.0, '현재 위치에 해당하는 이전 프레임의 표본을 다시 찾는 재투영을 설명합니다.'), (85.5, '현재 주변 색 범위를 기준으로 지나치게 다른 과거 색의 영향을 줄입니다.')],
    6: [(51.5, '부착 가능 영역의 면 위에서 기준점과 가까운 후보를 고르는 자체 도식입니다.'), (77.1, '후보가 플레이어의 진행 방향과 실제 주변 지형에 맞는지 검사합니다.')],
    7: [(30.2, '한 덩어리에서 큰 조각과 작은 파편으로 이어지는 계층을 보여 줍니다.'), (85.5, '연결이 끊어진 조각과 아직 지지를 받는 조각을 구분합니다.')],
    8: [(65.4, '뒤쪽 입자가 앞쪽 입자의 이전 위치를 따라가며 움직임이 차례로 전달됩니다.'), (98.3, '중심선을 따라 표면 방향을 정합니다. 굽은 곳에서 방향이 뒤집히는지 살펴보세요.')],
    9: [(18.3, '파일 읽기, 압축 해제, 사용 가능한 자원으로의 변환을 다른 단계로 나눕니다.'), (47.2, '같은 이동 경로에서 자료 준비 방법에 따른 차이를 보여 주는 가상 실험입니다.')],
    10:[(27.5, '체력은 근접 마무리 보상, 탄약은 연료를 사용하는 전기톱 보상으로 구분한 교육용 도식입니다.'), (8.5, '낮은 체력에서 거리를 줄일지 기다릴지 비교하는 자체 시연입니다. 모형의 값은 실제 게임 수치가 아닙니다.')],
    11:[(31.4, '물체의 움직임과 불이 붙는 상태의 변경을 서로 다른 질문으로 분리합니다.'), (58.8, '예제의 불과 물은 공통 상태와 조건에 따라 반응합니다. 설명용 규칙입니다.')],
    12:[(24.8, '일반 주행과 반중력 주행은 같은 접촉을 다르게 처리합니다.'), (56.0, '조건을 만족한 접촉 뒤 회전과 가속이 이어지는 자체 비교 모형입니다.')],
}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def exact_frame(master, seconds):
    target = round(seconds * 60)
    with av.open(str(master)) as container:
        stream = container.streams.video[0]
        stream.thread_count = 2
        assert stream.average_rate == 60
        container.seek(int((target / 60) / stream.time_base), stream=stream)
        for frame in container.decode(stream):
            if frame.time is not None and round(frame.time * 60) >= target:
                assert round(frame.time * 60) == target
                return frame.to_image(), float(frame.time), frame.pts, str(stream.time_base)
    raise ValueError(f'Frame {target} is missing in {master}')


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(SOURCE.read_text(encoding='utf-8-sig'))
    plans = json.loads(PLAN.read_text(encoding='utf-8-sig'))['rows']
    frames = []
    for row, plan in zip(manifest['projects'], plans, strict=True):
        order = row['order']
        assert plan['slug'] == row['slug']
        master_ref = row['artifacts']['captioned']
        master = Path(master_ref['path'])
        assert sha(master) == master_ref['sha256']
        beats = json.loads(Path(plan['baselineFilm']['path']).read_text(encoding='utf-8-sig'))['identity']['beats']
        for number, (body_seconds, caption) in enumerate(SELECTIONS[order], start=1):
            beat = next(item for item in beats if item['start'] <= body_seconds < item['end'])
            assert beat['kind'] in ('native', 'pairedNative', 'diagram'), (order, body_seconds, beat['kind'])
            wanted = row['addedOpeningSeconds'] + body_seconds
            image, seconds, pts, time_base = exact_frame(master, wanted)
            path = OUTPUT / f'ot12-{order:02d}-figure-{number}.jpg'
            image.resize((720, 1280), Image.Resampling.LANCZOS).save(path, quality=91)
            frames.append(dict(order=order, figure=number, slug=row['slug'], actualMaster=master_ref,
                               bodySeconds=body_seconds, actualSeconds=seconds, pts=pts, timeBase=time_base,
                               image=str(path), imageSha256=sha(path), caption=caption, beatKind=beat['kind'],
                               beatName=beat.get('key') or beat.get('mode'),
                               imageRights='Yamyam Coding explanatory diagram or Unity demonstration retained from its captioned master. No third-party gameplay or Kyoto performance is reproduced in these stills.',
                               edit='Full portrait frame, resized from 1080×1920 to 720×1280 without crop or added marks'))
    for start in range(0, len(frames), 8):
        sheet = Image.new('RGB', (1060, 1000), '#14221c')
        draw = ImageDraw.Draw(sheet)
        font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 15)
        for index, item in enumerate(frames[start:start + 8]):
            x, y = (index % 4) * 265 + 4, (index // 4) * 500
            draw.text((x + 4, y + 5), f"{item['order']:02d} · {item['figure']} · {item['actualSeconds']:.2f}s", font=font, fill='white')
            with Image.open(item['image']) as image:
                sheet.paste(image.resize((257, 457), Image.Resampling.LANCZOS), (x, y + 30))
        sheet.save(OUTPUT / f'contact-{start // 8 + 1}.jpg', quality=92)
    (OUTPUT / 'frames.json').write_text(json.dumps(frames, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(f'Extracted {len(frames)} captioned frames from {len(plans)} masters')


if __name__ == '__main__':
    main()
