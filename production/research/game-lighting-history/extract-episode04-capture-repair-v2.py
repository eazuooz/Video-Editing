from pathlib import Path
import hashlib,json,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'production/research/game-lighting-history/local/episode03-chapter-render-v4/renders/additive-prerequisite-capture-repair-v2-project.mp4'
out=ROOT/'production/research/game-lighting-history/local/episode04-prerequisite-capture-repair-v2.png'
if out.exists():raise RuntimeError('Preserve existing scoped repair pixels')
frames=[24,168,336,504];expr='+'.join(f'eq(n,{n})' for n in frames)
cmd=['ffmpeg','-v','error','-threads','1','-i',str(p),'-vf',f"select='{expr}',scale=960:540",'-vsync','0','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
r=subprocess.run(cmd,capture_output=True,check=True)
block=960*540*3
if len(r.stdout)!=block*4:raise RuntimeError('Four exact frames required')
board=Image.new('RGB',(1920,1160),'#181818');draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
for i,f in enumerate(frames):
 x=i%2*960;y=i//2*580;draw.text((x+16,y+7),f'capture-dataflow label repair | encoded frame {f} | {f/60:.3f}s',font=font,fill='white');board.paste(Image.frombytes('RGB',(960,540),r.stdout[i*block:(i+1)*block]),(x,y+40))
board.save(out)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=dict(proof=dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)),board=dict(path=out.relative_to(ROOT).as_posix(),sha256=sha(out)),frames=frames,extractionCommand=cmd,exitCode=0,cpuThreads=1,gpuJobs=0,allSamplesDirectlyRead=False,finalNarratedQaApproved=False,newGitImages=0)
(ROOT/'projects/game-lighting-history-04/production/additive-prerequisite-capture-repair-v2.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(frames=4,newGitImages=0,board=str(out))))
