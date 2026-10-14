"""One CPU decode of the actual silent proof; all boards remain local-only."""
from pathlib import Path
import hashlib,json,subprocess,os
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/game-lighting-history-04/production'
record=json.loads((BASE/'additive-prerequisite-render-execution-v1.json').read_text('utf-8'))
p=ROOT/record['output']['path'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if sha(p)!=record['output']['sha256'] or record['status']!='complete-silent-proof-awaiting-pixel-review':raise RuntimeError('Current proof hash/completion required')
folder=ROOT/'production/research/game-lighting-history/local/episode04-prerequisite-pixels-v1'
if folder.exists() and any(folder.iterdir()):raise RuntimeError('Preserve prior extracted proof pixels')
folder.mkdir(exist_ok=True)
ids=['vsm-address','upscaling-grid','visibility-interpolation','mobile-local-memory','path-probability','path-survival','reconstruction-boundary','direct-versus-transparent','generated-frame-count','display-transform','capture-dataflow']
# Interior samples avoid the unapproved nominal8.8s boundaries. Actual final
# narration timing will be independently measured and checked at exact cuts.
frames=[min(5797,i*527+n) for i in range(11) for n in [24,168,336,504]]
expr='+'.join(f'eq(n,{n})' for n in frames)
cmd=['ffmpeg','-v','error','-threads','1','-i',str(p),'-vf',f"select='{expr}',scale=960:540",'-vsync','0','-an','-pix_fmt','rgb24','-f','rawvideo','pipe:1']
proc=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
raw,error=proc.communicate()
if proc.returncode or len(raw)!=len(frames)*960*540*3:raise RuntimeError('Frame decode failed '+error.decode(errors='replace'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24);boards=[];block=960*540*3
for i,id in enumerate(ids):
    board=Image.new('RGB',(1920,1160),'#181818');draw=ImageDraw.Draw(board)
    for j in range(4):
        k=i*4+j;im=Image.frombytes('RGB',(960,540),raw[k*block:(k+1)*block]);x=(j%2)*960;y=(j//2)*580
        draw.text((x+16,y+7),f'{i+1:02d} {id} | encoded frame {frames[k]} | {frames[k]/60:.3f}s',font=font,fill='white');board.paste(im,(x,y+40))
    out=folder/f'{i+1:02d}-{id}.png';board.save(out)
    boards.append(dict(id=id,path=out.relative_to(ROOT).as_posix(),sha256=sha(out),encodedFrames=frames[i*4:i*4+4],directlyRead=False))
manifest=dict(schemaVersion=1,currentProof=record['output'],extractionCommand=cmd,actualExitCode=0,cpuThreads=1,gpuJobs=0,uniqueFrames=len(frames),boards=boards,all11BoardsDirectlyRead=False,allFinalPixelsReviewed=False,wholeMovingProofsApproved=False,gitPolicy='All extracted/contact PNGs local-only. No essential-image exception.',newGitImages=0)
out=BASE/'additive-prerequisite-encoded-pixels-v1.json';out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(uniqueFrames=len(frames),boards=len(boards),record=str(out),allFinalPixelsReviewed=False,newGitImages=0)))
