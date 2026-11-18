"""Decode candidate opening sources on CPU and preserve actual PTS contact evidence."""
from pathlib import Path
import hashlib,json
import av
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;M=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115');OUT=M/'innovation-openings-v176/source-candidates'
def main():
 assert not OUT.exists();OUT.mkdir(parents=True);plan=json.loads((H/'innovation-opening-plan-v176.json').read_text('utf8'));records=[]
 for row in plan['rows']:
  with av.open(row['introSource']['path'])as c:
   st=c.streams.video[0];st.thread_count=2;assert st.width>=1920 and st.height>=1080
   for wi,w in enumerate(row['candidateWindows']):
    samples=[]
    for j,fraction in enumerate([0,.33,.66,.98]):
     t=w['sourceStartSeconds']+w['availableSeconds']*fraction;c.seek(int(t/st.time_base),stream=st,backward=True)
     for frame in c.decode(st):
      if frame.time is not None and frame.time>=t:break
     im=frame.to_image();p=OUT/f'{row["order"]:02}-{wi}-{j}.jpg';im.resize((480,270),Image.Resampling.LANCZOS).save(p,quality=94);samples.append(dict(requestedSeconds=t,actualSeconds=frame.time,path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    records.append(dict(order=row['order'],windowIndex=wi,source=row['introSource'],window=w,decodedSize=[st.width,st.height],samples=samples))
 contacts=[]
 for start in range(0,len(records),4):
  group=records[start:start+4];im=Image.new('RGB',(1920,4*305),'#14221c');d=ImageDraw.Draw(im)
  for k,r in enumerate(group):
   for j,s in enumerate(r['samples']):
    x=j*480;y=k*305;d.text((x+6,y+5),f'{r["order"]:02} win{r["windowIndex"]} t={s["actualSeconds"]:.3f}',fill='white');im.paste(Image.open(s['path']),(x,y+30))
  p=OUT/f'contact-{start//4:02}.jpg';im.save(p,quality=94);contacts.append(str(p))
 (OUT/'observations.json').write_text(json.dumps(dict(records=records,contacts=contacts,actualVisualReviewPending=True,actualContinuousPlayback=False),ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(windows=len(records),actualSamples=sum(len(x['samples'])for x in records),contacts=contacts)))
if __name__=='__main__':main()
