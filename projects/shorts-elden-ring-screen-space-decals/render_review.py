"""Render the review cut with a CPU reference for depth-projected decals."""

import argparse
from contextlib import ExitStack
import json
import math
from pathlib import Path
import subprocess
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT / "storyboard-v1.json").read_text(encoding="utf-8"))
WIDTH, HEIGHT = 540, 960
NEAR, FAR = 0.15, 32.0
PROJECTOR_MIN = np.array([-0.76, -0.06, 0.42], dtype="f")
PROJECTOR_MAX = np.array([0.75, 0.46, 2.10], dtype="f")
STEP_MIN = np.array([-0.93, 0, 1.75], dtype="f")
STEP_MAX = np.array([1.75, 0.56, 3.56], dtype="f")
TEAL = "#72e9d1"
GOLD = "#ffe1a6"
PALE = "#f3f5f5"
SOFT = "#aebfc3"


@lru_cache
def font(size, bold=False):
    name = "malgunbd.ttf" if bold else "malgun.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def unit(vector):
    return vector / np.linalg.norm(vector)


@lru_cache
def pixel_coordinates(width, height):
    x = ((np.arange(width, dtype="f") + 0.5) / width * 2 - 1) * 0.62
    y = (1 - (np.arange(height, dtype="f") + 0.5) / height * 2) * (0.62 * height / width)
    return x[None, :, None], y[:, None, None]


def camera(t, width, height, direction=1):
    shift = math.sin(t * 0.66 + 0.45) * 1.65 * direction
    eye = np.array([1.15 + shift, 2.50, -2.32 + 0.24 * math.cos(t * 0.48)], dtype="f")
    forward = unit(np.array([0.22, 0.28, 1.46], dtype="f") - eye)
    right = unit(np.cross(np.array([0, 1, 0], dtype="f"), forward))
    upward = np.cross(forward, right)
    x, y = pixel_coordinates(width, height)
    rays = forward + x * right + y * upward
    return eye, forward, right, upward, rays


def hit_box(eye, rays, lo, hi):
    safe = np.where(abs(rays) < 1e-6, np.copysign(1e-6, rays), rays)
    ends_a = (lo - eye) / safe
    ends_b = (hi - eye) / safe
    lower = np.minimum(ends_a, ends_b)
    upper = np.maximum(ends_a, ends_b)
    entering = lower.max(axis=2)
    leaving = upper.min(axis=2)
    valid = (entering > NEAR) & (entering < leaving)
    axis = lower.argmax(axis=2)
    normal_y = np.where(axis == 1, -np.sign(rays[:, :, 1]), 0.0)
    return np.where(valid, entering, FAR), normal_y, axis


def surface_depth(eye, rays):
    ray_y = rays[:, :, 1]
    vertical = np.where(ray_y < -1e-6, ray_y, -1e-6)
    floor = np.minimum(-eye[1] / vertical, FAR)
    block, block_normal_y, block_axis = hit_box(eye, rays, STEP_MIN, STEP_MAX)
    on_block = block < floor
    eye_z = np.where(on_block, block, floor)
    surface_normal_y = np.where(on_block, block_normal_y, 1.0)
    # Perspective depth in [0, 1], separate from the recovered surface position.
    raw_depth = FAR / (FAR - NEAR) - (FAR * NEAR / (FAR - NEAR)) / eye_z
    return raw_depth, eye_z < FAR, surface_normal_y, on_block, block_axis


def reconstruct(eye, rays, raw_depth):
    eye_z = FAR * NEAR / (FAR - (FAR - NEAR) * raw_depth)
    return eye + rays * eye_z[:, :, None], eye_z


def footprint(u, v):
    heel = np.clip((1.10 - ((u / 0.36) ** 2 + ((v + 0.49) / 0.36) ** 2)) * 3, 0, 1)
    toe = np.clip((1.04 - ((u / 0.54) ** 2 + ((v - 0.30) / 0.61) ** 2)) * 3, 0, 1)
    bands = 0.45 + 0.55 * np.clip(8 * abs(np.sin(14.5 * v + 4.0 * abs(u))), 0, 1)
    pores = 0.78 + 0.22 * np.sin(43 * u + 17 * v) * np.sin(56 * v)
    return np.maximum(heel, toe) * bands * pores


def decal_mask(world, visible, normal_y, filter_normals):
    inside = visible & np.all((world >= PROJECTOR_MIN) & (world <= PROJECTOR_MAX), axis=2)
    if filter_normals:
        inside &= normal_y >= 0.7
    local = (world - PROJECTOR_MIN) / (PROJECTOR_MAX - PROJECTOR_MIN)
    u, v = local[:, :, 0], local[:, :, 2]
    first = footprint((u - 0.36) * 4.6 + (v - 0.31) * 0.80, (v - 0.31) * 5.7)
    second = footprint((u - 0.60) * 4.6 - (v - 0.72) * 0.73, (v - 0.72) * 5.7)
    return np.maximum(first, second) * inside


def to_pixel(point, eye, forward, right, upward, width, height):
    delta = point - eye
    z = float(delta @ forward)
    x = 0.5 + float(delta @ right) / (1.24 * z)
    y = 0.5 - float(delta @ upward) * width / (1.24 * height * z)
    return round(x * width), round(y * height)


def color_frame(t, width, height, mode, filter_normals=True):
    eye, forward, right, upward, rays = camera(t, width, height)
    raw, visible, normal_y, on_block, axis = surface_depth(eye, rays)
    world, eye_z = reconstruct(eye, rays, raw)
    x, y, z = (world[:, :, i] for i in range(3))
    if mode == "depth":
        near_factor = np.clip((7.6 - eye_z) / 5.2, 0, 1) * visible
        frame = np.array([14, 29, 47], dtype="f") + near_factor[:, :, None] * [109, 169, 182]
    else:
        scale = 0.88
        edge = np.minimum(np.mod(x / scale + 0.49 * (np.floor(z / scale) % 2), 1),
                          np.mod(z / scale, 1))
        tile_pattern = np.sin(np.floor(x / scale + 0.49 * (np.floor(z / scale) % 2)) * 14 +
                              np.floor(z / scale) * 9)
        grain = np.sin(x * 28 + z * 13) * np.sin(z * 30 - x * 15) * 2.5
        luma = 48 + 8 * tile_pattern + grain - 12 * (edge < 0.038)
        luma += 10 * np.exp(-0.16 * (x * x + (z - 0.5) ** 2))
        luma = np.where(on_block, np.where(normal_y > 0.7, luma + 14, 46 + grain * 0.5 - 9 * (axis == 0)), luma)
        frame = np.stack((luma * 0.90, luma * 1.14, luma * 1.22), axis=2)
        alpha = decal_mask(world, visible, normal_y, filter_normals)
        hue = np.array([215, 151, 79] if mode in ("case", "volume", "compare") else [160, 112, 63])
        frame = frame * (1 - 0.83 * alpha[:, :, None]) + hue * (0.83 * alpha[:, :, None])
        falloff = np.clip((17 - eye_z) / 13, 0, 1) * visible
        frame = 12 + (frame - 12) * falloff[:, :, None]
    img = Image.fromarray(np.clip(frame, 0, 255).astype("uint8"))
    draw = ImageDraw.Draw(img)
    project = lambda p: to_pixel(np.asarray(p, dtype="f"), eye, forward, right, upward, width, height)
    if mode == "volume":
        corners = [project([PROJECTOR_MAX[i] if key & (1 << i) else PROJECTOR_MIN[i] for i in range(3)])
                   for key in range(8)]
        for key, point in enumerate(corners):
            for axis_index in range(3):
                if not key & (1 << axis_index):
                    other = corners[key | (1 << axis_index)]
                    draw.line((point, other), fill=TEAL, width=2 if axis_index != 1 else 3)
    if mode in ("depth", "reconstruct"):
        sx, sy = project([-0.28, 0.0, 0.98])
        sx, sy = min(width - 1, max(0, sx)), min(height - 1, max(0, sy))
        draw.ellipse((sx - 8, sy - 8, sx + 8, sy + 8), outline=GOLD, width=3)
        draw.line((sx - 14, sy, sx + 14, sy), fill=GOLD, width=1)
        if mode == "reconstruct":
            point = world[sy, sx]
            label = f"X {point[0]:.2f}   Y {point[1]:.2f}   Z {point[2]:.2f}"
            label_x = max(12, min(width - 195, sx + 17))
            label_y = max(21, min(height - 40, sy - 34))
            draw.rounded_rectangle((label_x - 8, label_y - 6, label_x + 183, label_y + 21), 6,
                                   fill="#101d22", outline=TEAL)
            draw.text((label_x, label_y), label, font=font(14, True), fill=PALE)
    return img


def centered(draw, y, content, face, fill):
    draw.text((WIDTH // 2, y), content, anchor="mt", font=face, fill=fill)


def chip(draw, x, y, label, fill):
    face = font(16, True)
    dx = draw.textlength(label, font=face)
    draw.rounded_rectangle((x, y, x + dx + 20, y + 28), 8, fill="#18252a", outline="#334349")
    draw.text((x + 10, y + 1), label, font=face, fill=fill)


PANELS = {
    "beauty": ("시점 이동", "같은 바닥에 남는 발자국"),
    "case": ("자체 시연", "엘든 링 PC 프레임 분석에서 관찰된 사례"),
    "depth": ("가까울수록 밝음", "화면의 각 픽셀에 표면의 깊이가 기록됩니다"),
    "reconstruct": ("자체 시연 좌표", "화면 좌표 + 깊이  →  월드 위치"),
    "volume": ("설명용 투영 상자", "상자 안에서만 발자국 무늬 읽기"),
    "closing": ("시점 이동", "깊이 읽기  →  위치 복원  →  무늬 투영"),
}


def panel(canvas, content, x, y):
    canvas.paste(content, (x, y))
    ImageDraw.Draw(canvas).rectangle((x - 1, y - 1, x + content.width, y + content.height),
                                    outline="#35525a", width=1)


def compose(scene_index, seconds):
    scene = PLAN["scenes"][scene_index]
    t = seconds - scene["start"]
    mode = scene["mode"]
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#10171b")
    draw = ImageDraw.Draw(canvas)
    centered(draw, 59, "스크린 스페이스 데칼", font(18, True), TEAL)
    centered(draw, 94, "카메라를 돌려도", font(38, True), GOLD)
    centered(draw, 142, "발자국이 남는 이유", font(38, True), GOLD)
    draw.line((34, 201, WIDTH - 34, 201), fill="#365158", width=1)
    centered(draw, 217, scene["title"], font(24, True), PALE)
    if mode == "compare":
        # Same camera, depth buffer and texture for both panels, with only the normal test changed.
        for index, enabled in enumerate((False, True)):
            y = 267 + index * 205
            scene_img = color_frame(0.70, 472, 184, mode, enabled)
            panel(canvas, scene_img, 34, y)
            chip(draw, 46, y + 11, "방향 검사 켬" if enabled else "방향 검사 끔", TEAL if enabled else GOLD)
        centered(draw, 680, "같은 상자와 깊이 · 표면 방향 검사만 변경", font(19, True), SOFT)
    else:
        visual_t = t * 0.35 if mode in ("depth", "reconstruct", "volume") else t * 0.76
        scene_img = color_frame(visual_t, 472, 378, mode)
        panel(canvas, scene_img, 34, 266)
        label, detail = PANELS[mode]
        chip(draw, 46, 279, label, TEAL)
        centered(draw, 665, detail, font(19, True), SOFT)
    for index in range(len(PLAN["scenes"])):
        x = 35 + index * 68
        draw.rounded_rectangle((x, 726, x + 57, 730), 2, fill=TEAL if index == scene_index else "#34444a")
    return canvas


def add_captions(canvas, scene_index):
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((32, 776, 508, 861), 13, fill="#eaf2ee")
    for line_index, line in enumerate(PLAN["scenes"][scene_index]["ko"]):
        size = 23
        while draw.textlength(line, font=font(size, True)) > 425:
            size -= 1
        centered(draw, 790 + line_index * 32, line, font(size, True), "#172925")


def srt_time(seconds):
    milliseconds = round(seconds * 1000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{milliseconds // 1000:02d},{milliseconds % 1000:03d}"


def check_reference():
    eye, _, _, _, rays = camera(0.70, 260, 170)
    raw, visible, normal_y, _, _ = surface_depth(eye, rays)
    world, _ = reconstruct(eye, rays, raw)
    mask_unfiltered = decal_mask(world, visible, normal_y, False)
    mask_filtered = decal_mask(world, visible, normal_y, True)
    wall = visible & (normal_y < 0.1)
    assert np.count_nonzero(mask_unfiltered[wall] > 0.20) > 3
    assert np.count_nonzero(mask_filtered[wall] > 0.20) == 0
    assert np.count_nonzero(mask_filtered > 0.20) > 30
    assert np.max(np.abs(world[:, :, 1][visible & (normal_y > 0.7)] -
                         np.where(world[:, :, 1][visible & (normal_y > 0.7)] > 0.25, STEP_MAX[1], 0))) < 0.005


def render(output, ffmpeg):
    fps = PLAN["framesPerSecond"]
    count = round(PLAN["durationSeconds"] * fps)
    output.mkdir(parents=True, exist_ok=True)
    check_reference()
    for language in ("ko", "en"):
        text = "".join(f"{i}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n" +
                       "\n".join(s[language]) + "\n\n" for i, s in enumerate(PLAN["scenes"], 1))
        (output / f"script-{language}.srt").write_text(text, encoding="utf-8")
    for index, scene in enumerate(PLAN["scenes"]):
        sample = compose(index, scene["start"] + 0.5)
        add_captions(sample, index)
        sample.save(output / f"scene-{index + 1}.jpg", quality=93)

    with ExitStack() as stack:
        encoders = {}
        for variant in ("clean", "captioned"):
            destination = output / f"short-review-{variant}.mp4"
            command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
                       "-pix_fmt", "rgb24", "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", str(fps),
                       "-i", "-", "-an", "-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264",
                       "-preset", "veryfast", "-threads", "3", "-crf", "18", "-pix_fmt", "yuv420p",
                       "-movflags", "+faststart", str(destination)]
            encoders[variant] = stack.enter_context(subprocess.Popen(command, stdin=subprocess.PIPE))
        for frame in range(count):
            seconds = frame / fps
            index = next(i for i, s in enumerate(PLAN["scenes"]) if seconds < s["end"])
            canvas = compose(index, seconds)
            encoders["clean"].stdin.write(canvas.tobytes())
            add_captions(canvas, index)
            encoders["captioned"].stdin.write(canvas.tobytes())
        for variant, encoder in encoders.items():
            encoder.stdin.close()
            if encoder.wait() != 0:
                raise RuntimeError(f"Encoding failed: {variant}")
            print(output / f"short-review-{variant}.mp4", flush=True)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    options = parser.parse_args()
    render(options.output, options.ffmpeg)
