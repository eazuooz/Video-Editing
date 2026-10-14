"""Readable boards: all captions, every cut edge, motion phases and joins."""
import pathlib,json,math,datetime
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/continuity-v2';D=O/'pair/encoded-review';B=D/'review-boards'
def rd(p):return json.loads(p.read_text(encoding='utf8'))
def main():
 assert not B.exists();B.mkdir()
 data=rd(D/'execution.json');caps=rd(O/'captions.json')['cues']['ko'];rows=data['images'];font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20);boards=[]
 def make(kind,items,cols,perPage,width,height,crop=None):
  for offset in range(0,len(items),perPage):
   subset=items[offset:offset+perPage];canvas=Image.new('RGB',(width*cols,height*math.ceil(len(subset)/cols)),(20,20,20));draw=ImageDraw.Draw(canvas)
   for j,(label,row) in enumerate(subset):
    x=j%cols*width;y=j//cols*height
    with Image.open(R/row['path']) as img:
     if crop:img=img.crop(crop)
     canvas.paste(img.resize((width,height-26)),(x,y+26))
    draw.text((x+5,y+3),label,fill='white',font=font)
   file=B/f'{kind}-{offset//perPage+1:02}.png';canvas.save(file);boards.append(dict(kind=kind,path=file.relative_to(R).as_posix(),frames=[r['frame'] for _,r in subset],labels=[l for l,r in subset],directlyReviewed=False))
 cueItems=[]
 for c in caps:
  matches=[r for r in rows if c['index'] in r['cueIds']];mid=(c['startSeconds']+c['endSeconds'])*30;r=min(matches,key=lambda r:abs(r['frame']-mid));cueItems.append((f"Cue{c['index']:03} {c['key']} f{r['frame']}",r))
 make('captions',cueItems,2,24,960,134,(0,864,1920,1080))
 cutItems=[(f"f{r['frame']} {r['node']}",r) for r in rows if any(x.startswith(('cut-first:','cut-last:')) for x in r['reasons'])]
 make('cuts',cutItems,4,24,480,296)
 motionItems=[(f"f{r['frame']} {r['node']}",r) for r in rows if any(x.startswith('motion:') for x in r['reasons'])]
 make('motion',motionItems,3,12,640,386)
 changed=set(rd(O/'plan.json')['replacedVoiceKeys']);joins=[(f"f{r['frame']} {r['node']}",r) for r in rows if any(x.startswith('voice-onset:') and x.split(':',1)[1] in changed for x in r['reasons'])]
 make('joins',joins,3,12,640,386)
 mobile=[]
 for anchor in ['01-p1','02-p4','04f-p3','09-p9','09a-p5','09b-p5']:
  matching=[r for r in rows if r['node']=='e-'+anchor and r['cueIds']]
  if matching:mobile.append((anchor,matching[len(matching)//2]))
 make('mobile375',mobile,3,6,375,237)
 result=dict(createdAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),sourceSha256=data['sourceSha256'],captionCount=len(cueItems),cutEdgeImages=len(cutItems),motionPhaseImages=len(motionItems),joinImages=len(joins),boards=boards,manualReviewComplete=False)
 (B/'index.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:result[k] for k in ['captionCount','cutEdgeImages','motionPhaseImages','joinImages']}));print(len(boards),'boards')
if __name__=='__main__':main()
