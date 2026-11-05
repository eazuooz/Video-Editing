from pathlib import Path
import subprocess,sys,json
H=Path(__file__).resolve().parent;D=H.parents[1]/'production/local/newsroom-v3/sources'
for name in sys.argv[1:]:
 f=D/(name+'.mp4');v=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(f)]))['streams'][0]
 assert v['width']>=1920 and v['height']>=1080
 step={'chicago':23,'bp-preview':2,'bp-work':8,'mcp':23,'graph':3}.get(name,6)
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(f),'-vf',f"fps=1/{step},scale=320:180,tile=5x6",'-frames:v','1','-threads','1',str(D/(name+'-contact.jpg'))],check=True)
 print(name,v['width'],v['height'],v.get('duration'),v.get('avg_frame_rate'),step)
