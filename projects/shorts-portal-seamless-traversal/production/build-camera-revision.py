"""Splice the 751 revised frames into the preserved visual master, without audio work."""
import subprocess,json,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def run(a):
 p=subprocess.run(a,cwd=R,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode(errors='replace')[-3000:])
 return p.stdout
a=read(R/'shared/publishing/video-production-control.json')['portalTraversalShortsAuthorization']
assert a['status']=='active' and a['fullProductionAuthorized'] and P.name in a['activeSlugs']
mode=sys.argv[1] if len(sys.argv)>1 else 'cameras-v3'
part=read(L/('motion-'+mode+'-sections-execution.json'));assert part['done'] and part['result']==0 and not part['errors']
root=R/'shared/output/motion-canvas';old=root/(P.name+'-portal-traversal-v3-full.mp4');new=root/(P.name+'-'+mode+'-sections.mp4');outMode=mode+'-stable-header';out=root/(P.name+'-'+outMode+'-full.mp4');assert not out.exists()
# The headline is static throughout this explanation. Cache its fully loaded
# pixels to prevent the browser's first-frame SVG decode from flashing black.
header=L/(mode+'-static-header.png')
if not header.exists():run(['ffmpeg','-v','error','-n','-i',str(new),'-vf','select=eq(n\\,1),crop=1080:540:0:0','-frames:v','1',str(header)])
f='[0:v]split=2[a][b];[a]trim=end_frame=415,setpts=PTS-STARTPTS[p];[1:v]setpts=PTS-STARTPTS[nr];[nr][2:v]overlay=0:0:shortest=1[n];[b]trim=start_frame=1166,setpts=PTS-STARTPTS[q];[p][n][q]concat=n=3:v=1:a=0[v]'
run(['ffmpeg','-v','error','-n','-i',str(old),'-i',str(new),'-loop','1','-framerate','60','-i',str(header),'-filter_complex',f,'-map','[v]','-an','-c:v','libx264','-threads','4','-preset','fast','-qp','0','-pix_fmt','yuv420p','-r','60','-frames:v','3666',str(out)])
checks=[]
for p in [old,out]:
 raw=run(['ffmpeg','-v','error','-threads','3','-i',str(p),'-vf','select=eq(n\\,0)+eq(n\\,414)+eq(n\\,1166)+eq(n\\,3665)','-fps_mode','vfr','-an','-f','framemd5','pipe:1']).decode()
 checks.append([s.split(',')[-1].strip() for s in raw.splitlines() if s and not s.startswith('#')])
assert checks[0]==checks[1] and len(checks[0])==4
proof={'done':True,'result':0,'errors':[],'frames':3666,'firstFrame':0,'revisedRange':[415,1166],'preservedVisual':str(old),'partialRender':str(new),'staticHeader':str(header),'unchangedBoundaryPixelChecks':{'frames':[0,414,1166,3665],'identical':True},'audioChanged':False}
(L/('motion-'+outMode+'-full-execution.json')).write_text(json.dumps(proof,indent=2)+'\n',encoding='utf8')
print('Spliced camera revision; unchanged boundary pixels verified.',flush=True)
