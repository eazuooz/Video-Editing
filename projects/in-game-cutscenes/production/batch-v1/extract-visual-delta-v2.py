"""Current encoded-pixel evidence for the three unchanged-clock visual fixes."""
from pathlib import Path
import hashlib,json,subprocess,sys
from PIL import Image,ImageDraw

H=Path(__file__).resolve().parent
sys.path.insert(0,str(H))
from audio_pipeline import require_authorized
from storage_paths import repo_path,relative

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def tree(terms):
 if len(terms)==1:return terms[0]
 m=len(terms)//2
 return '('+tree(terms[:m])+'+'+tree(terms[m:])+')'

def main():
 require_authorized('three-cut visual-delta encoded pixel extraction')
 plan=json.loads((H/'edit-plan.json').read_text(encoding='utf-8'))
 local=repo_path(plan['outputDir']);master=local/(plan['outputStem']+'-captioned.mp4')
 qa=local/'qa/final-v2-delta';qa.mkdir(exist_ok=True)
 inputs={'captionedSha256':sha(master),'planSha256':sha(H/'edit-plan.json'),'captionSha256':sha(local/'captions.json')}
 receipt=qa/'frame-index.json'
 if receipt.exists():
  assert json.loads(receipt.read_text(encoding='utf-8'))['inputs']==inputs,'Preserve prior evidence'
  print('Unchanged delta evidence reused');return
 cuts={c['id']:c for c in plan['cuts']};changed={'cut017','cut022','cut027'}
 groups={k:[] for k in ['captions','boundaries','marks','states']};points=set()
 def add(t,group,label,**data):
  frame=max(0,min(plan['totalFrames']-1,round(t*60)));row={'group':group,'label':label,'frame':frame,'time':frame/60,**data};groups[group].append(row);points.add(frame)
 captions=json.loads((local/'captions.json').read_text(encoding='utf-8'))['cues']
 for cue in captions:
  t=(cue['start']+cue['end'])/2
  if any(c['startFrame']/60<=t<c['endFrame']/60 for c in cuts.values()if c['id']in changed):add(t,'captions',f"Cue{cue['cue']:03d}",cue=cue['cue'],ko=cue['ko'],en=cue['en'])
 for cid in sorted(changed):
  c=cuts[cid]
  for tag,frame in [('before',c['startFrame']-1),('start',c['startFrame']+2),('end',c['endFrame']-2),('after',c['endFrame'])]:add(frame/60,'boundaries',cid+' '+tag,cut=cid)
  if cid in {'cut017','cut022'}:
   mark=c['marks'][0]
   for f in [.15,mark['t0']-.10,mark['t0']+.15,(mark['t0']+mark['t1'])/2,mark['t1']+.10]:add(c['startFrame']/60+f,'marks',cid+' target clearance',cut=cid)
 audit=json.loads((H/'mc-cue-deadline-review.json').read_text(encoding='utf-8'))
 assert audit['planSha256']==inputs['planSha256']
 for review in audit['reviews']:
  if review['cut']not in changed:continue
  c=cuts[review['cut']]
  for event in review['events']:
   t=min(event['fullyVisible']+.1,c['frames']/60-1/60)
   add(c['startFrame']/60+t,'states',review['cut']+' '+event['name'],cut=review['cut'],event=event['name'])
 frames=qa/'frames';frames.mkdir(exist_ok=True);ordered=sorted(points)
 expr=tree([f'eq(n,{n})'for n in ordered])
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-threads','2','-i',str(master),'-vf',"select='"+expr+"'",'-fps_mode','vfr','-frames:v',str(len(ordered)),'-threads','2','-compression_level','1','-n',str(frames/'%04d.png')],check=True)
 assert len(list(frames.glob('*.png')))==len(ordered)
 mapping={n:frames/f'{i+1:04d}.png'for i,n in enumerate(ordered)}
 for group,rows in groups.items():
  for width in [375,640]:
   height=round(width*9/16)
   for page in range((len(rows)+7)//8):
    board=Image.new('RGB',(width*2,(height+30)*4),'#151515');draw=ImageDraw.Draw(board)
    for i,row in enumerate(rows[page*8:(page+1)*8]):
     x,y=(i%2)*width,(i//2)*(height+30)
     with Image.open(mapping[row['frame']])as im:board.paste(im.convert('RGB').resize((width,height),Image.Resampling.LANCZOS),(x,y))
     draw.text((x+4,y+height+4),row['label'][:68]+f" {row['time']:.3f}s",fill='white')
    board.save(qa/f'{group}-{width}-{page+1:02d}.jpg',quality=93)
 out={'status':'extracted-awaiting-direct-pixel-review','inputs':inputs,'changedCuts':sorted(changed),'groups':groups,'frames':[{'frame':n,'time':n/60,'file':relative(mapping[n]),'sha256':sha(mapping[n])}for n in ordered],'baseFullReview':'production/batch-v1/pixel-review-base-v1.json','wholeListening':False}
 receipt.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'uniqueFrames':len(ordered),'groups':{k:len(v)for k,v in groups.items()},'directory':relative(qa)}))

if __name__=='__main__':main()
