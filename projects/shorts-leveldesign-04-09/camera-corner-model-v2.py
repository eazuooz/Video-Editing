"""Render two CPU previews of a fixed corner scene with different camera positions."""

import argparse
from hashlib import sha256
from io import BytesIO
import json
from math import radians, tan
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


SIZE = (640, 360)
VERTICAL_FOV = 45
EYE = (-0.95, 1.65, 2.6)
REAR_CAMERA = (1.08, 1.65, -1.7)
TARGET = (0.85, 0.9, 7.0)
WALL = ((-3.0, 0.0, 3.6), (-0.32, 2.7, 3.9))
SCENE = (
    ("floor", (-25, -0.1, -2), (25, 0, 24), (62, 77, 90)),
    ("wall", *WALL, (126, 140, 153)),
    ("player", (-1.2, 0.43, 2.36), (-0.70, 1.28, 2.67), (116, 224, 194)),
    ("player", (-1.12, 1.26, 2.38), (-0.78, 1.58, 2.63), (147, 242, 214)),
    ("player", (-1.18, 0, 2.37), (-1.00, 0.45, 2.65), (92, 187, 163)),
    ("player", (-0.90, 0, 2.37), (-0.72, 0.45, 2.65), (92, 187, 163)),
    ("enemy", (0.46, 0.48, 6.79), (1.24, 1.43, 7.21), (238, 126, 105)),
    ("enemy", (0.63, 1.39, 6.84), (1.07, 1.80, 7.16), (255, 163, 142)),
    ("enemy", (0.53, 0, 6.81), (0.77, 0.51, 7.19), (209, 104, 91)),
    ("enemy", (0.93, 0, 6.81), (1.17, 0.51, 7.19), (209, 104, 91)),
)


def render_view(origin):
    width, height = SIZE
    vertical_scale = tan(radians(VERTICAL_FOV) / 2)
    horizontal_scale = vertical_scale * width / height
    u = ((np.arange(width) + 0.5) / width * 2 - 1) * horizontal_scale
    v = (1 - (np.arange(height) + 0.5) / height * 2) * vertical_scale
    dx, dy = np.meshgrid(u, v)
    rays = np.stack((dx, dy, np.ones_like(dx)), axis=-1)

    depth = np.full((height, width), np.inf)
    owners = np.full((height, width), -1, dtype=np.int16)
    pixels = np.full((height, width, 3), (29, 38, 49), dtype=np.uint8)
    for index, (name, lower, upper, color) in enumerate(SCENE):
        first = (np.array(lower) - origin) / rays
        second = (np.array(upper) - origin) / rays
        entry_faces = np.minimum(first, second)
        near = entry_faces.max(axis=-1)
        far = np.maximum(first, second).min(axis=-1)
        visible = (near >= 0.08) & (near <= far) & (near < depth)
        depth[visible] = near[visible]
        owners[visible] = index
        if name == "floor":
            world_x = origin[0] + dx[visible] * near[visible]
            world_z = origin[2] + near[visible]
            checker = (np.floor(world_x) + np.floor(world_z)) % 2
            shade = 0.89 + 0.11 * checker
        else:
            shade = np.take((0.78, 1.0, 0.91), entry_faces.argmax(axis=-1)[visible])
        if name == "wall":
            wall_x = origin[0] + dx[visible] * near[visible]
            wall_y = origin[1] + dy[visible] * near[visible]
            seams = (np.mod(wall_x, 0.56) < 0.014) | (np.mod(wall_y, 0.42) < 0.014)
            shade = shade * np.where(seams, 0.76, 1.0)
        pixels[visible] = (np.array(color) * shade[:, None]).astype(np.uint8)

    counts = {
        name: sum(int(np.count_nonzero(owners == i)) for i, box in enumerate(SCENE) if box[0] == name)
        for name in ("player", "enemy", "wall")
    }
    return Image.fromarray(pixels), counts


def compose(eye_view, rear_view):
    image = Image.new("RGB", (1080, 1920), "#11161B")
    draw = ImageDraw.Draw(image)
    white, light, teal, red, gold = "#FFFFFF", "#D5DFE6", "#9AEBD0", "#FFAC9A", "#FFE194"

    def label(x, y, text, size, color=light, bold=False):
        font_path = "C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf"
        draw.text((x, y), text, font=ImageFont.truetype(font_path, size), fill=color, anchor="lt")

    def plan(position):
        x, _, z = position
        return 530 + 104 * x, 684 - 42 * (z + 1.7)

    def dot(position, color):
        x, y = plan(position)
        draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill="#1E262E", outline=color, width=5)

    label(65, 72, "같은 모퉁이의 두 카메라", 62, gold, True)
    label(69, 176, "벽과 두 캐릭터는 같은 위치에 있습니다", 38)
    draw.rounded_rectangle((58, 258, 1022, 728), radius=18, fill="#1E262E", outline="#526575", width=2)
    label(89, 284, "위에서 본 배치", 42, white, True)
    left, bottom = plan(WALL[0])
    right, top = plan(WALL[1])
    draw.rectangle((left, top, right, bottom), fill="#81909E")
    label(230, 480, "가림벽", 34)

    fraction = (WALL[0][2] - EYE[2]) / (TARGET[2] - EYE[2])
    eye_hit = tuple(start + fraction * (end - start) for start, end in zip(EYE, TARGET))
    draw.line((plan(EYE), plan(eye_hit)), fill=red, width=8)
    draw.line((plan(REAR_CAMERA), plan(TARGET)), fill=teal, width=8)
    dot(EYE, red)
    dot(REAR_CAMERA, teal)
    dot(TARGET, gold)
    label(382, 548, "눈 위치", 32, red, True)
    label(677, 651, "뒤쪽 카메라", 32, teal, True)
    label(658, 302, "적", 32, gold, True)

    for y, title, view, color in (
        (748, "눈 위치 · 벽이 적을 가림", eye_view, red),
        (1234, "뒤쪽 카메라 · 벽 옆으로 적이 보임", rear_view, teal),
    ):
        label(82, y, title, 40, color, True)
        image.paste(view.resize((704, 396), Image.Resampling.BILINEAR), (188, y + 58))
    label(69, 1761, "같은 시야각으로 계산한 자체 모형", 33)
    return image, eye_hit


def write_exact(path, data):
    if path.exists():
        assert path.read_bytes() == data, path
    else:
        with path.open("xb") as handle:
            handle.write(data)
    return {"path": path.as_posix(), "sha256": sha256(data).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    eye_view, eye_counts = render_view(EYE)
    rear_view, rear_counts = render_view(REAR_CAMERA)
    assert eye_counts["enemy"] == eye_counts["player"] == 0
    assert rear_counts["enemy"] > 0 and rear_counts["player"] > 0
    image, eye_hit = compose(eye_view, rear_view)
    previews = []
    for width in (1080, 375):
        display = image.resize((width, round(1920 * width / 1080)), Image.Resampling.LANCZOS)
        buffer = BytesIO()
        display.save(buffer, format="PNG")
        previews.append(write_exact(args.output / f"04-09-camera-corner-{width}px-v2.png", buffer.getvalue()))

    source = Path(__file__).resolve()
    source_pin = {"path": source.relative_to(Path.cwd()).as_posix(), "sha256": sha256(source.read_bytes()).hexdigest()}
    proof = {
        "topicId": "04.09", "sceneId": "04-09-P05", "oneChangedVariable": "Camera position",
        "fixedScene": SCENE, "fixedSceneSHA256": sha256(json.dumps(SCENE).encode()).hexdigest(),
        "fixedProjection": {"width": SIZE[0], "height": SIZE[1], "verticalFovDegrees": VERTICAL_FOV,
                            "heading": "+Z", "near": 0.08},
        "eyeCamera": {"position": EYE, "visiblePixels": eye_counts, "targetRayWallCrossing": eye_hit},
        "rearCamera": {"position": REAR_CAMERA, "visiblePixels": rear_counts},
        "scope": "CPU pixel visibility in the authored scene. The geometry and projection are identical across the two images.",
        "editableSource": source_pin, "layoutPreviews": previews,
    }
    raw = (json.dumps(proof, ensure_ascii=False, indent=2) + "\n").encode()
    proof_pin = write_exact(args.output / "04-09-camera-corner-proof-v2.json", raw)
    print(json.dumps({"proof": proof_pin, "editableSource": source_pin, "layoutPreviews": previews,
                      "eyeVisiblePixels": eye_counts, "rearVisiblePixels": rear_counts}))


if __name__ == "__main__":
    main()
