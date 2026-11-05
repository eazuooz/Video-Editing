"""Generate timestamped, aspect-preserved evidence sheets from source media."""
import argparse
import io
import json
from pathlib import Path
import subprocess
from fractions import Fraction
from PIL import Image, ImageDraw

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=Path)
    parser.add_argument('start', type=float)
    parser.add_argument('stop', type=float)
    parser.add_argument('stride', type=float)
    parser.add_argument('name')
    parser.add_argument('--width', type=int, default=320)
    parser.add_argument('--cols', type=int, default=4)
    args = parser.parse_args()
    metadata = json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',str(args.file)]))['streams'][0]
    rate = float(Fraction(metadata['avg_frame_rate']))
    h = round(args.width * metadata['height'] / metadata['width'])
    samples = sorted(set(round((args.start+i*args.stride)*rate) for i in range(round((args.stop-args.start)/args.stride)+1)))
    first = max(0, samples[0]-2)
    select = '+'.join(f'eq(n\\,{f-first})' for f in samples)
    raw = subprocess.check_output(['ffmpeg','-v','error','-threads','2','-ss',str(first/rate),'-i',str(args.file),'-map','0:v:0','-an','-vf',f'select={select},scale={args.width}:{h}', '-threads','1','-fps_mode','passthrough','-frames:v',str(len(samples)),'-f','rawvideo','-pix_fmt','rgb24','-'])
    stride=h*args.width*3
    sheet=Image.new('RGB',(args.cols*args.width,((len(samples)+args.cols-1)//args.cols)*(h+22)),'#141819')
    draw=ImageDraw.Draw(sheet)
    for i, sample in enumerate(samples[:len(raw)//stride]):
        im=Image.frombytes('RGB',(args.width,h),raw[i*stride:(i+1)*stride])
        x=i%args.cols*args.width; y=i//args.cols*(h+22)
        sheet.paste(im,(x,y));draw.text((x+4,y+h+2),f'{sample/rate:.3f}s   f{sample}',fill='white')
    sheet.save(args.file.parent / (args.name+'.jpg'),quality=90)

if __name__=='__main__':
    main()
