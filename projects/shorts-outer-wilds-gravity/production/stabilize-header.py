"""Cache the fully decoded static heading; preserve the unmodified browser render."""
from pathlib import Path
import subprocess,sys,json
P=Path(__file__).resolve().parents[1];R=P.parents[1]
source=Path(sys.argv[1]);output=source.with_stem(source.stem+'-stable-header')
assert source.is_file() and not output.exists()
header=P/'production/local'/('static-header-'+source.stem+'.png')
def run(a):subprocess.run(a,check=True,cwd=R)
run(['ffmpeg','-v','error','-n','-i',str(source),'-vf',r'select=eq(n\,1),crop=1080:440:0:0','-frames:v','1',str(header)])
run(['ffmpeg','-v','error','-n','-i',str(source),'-loop','1','-framerate','60','-i',str(header),'-filter_complex','[0:v][1:v]overlay=0:0:shortest=1[v]','-map','[v]','-an','-c:v','libx264','-threads','2','-preset','fast','-crf','16','-pix_fmt','yuv420p',str(output)])
print(json.dumps({'visual':str(output),'header':str(header),'scope':'Only fixed brand/headline top 440 pixels. Dynamic term and picture labels below stay intact.'}))
