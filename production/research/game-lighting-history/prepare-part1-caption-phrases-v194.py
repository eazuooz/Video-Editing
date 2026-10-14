"""Light CPU preparation: literal words and exact 48px font metrics, no images."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import ImageFont
import json,hashlib,re,math
ROOT=Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-04/production'
SCRIPT=ROOT/'projects/game-lighting-history-04/script/physical-part1-guided-actions.koen.v175.json'
TARGET=P/'part1-caption-phrases-v194.json'
assert not TARGET.exists(),'Preserve existing draft'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
fontpath=Path('C:/Windows/Fonts/malgun.ttf');font=ImageFont.truetype(str(fontpath),48)
script=json.loads(SCRIPT.read_text('utf-8-sig'))
rows=[]
for scene in script['scenes']:
 text=scene['ko'];maximum=980 if scene['id'].startswith('fortnite-') else 1340
 limit=maximum-44;cache={}
 def width(t):
  if t not in cache:cache[t]=font.getlength(t)
  return cache[t]
 def wrap(tokens):
  t=' '.join(tokens)
  if width(t)<=limit:return t
  candidates=[]
  for i in range(1,len(tokens)):
   a,b=' '.join(tokens[:i]),' '.join(tokens[i:]);wa,wb=width(a),width(b)
   if max(wa,wb)<=limit:candidates.append((abs(wa-wb),a+'\n'+b))
  return min(candidates)[1] if candidates else None
 cues=[]
 for sentence in re.finditer(r'[^.!?]+(?:[.!?](?!\d)|$)',text):
  words=list(re.finditer(r'\S+',sentence.group(0)));n=len(words)
  if not n:continue
  costs=[math.inf]*(n+1);costs[n]=0;steps={}
  for i in range(n-1,-1,-1):
   for z in range(i+1,n+1):
    tokens=[w.group(0) for w in words[i:z]];t=wrap(tokens)
    if not t:continue
    lengths=[width(line) for line in t.split('\n')]
    score=180+((max(lengths)-limit*.80)/18)**2+(1600 if i and z==n and len(tokens)<2 else 0)+costs[z]
    if score<costs[i]:costs[i]=score;steps[i]=(z,t)
  assert 0 in steps,(scene['id'],sentence.group(0))
  i=0
  while i<n:
   z,t=steps[i];first=sentence.start()+words[i].start();last=sentence.start()+words[z-1].end()
   widths=[width(line) for line in t.split('\n')];boxwidth=math.ceil(max(widths)+44)
   assert boxwidth<=maximum and len(widths)<=2
   cues.append(dict(text=t,sourceCharacters=[first,last],lineWidths=widths,boxWidth=boxwidth,maximumBoxWidth=maximum,center=[960,970],fontSize=48,timingDirectlyReviewed=False,pixelsReviewed=False))
   i=z
 assert re.sub(r'\s+',' ', ' '.join(c['text'].replace('\n',' ') for c in cues)).strip()==re.sub(r'\s+',' ',text).strip(),scene['id']
 rows.append(dict(id=scene['id'],ko=text,cues=cues,allOriginalWordsPreserved=True,maximumBoxWidth=maximum))
proof=dict(preparedAt=datetime.now(timezone.utc).isoformat(),script=dict(path=SCRIPT.relative_to(ROOT).as_posix(),sha256=sha(SCRIPT)),font=dict(path=str(fontpath),sha256=sha(fontpath),size=48,family='Malgun Gothic',reason='Approved fallback; identical family to current reviewed episode04 caption encoder'),captionStyle='boxed-white-forest-v1',center=[960,970],maximumLines=2,paddingHorizontal=44,borderPixels=3,shadowOffset=[14,14],rows=rows,cues=sum(len(r['cues']) for r in rows),newImages=0,allWordsPreserved=True,allWordTimingsReviewed=False,allPixelsReviewed=False,uploaded=False)
TARGET.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps(dict(paragraphs=len(rows),cues=proof['cues'],maxPhoneBox=max(c['boxWidth'] for r in rows if r['id'].startswith('fortnite-') for c in r['cues']),newImages=0,approved=False)))
