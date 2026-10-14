"""Normalize selected independent source ranges; preserve originals and hashes."""
from pathlib import Path
import subprocess,json,hashlib
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
OUT=ROOT/'shared/output'/SLUG;SRC=ROOT/'shared/sources'/SLUG
def run(args):return subprocess.run(args,cwd=ROOT,check=True,creationflags=subprocess.CREATE_NO_WINDOW,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def probe(p):return json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]).stdout)
out=OUT/'selected-footage';out.mkdir(parents=True,exist_ok=True)
records=[]
for name,start,duration in [('mixandjam-movie001',0,None),('mixandjam-movie002',0,None),('wow-nyhver-120-240',36,55)]:
 source=SRC/(name+'.mp4');target=out/(name+'-silent.mp4');info=probe(source)
 args=['ffmpeg','-v','error','-n','-i',str(source)]
 if start:args+=['-ss',str(start)]
 if duration:args+=['-t',str(duration)]
 args+=['-an','-vf','setpts=PTS-STARTPTS,fps=60,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2','-c:v','libx264','-threads','4','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
 if not target.exists():run(args)
 result=probe(target);v=next(s for s in result['streams'] if s['codec_type']=='video')
 assert not any(s['codec_type']=='audio' for s in result['streams'])
 assert v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='60/1'
 records.append({'name':name,'path':target.relative_to(ROOT).as_posix(),'duration':float(result['format']['duration']),'sha256':sha(target),'sourcePath':source.relative_to(ROOT).as_posix(),'sourceSha256':sha(source),'sourceFileIn':start,'sourceFileOut':start+(duration or float(result['format']['duration'])),'audio':'omitted: source includes third-party music / not required for visual demonstration'})
(out/'selection.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(records,ensure_ascii=False))
