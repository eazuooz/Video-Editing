"""Extract unreviewed motion phases with actual retained ASS captions."""
import json,pathlib,subprocess,hashlib,shutil,sys
from PIL import Image,ImageDraw
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';B=P/'production/local/beginner-revision-v1';O=P/'production/local/continuity-v2/restored-motion';O.mkdir(parents=True,exist_ok=True)
plan=json.loads((B/'plan.json').read_text(encoding='utf8'))
keys=['02-p4','09-p9','09a-p5','04f-p3','04f-p5','09-p7']
updated='--updated' in sys.argv
if updated:
 keys=keys[:3];O=P/'production/local/continuity-v2/policy-motion';O.mkdir(parents=True,exist_ok=True)
receipt=[]
for key in keys:
 n=next(n for n in plan['nodes'] if n.get('anchor')==key and n['role']=='explanation')
 if updated:n=dict(n,framedPath=f'projects/game-lighting-history-01/production/local/continuity-v2/scenes/{key}.mp4',framedStartFrame=0)
 points=sorted(set([0,n['frames']-1]+[round((n['frames']-1)*i/7) for i in range(1,7)]))
 folder=O/key;folder.mkdir(exist_ok=True)
 ass=(B/'captions.ko.ass').relative_to(R).as_posix();fonts=(P/'production/local/final-edit-v1/fonts').relative_to(R).as_posix()
 select='+'.join(f'eq(n,{i})' for i in points)
 filt=f"trim=start_frame={n['framedStartFrame']}:end_frame={n['framedStartFrame']+n['frames']},setpts=N/(60*TB),select='{select}',setpts=PTS+{n['startFrame']/60}/TB,ass='{ass}':fontsdir='{fonts}'"
 cmd=[shutil.which('ffmpeg'),'-v','error','-nostdin','-n','-threads','2','-i',str(R/n['framedPath']),'-filter_threads','2','-vf',filt,'-fps_mode','vfr',str(folder/'%02d.png')]
 if not (folder/'08.png').exists():subprocess.run(cmd,cwd=R,check=True,creationflags=subprocess.CREATE_NO_WINDOW)
 board=Image.new('RGB',(1600,1928),'#232323');draw=ImageDraw.Draw(board)
 for i,point in enumerate(points):
  im=Image.open(folder/f'{i+1:02}.png').convert('RGB').resize((800,450));x=(i%2)*800;y=(i//2)*482
  draw.text((x+8,y+5),f'{key} frame {point} / {n["frames"]}   {point/60:.2f}s',fill='white');board.paste(im,(x,y+28))
 board.save(O/f'{key}-board.jpg',quality=92)
 receipt.append(dict(key=key,source=n['framedPath'],sourceSha256=hashlib.sha256((R/n['framedPath']).read_bytes()).hexdigest(),frames=points,captionSha256=hashlib.sha256((B/'captions.ko.ass').read_bytes()).hexdigest(),method='Eight motion phase frames with actual ASS, not continuous normal-speed playback.',reviewed=False))
(O/'extraction.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(boards=len(receipt),frames=sum(len(x['frames']) for x in receipt))))
