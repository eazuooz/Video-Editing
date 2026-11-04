from pathlib import Path
import sys,json,hashlib,subprocess,math
ROOT=Path('D:/Github/VideoEditing')
OUT=ROOT/'production/batches/animation-18-20261031/sources/A01'
sys.path.insert(0,str(ROOT/'production/batches/animation-18-20261031/visual-feasibility/local-deps'))
import cv2,numpy as np
cv2.setNumThreads(2)
def source(path,url,game,genre,windows,rate=2):
 return dict(path=path,url=url,game=game,genre=genre,windows=windows,reviewSamplingFps=rate)
S={
 'inkling':source(str(OUT/'smash-inkling.mp4'),'https://www.youtube.com/watch?v=O4-7-bJWUsc','Super Smash Bros. Ultimate','platform fighting',[[2,6.2,'weapon-body-direction'],[6.6,9,'ground-squid-transition'],[9.6,13.5,'roller-and-attack-pose']],4),
 'piranha':source(str(OUT/'smash-piranha.mp4'),'https://www.youtube.com/watch?v=3sZsk8VHY2g','Super Smash Bros. Ultimate','platform fighting',[[4.4,6.7,'nonhumanoid-idle-expression'],[12,18,'stem-extension-and-projectile'],[18.2,24,'bend-turn-and-rise']],4),
 'mario':source(str(ROOT/'projects/computer-controlled-players/production/local/batch-v1/sources/smash-mario-INk1W8OujQI.mp4'),'https://www.youtube.com/watch?v=INk1W8OujQI','Super Smash Bros. Ultimate','platform fighting',[[2,3.8,'whole-body-greeting'],[4,7.7,'punch-then-prop-aim'],[8,10.8,'expressive-outfit-gesture']],4),
 'samus':source(str(ROOT/'projects/computer-controlled-players/production/local/batch-v1/sources/smash-samus-I9tcvSeemVo.mp4'),'https://www.youtube.com/watch?v=I9tcvSeemVo','Super Smash Bros. Ultimate','platform fighting',[[2,5.8,'aim-charge-release'],[6,12.8,'air-ground-and-grab-actions']],4),
 'vf':source(str(ROOT/'production/batches/animation-18-20261031/visual-feasibility/vf-training.mp4'),'https://www.youtube.com/watch?v=KkGmeofGSw0','New VIRTUA FIGHTER Project','3D fighting',[[18,24,'two-body-contact'],[24,28,'duck-and-counter'],[28,34,'hit-recovery'],[34,40,'pose-contact-recovery'],[40,46,'dodge-and-kick'],[51,55,'close-hit-reaction'],[55,59,'ground-to-standing']],4),
 'goose-retail':source(str(OUT/'goose-official.mp4'),'https://www.youtube.com/watch?v=YRcGyzhT24g','Untitled Goose Game','stealth-puzzle sandbox',[[3,11,'honk-and-attention'],[20.5,23.4,'two-body-coordination'],[25,29,'beak-pickup-carry-drop'],[36,43,'bow-flower-body-expression'],[54,57,'honk-and-human-reaction']],2),
 'goose-prealpha':source(str(OUT/'goose-prealpha.mp4'),'https://www.youtube.com/watch?v=wQknBJo4aBQ','Untitled Goose Game','stealth-puzzle sandbox',[[6,23,'swim-walk-bend-pickup-drop'],[30,48,'gate-beak-prop-transport'],[66,90,'honk-key-pickup-human-reaction'],[96,116,'hat-reach-pickup-carry'],[117,129,'standing-walking-prop-handoff'],[132,141,'beak-ground-contact'],[144,158,'sprinkler-surprise-and-turn'],[159,177,'head-down-search-and-body-orientation']],2),
}
result={'dateKst':'2026-10-31','scope':'A01 candidate windows; no footage interval repeated','sources':{},'totalCandidateSeconds':0}
for key,s in S.items():
 p=Path(s['path']); probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,sample_rate,channels','-show_entries','format=duration','-of','json',str(p)]))
 cap=cv2.VideoCapture(str(p)); fps=cap.get(cv2.CAP_PROP_FPS); pages=[]; tiles=[]; page=1
 def flush():
  global tiles,page
  if not tiles:return
  while len(tiles)<20:tiles.append(np.zeros((294,480,3),np.uint8))
  sheet=np.vstack([np.hstack(tiles[i:i+4]) for i in range(0,20,4)])
  name=f'review-{key}-{page:02d}.jpg';cv2.imwrite(str(OUT/name),sheet,[cv2.IMWRITE_JPEG_QUALITY,88]);pages.append(name);page+=1;tiles=[]
 for start,end,role in s['windows']:
  for t in np.arange(start,end,1/s['reviewSamplingFps']):
   cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,frame=cap.read()
   if not ok:raise RuntimeError((key,t))
   tile=np.zeros((294,480,3),np.uint8);tile[:270]=cv2.resize(frame,(480,270),interpolation=cv2.INTER_AREA)
   cv2.putText(tile,f'{key}  {t:06.2f}s  {role[:23]}',(6,288),cv2.FONT_HERSHEY_SIMPLEX,.43,(240,240,240),1,cv2.LINE_AA)
   tiles.append(tile)
   if len(tiles)==20:flush()
 flush();cap.release()
 sha=hashlib.sha256(p.read_bytes()).hexdigest();duration=sum(b-a for a,b,_ in s['windows'])
 result['sources'][key]={**s,'sha256':sha,'decoded':probe,'candidateSeconds':round(duration,3),'contactSheets':pages,'visualReviewStatus':'pending explicit inspection','audioTrackPreserved':any(x['codec_type']=='audio' for x in probe['streams']),'originalSpeed':True,'cutTimingNotFinal':True}
 result['totalCandidateSeconds']+=duration
 print(key,len(pages),round(duration,2),flush=True)
result['totalCandidateSeconds']=round(result['totalCandidateSeconds'],3)
(OUT/'source-window-inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('total',result['totalCandidateSeconds'])
