"""Read-only selected baseline PPT residue sweep; no production changes."""
from pathlib import Path
import json, hashlib, subprocess
from PIL import Image, ImageDraw, ImageFont
H=Path(__file__).resolve().parent;R=H.parents[3]
OUT=Path('C:/Users/1/Videos/YamyamProduction/animation-contrast-v5-work/baseline-residue-team-b')
IDS=['A06','A08','A10','A12','A14','A16','A18']
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 gm=read(H/'game-plates-caption-safe.json');em=read(H/'renderer/integration-caption-safe.json')
 bm=read(H/'baseline-review-manifest.json');tim=read(H/'baseline-sentence-timing.json');rev=read(H/'narration/source-verified-revisions.json')
 replacements={(e['id'],s['id']):s['ko']for e in rev['episodes']for s in e['changes']}
 replacements.update({(s['episode'],s['id']):s['ko']for s in rev['existingApprovedChanges']})
 samples=[]
 for ep in IDS:
  e=next(x for x in em['episodes']if x['id']==ep);g=next(x for x in gm['episodes']if x['id']==ep);b=next(x for x in bm['records']if x['id']==ep)
  mask=sorted([(r['relationFrameStart'],r['relationFrameEnd'])for r in e['rows']]+[(r['startFrame'],r['endFrame'])for r in g['pictureEdits']])
  at=120;gaps=[]
  for a,z in mask:
   a=max(a,120);z=min(z,b['frames']-600)
   if a>at:gaps.append([at,a])
   at=max(at,z)
  if at<b['frames']-600:gaps.append([at,b['frames']-600])
  src=next(x for x in b['files']if x['kind']=='clean.mp4');p=R/src['path'];assert sha(p)==src['sha256']
  sentences=next(x for x in tim['records']if x['id']==ep)['sentences']
  for k,(a,z)in enumerate(gaps):
   f=(a+z)//2;target=OUT/f'{ep}-{k+1:02}-{f}.png';seek=max(0,f//60-2)
   if not target.exists():subprocess.run(['ffmpeg','-v','error','-nostdin','-y','-threads','1','-ss',str(seek),'-i',str(p),'-filter_threads','1','-vf',f'select=eq(n\\,{f-seek*60})','-frames:v','1','-threads','1',str(target)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
   context=[{'id':s['id'],'oldStart':s['startSeconds'],'oldEnd':s['endSeconds'],'currentKo':replacements.get((ep,s['id']),s['text']),'changed':(ep,s['id'])in replacements}for s in sentences if s['endSeconds']>a/60 and s['startSeconds']<z/60]
   samples.append({'episode':ep,'oldRangeFrames':[a,z],'sampleFrame':f,'source':str(p),'sourceSha256':src['sha256'],'frame':str(target),'frameSha256':sha(target),'currentNarration':context})
 sheets=[];font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
 for n in range(0,len(samples),6):
  group=samples[n:n+6];can=Image.new('RGB',(1280,((len(group)+1)//2)*396),'#101010');d=ImageDraw.Draw(can)
  for i,s in enumerate(group):
   x=(i%2)*640;y=(i//2)*396;im=Image.open(s['frame']);assert im.size==(1920,1080);can.paste(im.resize((640,360)),(x,y));d.text((x+5,y+365),f"{s['episode']} | old {s['sampleFrame']/60:.2f}s | {s['oldRangeFrames']}",font=font,fill='white')
  p=OUT/f'contact-{n//6+1:02}.jpg';can.save(p,quality=92);sheets.append(str(p))
 report={'status':'samples-generated-inspection-pending','scope':IDS,'method':'Complement of selected safe explanation/game edits in baseline relations clock. Conservative when final speech composites may additionally cover a baseline gap. Excludes branding/member. Existing planning EDLs for unrendered episodes may be stale.','inputs':{name:sha(H/name)for name in ['game-plates-caption-safe.json','renderer/integration-caption-safe.json','narration/source-verified-revisions.json']},'samples':samples,'contactSheets':sheets,'humanFullWatch':False,'modelInspection':None}
 (H/'visual-qa/baseline-residue-team-b.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
 print(json.dumps({'samples':len(samples),'sheets':sheets},ensure_ascii=False))
if __name__=='__main__':main()
