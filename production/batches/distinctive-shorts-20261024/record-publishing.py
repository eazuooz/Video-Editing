"""Record only observed Studio state for the explicitly authorized Shorts batch."""
import json,sys,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[3]
B=Path(__file__).parent
slug,vid,stage=sys.argv[1:4]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return json.loads(p.read_text(encoding='utf8'))
def save(p,d): p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=R/'projects'/slug/'publishing/youtube-upload.json'
j=read(p); assert j['videoId'] in (None,vid)
j['videoId']=vid;j['url']='https://www.youtube.com/shorts/'+vid;j['updatedAt']=now
j.setdefault('observations',[]).append({'at':now,'stage':stage,'details':sys.argv[4:]})
if stage=='scheduled':
 j['status']='scheduled-settings-in-progress';j['schedule'].update(status='saved-confirmed-in-studio',active=True,verifiedAt=now)
 j['platformStateVerified']=True
 j['checks']={'copyright':'no-issues-observed','advertiserSuitability':'no-issues-observed','processing':'complete'}
elif stage in ('ko','en'):
 for s in j['subtitles']:
  if s['language']==stage:s['status']='published-verified-in-studio';s['verifiedAt']=now
elif stage=='english-metadata':j['englishMetadataStatus']='published-verified-in-studio'
elif stage=='playback':j['platformPlayback']={'observedAt':now,'evidence':sys.argv[4:]}
save(p,j)
if stage=='scheduled':
 sched=read(B/'publishing-schedule.json')
 for x in sched['items']:
  if x['slug']==slug:x.update(videoId=vid,status=j['status'],verifiedAt=now)
 save(B/'publishing-schedule.json',sched)
 cpath=R/'shared/publishing/video-production-control.json';c=read(cpath)
 c['shortsPublishingBatchAuthorization']=sched;save(cpath,c)
 cp=R/'projects'/slug/'production/checkpoint.json';c=read(cp);c['youtube']={'videoId':vid,'schedule':j['schedule'],'status':j['status']};save(cp,c)
print(json.dumps({'slug':slug,'videoId':vid,'recorded':stage},ensure_ascii=False))
