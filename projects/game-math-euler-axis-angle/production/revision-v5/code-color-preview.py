"""Extract bounded actual encoded FHD60 examples with unchanged global captions."""
from pathlib import Path
import importlib.util, json, subprocess
from PIL import Image, ImageDraw, ImageFont

SPEC=importlib.util.spec_from_file_location('m04_code_color',Path(__file__).with_name('code-color-render.py'))
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

def seconds(s):
    h,m,s=s.split(':');return int(h)*3600+int(m)*60+float(s)
def main():
    M.selected();ass=M.CAPTIONS.read_text(encoding='utf-8-sig');samples=[]
    for sid,index in [('15',0),('15',3),('15',4),('25',2),('25',4)]:
        r=M.read(M.OUT/f'{sid}.json');frame=r['stateBoundaries'][index]+72
        assert frame<r['stateBoundaries'][index+1]
        global_frame=r['globalStartFrame']+frame;t=global_frame/60
        clip=M.ROOT/r['output'];assert M.sha(clip)==r['outputSha256']
        p=M.OUT/f'qa-{sid}-{index}-captioned.png'
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',f'{frame/60:.12f}','-i',str(clip),'-vf',f'setpts=PTS-STARTPTS+{global_frame}/60/TB,ass={M.rel(M.CAPTIONS)}','-an','-frames:v','1','-fps_mode','passthrough','-update','1',str(p)]
        M.run(cmd,M.OUT/f'qa-{sid}-{index}.log')
        im=Image.open(p);assert im.size==(1920,1080)
        mobile=M.OUT/f'qa-{sid}-{index}-375.png';im.resize((375,211),Image.Resampling.LANCZOS).save(mobile)
        cue=[]
        for line in ass.splitlines():
            if not line.startswith('Dialogue: 12,'):continue
            parts=line.split(',',9)
            if seconds(parts[1])<=t<seconds(parts[2]):cue.append(parts[-1])
        assert cue,('Sample must include actual canonical caption',sid,index,t)
        samples.append(dict(scene=sid,state=index,localFrame=frame,globalFrame=global_frame,globalSeconds=t,native=M.rel(p),nativeSha256=M.sha(p),mobile=M.rel(mobile),mobileSha256=M.sha(mobile),canonicalCue=cue,command=cmd))
    board=Image.new('RGB',(1125,482),'#171A20');d=ImageDraw.Draw(board);f=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',18)
    for i,s in enumerate(samples):
        x=(i%3)*375;y=(i//3)*241
        d.text((x+8,y+2),f"Scene {s['scene']} / cue {s['state']+1}",fill='white',font=f)
        board.paste(Image.open(M.ROOT/s['mobile']),(x,y+28))
    b=M.OUT/'qa-mobile-board.png';board.save(b)
    M.save(M.OUT/'preview.json',dict(masterCaptionAss=M.rel(M.CAPTIONS),masterCaptionAssSha256=M.sha(M.CAPTIONS),fixedCaptionCenter=[960,970],fixedCaptionFontSize=48,samples=samples,mobileBoard=M.rel(b),mobileBoardSha256=M.sha(b),scope='Five actual encoded samples only; no whole final-master or listening approval'))
    print(json.dumps(dict(samples=len(samples),mobileBoard=M.rel(b))))
if __name__=='__main__':main()
