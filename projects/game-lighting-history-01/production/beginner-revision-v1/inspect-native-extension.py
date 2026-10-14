"""Single-thread still inspection of three untouched candidate source intervals."""
import pathlib,json,subprocess,datetime,os
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/beginner-revision-v1/native-candidates'
FF='C:/Users/eazuo/miniconda3/envs/renderformer/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
rows=[('far-shadow','production/research/game-lighting-history/local/epic-lighting-techniques.mp4',1870,1954),('surface-work','production/research/game-lighting-history/local/episode01-robo-performance-v1/source.mp4',2612,2698),('light-toggle','production/research/game-lighting-history/local/epic-lighting-techniques.mp4',2342,2382)]
def main():
 assert not (O/'execution.json').exists(),'Inspect existing stills; do not repeat source sampling'
 O.mkdir(parents=True,exist_ok=True)
 state=dict(pid=os.getpid(),startedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),cpuThreads=1,gpuJobs=0,status='extracting-stills',sources=[],selectedSeconds=0,approved=False)
 def save():(O/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 save()
 font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',24)
 for key,file,a,z in rows:
  d=O/key;d.mkdir();args=[FF,'-v','error','-nostdin','-n','-threads','1','-ss',str(a),'-i',str(R/file),'-t',str(z-a),'-vf','fps=1/2,scale=960:540','-threads','1',str(d/'frame-%03d.png')]
  subprocess.run(args,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  fs=sorted(d.glob('frame-*.png'));boards=[]
  for off in range(0,len(fs),6):
   board=Image.new('RGB',(1920,1710),'#111');draw=ImageDraw.Draw(board)
   for j,f in enumerate(fs[off:off+6]):
    x=(j%2)*960;y=(j//2)*570;board.paste(Image.open(f),(x,y+30));draw.text((x+8,y+2),f'{key} source {a+(off+j)*2}s',fill='white',font=font)
   out=d/f'board-{off//6:02}.jpg';board.save(out,quality=91);boards.append(out.relative_to(R).as_posix())
  state['sources'].append(dict(key=key,path=file,startSeconds=a,endSeconds=z,sampleEverySeconds=2,images=len(fs),boards=boards,directlyViewed=False));save()
 state.update(status='complete-awaiting-direct-view',exitCode=0,finishedAt=datetime.datetime.now(datetime.timezone.utc).isoformat());save();print(json.dumps(state))
if __name__=='__main__':main()
