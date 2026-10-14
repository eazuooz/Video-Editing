from pathlib import Path
import hashlib,json,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
base=ROOT/'projects/game-lighting-history-04/production';record=json.loads((base/'renderdoc-native-framing-proof-v1.json').read_text('utf-8'))
p=ROOT/record['output']['path'];out=ROOT/'production/research/game-lighting-history/local/episode04-native-framing-v1/renderdoc125-133-framing-board.png'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(p)!=record['output']['sha256'] or out.exists():raise RuntimeError('Preserve unchanged proof and existing pixels')
frames=[0,150,300,450];expr='+'.join(f'eq(n,{n})' for n in frames)
cmd=['ffmpeg','-v','error','-threads','1','-i',str(p),'-vf',f"select='{expr}',scale=960:540",'-vsync','0','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
r=subprocess.run(cmd,capture_output=True,check=True);block=960*540*3
if len(r.stdout)!=block*4:raise RuntimeError('Four encoded frames required')
board=Image.new('RGB',(1920,1160),'#181818');draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for i,f in enumerate(frames):
 x=i%2*960;y=i//2*580;draw.text((x+16,y+7),f'native RenderDoc same-frame enlargement | local source {125+f/60:.3f}s',font=font,fill='white');board.paste(Image.frombytes('RGB',(960,540),r.stdout[i*block:(i+1)*block]),(x,y+40))
board.save(out);record.update(extractedBoard=dict(path=out.relative_to(ROOT).as_posix(),sha256=sha(out),frames=frames,allDirectlyRead=False),extractionCommand=cmd,extractionExitCode=0,wholeDecodeExitCode=0,actualProbe=dict(frames=480,width=1920,height=1080,fps=60,timeBase='1/90000',startPts=0,durationTs=720000,durationSeconds=8),newGitImages=0)
(base/'renderdoc-native-framing-proof-v1.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8');print(json.dumps(dict(boards=1,frames=4,newGitImages=0)))
