"""Verify FHD phone-copy timing, full decode, unchanged AAC, and caption samples."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,math
import av
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;C=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/innovation-openings-v181')
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def pin(p):
 p=Path(p)
 with p.open('rb')as f:return dict(path=str(p.resolve()),sha256=hashlib.file_digest(f,'sha256').hexdigest())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--order',type=int,required=True);a=ap.parse_args();assert a.order in [4,6,8,9,12];row=read(H/'innovation-opening-plan-v181.json')['rows'][a.order-1];out=C/row['slug'];proof=read(out/'phone-encode-v188.json');masterqa=read(out/'encoded-qa-v184.json');assert masterqa['allowedForUserReview'];video=proof['phoneCopy']['path'];assert pin(video)==proof['phoneCopy'];assert pin(proof['source']['master']['path'])==proof['source']['master'];target=out/'phone-qa-v189.json';folder=out/'phone-qa-v189';assert not target.exists()and not folder.exists();folder.mkdir()
 s=importlib.util.spec_from_file_location('phone189_packets',H/'verify-innovation-encoded-v184.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v);assert v.packets(video)==v.packets(proof['source']['master']['path']);mix=read(out/'audio-build-v182.json');render=read(out/'render-proof-v183.json');samples={min(render['introVideoFrames']-1,math.floor((x['start']+x['spokenEnd'])*30)):'intro-'+str(i)for i,x in enumerate(mix['captionCues'])}
 for i,t in enumerate([1.0,(mix['durationSeconds']-mix['introSeconds'])/2,mix['durationSeconds']-mix['introSeconds']-2]):samples[min(render['expectedTotalVideoFrames']-1,render['introVideoFrames']+math.floor(t*60))]='body-'+str(i)
 images=[];count=0
 with av.open(str(video))as c:
  st=c.streams.video[0];st.thread_count=2;assert (st.width,st.height)==(1080,1920)and st.average_rate==60
  assert abs(float(c.streams.audio[0].duration*c.streams.audio[0].time_base)-mix['durationSeconds'])<=1/24000+.000001
  for i,f in enumerate(c.decode(st)):
   assert abs(f.time-i/60)<=1/15360+.000001;count+=1
   if i in samples:
    p=folder/(samples[i]+'.jpg');f.to_image().resize((375,667),Image.Resampling.LANCZOS).save(p,quality=94);images.append(dict(frame=i,kind=samples[i],image=pin(p)))
 assert count==render['expectedTotalVideoFrames']and len(images)==len(samples);contacts=[]
 for k in range(0,len(images),8):
  im=Image.new('RGB',(1500,1394),'#14221c');dr=ImageDraw.Draw(im)
  for j,item in enumerate(images[k:k+8]):
   x=j%4*375;y=j//4*697;dr.text((x+4,y+5),str(a.order)+' '+item['kind'],fill='white');im.paste(Image.open(item['image']['path']),(x,y+30))
  p=folder/f'contact-{k//8:02}.jpg';im.save(p,quality=94);contacts.append(pin(p))
 report=dict(order=a.order,sourceEncode=pin(out/'phone-encode-v188.json'),sourceMasterQa=pin(out/'encoded-qa-v184.json'),phoneCopy=pin(video),decodedFrames=count,fullVideoDecodeAndPtsPassed=True,dimensions=[1080,1920],fps=60,aacPacketBytesAndPtsExactToMaster=True,voiceAndMusicUnmodified=True,originalMasterPreserved=True,bytes=Path(video).stat().st_size,connectorUploadLimitBytes=104857600,samples=images,contacts=contacts,technicalChecksPassed=True,actualVisualReviewRequired=True,actualPhonePlayback=False,actualFullListening=False,humanApproval=False)
 target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(order=a.order,phoneQa=pin(target),contacts=contacts)),flush=True)
if __name__=='__main__':main()
