"""CPU source frames and PCM-derived timing; preview estimates are explicitly marked."""
from pathlib import Path
import argparse,json,math,subprocess,hashlib
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
slugs=['shorts-d2r-renderer-logic-separation','shorts-d2r-controller-input-adapter']
parser=argparse.ArgumentParser();parser.add_argument('--actual',action='store_true');parser.add_argument('--slug',choices=slugs);args=parser.parse_args()
for slug in [args.slug] if args.slug else slugs:
 p=R/'projects'/slug
 plan=read(p/'planning/production-plan.json')
 assert plan.get('independentFootageViewed') and plan.get('directReview'), 'Inspect the independent source before preparing visuals.'
 lines=read(p/'script/narration.spoken.ko.json')['scenes'][0]['lines'];spec=read(p/'production/section-plan.json')
 if args.actual:
  a=read(p/'production/local/audio-v1/voice/narration.timing.json');captions=read(p/'script/captions.json');offset=captions['voiceOffsetSeconds'];entries=[dict(start=r['start']+offset,end=r['end']+offset) for r in a['entries']];entries[0]['start']=0;duration=captions['durationSeconds']
 else:
  entries=[];end=0
  for line in lines:
   seconds=max(4,len(line)/7.0);entries.append(dict(start=end,end=end+seconds));end+=seconds+.28
  duration=entries[-1]['end']+.35
 sections=[]
 for i,s in enumerate(spec):
  start=entries[i]['start'];end=entries[i+1]['start'] if i+1<len(entries) else duration
  sections.append(dict(**s,start=round(start*60)/60,end=round(end*60)/60,startFrame=round(start*60),endFrame=round(end*60)))
 frames=round(duration*60);duration=frames/60;sections[-1]['end']=duration;sections[-1]['endFrame']=frames
 # Use only the inspected six seconds. Speech can continue over the same topic's diagram.
 bounded=[]
 for s in sections:
  if s['kind']=='game' and s['endFrame']-s['startFrame']>360:
   endFrame=s['startFrame']+360
   bounded.extend([{**s,'endFrame':endFrame,'end':endFrame/60},{**s,'id':s['id']+'-explain','kind':'diagram','startFrame':endFrame,'start':endFrame/60}])
  else:bounded.append(s)
 sections=bounded
 renderer=slug.endswith('logic-separation')
 config=dict(topic='renderer' if renderer else 'controller',head=['그래픽을 바꿨는데','전투는 그대로?'] if renderer else ['마우스로 만들었는데','패드는 어떻게?'])
 timing=dict(revision='distinctive-ten-v1',previewOnly=not args.actual,frames=frames,durationSeconds=duration,sections=sections,sources={},cues=captions['cues'] if args.actual else [],reactions=[dict(kind='realize',start=.2,end=min(2.7,sections[0]['end']))])
 fingerprint=hashlib.sha256(json.dumps(dict(timing=timing,captionInputs=captions.get('timingInputs') if args.actual else None,builder=hashlib.file_digest(Path(__file__).open('rb'),'sha256').hexdigest()),sort_keys=True).encode()).hexdigest()[:16]
 timing['frameRoot']='game-frames/'+fingerprint
 timing['inputFingerprint']=fingerprint
 def extract(command,out,count):
  receipt=out/'extraction.json'
  existing=list(out.glob('*.jpg'))
  if existing:
   assert receipt.exists() and read(receipt).get('inputFingerprint')==fingerprint and len(existing)==count, 'Preserve partial or different extraction for inspection.'
   return
  subprocess.run(command,check=True)
  assert len(list(out.glob('*.jpg')))==count, 'Incomplete source extraction.'
  save(receipt,dict(inputFingerprint=fingerprint,frames=count))
 media=B/'local/d2r-official'
 for s in sections:
  if s['kind']!='game':continue
  out=p/'production/local'/timing['frameRoot']/s['id'];out.mkdir(parents=True,exist_ok=True)
  count=s['endFrame']-s['startFrame'];seconds=count/60
  if renderer:
   assert seconds<=6,'Paired source time must advance continuously within the six-second capture.'
   # Same-frame timeline: classic then remaster. Source switch is editorial.
   pair='tristram' if s['id']=='game' else 'barracks';variants=['old','new'];cursor=0;s['cuts']=[]
   for index,variant in enumerate(variants):
    segment=count//2 if index==0 else count-count//2
    source=media/'comparison'/f'{pair}_{variant}_comparison_slider.mp4'
    start=cursor/60
    key=pair+'-'+variant;timing['sources'][key]=dict(path=source.relative_to(R).as_posix(),sourceSHA256=hashlib.file_digest(source.open('rb'),'sha256').hexdigest(),originalOffsetSeconds=0,nativeAudioAdopted=False)
    s['cuts'].append(dict(source=key,sourceStart=start,sourceEnd=start+segment/60,start=s['start']+cursor/60,end=s['start']+(cursor+segment)/60,rate=1,nativeAudioAdopted=False))
    # Separate segment folders preserve partial output without overwriting it.
    segment_out=out/variant;segment_out.mkdir(exist_ok=True)
    extract(['ffmpeg','-v','error','-threads','2','-ss',str(start),'-i',str(source),'-vf','fps=60','-frames:v',str(segment),'-start_number',str(cursor),'-threads','1','-q:v','3','-n',str(segment_out/'%05d.jpg')],segment_out,segment)
    import shutil
    for file in segment_out.glob('*.jpg'):
     target=out/file.name
     if not target.exists():shutil.copy2(file,target)
    cursor+=segment
   s['source']=pair+'-old';s['nativeAudioAdopted']=False;s['edit']='editorial old/new comparison, not live keypress capture'
  else:
   assert seconds<=6,'Inspect more source before extending this introduction.'
   source=media/'D2R_Launch_Broll_.mp4';key='launch-pc'
   timing['sources'][key]=dict(path=source.relative_to(R).as_posix(),sourceSHA256=read(media/'receipt.json')['sha256'],originalOffsetSeconds=0,nativeAudioAdopted=True,audioListening='pending')
   extract(['ffmpeg','-v','error','-threads','2','-ss','23','-i',str(source),'-vf','fps=60','-frames:v',str(count),'-start_number','0','-threads','1','-q:v','3','-n',str(out/'%05d.jpg')],out,count)
   s.update(source=key,sourceStart=23,sourceEnd=23+seconds,rate=1,nativeAudioAdopted=True)
 for previous in [p/'production/visual-timing.json',p/'production/local/visual-timing.json']:
  if previous.exists():
   previous_hash=hashlib.file_digest(previous.open('rb'),'sha256').hexdigest()
   snapshot=p/'production/local/timing-history'/(previous_hash+'.json')
   if not snapshot.exists():save(snapshot,read(previous))
 save(p/'production/visual-config.json',config);save(p/'production/visual-timing.json',timing);save(p/'production/local/visual-timing.json',timing)
 print(slug,frames,'actual' if args.actual else 'preview-only',flush=True)
