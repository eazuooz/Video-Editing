"""Current encoded outputs: complete frame decode, PTS, AAC and subtitle integrity."""
from pathlib import Path
import json, subprocess, hashlib, re, argparse
import numpy as np
ROOT=Path(__file__).resolve().parents[2];SLUG='ai-game-development-human-craft'
from revision_paths import workroot
OUT=workroot(ROOT)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):
 p=subprocess.run(args,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,creationflags=subprocess.CREATE_NO_WINDOW)
 if p.returncode or p.stderr.strip():raise RuntimeError(p.stderr.decode('utf-8','replace'))
 return p.stdout
parser=argparse.ArgumentParser();parser.add_argument('--clean-only',action='store_true');args=parser.parse_args()
m=read(ROOT/f'projects/{SLUG}/project.json');assembly=read(OUT/'assembly.json');expected=assembly['frames']
receipts=OUT/'integrity-stages';receipts.mkdir(exist_ok=True)
results=[];aac=[]
mix_packets=run(['ffmpeg','-v','error','-i',str(OUT/'audio/mix.m4a'),'-map','0:a:0','-c:a','copy','-f','adts','-'])
mix_packet_sha=hashlib.sha256(mix_packets).hexdigest()
for key in (['videoClean'] if args.clean_only else ['videoClean','videoBurnedCaptions']):
 path=ROOT/m['paths'][key]
 receipt=receipts/(key+'.json');current_sha=sha(path)
 if receipt.exists():
  prior=read(receipt)
  if (prior['sha256']==current_sha and prior['frames']==expected and prior['aacAdtsSha256']==mix_packet_sha
      and all(prior[x]=='pass' for x in ['fullVideoDecode','fullAudioDecode','pts'])):
   results.append(prior);aac.append(prior['aacAdtsSha256']);continue
 metadata=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
 v=next(s for s in metadata['streams'] if s['codec_type']=='video');a=next(s for s in metadata['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',expected)
 assert a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==2
 # -show_frames actually decodes the complete video; any error is fatal.
 frames=json.loads(run(['ffprobe','-v','error','-err_detect','explode','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time,pkt_duration_time','-of','json',str(path)]))['frames']
 pts=np.array([float(f['best_effort_timestamp_time']) for f in frames]);assert len(pts)==expected
 assert abs(pts[0])<=.0001 and np.max(np.abs(np.diff(pts)-1/60))<.0001
 assert abs(float(metadata['format']['duration'])-expected/60)<.08
 packets=run(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','adts','-'])
 digest=hashlib.sha256(packets).hexdigest();aac.append(digest)
 assert digest==mix_packet_sha,'Encoded master differs from the reviewed final AAC mix'
 run(['ffmpeg','-v','error','-err_detect','explode','-i',str(path),'-map','0:a:0','-f','null','-'])
 result={'path':path.relative_to(ROOT).as_posix(),'sha256':current_sha,'bytes':path.stat().st_size,'frames':len(pts),'fullVideoDecode':'pass','fullAudioDecode':'pass','pts':'pass','duration':float(metadata['format']['duration']),'aacAdtsSha256':digest}
 receipt.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');results.append(result)
if args.clean_only:
 print('Current clean master full decode/PTS/AAC passed; captioned integrity remains pending.')
 raise SystemExit(0)
assert aac[0]==aac[1],'Clean/captioned audio differs'
script=read(ROOT/m['paths']['script']);translated=read(ROOT/m['paths']['scriptEn'])
cue_reports=[]
def normalized(t):return re.sub(r'\s+','',t)
for lang,script in [('ko',script),('en',translated)]:
 path=OUT/f'final.{lang}.srt';blocks=re.split(r'\r?\n\s*\r?\n',path.read_text(encoding='utf-8').strip())
 texts=[];previous=0;count=0
 for block in blocks:
  lines=block.splitlines();count+=1;assert int(lines[0])==count
  a,b=lines[1].split(' --> ')
  def sec(t):
   h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
  a,b=sec(a),sec(b);assert 2<=a<b<=expected/60-10+.02 and a>=previous-.001;previous=b
  assert len(lines[2:])<=2;texts+=lines[2:]
 assert normalized(''.join(texts))==normalized(''.join(line for s in script['scenes'] for line in s['lines'])),'Caption text lost/added'
 cue_reports.append({'language':lang,'cues':count,'sha256':sha(path),'allScriptTextRetained':True,'introAndMemberClear':True})
(OUT/'encoded-integrity.json').write_text(json.dumps({'outputs':results,'identicalAAC':True,'captions':cue_reports,'semanticAndListeningReview':'separate-review-ledger'},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'fullDecodeAndPTS':'pass','frames':expected,'identicalAAC':True,'captions':cue_reports}))
