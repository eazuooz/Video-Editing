"""Draft exposure changes; actual end-frame targets must be inspected separately."""
from pathlib import Path
import json, subprocess, io, math
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[3];B=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
base='shared/output/game-math-part2-full-series/sources/'
new='shared/output/private-math-concept-fit-20261023/sources/'
sources={
 'dorf':(base+'dorfromantik-official/Dorfromantik_Explanation_Trailer.webm','Dorfromantik'),
 'tiny':(new+'tiny-glade-official/release-date-trailer.mp4','Tiny Glade'),
 'tinyA':(new+'tiny-glade-official/release-date-trailer.mp4','Tiny Glade'),
 'tinyB':('shared/output/game-math-part2-teaching-revision/polygons-fresh-candidates/tiny-glade/tiny-glade-256965562.mp4','Tiny Glade'),
 'big':(base+'wzQLP0Z3zII.mp4','Big Walk'),
 'sub':(base+'dYyWmhVuc3w.mp4','Subnautica'),
 'split':(base+'8RZ1nPWzWtg.mp4','Split Fiction'),
 'town':(base+'FRfnXAIbA-M.mp4','Townscaper'),
 'portal':(base+'yFRbGppLaUI.mp4','Portal 2'),
 'launch':(new+'se2-official/launch.mp4','Space Engineers 2'),
 'se2':(new+'se2-official/vs1.2.mp4','Space Engineers 2')}
goals={
 'M13':{'02':15,'QG01':10,'QG02':12.8,'QG03':7.5,'11':10.6},
 'M15':{'02':13,'05-hole':8.5,'05-glass':12,'08-entry':12,'08-preview':6,'11':12,'14':14,'17':18.5,'19':14,'21':14},
 'M16':{'02':18.5,'05':8.3,'08':18.8,'11':11.2,'13':17.2,'16':16.2,'19':10.6,'21-view':10.5,'21-build':12},
 'M17':{'02':10.5,'05':18,'08':15.7,'11-carry':7.3,'11-place':10,'14':7.3},
 'M18':{'03':17.4,'06':9.2,'09-view':13.4,'09-build':16},
 'M19':{'02':17.5,'06':18.1,'07':16.7,'10':9.4,'11-front':10,'11-depth':11.4,'15':19},
 'M20':{'04':15.8,'05':9.3,'08':16.5,'09':15.8,'12':18.5}}
O=R/'shared/output/private-math-gameplay-20261024/end-frame-review';O.mkdir(parents=True,exist_ok=True)
for e in read(B/'edit-list-audit.json')['entries']:
 ep=e['id']
 if ep not in goals:continue
 old=R/'projects'/e['slug']/'production/concept-fit-v2';shots=read(old/'scene-visual-plan.json')['sourceShots'];tracks=read(old/'audio-mix.json').get('tracks',[]);plan=dict(episode=ep,slug=e['slug'],revision='gameplay-v3',patchSet='review-1',status='draft-target-review',sources={},patches=[],newTts=False)
 images=[]
 for key,s in shots.items():
  name=s['source'];path,game=sources[name];assert (R/path).exists(),path
  info=dict(path=path,game=game,rightsEvidence=(old/'source-evidence.json').relative_to(R).as_posix())
  tr=next((t for t in tracks if t['scene']==key and t.get('source')),None)
  if tr and (R/tr['source']).exists():info['audioPath']=tr['source']
  if name=='portal':info['resolutionException']='Explicit user approval for original Portal 2 scenes; source remains 720p.'
  plan['sources'][name]=info
  native=s['seconds'];start=s['start'];freeze=start+native-.1
  if ep=='M13' and key=='11':start=116;native=6.5;freeze=122.4
  dur=goals[ep][key];assert dur>=native
  p=dict(key=key,scene=s.get('scene',key),source=name,offset=s.get('offset',0),duration=dur,title=s['title'],meaning=s['model'].replace(' / ',' · '),segments=[dict(kind='motion',**{'in':start},seconds=native),dict(kind='still',**{'in':freeze},seconds=round(dur-native,5))],guides=[],modelCrop=[80,150,850,750],stillTargetReview='pending',role='Retain inspected action and continue the same explanation over its result; no added silence, slowdown or invented internal measurements.')
  plan['patches'].append(p)
  b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(freeze),'-i',str(R/path),'-frames:v','1','-vf','scale=640:360','-f','image2pipe','-vcodec','mjpeg','-'])
  im=Image.open(io.BytesIO(b)).convert('RGB');ImageDraw.Draw(im).text((8,8),f'{ep} {key} source {freeze:.2f}',fill='yellow',stroke_width=1,stroke_fill='black');images.append(im)
 save(B/f'{ep.lower()}-gameplay-plan.json',plan)
 for n in range(math.ceil(len(images)/6)):
  sheet=Image.new('RGB',(1920,720),'black')
  for i,im in enumerate(images[n*6:n*6+6]):sheet.paste(im,((i%3)*640,(i//3)*360))
  sheet.save(O/f'{ep}-{n}.jpg',quality=93)
 print(ep,'draft + exact end frames',flush=True)
