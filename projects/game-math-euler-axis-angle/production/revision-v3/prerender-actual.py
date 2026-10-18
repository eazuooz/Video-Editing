"""Render inspected source cuts while voice alignment runs; final assembly revalidates."""
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).parent
s=importlib.util.spec_from_file_location('edit',HERE/'render-edit.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.selected();plan=m.read(m.P/'sources/cut-plan-v3.json');media=m.read(m.P/'sources/media-revision-v3.json');annotations=m.read(m.P/'sources/annotation-plan-v3.json')
assert annotations['status']=='source-keyframes-reviewed'
allowed={'02','11','14','17'};selected=set(sys.argv[1:]) or allowed;assert selected<=allowed
for sid in sorted(selected):
 p=plan['scenes'][sid];source=plan['sources'][p['sourceId']];src=m.R/source['file'];digest=m.sha(src)
 assert digest==next(x for x in media['sources'] if x['id']==p['sourceId'])['downloadedSha256']
 v=m.probe(src);assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'60/1')
 for i,(a,b) in enumerate(p['ranges'],1):
  m.selected();c=dict(id=f'{sid}-cut-{i:02}',scene=sid,sourceId=p['sourceId'],sourceStart=a,frames=round(b*60)-round(a*60),credit=source['credit'])
  ass=m.E/(c['id']+'.ass');out=m.E/(c['id']+'.mp4');receipt=m.E/(c['id']+'.json')
  body,_=m.cut_ass(c,annotations);ass.write_text(body,encoding='utf8');vf='fps=60,setsar=1,ass='+ass.relative_to(m.R).as_posix()
  sig=dict(sourceSha256=digest,sourceStart=a,frames=c['frames'],assSha256=m.sha(ass),videoFilter=vf,codec=m.ENC,nativeSpeed=1,upscale=False)
  if not(out.exists() and receipt.exists() and m.read(receipt)==sig):
   m.run(['ffmpeg','-hide_banner','-y','-loglevel','warning','-ss',str(a),'-i',str(src),'-an','-vf',vf,'-frames:v',str(c['frames']),*m.ENC,str(out)],c['id'])
   receipt.write_text(json.dumps(sig,indent=2)+'\n')
  m.check(out,c['frames']);print('Prepared',c['id'],flush=True)
