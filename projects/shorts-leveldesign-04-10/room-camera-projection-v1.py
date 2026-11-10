"""Orthographic proof for the fixed-room comparison in 04.10 P05 and P06."""

from hashlib import sha256
from io import BytesIO
import json
from math import sqrt
from pathlib import Path

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFont


PROJECT = Path(__file__).resolve().parent
OUTPUT = Path('C:/Users/1/Videos/YamyamProduction/architectural-111-20261106/shorts-leveldesign-04-10')
WIDTH, HEIGHT = 936, 340
SCALE = 57
CENTER = np.array((0, 1.1, 0))
CAMERA_DISTANCE = 30
FLOOR_COLOR = '#30424c'
NEAR_COLOR = '#ffb977'
FAR_COLOR = '#6edbbd'
PLAYER_COLOR = '#ffe194'

# X is horizontal along each lane, Y is up and Z is room depth.
# All coordinates and scale stay fixed when the camera rotates about CENTER.
BOXES = (
    ('floor', (-5, -.21, -2.9), (5, 0, 2.9), FLOOR_COLOR),
    ('near lane', (-4.5, .02, 1.2), (-.5, .10, 1.54), NEAR_COLOR),
    ('far lane', (-4.5, .02, -1.54), (-.5, .10, -1.2), FAR_COLOR),
    ('lower deck', (.65, .74, .6), (2.8, .98, 1.95), '#729bbd'),
    ('upper deck', (.65, 1.98, .6), (2.8, 2.22, 1.95), '#83bad2'),
    ('deck post', (.74, 0, 1.68), (1.02, 2.22, 1.96), '#54738b'),
    ('deck post', (2.46, 0, 1.68), (2.74, 2.22, 1.96), '#54738b'),
    ('screen', (3.5, 0, .05), (4.92, 2.8, .38), '#af7774'),
    ('player', (2.99, .26, -1.18), (3.41, .71, -.82), PLAYER_COLOR),
    ('player', (3.06, .73, -1.13), (3.34, 1.02, -.87), PLAYER_COLOR),
    ('player', (3.00, 0, -1.13), (3.14, .30, -.87), PLAYER_COLOR),
    ('player', (3.26, 0, -1.13), (3.40, .30, -.87), PLAYER_COLOR),
)
CAMERAS = {
    'side': ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    'top': ((1, 0, 0), (0, 0, -1), (0, 1, 0)),
    'isometric': (
        np.array((1, 0, -1)) / sqrt(2),
        np.array((-1, 2, -1)) / sqrt(6),
        np.ones(3) / sqrt(3),
    ),
}


def pin(path):
    return {'path': path.as_posix(), 'sha256': sha256(path.read_bytes()).hexdigest()}


def write_once(path, raw):
    if path.exists():
        assert path.read_bytes() == raw, path
        return
    with path.open('xb') as output:
        output.write(raw)


def render(camera):
    right, up, normal = map(np.asarray, camera)
    basis = np.array((right, up, normal))
    assert np.allclose((basis[:, None] * basis[None, :]).sum(axis=-1), np.eye(3))
    assert np.allclose(np.cross(right, up), normal)
    row, column = np.ogrid[:HEIGHT, :WIDTH]
    plane = (
        CENTER + normal * CAMERA_DISTANCE
        + ((column + .5 - WIDTH / 2) / SCALE)[..., None] * right
        - ((row + .5 - HEIGHT / 2) / SCALE)[..., None] * up
    )
    closest = np.full((HEIGHT, WIDTH), np.inf)
    visible = np.full((HEIGHT, WIDTH), -1)
    pixels = np.full((HEIGHT, WIDTH, 3), (13, 18, 23), dtype=np.uint8)
    lighting = np.array((.76, 1., .88))
    for index, (_, low, high, color) in enumerate(BOXES):
        entry = np.full(plane.shape, -np.inf)
        exit_at = np.full(plane.shape, np.inf)
        inside = np.ones((HEIGHT, WIDTH), dtype=bool)
        for axis, direction in enumerate(-normal):
            coordinate = plane[..., axis]
            if direction == 0:
                inside &= (coordinate >= low[axis]) & (coordinate <= high[axis])
                continue
            edges = ((low[axis] - coordinate) / direction, (high[axis] - coordinate) / direction)
            entry[..., axis] = np.minimum(*edges)
            exit_at[..., axis] = np.maximum(*edges)
        distance = entry.max(axis=-1)
        hit = inside & (distance >= 0) & (distance <= exit_at.min(axis=-1)) & (distance < closest)
        closest[hit] = distance[hit]
        visible[hit] = index
        shade = lighting[entry.argmax(axis=-1)[hit]]
        pixels[hit] = np.rint(shade[:, None] * ImageColor.getrgb(color)).astype(np.uint8)
    counts = {name: 0 for name, *_ in BOXES}
    for index, (name, *_) in enumerate(BOXES):
        counts[name] += int(np.count_nonzero(visible == index))
    return Image.fromarray(pixels), counts


def main():
    source = PROJECT / 'preproduction-v2.json'
    assert pin(source)['sha256'] == '7ebe109520821a20cb94bff9e6679eb18bfcb97417ad32a0e3ee62f6fb7159cf'
    scenes = json.loads(source.read_bytes())['sceneBeats'][4:6]
    assert [s['sceneId'] for s in scenes] == ['04-10-P05', '04-10-P06']
    assert scenes[0]['oneChangedVariable'] == '카메라 보는 방향'
    views = {name: render(camera) for name, camera in CAMERAS.items()}
    side, top, iso = (views[key][1] for key in CAMERAS)
    assert side['near lane'] > 0 and side['far lane'] == 0
    assert top['near lane'] > 0 and top['far lane'] > 0
    assert side['lower deck'] > 0 and side['upper deck'] > 0
    assert top['lower deck'] == 0 and top['upper deck'] > 0
    assert top['player'] > 0 and iso['player'] == 0

    labels = (
        ('Side View (측면)', '두 길은 겹치고 발판 높이는 나뉜다'),
        ('Top View (탑뷰)', '두 길은 나뉘고 위 발판이 아래를 가린다'),
        ('Isometric View (등각)', '발판 옆면은 보이고 벽 뒤 캐릭터는 가려진다'),
    )
    page = Image.new('RGB', (1080, 1920), '#0d1217')
    draw = ImageDraw.Draw(page)
    font_dir = Path('C:/Windows/Fonts')

    def label(x, y, value, color, size, bold=False):
        font = ImageFont.truetype(str(font_dir / ('malgunbd.ttf' if bold else 'malgun.ttf')), size)
        draw.text((x, y), value, fill=color, font=font)

    label(72, 72, '같은 방, 카메라 방향만 변경', '#ffe194', 60, True)
    label(74, 170, '직교 투영 · 동일 배치와 화면 배율', '#d9e4eb', 38)
    for (picture, _), (heading, caption), y in zip(views.values(), labels, (265, 728, 1191)):
        label(72, y, heading, 'white', 46, True)
        page.paste(picture, (72, y + 64))
        label(72, y + 403, caption, '#d9e4eb', 35)
    for x, color, name in ((74, NEAR_COLOR, '앞쪽 길'), (306, FAR_COLOR, '뒤쪽 길'), (534, PLAYER_COLOR, '캐릭터')):
        draw.rounded_rectangle((x, 1662, x + 34, 1696), radius=6, fill=color)
        label(x + 49, 1655, name, 'white', 35)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    images = []
    for name, image in (
        ('room-camera-projection-v1-1080.png', page),
        ('room-camera-projection-v1-375.png', page.resize((375, 667), Image.Resampling.LANCZOS)),
    ):
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        path = OUTPUT / name
        write_once(path, buffer.getvalue())
        images.append(pin(path))
    report = {
        'kind': 'self-authored CPU orthographic scene proof',
        'scenes': [scene['sceneId'] for scene in scenes],
        'source': pin(source),
        'implementation': pin(Path(__file__).resolve()),
        'scalePixelsPerUnit': SCALE,
        'cameraDistance': CAMERA_DISTANCE,
        'roomCenter': CENTER.tolist(),
        'cameraBases': {name: np.asarray(basis).tolist() for name, basis in CAMERAS.items()},
        'pixelCounts': {name: counts for name, (_, counts) in views.items()},
        'images': images,
        'scope': 'Analytic opaque AABB visibility. No game measurement, Unity capture, or final captions.',
    }
    path = OUTPUT / 'room-camera-projection-proof-v1.json'
    write_once(path, (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({'proof': pin(path), **report}, ensure_ascii=False))


if __name__ == '__main__':
    main()
