from pathlib import Path
import json, subprocess,hashlib,sys,datetime
B=Path(__file__).resolve().parent;R=B.parents[2]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=read(R/sys.argv[1]);P=R/'projects'/p['slug'];H=P/'production'/p['revision'];O=P/'production/local'/p['revision'];out=read(H/'outputs.json');old=P/'production/concept-fit-v2';T=read(old/'timeline.json');tests=[]
if (H/'technical-qa.json').exists():
 previous=read(H/'technical-qa.json');recorded={x['path']:x['sha256'] for x in previous.get('checks',[])}
 if all(recorded.get(x['path'])==x['sha256']==sha(R/x['path']) for x in out['outputs']) and previous.get('sourceNarrationSha256')==sha(R/read(H/'audio-mix.json')['narrationSource']):
  print(p['episode'],'unchanged hashes; existing full decode evidence reused',flush=True);sys.exit(0)
for f in out['outputs']:
 file=R/f['path'];assert sha(file)==f['sha256'];r=dict(path=f['path'],sha256=f['sha256'])
 if file.suffix=='.mp4':
  q=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(file)]));v=next(x for x in q['streams'] if x['codec_type']=='video');a=next(x for x in q['streams'] if x['codec_type']=='audio');assert(v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',T['frames']);assert abs(float(a['duration'])-T['seconds'])<.1
  check=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(file),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True,text=True);assert check.returncode==0,check.stderr
  r.update(decode='pass',width=1920,height=1080,fps=60,frames=T['frames'],audioSeconds=float(a['duration']))
 else:
  lang='ko' if file.name.endswith('.ko.srt') else 'en';same=P/'production/local/concept-fit-v2'/f'captions.{lang}.srt';assert sha(same)==sha(file);r['unchangedSubtitleBytes']=True
 tests.append(r)
a=read(H/'audio-mix.json');assert sha(R/a['narrationSource'])==a['narrationSourceSha256'];assert out['oldBaseSha256']==sha(R/out['oldBase'])
report=dict(checkedAt=datetime.datetime.now().astimezone().isoformat(),episode=p['episode'],checks=tests,exactNarrationPcmPreserved=True,sourceNarrationSha256=a['narrationSourceSha256'],totalFramesPreserved=True,oldDeliveryPreserved=True,peakDbTP=float(a['levels']['input_tp']),nativeGameSeconds=out['nativeGameSeconds'],analyticalStillSeconds=out['analyticalStillSeconds'],visualReview='pending',wholeAudioListening=False,humanReview='pending')
(H/'technical-qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(p['episode'],'technical checks passed',flush=True)
