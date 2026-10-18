"""Six exact5second slides, with current script captions. Silent layout proof only."""
from pathlib import Path
import json, subprocess, hashlib, re
from PIL import ImageFont
R=Path(__file__).resolve().parents[3];P=R/'projects/ai-games-showcase-2026'
O=P/'production/local/tool-slides';D=R/'output/ai-games-showcase-2026/planning'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
plan=read(P/'planning/production-plan.json');narration=read(P/'script/narration.ko.json');aliases=read(P/'script/pronunciation.json')['aliases']
assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']=='ai-games-showcase-2026'
font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',48)
def display(text):
 for canonical,spoken in sorted(aliases.items(),key=lambda x:len(x[1]),reverse=True):text=re.sub(r'(?<![가-힣A-Za-z0-9])'+re.escape(spoken),lambda _:canonical,text)
 return text
def wrap(text):
 if font.getlength(text)<=1500:return text
 words=text.split();best=min(range(1,len(words)),key=lambda i:abs(font.getlength(' '.join(words[:i]))-font.getlength(' '.join(words[i:]))))
 lines=[' '.join(words[:best]),' '.join(words[best:])];assert max(font.getlength(x) for x in lines)<=1728
 return r'\N'.join(lines)
def stamp(seconds):return f'0:{seconds//60:02d}:{seconds%60:02d}.00'
header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Malgun Gothic,48,&H00FFFFFF,&H00FFFFFF,&H00151F1B,&H00151F1B,-1,0,0,0,100,100,0,0,3,12,0,2,96,96,110,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
cards=[s for s in plan['scenes'] if s.get('developmentSummary')]
events=[];concat=[]
for i,s in enumerate(cards):
 text=display(next(n for n in narration['scenes'] if n['id']==s['id'])['lines'][s['developmentSummary']['paragraph']-1])
 events.append(f'Dialogue: 2,{stamp(i*5)},{stamp((i+1)*5)},Caption,,0,0,0,,{{\\pos(960,970)}}{wrap(text)}')
 concat.extend([f"file 'slide-{i+1:02d}.png'",'duration 5'])
concat.append("file 'slide-06.png'")
(O/'slides.ffconcat').write_text('\n'.join(concat)+'\n',encoding='utf-8')
(O/'captions.ass').write_text(header+'\n'.join(events)+'\n',encoding='utf-8')
out=D/'tool-summary-30s-silent.mp4';rel=(O/'captions.ass').relative_to(R).as_posix()
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(O/'slides.ffconcat'),'-vf',f"fps=60,ass='{rel}'",'-frames:v','1800','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','4','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],cwd=R,check=True)
probe=read_probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]))
v=probe['streams'][0];assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',1800)
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True,capture_output=True)
for i in range(6):
 for mobile in [False,True]:
  target=O/f"qa-{i+1:02d}-{'375' if mobile else '1080'}.png"
  cmd=['ffmpeg','-v','error','-y','-ss',str(i*5+2),'-i',str(out),'-frames:v','1']
  if mobile:cmd+=['-vf','scale=375:-1']
  subprocess.run(cmd+[str(target)],check=True)
receipt={'scope':'Six tool-slide visual preview only; no voice or whole-video approval','seconds':30,'fps':60,'frames':1800,'captionStyle':'boxed-white-forest-v1:960,970/48px/max2lines','sourcePptx':'output/ai-games-showcase-2026/planning/ai-games-development-tools-v2.pptx','pptxSha256':hashlib.sha256((D/'ai-games-development-tools-v2.pptx').read_bytes()).hexdigest(),'outputSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'probe':probe,'decode':'pass','visualReview':'pending'}
(O/'preview-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'preview':str(out),'frames':1800,'voice':False}))
