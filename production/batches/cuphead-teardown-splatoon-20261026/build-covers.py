"""Build only still-image Shorts covers from already-inspected adopted FHD frames.

No video decoder, renderer, image generation, platform mutation or master editing.
The output is a separate cover candidate; it is not an encoded video frame.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[3]
BATCH = Path("C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026")
OUT = BATCH / "delivery/covers"
FONT = Path("C:/Windows/Fonts/malgunbd.ttf")
WHITE = "#FFFFFF"
YELLOW = "#FFD15A"
BLACK = "#050505"
SECONDARY = "#BBBBBB"
AUTHOR = "explicit-cuphead-teardown-splatoon-20261026"

ITEMS = [
    dict(
        slug="shorts-cuphead-animation-tick", game="컵헤드", subtitle="애니메이션의 비밀",
        headline=["그림은 24프레임", "왜 매끄러울까?"],
        frame="shorts-cuphead-animation-tick/local/sources/inspect/graveyard-34-5.png",
        video="shorts-cuphead-animation-tick/local/sources/cuphead-launch-trailer.mp4",
        videoSha256="2c65d42024ad2c1a0ca62092ba8ce7ff886d0653960a86b2753c141b463e3ca4",
        seconds=34.5, sourceFrame=None, timeBasis="Existing native still named graveyard-34-5.png; inspected source timestamp34.5s. Exact decoded-frame index is not separately asserted.",
        sourceUrl="https://store.steampowered.com/app/268910/Cuphead/", segment="game",
        focus=[690, 515, 135, 145], focusMeaning="The visible Cuphead pose; editorial focus, not a measured hitbox.",
        observation="Airborne Cuphead at left and the large graveyard boss at right; both remain visible.",
        claimLimit="24fps art and60fps game are Unity's developer case-study statements. A still does not measure either clock; the lesson explains them separately.",
        rightsRecord="projects/shorts-cuphead-animation-tick/sources/selected-footage.json",
    ),
    dict(
        slug="shorts-teardown-spray-palette", game="티어다운", subtitle="스프레이의 비밀",
        headline=["칠한 건 색인데", "바뀐 건 번호?"],
        frame="shorts-teardown-spray-palette/local/qa/retry-GCuCQSyqeXM/spray-close/native-128.5.jpg",
        video="shorts-teardown-spray-palette/local/sources/teardown-GCuCQSyqeXM.mp4",
        videoSha256="99943e1f9c7bfba173aeaedc67c4702f3f957a45dea75f8390951ff88675620c",
        seconds=128.5, sourceFrame=None, timeBasis="Previously inspected native still native-128.5.jpg and selected-official-spray-source.json. Exact decoded-frame index is not separately asserted.",
        sourceUrl="https://www.youtube.com/watch?v=GCuCQSyqeXM", segment="game",
        focus=[610, 650, 235, 155], focusMeaning="Yellow spray on brick surface; editorial focus, not observed material-index data.",
        observation="Yellow spray lettering on red-brown bricks; original SPRAY CAN UI is retained.",
        claimLimit="The image is a2019 development demonstration. Material-index translation is supported separately by the developer's2020 article, not read from this frame.",
        rightsRecord="projects/shorts-teardown-spray-palette/sources/selected-footage.json",
    ),
    dict(
        slug="shorts-splatoon-ink-readability", game="스플래툰", subtitle="잉크 그래픽의 비밀",
        headline=["잉크가 반짝이면", "적을 놓친다?"],
        frame="shorts-splatoon-ink-readability/local/qa/native-focus-v1/frame-000.jpg",
        video="shorts-splatoon-ink-readability/local/sources/splatoon3-charger-mEAk2nQydPg.mp4",
        videoSha256="164a876b17ae78c4fbcbe0c3321d7ff7ae752fa806c68b62c22f9350288baa75",
        seconds=66.0, sourceFrame=3960, timeBasis="native-focus-v1/samples.json records sourceFrame3960 at60fps.",
        sourceUrl="https://www.youtube.com/watch?v=mEAk2nQydPg", segment="game-surface",
        focus=[1335, 893, 190, 95], focusMeaning="Visible bright reflection on the ink floor; editorial focus, not an enemy marker.",
        observation="Actual Splatoon3 training-area green ink and floor reflections. The player and target dummies remain visible.",
        claimLimit="Actual cover is Splatoon3. The historical visibility lesson is from Nintendo's Splatoon2 development article; this image is not evidence of an enemy being missed or a retail shader failure.",
        rightsRecord="projects/shorts-splatoon-ink-readability/sources/selected-sources.json",
    ),
    dict(
        slug="shorts-splatoon-surface-ink", game="스플래툰", subtitle="표면 페인팅의 비밀",
        headline=["벽에 남는 잉크", "어떻게 붙일까?"],
        frame="shorts-splatoon-ink-readability/local/qa/native-focus-v1/frame-014.jpg",
        video="shorts-splatoon-surface-ink/local/sources/splatoon3-charger-mEAk2nQydPg.mp4",
        videoSha256="164a876b17ae78c4fbcbe0c3321d7ff7ae752fa806c68b62c22f9350288baa75",
        seconds=70.5, sourceFrame=4230, timeBasis="Same hash-identical adopted charger source; native-focus-v1/samples.json records sourceFrame4230 at60fps.",
        sourceUrl="https://www.youtube.com/watch?v=mEAk2nQydPg", segment="game-wall",
        focus=[1090, 450, 135, 190], focusMeaning="Visible ink mark on the vertical black wall; editorial focus, not a texture-coordinate measurement.",
        observation="Green ink mark adheres to the vertical black wall while the player's own squid is near its base.",
        claimLimit="The frame demonstrates a visible wall mark only. Nintendo's public patent supports the explained approach, not a claim that this retail build uses the exact disclosed implementation.",
        rightsRecord="projects/shorts-splatoon-surface-ink/sources/selected-footage.json",
    ),
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fit(draw: ImageDraw.ImageDraw, text: str, maximum: int, max_width: int):
    for size in range(maximum, 20, -1):
        font = ImageFont.truetype(str(FONT), size)
        if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
            return font
    raise ValueError("Cover text does not fit")


def centered(draw, text, y, color, maximum, max_width=980):
    font = fit(draw, text, maximum, max_width)
    bbox = draw.textbbox((0, 0), text, font=font)
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (1080 - width) / 2 - bbox[0]
    draw.text((x, y - bbox[1]), text, fill=color, font=font)
    return {"text": text, "fontPx": font.size, "boundingBox": [x + bbox[0], y, x + bbox[2], y + height], "color": color}


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    record = {
        "schemaVersion": 1, "policy": "shorts-real-frame-covers-v1", "authorizationId": AUTHOR,
        "status": "candidate-covers-pending-parent-visual-review", "createdOnKst": "2026-10-26",
        "platformMutation": False, "existingMastersModified": False,
        "method": "CPU Pillow still-image composition from existing native source stills. No new video decoding, encoding, image generation or source extraction.",
        "dimensions": [1080, 1920], "sourceAspectRatioPreserved": True, "sourceCrop": "none",
        "mascotUsed": False, "font": str(FONT), "fontSha256": sha(FONT),
        "palette": {"background": BLACK, "body": WHITE, "heading": YELLOW},
        "layout": {"sourceRect": [12, 674, 1068, 1268], "sourceFit": "Exact16:9 fit1056x594; equal-axis0.55 scale, no stretch/crop", "focusStrokePx": 8},
        "editorialAnnotationsAreMeasurements": False,
        "mobilePreviewWidth": 375, "items": [],
    }
    previews = []
    for item in ITEMS:
        slug = item["slug"]
        metadata_path = REPO / "projects" / slug / "publishing/metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
        project = json.loads((REPO / "projects" / slug / "project.json").read_text(encoding="utf-8-sig"))
        assert project["authorization"]["id"] == AUTHOR
        timing_path = REPO / "projects" / slug / "production/visual-timing.json"
        timing = json.loads(timing_path.read_text(encoding="utf-8-sig"))
        segment = next(s for s in timing["nativeSegments"] if s["id"] == item["segment"])
        assert segment["sourceStart"] <= item["seconds"] < segment["sourceEnd"]
        frame_path = BATCH / item["frame"]
        source = Image.open(frame_path).convert("RGB")
        assert source.size == (1920, 1080)
        cover = Image.new("RGB", (1080, 1920), BLACK)
        draw = ImageDraw.Draw(cover)
        elements = [centered(draw, "얌얌코딩", 170, SECONDARY, 42), centered(draw, item["game"], 270, WHITE, 56)]
        elements.append(centered(draw, item["headline"][0], 385, WHITE, 106))
        elements.append(centered(draw, item["headline"][1], 510, YELLOW, 106))
        # Both axes use exactly0.55 scale:1056x594 retains the native16:9 ratio.
        target = source.resize((1056, 594), Image.Resampling.LANCZOS)
        cover.paste(target, (12, 674))
        draw = ImageDraw.Draw(cover)
        # The exact same isotropic scale maps the inspected native-frame focus point.
        cx, cy, rx, ry = item["focus"]
        scale = 1056 / 1920
        ring = [round(12+(cx-rx)*scale), round(674+(cy-ry)*scale), round(12+(cx+rx)*scale), round(674+(cy+ry)*scale)]
        draw.ellipse(ring, outline=YELLOW, width=8)
        elements.append(centered(draw, item["subtitle"], 1380, WHITE, 64))
        elements.append(centered(draw, "게임 속 기술을 눈으로 이해하기", 1480, SECONDARY, 39))
        path = OUT / f"{slug}.cover-v1.jpg"
        cover.save(path, "JPEG", quality=96, subsampling=0, optimize=True)
        mobile = cover.resize((375, 667), Image.Resampling.LANCZOS)
        mobile_path = OUT / f"{slug}.mobile-375.jpg"
        mobile.save(mobile_path, "JPEG", quality=94, subsampling=0)
        previews.append(mobile)
        frame_copy = dict(item)
        frame_copy.update({
            "metadataTitle": metadata["title"], "metadataPath": metadata_path.as_posix(), "metadataSha256": sha(metadata_path),
            "adoptedSegment": segment, "visualTimingPath": timing_path.as_posix(), "visualTimingSha256": sha(timing_path),
            "framePath": frame_path.as_posix(), "frameSha256": sha(frame_path), "frameDimensions": list(source.size),
            "videoPath": (BATCH / item["video"]).as_posix(), "videoHashVerification": "Previously verified selected-source record; this still-only job does not redundantly hash video media.",
            "coverPath": path.as_posix(), "coverSha256": sha(path), "mobilePreview": mobile_path.as_posix(), "mobileSha256": sha(mobile_path),
            "sourceRect": [12, 674, 1068, 1268], "focusOutputEllipse": ring, "text": elements,
            "visualReview": {"sourceFrameActuallyOpened": True, "cover1080Reviewed": False, "mobile375Reviewed": False, "humanReview": "pending"},
        })
        record["items"].append(frame_copy)
    sheet = Image.new("RGB", (375 * 4, 667), "#262626")
    for i, preview in enumerate(previews):
        sheet.paste(preview, (i*375, 0))
    sheet_path = OUT / "covers-contact-375.jpg"
    sheet.save(sheet_path, "JPEG", quality=94, subsampling=0)
    record["contactSheet"] = {"path": sheet_path.as_posix(), "sha256": sha(sheet_path), "dimensions": [1500, 667]}
    path = Path(__file__).with_name("covers.json")
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"records": path.as_posix(), "covers": [x["coverPath"] for x in record["items"]], "contactSheet": sheet_path.as_posix()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    build()
