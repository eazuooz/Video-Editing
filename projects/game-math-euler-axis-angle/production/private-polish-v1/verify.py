"""Current input-bound layout, clock, audio identity and whole decode checks."""
import argparse,itertools,json,re,subprocess
from pathlib import Path
import common as c
import unity as u

def layout():
 b=u.b;previous={};total=0;records=[]
 for slot in c.read(c.H/'unity-placement.json')['placements']:
  sid=slot['sceneId'];pair=sid in u.PAIRS and not(sid=='16' and slot['lineIndex']==1)
  states=[json.loads(x) for x in Path(slot['anchors']).read_text().splitlines()]
  labels=b.clip_label_layouts(states,pair,previous.get(sid));previous[sid]=labels[-1]
  for state,items in zip(states,labels):
   expected={(g,k,a) for g in (['a','b'] if pair else ['a']) for k in ['world','body'] for a in 'xyz'}
   shown={(x['group'],k,x['axis']) for x in items for k in (['world','body'] if x['text'].startswith('world/body') else [x['kind']])}
   assert not(expected-shown),(sid,expected-shown)
   for a,z in itertools.combinations(items,2):assert not b.boxes_overlap(a['bbox'],z['bbox']),(sid,a,z)
   for x in items:
    box=x['bbox'];bound=x['plotBounds']
    assert box[0]>=bound[0]-.001 and box[1]>=bound[1]-.001 and box[2]<=bound[2]+.001 and box[3]<=bound[3]+.001
   total+=1
  records.append({'scene':sid,'cue':slot['lineNumber'],'states':len(states),'pairLayout':pair})
 report={'status':'pass','framesOfNativeMotionChecked':total,'slots':records,'boundsAndNoLabelCollision':True,
  'allAxesPresent':True,'placementSha256':c.sha(c.H/'unity-placement.json'),'actualPixelReview':'recorded separately'}
 c.save(c.H/'layout-qa.json',report);print('Current layout passed:',total,'native states',flush=True)

def pcm(path):
 result=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-vn','-c:a','pcm_s16le','-f','hash','-hash','sha256','-'],text=True)
 return result.strip()

def final():
 c.authorized();out=c.read(c.H/'outputs.json');checks=[]
 original=c.O/'baseline-audio.m4a';audio_hash=pcm(original)
 for item in out['outputs']:
  path=c.R/item['path'];assert c.sha(path)==item['sha256']
  if path.suffix=='.mp4':
   v=c.video(path);assert (v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==(1920,1080,'60/1',67885)
   assert pcm(path)==audio_hash,'Recovered narration PCM differs after mux; investigate priming/time stamps'
   c.run(['ffmpeg','-hide_banner','-v','error','-xerror','-threads','4','-i',path,'-f','null','-'],'decode-'+path.name+'.log')
   checks.append({'file':item['path'],'sha256':item['sha256'],'fullDecode':'pass','frames':67885,
     'decodedAudioEqualsRecoveredSource':True,'audioPcmSha256':audio_hash})
 layout=c.read(c.O/'caption-layout.json');assert len(layout['cues'])==253
 for lang,orig in [('ko',c.T['koCaptions']),('en',c.T['enCaptions'])]:
  for a,z in zip(layout['cues'],orig):
   assert ''.join(a[lang].split())==''.join(z['text'].split())
   assert abs(a['start']-z['start'])<.00001 and abs(a['end']-z['end'])<.00001
   assert len(a[lang+'Lines'])<=2
 c.save(c.H/'technical-qa.json',{'status':'pass','outputs':checks,'bilingualCues':253,'originalWordsAndTimesRetained':True,
  'fixedCaptionGeometry':{'center':[960,970],'fontPx':48,'maxLines':2},'audioRecoveryLimitation':'Recovered AAC performance preserved exactly when decoded; original production PCM unavailable.',
  'fullHumanListening':'pending','source720PixelsUsed':False})
 print('Full files decoded; recovered audio unchanged;253 cue pairs preserved.',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['layout','final']);a=p.parse_args();globals()[a.mode]()
