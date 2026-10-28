"""Assemble visual-only D29/D30 revision while copying approved AAC packets.

No TTS, remixes, platform operations, or original-output replacement. Heavy
encoding is explicit (--phase encode), separate from preparation/pixel review.
"""
from __future__ import annotations
from pathlib import Path
import argparse, hashlib, json, shutil, subprocess
from fractions import Fraction

ROOT=Path(__file__).resolve().parents[4]
MEDIA=Path('C:/Users/1/.codex/video-production/design-25-30-unity-v2-20261028')
BATCH=ROOT/'production/batches/design-25-30-unity-v2-20261028'
ALLOWED=['kind-to-beginners','respect-player-time']
CAPTURE_VERSION=None

def load(p):return json.loads(Path(p).read_text('utf-8-sig'))
def save(p,o):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n','utf-8')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def absolute(p):return Path(p) if Path(p).is_absolute() else ROOT/p
def run(args,log):
 with Path(log).open('w',encoding='utf-8') as out:subprocess.run(args,stdout=out,stderr=subprocess.STDOUT,check=True,cwd=ROOT)
def probe(p,count=False):
 args=['ffprobe','-v','error','-threads','2','-show_streams','-show_format','-of','json']
 if count:args+=['-count_frames']
 return json.loads(subprocess.check_output(args+[str(p)],text=True,encoding='utf-8'))
def stream_hash(p,selector):
 return subprocess.check_output(['ffmpeg','-v','error','-threads','2','-i',str(p),'-map',selector,'-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def authorized(slug):
 a=load(BATCH/'authorization.json');c=load(ROOT/'shared/publishing/video-production-control.json')
 assert slug in a['slugs'] and a['localProductionAuthorized'] and a['platformMutation'] is False and a['newTts'] is False
 return {'authorizationSha256':sha(BATCH/'authorization.json'),'currentControlSha256':sha(ROOT/'shared/publishing/video-production-control.json'),'controlRead':bool(c)}
def frozen(slug):
 p=ROOT/'projects'/slug;revision=load(p/'production/unity-visual-v2/visual-plan.json')
 for v in revision['baseline'].values():assert sha(absolute(v['path']))==v['sha256'],'Frozen baseline changed: '+v['path']
 ep=absolute(revision['baselineEditPlan']);assert sha(ep)==revision['baselineEditPlanSha256']
 return p,revision,load(ep)
def metadata_signature(c):
 # The v3 change restored game audio but did not alter rendered visual cuts.
 return {k:v for k,v in c.items() if k not in ['sourceAudioEnabled','sourceAudioReviewStatus','audioRightsReview']}

def capture_pin(slug):
 # These reviewed v4 captures predate the D26-only pose repair. Validate their
 # exact archived source/receipts, not the subsequently changed common runtime.
 pin=load(ROOT/'projects'/slug/'production/unity-visual-v2/capture-source-pin.json')
 assert pin['captureVersion']==CAPTURE_VERSION and pin['status']=='reviewed-native-version-retained'
 for record in pin['sourceEvidence']:
  assert sha(absolute(record['path']))==record['sha256'],'Pinned source evidence changed: '+record['path']
 snapshot=load(absolute(pin['fingerprintRecord']))
 assert snapshot['fingerprints']['D29D30Stage']==pin['compiledSourceFingerprint']
 audit=load(absolute(pin['nativePoseReview']))
 assert audit['status']=='bounded-native-pose-comparison-passed' and audit['compiledSourceFingerprint']==pin['compiledSourceFingerprint']
 for row in pin['captureReceipts']:
  receipt=absolute(row['path']);assert sha(receipt)==row['sha256'],'Pinned native receipt changed: '+row['path']
  r=load(receipt);assert r['status']=='complete' and r['compiledSourceFingerprint']==pin['compiledSourceFingerprint']
 return pin
def prepare(slug):
 authorization=authorized(slug);project,revision,plan=frozen(slug)
 pin=capture_pin(slug);expected_fingerprint=pin['compiledSourceFingerprint']
 out=MEDIA/slug/'final';out.mkdir(parents=True,exist_ok=True)
 joined=out/'join';joined.mkdir(exist_ok=True)
 old=absolute(plan['outputDir']);segments=[]
 for name in ['branding']+[c['id'] for c in plan['cuts']]+['membership']:
  cut=next((c for c in plan['cuts'] if c['id']==name),None)
  if cut is not None and cut['kind']=='explanation':
   src=MEDIA/slug/'render'/CAPTURE_VERSION/name/'unity.mp4';success=src.parent/'render-success.json'
   if not src.exists() or not success.exists():raise FileNotFoundError('Native capture pending: '+str(src))
   native=load(success);assert native['status']=='complete' and native['frames']==cut['frames']
   assert native['compiledSourceFingerprint']==expected_fingerprint,'Stale compiled scene: '+name
   count=cut['frames'];basis='new Unity explanation';extra={'unityReceipt':str(success),'scene':native['scene'],'usedAssets':native['assets'],'compiledSourceFingerprint':native['compiledSourceFingerprint']}
  else:
   src=old/(name+'.mp4');count=120 if name=='branding' else 600 if name=='membership' else cut['frames']
   basis='exact reused completed cut'
   if cut:
    prior=load(old/(name+'-render.json'));assert prior['outputSha256']==sha(src)
    assert metadata_signature(prior['signature']['cut'])==metadata_signature(cut),'Visual cut definition changed: '+name
   extra={}
  info=probe(src);v=next(x for x in info['streams'] if x['codec_type']=='video')
  assert (v['width'],v['height'])==(1920,1080) and Fraction(v['avg_frame_rate'])==60
  assert int(v['nb_frames'])==count
  dest=joined/(name+'.mp4');sig={'source':str(src),'sha256':sha(src),'frames':count}
  receipt=dest.with_suffix('.json')
  if dest.exists():assert receipt.exists() and load(receipt)['signature']==sig and load(receipt)['outputSha256']==sha(dest)
  else:
   run(['ffmpeg','-n','-v','error','-i',str(src),'-map','0:v:0','-an','-c:v','copy','-video_track_timescale','60000','-movflags','+faststart',str(dest)],dest.with_suffix('.log'))
   assert stream_hash(src,'0:v:0')==stream_hash(dest,'0:v:0')
   save(receipt,{'signature':sig,'outputSha256':sha(dest),'videoPacketsExact':True})
  segments.append({'id':name,'kind':cut['kind'] if cut else name,'frames':count,'source':str(src),'sourceSha256':sha(src),'join':str(dest),'joinSha256':sha(dest),'basis':basis,**extra})
 assert sum(x['frames'] for x in segments)==plan['totalFrames']
 concat=out/'concat.txt';concat.write_text('\n'.join("file '"+Path(s['join']).as_posix().replace("'","'\\''")+"'" for s in segments)+'\n','utf-8')
 source_caption=absolute(revision['baseline']['captionsKo']['path']).parent
 for name in ['captions.ko.srt','captions.en.srt','captions.ko.ass','captions.en.ass','captions.json']:
  src=source_caption/name
  if not src.exists():src=absolute(plan.get('captionsAss','')).parent/name
  if not src.exists():raise FileNotFoundError(str(src))
  dst=out/name
  if dst.exists():assert sha(dst)==sha(src)
  else:shutil.copy2(src,dst)
 old_master=absolute(revision['baseline']['videoBurnedCaptions']['path'])
 packet_hash=stream_hash(old_master,'0:a:0')
 record={'slug':slug,'stage':'prepared','authorization':authorization,'captureVersion':CAPTURE_VERSION,'compiledSourceFingerprint':expected_fingerprint,'baselineCaptioned':str(old_master),'baselineCaptionedSha256':sha(old_master),'baselineAudioPacketsSha256':packet_hash,'baselineEditPlanSha256':revision['baselineEditPlanSha256'],'expectedFrames':plan['totalFrames'],'seconds':plan['totalFrames']/60,'segments':segments,'captioned':str(out/(slug+'-unity-visual-v2-captioned.mp4')),'clean':str(out/(slug+'-unity-visual-v2-clean.mp4')),'newTtsRuns':0,'newAsrRuns':0,'audioRemix':False,'humanWholeReview':'pending'}
 save(out/'assembly-plan.json',record);return record
def encode(slug):
 authorized(slug);out=MEDIA/slug/'final';r=load(out/'assembly-plan.json')
 assert r['captureVersion']==CAPTURE_VERSION
 pin=capture_pin(slug);assert r['compiledSourceFingerprint']==pin['compiledSourceFingerprint']
 assert sha(r['baselineCaptioned'])==r['baselineCaptionedSha256']
 for s in r['segments']:assert sha(s['join'])==s['joinSha256']
 assert not Path(r['captioned']).exists() and not Path(r['clean']).exists(),'Preserve completed outputs'
 ass=(out/'captions.ko.ass').as_posix().replace(':',r'\:')
 command=['ffmpeg','-n','-hide_banner','-nostdin','-threads','3','-reinit_filter','0','-f','concat','-safe','0','-i',str(out/'concat.txt'),'-threads','2','-i',r['baselineCaptioned'],'-filter_complex_threads','2','-filter_complex',f"[0:v]setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709,setpts=N/(60*TB),split=2[clean][text];[text]ass='{ass}'[captioned]"]
 for label in ['clean','captioned']:
  command+=['-map','['+label+']','-map','1:a:0','-c:v','libx264','-threads','3','-preset','veryfast','-crf','17','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-video_track_timescale','60000','-c:a','copy','-movflags','+faststart',r[label]]
 run(command,out/'pair-encode.log')
 r['stage']='encoded-awaiting-visual-review';r['outputs']={}
 for kind in ['clean','captioned']:
  dst=Path(r[kind]);assert stream_hash(dst,'0:a:0')==r['baselineAudioPacketsSha256'],'Frozen AAC changed'
  r['outputs'][kind]={'path':str(dst),'sha256':sha(dst),'bytes':dst.stat().st_size,'exactApprovedAudioPackets':True}
 save(out/'assembly-result.json',r)
def verify(slug):
 out=MEDIA/slug/'final';r=load(out/'assembly-result.json');proof={'slug':slug,'scope':'complete stream structure/decode; not human whole viewing/listening','outputs':[]}
 for kind in ['clean','captioned']:
  p=Path(r[kind]);info=probe(p,True);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
  assert (v['width'],v['height'])==(1920,1080) and Fraction(v['avg_frame_rate'])==60
  assert int(v['nb_read_frames'])==r['expectedFrames']
  assert a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==2
  assert abs(float(info['format']['duration'])-r['seconds'])<.1
  packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,dts,duration','-of','json',str(p)],text=True))['packets']
  time_base=Fraction(v['time_base']);pts=sorted(int(x['pts']) for x in packets);dts=[int(x['dts']) for x in packets]
  assert len(pts)==r['expectedFrames'] and all(Fraction(t)*time_base==Fraction(i,60) for i,t in enumerate(pts)),'Final frame clock changed'
  assert all(a<b for a,b in zip(dts,dts[1:])),'Non-monotonic DTS'
  run(['ffmpeg','-v','error','-xerror','-threads','3','-i',str(p),'-f','null','-'],out/(kind+'-full-decode.log'))
  log=out/(kind+'-full-decode.log');assert not log.read_text('utf-8').strip()
  proof['outputs'].append({'kind':kind,'sha256':sha(p),'decodedFrames':int(v['nb_read_frames']),'dimensions':[v['width'],v['height']],'fps':v['avg_frame_rate'],'duration':info['format']['duration'],'everyFramePtsExact':True,'monotonicDts':True,'fullDecodeLogSha256':sha(log),'audioPacketsSha256':stream_hash(p,'0:a:0')})
 revision=load(ROOT/'projects'/slug/'production/unity-visual-v2/visual-plan.json')
 for key,filename in [('captionsKo','captions.ko.srt'),('captionsEn','captions.en.srt')]:assert sha(out/filename)==revision['baseline'][key]['sha256']
 proof['captionsExact']=True;proof['audioExact']=all(p['audioPacketsSha256']==r['baselineAudioPacketsSha256'] for p in proof['outputs'])
 save(out/'structural-verification.json',proof)
def samples(slug):
 from PIL import Image,ImageDraw,ImageFont
 out=MEDIA/slug/'final';r=load(out/'assembly-result.json');dst=out/'qa';dst.mkdir(exist_ok=True)
 index=[];timeline=0
 for s in r['segments']:
  if s['kind']=='explanation':
   for n,local in enumerate(sorted(set([0,int(s['frames']*.28),int(s['frames']*.60),s['frames']-1]))):
    global_frame=timeline+local;p=dst/(s['id']+f'-{n}.png')
    if not p.exists():run(['ffmpeg','-n','-v','error','-ss',f'{global_frame/60:.9f}','-threads','2','-i',r['captioned'],'-frames:v','1','-threads','1',str(p)],p.with_suffix('.log'))
    img=Image.open(p);img.resize((375,211),Image.Resampling.LANCZOS).save(dst/(p.stem+'-mobile.png'))
    index.append({'cutId':s['id'],'globalFrame':global_frame,'seconds':global_frame/60,'image':str(p),'mobile':str(dst/(p.stem+'-mobile.png'))})
  timeline+=s['frames']
 font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
 for start in range(0,len(index),8):
  page=index[start:start+8];board=Image.new('RGB',(1500,480),(25,25,25));draw=ImageDraw.Draw(board)
  for i,row in enumerate(page):
   x=(i%4)*375;y=(i//4)*240;board.paste(Image.open(row['mobile']),(x,y));draw.text((x+5,y+214),f"{row['cutId']} / {row['seconds']:.2f}s",font=font,fill='white')
  board.save(dst/f'board-{start//8+1:02d}.jpg',quality=94)
 save(dst/'pixel-sample-index.json',{'samples':index,'purpose':'All changed explanation cuts at four states, actual final captions, 1080 and375; direct visual review remains required','humanReview':'pending'})
def main():
 global CAPTURE_VERSION
 p=argparse.ArgumentParser();p.add_argument('--slug',choices=ALLOWED,required=True);p.add_argument('--phase',choices=['prepare','encode','verify','samples'],required=True);p.add_argument('--capture-version',required=True);a=p.parse_args()
 assert a.capture_version.startswith('v') and a.capture_version[1:].isdigit()
 CAPTURE_VERSION=a.capture_version
 globals()[a.phase](a.slug);print(a.slug,a.phase,'complete',flush=True)
if __name__=='__main__':main()
