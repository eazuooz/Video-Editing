"""Encoded caption presence, topic/transition samples and exact delivery clocks."""
from common import *
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from urllib.parse import quote

def points(e,audio):
 changes=audio['changes'];total=audio['frames'];rows={}
 def add(n,role):
  n=max(0,min(total-1,round(n)));rows.setdefault(n,[]).append(role)
 add(60,'branding');add(total-300,'member-ending')
 add(map_frame(e['opening']['startFrame'],changes)+90,'opening')
 add(map_frame(round(e['summaryAt']*60),changes)+180,'recap')
 for key in e['studyDefinitions']:
  choices=[x for x in e['replacementSpans'] if x['key']==key and x['mode']!='native']
  if not choices:choices=[x for x in e['replacementSpans'] if x['key']==key]
  span=max(choices,key=lambda x:x['end']-x['start']);add(map_frame((span['start']+span['end'])//2,changes),'study:'+key)
 for span in e['replacementSpans']:
  for n in [map_frame(span['start'],changes),map_frame(span['end'],changes)]:
   add(n-1,'join-before');add(n,'join-after')
 for i,c in enumerate(srt(WORK/e['id']/'ko.srt')):add((c['start']+c['end'])*30,'caption:'+str(i))
 for lead in e.get('nativeLeads',[]):
  for p in range(3):add(map_frame(lead['start'],changes)+p*lead['framesPerPass']+lead['framesPerPass']//2,'native:'+lead['bank']+':'+str(p+1))
 return [dict(frame=n,roles=roles) for n,roles in sorted(rows.items())]

def extract_during_decode(e,audio,movie):
 folder=WORK/e['id']/'encoded-qa';folder.mkdir(exist_ok=True);rows=points(e,audio)
 assert folder.resolve().is_relative_to(WORK.resolve())
 for p in folder.glob('*.jpg'):p.unlink()
 expr='+'.join('eq(n,'+str(r['frame'])+')' for r in rows)
 ff('-threads',2,'-i',movie,'-map','0:v:0','-vf',"select='"+expr+"'",'-fps_mode','vfr','-q:v',2,'-start_number',0,folder/'%04d.jpg',
    '-map','0:a:0','-f','null','NUL')
 files=sorted(folder.glob('*.jpg'));assert len(files)==len(rows),(e['id'],len(files),len(rows))
 for r,p in zip(rows,files):r['path']=str(p)
 save(folder/'frames.json',dict(episode=e['id'],movieSha256=sha(movie),samples=rows,allSelectedDecoded=True))

def packet_clock(p,frames):
 raw=run(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts','-of','json',p],True)
 packets=__import__('json').loads(raw)['packets'];pts=sorted(int(p['pts']) for p in packets)
 assert len(pts)==frames and pts[0]==0 and all(b-a==1000 for a,b in zip(pts,pts[1:])),(p,'PTS discontinuity')
 return dict(frames=frames,firstPts=0,lastPts=pts[-1],ptsStep=1000,timeBase='1/60000',status='passed')

def check_episode(ep):
 folder=WORK/ep/'encoded-qa';m=read(folder/'frames.json');layout=read(WORK/ep/'caption-layout.json')['cues'];checks=[];posters=[]
 for r in m['samples']:
  with Image.open(r['path']) as im:
   for role in r['roles']:
    if role.startswith('caption:'):
     index=int(role.split(':')[1]);g=layout[index]['geometry'];x,y,w,h=g['x'],g['y'],g['width'],g['height']
     region=np.asarray(im.crop((x+5,y+5,x+w-5,y+h-5)))
     white=float(np.mean(np.all(region>215,axis=2)));ink=float(np.mean(np.max(region,axis=2)<95))
     assert white>.50 and ink>.005,(ep,index,'encoded caption absent or occluded',white,ink)
     checks.append(dict(index=index,frame=r['frame'],whiteFraction=white,inkFraction=ink,geometryPassed=True))
   if any(x.startswith('study:') for x in r['roles']) or any(x in r['roles'] for x in ['opening','recap']):
    name=next((x for x in r['roles'] if x.startswith('study:')),'opening' if 'opening' in r['roles'] else 'recap').replace(':','-')
    im.save(folder/(name+'.png'));im.resize((375,211),Image.Resampling.LANCZOS).save(folder/(name+'-mobile.png'));posters.append(dict(name=name,path=str(folder/(name+'.png'))))
 assert len(checks)==len(layout),(ep,len(checks),len(layout))
 save(folder/'caption-presence.json',dict(allCues=len(checks),passed=True,checks=checks,
  limitation='Automated box/ink presence and measured layout for every cue; semantic/motion/mobile inspection is separately scoped.'))
 save(folder/'posters.json',posters)
 for page in range((len(posters)+5)//6):
  sheet=Image.new('RGB',(1440,660),'#080c0a');d=ImageDraw.Draw(sheet)
  for j,p in enumerate(posters[page*6:(page+1)*6]):
   x=(j%3)*480;y=(j//3)*330
   with Image.open(p['path']) as im:sheet.paste(im.resize((480,270)),(x,y+35))
   d.text((x+5,y+3),ep+' '+p['name'],font=ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf',23),fill='white')
  sheet.save(folder/f'contact-{page}.jpg',quality=94)
 print(ep,'all',len(checks),'encoded caption cues present;',len(posters),'topic/overview/recap samples',flush=True)

if __name__=='__main__':
 import sys
 for ep in sys.argv[1:] or SCOPE:check_episode(ep)
