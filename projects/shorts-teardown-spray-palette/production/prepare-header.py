"""Code-authored fixed brand title; independent of the voice and GPU."""
from pathlib import Path
import hashlib
import json
import argparse
from visual_revision import static_guard, execution_guard
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).resolve().parents[1]
LOCAL = P / 'production/local'
EXPECTED = Path('C:/Users/1/Videos/YamyamProduction/cuphead-teardown-splatoon-20261026/shorts-teardown-spray-palette/local')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    static_guard(require_current_selection=not args.check)
    if args.check:
        print(json.dumps({'slug':P.name,'revision':'spray-palette-v1','inputGuard':'passed','imagesGenerated':0}));return
    execution_guard()
    assert LOCAL.resolve() == EXPECTED.resolve()
    target = LOCAL / 'static-header-v1.png'
    assert not target.exists(), 'Preserve an existing header; version changed titles.'
    config = json.loads((P / 'production/visual-config.json').read_text(encoding='utf8'))
    image = Image.new('RGB', (1080, 440), '#000000')
    draw = ImageDraw.Draw(image)
    fontpath = 'C:/Windows/Fonts/malgunbd.ttf'
    for line, y, fill in zip(config['headline'], [105, 230], ['#FFFFFF', '#FFD25A']):
        size = 91
        font = ImageFont.truetype(fontpath, size)
        while draw.textbbox((0, 0), line, font=font)[2] > 940:
            size -= 1
            font = ImageFont.truetype(fontpath, size)
        draw.text((540, y), line, font=font, fill=fill, anchor='mm', stroke_width=1)
    brand = ImageFont.truetype(fontpath, 34)
    draw.text((540, 374), '얌얌코딩  ·  게임 속 기술', font=brand, fill='#B8C3BC', anchor='mm')
    image.save(target)
    receipt = {'path': str(target), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
               'size': [1080, 440], 'text': config['headline'], 'font': fontpath,
               'status': 'generated; final encoded mobile inspection still required'}
    (LOCAL / 'header-build.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(receipt, ensure_ascii=False))

if __name__ == '__main__':
    main()
