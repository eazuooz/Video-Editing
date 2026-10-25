"""Evidence for unchanged audio/captions/body plus actual opening frame review."""
from render import *
from PIL import Image,ImageDraw,ImageFont
import io
def stream_hash(path,kind,cut=None):
 cmd=['ffmpeg','-v','error','-nostdin']
 if cut is not None:cmd+=['-ss',str(cut)]
 cmd+=['-i',str(path),'-map',f'0:{kind}:0','-c','copy']
 if kind=='v':cmd+=['-bsf:v','h264_mp4toannexb,filter_units=remove_types=7|8|9']
 cmd+=['-f','hash','-hash','sha256','-'];return subprocess.check_output(cmd,text=True).strip()
def frame(file,t,width=480):
 return Image.open(io.BytesIO(subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(file),'-frames:v','1','-vf',f'scale={width}:-1','-f','image2pipe','-vcodec','png','pipe:1']))).convert('RGB')
def run(id,prior_qa=None):
 pp=B/'plans'/f'{id}.json';p=read(pp);W=Path(p['work']);D=R/p['output'];old=R/p['oldOutput'];slug=p['slug'];r=read(W/'render-receipt.json');results=[]
 for kind in ['clean','captioned']:
  f=D/f'{slug}.{kind}.mp4';before=old/f.name;v=next(x for x in probe(f)['streams'] if x['codec_type']=='video')
  assert int(v['nb_frames'])==p['totalFrames'] and v['r_frame_rate']=='60/1' and abs(float(v['duration'])-p['seconds'])<.001
  audioOld=stream_hash(before,'a');audioNew=stream_hash(f,'a');assert audioOld==audioNew
  bodyOld=stream_hash(before,'v',r['copyBodyFromSeconds']);bodyNew=stream_hash(f,'v',r['copyBodyFromSeconds']);assert bodyOld==bodyNew,(id,kind,'body bitstream mismatch')
  log=W/f'decode-{kind}.log'
  # Captioned master is decoded in full. Clean body is an exact previously
  # checked bitstream, so decode its changed prefix plus join, and verify the
  # remaining VCL payload against the previous master rather than duplicating
  # the full-body decoding work.
  args=['-hwaccel','cuda','-hwaccel_output_format','cuda','-i',f]
  if kind=='clean' or prior_qa is not None:args+=['-t',r['copyBodyFromSeconds']+1]
  if prior_qa is not None:
   previous=next(x for x in prior_qa['results'] if x['kind']==kind)
   assert previous['unchangedBodyVclHash']==bodyNew
  ff(args+['-map','0:v:0','-map','0:a:0','-f','null','-'],log,W)
  assert not log.read_text('utf8').strip(),log.read_text('utf8')[-1000:]
  results.append(dict(kind=kind,dimensions=[v['width'],v['height']],fps=v['r_frame_rate'],frames=int(v['nb_frames']),duration=float(v['duration']),audioPacketHash=audioNew,unchangedBodyVclHash=bodyNew,bodyStartFrame=r['copyBodyFromFrame'],decode='full-pass' if kind=='captioned' and prior_qa is None else 'changed-prefix-and-join-pass; unchanged-body-bitstream-verified',priorFullDecodeEvidence='qa-initial.json' if prior_qa else None))
 for lang in ['ko','en']:assert sha(D/f'{slug}.{lang}.srt')==sha(old/f'{slug}.{lang}.srt')
 # Changed sections and exact joins, at both delivery and mobile sizes.
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',17)
 times=[]
 for s in p['segments']:
  g=s['guides'][0];times += [s['start']+.15,s['start']+(g['from']+g['to'])/2,s['end']-.15]
 times += [p['abstractEnd']+1/60,r['copyBodyFromSeconds']-1/60,r['copyBodyFromSeconds']+1/60]
 f=D/f'{slug}.captioned.mp4';sheet=Image.new('RGB',(1440,math.ceil(len(times)/3)*300),'#111611');draw=ImageDraw.Draw(sheet)
 for i,t in enumerate(times):
  im=frame(f,t);x=i%3*480;y=i//3*300;sheet.paste(im,(x,y+27));draw.text((x+5,y+4),f'{id} {t:.3f}s',fill='white',font=font)
 sheet.save(W/'final-contact.png')
 s=p['segments'][0];g=s['guides'][0];im=frame(f,s['start']+(g['from']+g['to'])/2,1920);im.save(W/'opening-1080.png');im.resize((375,211),Image.Resampling.LANCZOS).save(W/'opening-mobile.png')
 qa=dict(id=id,status='technical-pass-visual-review-pending',results=results,subtitlesByteIdentical=True,sourceNativeSpeed=1,newTts=False,freezePadding=0,actualWholeHumanPlayback=False,actualWholeHumanListening=False,humanReview='pending',priorAudioEvidence='Existing complete AAC elementary stream unchanged; previous body audio review evidence reused.',visualContact=str(W/'final-contact.png'))
 save(W/'qa.json',qa);save(R/'projects'/slug/'production/actual-abstract-v6/qa.json',qa);print(id,'technical QA PASS; visual review pending',flush=True)
if __name__=='__main__':
 for id in sys.argv[1:]:run(id)
